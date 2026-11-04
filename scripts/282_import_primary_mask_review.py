"""Import exact primary-mask decisions and validate recipe-specific admissions."""
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.distortion_generation.table2_composite import SETTINGS
h=importlib.import_module('256_compare_clean_control_tree_depth')


def main():
    folder=ROOT/'outputs/primary_training_review_v1';out=ROOT/'outputs/primary_mask_review_import_v1'
    if out.exists():raise FileExistsError(out)
    manifest=h.read(folder/'manifest.json');export=folder/'truehue_primary_mask_decisions.json';review=h.read(export)
    assert review['schema_version']=='truehue_primary_mask_review_v1' and review['manifest_sha256']==h.digest(folder/'manifest.json')
    assert review['review_scope']=='exact_new_primary_candidate_input_masks_only'
    for path,sha in h.read(folder/'verification.json')['evidence_sha256'].items():assert h.digest(folder/path)==sha
    expected={r['pair_id']:r for r in manifest['rows']};assert len(expected)==61 and set(review['reviews'])==set(expected)
    prepared={}
    dependencies=[]
    for name in ('primary_training_preparation_v1','gamma_exposure_controls_v1'):
        parent=ROOT/'outputs'/name;verified=h.read(parent/'verification.json');assert verified['status']=='pass'
        for path,sha in verified['evidence_sha256'].items():assert h.digest(parent/path)==sha
        prepared.update({r['pair_id']:r for r in h.read(parent/'attempts.json')});dependencies.extend([parent/'verification.json',parent/'attempts.json'])
    old=ROOT/'outputs/endpoint_feature_tree_v1';old_plan=h.read(old/'plan.json')
    controls={r['source_image_id']:r for r in old_plan['rows'] if r['variant']=='identity'}
    _,identity=contract(ROOT);assert identity==manifest['measurement_contract_sha256']==old_plan['measurement_contract_sha256']
    lookup=DevelopmentMonotoneLookup(h.read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),identity)
    reconciled=[];accepted=[]
    for pair,item in expected.items():
        entry=review['reviews'][pair];assert entry['decision'] in ('accept','reject','uncertain','') and isinstance(entry['notes'],str)
        reconciled.append(dict(pair_id=pair,source_image_id=item['source_image_id'],variant=item['variant'],**entry))
        if entry['decision']!='accept':continue
        r=prepared[pair];control=controls[r['source_image_id']]
        assert r['lane']=='primary_pending_exact_mask_review' and r['measurement']['status']=='success' and r['support_screen']['screen_pass']
        assert r['duplicate_group_id']==control['duplicate_group_id'] and control['partition']=='train'
        for key in ('input_sha256','input_mask_sha256'):assert r[key]==item[key]
        for key,sha in (('input_path','input_sha256'),('input_mask_path','input_mask_sha256')):assert h.digest(ROOT/r[key])==r[sha]
        for key in ('reference_path','reference_mask_path'):assert h.digest(ROOT/r[key])==h.digest(ROOT/control[key])
        image=cv2.imread(str(ROOT/r['input_path']));mask=cv2.imread(str(ROOT/r['input_mask_path']),0)>0
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
        features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)};features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        assert features==r['features']
        endpoints=facial_endpoint_features(image,mask);assert endpoints['valid'] and endpoints['features']==r['endpoint_features']
        target=r['paper_target'];reference=cv2.cvtColor(cv2.imread(str(ROOT/r['reference_path'])),cv2.COLOR_BGR2RGB)
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);support=cv2.imread(str(ROOT/r['reference_mask_path']),0)>0
        if r['variant'].startswith('gamma_'):
            g=SETTINGS[r['severity']]['gamma'];exponent=g if r['variant']=='gamma_lighten' else 1/g
            assert r['clipped_pixels']==0 and r['exponent']==exponent and target==[1/exponent,1.,1.]
            expected_image=reference.copy();expected_image[support]=np.rint((reference.astype(float)/255)**exponent*255)[support].astype(np.uint8)
            np.testing.assert_array_equal(rgb,expected_image)
        else:
            assert r['clipping']['clipped_pixels']==0
            fit=r['target_fit'];gamma,red,blue=fit['parameters']
            assert fit['converged'] and fit['jacobian_rank']==3 and target==[1/gamma,red,blue]
            selected=mask&support;raw=np.clip((rgb.astype(float)/255)**(1/gamma)*[red,1,blue],0,1)
            residual=float(np.sqrt(np.mean((raw[selected]-reference[selected].astype(float)/255)**2)))
            assert abs(residual-fit['float_rgb_rmse'])<1e-12
        assert np.isfinite(target).all() and min(target)>0
        accepted.append(dict(r,cohort='primary',partition='train',measurement_contract_sha256=identity,
            exact_input_mask_review='accept',exact_review_notes=entry['notes'],review_updated_at=entry.get('updated_at'),
            training_eligible=True,**features,**endpoints['features']))
    counts={d:sum(r['decision']==d for r in reconciled) for d in ('accept','reject','uncertain','')}
    assert counts=={'accept':58,'reject':3,'uncertain':0,'':0}
    assert len(accepted)==58
    out.mkdir();(out/'original_user_export.json').write_bytes(export.read_bytes())
    h.write(out/'reconciled_reviews.json',reconciled);h.write(out/'accepted_primary_rows.json',accepted)
    h.write(out/'summary.json',dict(decisions=counts,accepted_with_notes=sum(bool(r['exact_review_notes']) for r in accepted),
        accepted_sources=len({r['source_image_id'] for r in accepted}),variant_counts={v:sum(r['variant']==v for r in accepted) for v in sorted({r['variant'] for r in accepted})},
        original_clean_controls_unchanged=26,model_fits=0,active_demo_changed=False))
    h.write(out/'verification.json',dict(status='pass',manifest_sha256=h.digest(folder/'manifest.json'),export_sha256=h.digest(export),
        recipe_specific_admissions_checked=58,exact_notes_preserved=True,source_role_and_feature_checks=True,
        dependency_sha256={p.relative_to(ROOT).as_posix():h.digest(p) for p in [Path(__file__),folder/'manifest.json',*dependencies]},
        evidence_sha256={p.relative_to(out).as_posix():h.digest(p) for p in out.rglob('*') if p.is_file()}))
    print('Imported 58 accepts / 3 rejects. All accepted recipe-specific targets, masks and notes checked; clean controls unchanged.')


if __name__=='__main__':main()
