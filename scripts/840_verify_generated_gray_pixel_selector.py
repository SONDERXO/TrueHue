"""Independent scalar ranking/pooled-code verification, generated fixtures only."""
from pathlib import Path
import sys
import json
import hashlib
import runpy
import math

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT/'outputs/gray_pixel_selector_engineering_v1'


def main():
    dest = OUT/'verification_PRIVATE.json'
    if dest.exists():
        raise FileExistsError('Preserve verification')
    bound = json.loads((OUT/'input_sha256_PRIVATE.json').read_text())
    # Test file gained the explicit 256px selected-count check after the fixture
    # run. Preserve its old binding and record the current verifier dependency;
    # it does not change selector/fixture outputs.
    changed_test = str(ROOT/'tests/test_gray_pixel_context.py')
    for p, h in bound.items():
        if p != changed_test:
            assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == h
    functions = runpy.run_path(str(ROOT/'tests/test_gray_pixel_context.py'))
    scalar = functions['scalar_reference']
    results = json.loads((OUT/'generated_results_PRIVATE.json').read_text())
    exact = 0;maxgap = 0.;false = 0
    with np.load(OUT/'generated_fixtures_ONLY.npz', allow_pickle=False) as arrays:
        assert len(arrays.files) == 12
        for r in results['records']:
            assert r['generated_fixture']
            image = arrays[r['fixture_id']]
            assert hashlib.sha256(image.tobytes()).hexdigest() == r['input_array_sha256']
            ranking = scalar(image)
            scores = {index:score for score,index in ranking}
            assert len(ranking) == r['valid_candidates']
            assert len(r['selected_flat_indices']) == r['selected_count'] == 1
            chosen = r['selected_flat_indices'][0]
            assert chosen in scores
            gap = scores[chosen]-ranking[0][0]
            assert abs(scores[chosen]-r['cutoff_score']) < 1e-12
            assert gap <= 1e-12
            maxgap = max(maxgap, gap)
            exact += chosen == ranking[0][1]
            pixel = image.reshape(-1, 3)[chosen].astype(float)
            assert pixel.tolist() == r['selected_mean_rgb_codes']
            expected = [math.log(pixel[0]/pixel[1]), math.log(pixel[2]/pixel[1])]
            assert np.allclose(expected, list(r['features'].values()), rtol=0, atol=1e-14)
            neutral = r['scene'] == 'neutral' or (r['scene'] == 'mixed' and chosen % 64 >= 32)
            assert int(neutral) == r['selected_generated_neutral_material']
            false += not neutral
    assert false == results['coloured_material_selected_conditions'] == 5
    report = dict(passed_numeric_equations_and_pooled_outputs=True,
        generated_conditions=12, scalar_local_windows=49152,
        scalar_final_windows=49152, exact_scalar_selected_index_matches=exact,
        max_scalar_selected_score_gap=maxgap,
        verification_score_tolerance=1e-12,
        tolerance_is_not_used_by_selector=True,
        ranking_limit='Floating-point near-ties may choose different indices; no bitwise scalar-rank parity claim.',
        full_selector_author_code_parity_claim=False,
        generated_coloured_material_selected=5, scientific_rows=0,
        photo_reads=0, fits=0, holdout_reads=0,
        test_file_at_fixture_run_sha256=bound[changed_test],
        current_test_sha256=hashlib.sha256(Path(changed_test).read_bytes()).hexdigest(),
        result_sha256=hashlib.sha256((OUT/'generated_results_PRIVATE.json').read_bytes()).hexdigest(),
        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(dest.read_text())


if __name__ == '__main__':
    main()
