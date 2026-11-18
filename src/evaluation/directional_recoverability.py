"""Fixed six-role reference-aware capacity diagnostic; no learned predictor or IO on import."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000
from src.distortion_generation.directional_exposure_recipe import render_rgb
from src.model_training.blended_recovery_targets import fit_target, render_rgb8

VERSION = 'fixed_directional_recoverability_v1'
ROLES = {'identity': ('clean', 'none'), 'colour_only': ('color', 'none'),
         'exposure_under': ('exposure', 'under'), 'exposure_over': ('exposure', 'over'),
         'combined_under': ('combined', 'under'), 'combined_over': ('combined', 'over')}


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def array_hash(value):
    return hashlib.sha256(str(value.dtype).encode() + str(value.shape).encode() + value.tobytes()).hexdigest()


def validate_source(source):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', source['source_id']):
        raise ValueError('Safe unique source ID required')
    if type(source['generated_fixture']) is not bool:
        raise ValueError('Explicit unchanged source provenance required')
    image, alpha, protected = source['reference'], source['alpha'], source['protected']
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[-1] != 3 or not image.size:
        raise ValueError('Nonempty RGB8 reference required')
    if (alpha.shape != image.shape[:2] or not np.issubdtype(alpha.dtype, np.floating)
            or not np.isfinite(alpha).all() or (alpha < 0).any() or (alpha > 1).any()
            or not (alpha > 0).any()):
        raise ValueError('Finite nonempty application alpha in [0,1] required')
    if protected.dtype != bool or protected.shape != alpha.shape:
        raise ValueError('Matching boolean protection required')
    if (alpha[protected] != 0).any():
        raise ValueError('Protection must already veto application alpha; never repair silently')


def raw_distortion(reference, role):
    """Preclip values for clipping accounting, checked independently in generated QA."""
    x = reference.astype(float) / 255
    if role.endswith('_under'):
        x = 1.08 * (x ** (1 / .70) - 1) + 1 - 35 / 255
    elif role.endswith('_over'):
        x = 1.08 * x ** .70 + 35 / 255
    if role == 'colour_only' or role.startswith('combined_'):
        x = x + [-10 / 255, 0, 10 / 255]
    return x


def regions(alpha):
    return {'primary': alpha > 0, 'core': alpha == 1,
            'feather': (alpha > 0) & (alpha < 1), 'whole': np.ones(alpha.shape, bool)}


def metrics(image, reference, mask):
    if not mask.any():
        return None
    a, b = image[mask], reference[mask]
    return {'RGB': float(np.abs(a.astype(float) - b).mean()),
            'DE': float(deltaE_ciede2000(rgb2lab(a / 255.), rgb2lab(b / 255.)).mean())}


def run_case(source, role, *, fitter=fit_target):
    validate_source(source)
    if role not in ROLES:
        raise ValueError('Only the six frozen roles are allowed')
    reference, alpha, protected = source['reference'], source['alpha'], source['protected']
    before = [array_hash(source[k]) for k in ('reference', 'alpha', 'protected')]
    image, generation = render_rgb(reference, np.ones(alpha.shape, float), 'medium', *ROLES[role])
    raw = raw_distortion(reference, role)
    clipped = (raw < 0) | (raw > 1)
    primary = alpha > 0
    if role == 'identity':
        target = {'status': 'exact_neutral_target', 'parameters': [1., 1., 1.], 'evaluations': 0}
    else:
        target = fitter(image, reference, alpha, primary)
    parameters = target.get('parameters')
    output = None
    if parameters is not None:
        if (target['status'] not in ('available_approximate_target', 'exact_neutral_target')
                or len(parameters) != 3 or not np.isfinite(parameters).all()
                or np.any(np.asarray(parameters) < .25) or np.any(np.asarray(parameters) > 4)):
            raise ValueError('Invalid target controls/status: no clamping or identity fallback')
        if target['status'] == 'available_approximate_target':
            if not target['converged'] or target['jacobian_rank'] != 3:
                raise ValueError('Approximate target must converge with rank3')
        output = render_rgb8(image, alpha, parameters)
        if not np.array_equal(output[alpha == 0], image[alpha == 0]):
            raise AssertionError('Zero-alpha preservation failed')
        if not np.array_equal(output[protected], image[protected]):
            raise AssertionError('Protection preservation failed')
        if role == 'identity' and not np.array_equal(output, reference):
            raise AssertionError('Identity changed')
    elif not target['status'].startswith('unavailable_'):
        raise ValueError('Missing controls must remain explicitly unavailable')
    records = {}
    for name, mask in regions(alpha).items():
        a = metrics(image, reference, mask)
        b = metrics(output, reference, mask) if output is not None else None
        records[name] = {'pixels': int(mask.sum()), 'input': a, 'output': b,
            'benefit': {k: a[k] - b[k] for k in a} if a is not None and b is not None else None,
            'change_RGB': float(np.abs(output[mask].astype(float) - image[mask]).mean())
                if output is not None and mask.any() else None}
    if before != [array_hash(source[k]) for k in ('reference', 'alpha', 'protected')]:
        raise AssertionError('Source or support mutated')
    record = {'source_id': source['source_id'], 'role': role,
        'generated_fixture': source['generated_fixture'], 'version': VERSION,
        'counterfactual_setting': 'medium_not_source_tone', 'target': target,
        'generation': generation, 'clipping': {name: {
            'channels': int(clipped[mask].sum()),
            'pixels': int(clipped.any(axis=2)[mask].sum())}
            for name, mask in {'whole': np.ones(alpha.shape, bool), 'primary': primary}.items()},
        'regions': records, 'training_admitted': False, 'model_ready': False}
    return record, image, output


def summarize(records):
    result = {}
    for role in ROLES:
        own = [r for r in records if r['role'] == role]
        available = [r for r in own if r['regions']['primary']['output'] is not None]
        result[role] = {'attempted': len(own), 'available': len(available),
            'unavailable_source_ids': [r['source_id'] for r in own if r not in available],
            'primary': {prefix: {key: float(np.mean([r['regions']['primary'][prefix][key]
                for r in available])) if available else None for key in ('RGB', 'DE')}
                for prefix in ('input', 'output', 'benefit')}}
    return result


def execute_sources(sources, destination, *, fitter=fit_target):
    """Persist exact supplied sources, preserving failures; caller binds eligible file IO separately."""
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError('Preserve prior or partial execution')
    if not sources or len({s['source_id'] for s in sources}) != len(sources):
        raise ValueError('Nonempty unique source roster required')
    for source in sources:
        validate_source(source)  # All supports validated before any optimization.
    destination.mkdir(parents=True)
    write(destination / 'status.json', {'status': 'running', 'completed_cases': 0})
    records = []
    try:
        for source in sources:
            source_dir = destination / source['source_id']
            source_dir.mkdir()
            np.savez(source_dir / 'support.npz', reference=source['reference'],
                     alpha=source['alpha'], protected=source['protected'])
            for role in ROLES:
                record, image, output = run_case(source, role, fitter=fitter)
                arrays = {'input': image}
                if output is not None:
                    arrays['output'] = output
                np.savez(source_dir / (role + '.npz'), **arrays)
                write(source_dir / (role + '.json'), record)
                records.append(record)
        write(destination / 'summary.json', summarize(records))
        write(destination / 'status.json', {'status': 'complete', 'completed_cases': len(records),
              'nonidentity_target_calls': len(sources) * 5, 'tree_fits': 0})
    except Exception as error:
        write(destination / 'status.json', {'status': 'failed_preserved',
              'completed_cases': len(records), 'error_type': type(error).__name__, 'error': str(error)})
        raise
    return records
