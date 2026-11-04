"""Verify direct-gamma samples, input-only features and target conversion."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.distortion_generation.paper_gamma import composite_rgb,transform_rgb,legacy_to_paper_parameters
from src.distortion_generation.generate_distortions import transform_rgb as legacy
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.evaluation.mask_support_quality import support_retention


def main():
    out=ROOT/'outputs/paper_gamma_input_comparison_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json')
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    assert contract(ROOT)[1]==plan['measurement_contract_sha256']
    rows=[json.loads(x) for x in (out/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    access=[json.loads(x) for x in (out/'access_ledger.jsonl').read_text(encoding='utf-8').splitlines()]
    assert [r['image_id'] for r in rows]==[r['image_id'] for r in access]==plan['sources'] and len(rows)==20
    conversions=0
    for r in rows:
        ref_bgr=cv2.imread(str(ROOT/r['reference_path']));ref=cv2.cvtColor(ref_bgr,cv2.COLOR_BGR2RGB)
        support=cv2.imread(str(ROOT/r['reference_mask_path']),0)>0
        transformed,_=composite_rgb(ref,r['assigned_severity']);expected=ref.copy();expected[support]=transformed[support]
        bgr=cv2.imread(str(out/'images'/f'{r["source_id"]}_input.png'))
        rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB);np.testing.assert_array_equal(expected,rgb)
        _,clipping=composite_rgb(ref[support][:,None,:],r['assigned_severity'])
        assert clipping==r['new_clipping']
        if r['measurement']['status']=='success':
            mask=cv2.imread(str(out/'images'/f'{r["source_id"]}_mask.png'),0)
            stats=compute_masked_lab_statistics(bgr,mask,1000);assert stats['valid']
            for f,k in zip(FEATURES,FEATURE_KEYS):assert stats[k]==r['input_features'][f]
            assert r['new_support_screen']==support_retention(support,mask>0,mask>0)
            if 'paper_correction_target' in r:
                old=r['target_fit_legacy_coordinates']['parameters']
                assert r['paper_correction_target']==legacy_to_paper_parameters(*old)
                np.testing.assert_allclose(transform_rgb(rgb.astype(float)/255,**r['paper_correction_target']),
                    legacy(rgb.astype(float)/255,*old),rtol=0,atol=1e-14)
                conversions+=1
            else:assert r['target_fit_legacy_coordinates']['parameters'] is None
        assert not r['training_eligible'] and r['distorted_mask_review']=='pending'
    summary=read(out/'summary.json')
    assert summary['new_clipped_pixels']==sum(r['new_clipping']['clipped_pixels'] for r in rows)
    assert summary['new_support_screen_pass']==sum(r.get('new_support_screen',{}).get('screen_pass',False) for r in rows)
    assert summary['approximate_targets_available']==conversions==19
    target.write_text(json.dumps(dict(status='pass',composites_reconstructed=20,input_measurements_verified=20,
        explicit_gamma_target_conversions_verified=conversions,legacy_measurement_contract_unchanged=True,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS:20 composites/features/screens;19 curve-equivalent target conversions;source hashes and legacy contract unchanged.')


if __name__=='__main__':main()
