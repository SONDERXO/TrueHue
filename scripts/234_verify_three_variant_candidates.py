"""Verify all80attempts and preserve explicit unreviewed training holds."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.distortion_generation.three_variant_recipe import render_rgb,VARIANTS
from src.distortion_generation.paper_gamma import transform_rgb,legacy_to_paper_parameters
from src.distortion_generation.generate_distortions import transform_rgb as legacy
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.square_measurement import contract
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.evaluation.mask_support_quality import support_retention


def main():
    out=ROOT/'outputs/three_variant_training_candidates_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json')
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    assert contract(ROOT)[1]==plan['measurement_contract_sha256']
    rows=[json.loads(x) for x in (out/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(rows)==len({r['pair_id'] for r in rows})==80
    assert set(r['source_image_id'] for r in rows)==set(plan['source_ids'])
    conversions=0;measurements=0;combined_parity=0
    for source in plan['source_ids']:
        values=[r for r in rows if r['source_image_id']==source]
        assert len(values)==4 and {r['variant'] for r in values}=={'identity',*VARIANTS}
        assert len({r['duplicate_group_id'] for r in values})==1
    for r in rows:
        ref=cv2.cvtColor(cv2.imread(str(ROOT/r['reference_path'])),cv2.COLOR_BGR2RGB)
        support=cv2.imread(str(ROOT/r['reference_mask_path']),0)>0
        image=cv2.imread(str(ROOT/r['input_path']))
        mask=cv2.imread(str(ROOT/r['input_mask_path']),0) if r['input_mask_path'] else None
        assert not r['training_eligible'] and r['table_use']=='held_development_candidate_not_fitting'
        if r['variant']=='identity':
            np.testing.assert_array_equal(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),ref)
            assert r['paper_correction_target']==dict(gamma=1.,red_gain=1.,blue_gain=1.)
            assert r['exact_identity_target'] is True
        else:
            transformed,_=render_rgb(ref,r['assigned_severity'],r['variant']);expected=ref.copy();expected[support]=transformed[support]
            rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);np.testing.assert_array_equal(rgb,expected)
            _,clipping=render_rgb(ref[support][:,None,:],r['assigned_severity'],r['variant'])
            assert clipping==r['clipping'] and clipping['clipped_pixels']==r['clipped_pixels']
            if r['variant']=='combined':
                old=cv2.imread(str(ROOT/'outputs/paper_gamma_input_comparison_v1/images'/f'{r["source_id"]}_input.png'))
                np.testing.assert_array_equal(image,old);combined_parity+=1
            if r['measurement']['status']=='success':assert r['support_screen']==support_retention(support,mask>0,mask>0)
            if 'paper_correction_target' in r:
                old_params=r['target_fit_legacy_coordinates']['parameters']
                assert r['paper_correction_target']==legacy_to_paper_parameters(*old_params)
                corrected=transform_rgb(rgb.astype(float)/255,**r['paper_correction_target'])
                np.testing.assert_allclose(corrected,legacy(rgb.astype(float)/255,*old_params),rtol=0,atol=1e-14)
                intersection=(mask>0)&support
                rmse=float(np.sqrt(np.mean((corrected[intersection]-ref[intersection]/255.)**2)))
                assert abs(rmse-r['target_fit_legacy_coordinates']['float_rgb_rmse'])<1e-12
                conversions+=1
            else:assert r['status'] in {'target_unavailable','input_failed'}
            assert r['distorted_mask_review']=='pending'
        if 'input_features' in r:
            stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
            for f,k in zip(FEATURES,FEATURE_KEYS):assert stats[k]==r['input_features'][f]
            measurements+=1
    summary=read(out/'summary.json')
    for variant in VARIANTS:
        values=[r for r in rows if r['variant']==variant]
        assert summary['variants'][variant]['statuses']==dict(Counter(r['status'] for r in values))
        assert summary['variants'][variant]['clipped_pixels']==sum(r['clipped_pixels'] for r in values)
    assert measurements==80 and conversions==58 and combined_parity==20
    target.write_text(json.dumps(dict(status='pass',unique_attempts=80,verified_measurements=80,
        approximate_targets_verified=58,combined_prior_version_parity=20,
        all_training_holds_preserved=True,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS:80attempts/features,60composites,58approximate targets,20combined parity checks;all fitting holds preserved.')


if __name__=='__main__':main()
