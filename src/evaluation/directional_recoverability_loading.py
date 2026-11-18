"""Hash barrier and narrowly allowed input decoding for a caller-bound source plan."""
from pathlib import Path
import hashlib
import cv2
import numpy as np
from .directional_recoverability import validate_source


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_sources(root, plan, *, generated_fixture):
    if type(generated_fixture) is not bool:
        raise ValueError('Explicit source provenance required')
    root = Path(root).resolve()
    refs, supports = plan['source_references'], plan['support_sources']
    ids = [r['source_id'] for r in refs]
    if len(ids) != 11 or len(set(ids)) != 11 or set(ids) != {s['source_id'] for s in supports} or len(supports) != 11:
        raise ValueError('Exactly eleven joined source/support bindings required')
    support_by_id = {s['source_id']: s for s in supports}

    def contained(value):
        path = (root / value).resolve()
        if not path.is_relative_to(root / 'outputs'):
            raise ValueError('Only explicitly bound output artifacts may be read')
        return path

    locations = []
    for ref in refs:
        if ref['allowed_key'] != 'input_rgb8' or ref['official_tone_label'] is not None:
            raise ValueError('Only original identity input RGB8; no invented source tone')
        container = contained(ref['identity_container'])
        if sha(container) != ref['identity_sha256']:
            raise ValueError('Identity container hash mismatch')
        selected = support_by_id[ref['source_id']]['selected']
        directory = contained(selected['directory'])
        receipt = contained(directory / selected['receipt'])
        if sha(receipt) != selected['receipt_sha256']:
            raise ValueError('Support receipt hash mismatch')
        for name, expected in selected['files'].items():
            if sha(contained(directory / name)) != expected:
                raise ValueError('Selected support file hash mismatch')
        alpha_path = contained(directory / selected['alpha_filename'])
        if selected['alpha_filename'] not in selected['files'] or 'protected_mask.png' not in selected['files']:
            raise ValueError('Alpha and protection must both have bound hashes')
        locations.append((ref, container, alpha_path, contained(directory / 'protected_mask.png')))
    # All declared containers/selected supports hashed before any array decode.
    sources = []
    for ref, container, alpha_path, protected_path in locations:
        with np.load(container, allow_pickle=False) as pack:
            reference = pack['input_rgb8'].copy()  # Never access other NPZ members.
        alpha = np.load(alpha_path, allow_pickle=False)
        protection = cv2.imread(str(protected_path), cv2.IMREAD_GRAYSCALE)
        if protection is None:
            raise ValueError('Protection cannot be decoded')
        source = dict(source_id=ref['source_id'], reference=reference, alpha=alpha,
                      protected=protection > 0, generated_fixture=generated_fixture)
        validate_source(source)
        sources.append(source)
    return sources
