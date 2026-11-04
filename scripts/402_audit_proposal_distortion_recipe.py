"""Fixed Table2 interpretation audit on generated pixels, never dataset admission."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from src.distortion_generation.three_variant_recipe import render_rgb, VARIANTS
from src.distortion_generation.table2_composite import SETTINGS
from src.correction.seamless_blend import inward_alpha
from src.model_training.blended_recovery_targets import fit_target

OUT = ROOT / 'outputs/proposal_distortion_recipe_audit_v1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    levels = np.arange(256, dtype=np.uint8)
    reference = np.tile(levels[None, :, None], (16, 1, 3))
    support = np.full(reference.shape[:2], 255, np.uint8)
    support[:, :4] = 0
    support[:, -4:] = 0
    alpha, _ = inward_alpha(support, face_width=80)
    score = alpha > 0
    rows = []
    for group in SETTINGS:
        for variant in VARIANTS:
            transformed, metadata = render_rgb(reference, group, variant)
            image = np.rint(reference*(1-alpha[..., None])+
                            transformed*alpha[..., None]).astype(np.uint8)
            result = fit_target(image, reference, alpha, score)
            # A second implementation of the documented formula checks recipe arithmetic.
            s = SETTINGS[group]
            raw = reference.astype(float)/255
            if variant in ('exposure', 'combined'):
                raw = (raw**s['gamma']-.5)*(1+s['contrast']/100)+.5+s['brightness']/255
            if variant in ('color', 'combined'):
                raw += np.array([s['cyan_red'], 0, s['yellow_blue']])/255
            assert np.array_equal(transformed, np.rint(np.clip(raw, 0, 1)*255).astype(np.uint8))
            assert np.array_equal(image[~score], reference[~score])
            neutral_levels = [32, 64, 128, 192, 224]
            rows.append(dict(group=group, variant=variant, recipe=metadata,
                neutral_samples=[dict(input=k, output=transformed[8, k].tolist()) for k in neutral_levels],
                mean_signed_RGB_code_shift=float((image[score].astype(float)-reference[score]).mean()),
                target=result))
    sources = ['Thesis Proposal Document.pdf', 'src/distortion_generation/three_variant_recipe.py',
               'src/distortion_generation/table2_composite.py',
               'src/model_training/blended_recovery_targets.py',
               'scripts/402_audit_proposal_distortion_recipe.py']
    payload = dict(status='engineering_interpretation_audit_not_training_recipe_adoption',
        source_sha256={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
        source='generated neutral 0..255 ramp, 16 rows; not real skin or tone coverage',
        proposed_order='direct gamma, contrast about 0.5, brightness/255, additive red/blue shifts/255, clip, RGB8 round, alpha blend, RGB8 round',
        variants='exposure-only, colour-only, combined: engineering decomposition, not verbatim proposal',
        scoring='all positive-alpha pixels, including fractional edges; RGB8 code error only',
        interpretation_warning='gamma<1 brightens, so Table2 is not automatically an underexposure recipe',
        photos=0, target_fits=9, tree_fits=0, mst_fits=0, runtime_changes=0, admissions=0,
        results=rows)
    OUT.mkdir()
    (OUT/'results.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'results.json': hashlib.sha256(
        (OUT/'results.json').read_bytes()).hexdigest()}, indent=2), encoding='utf-8')
    print(json.dumps([dict(group=r['group'], variant=r['variant'],
        shift=r['mean_signed_RGB_code_shift'], residual=r['target']['rgb8_mae_codes'],
        input64=r['neutral_samples'][1]['output']) for r in rows], indent=2))


if __name__ == '__main__':
    main()
