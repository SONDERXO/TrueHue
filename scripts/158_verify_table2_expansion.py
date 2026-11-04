"""Replay saved expansion pixels/features and prepare provisional combined folds."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.ita_estimation.square_measurement import MIN_SKIN_PIXELS
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.data_preparation.source_group_folds import source_group_folds
from src.distortion_generation.table2_composite import composite_rgb


def main():
    folder=ROOT/'outputs/table2_stress_expansion_v1';target=folder/'independent_verification.json'
    if target.exists():raise FileExistsError(target)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    source=folder/'summary.json';data=json.loads(source.read_text());first=json.loads((folder/'verification.json').read_text())
    assert digest(source)==first['summary_sha256'] and digest(folder/'review.html')==first['review_sha256']
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    for p,h in data['evidence_sha256'].items():assert digest(folder/p)==h
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(artifact)==data['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(json.loads(artifact.read_text()),data['measurement_contract_sha256'])
    checks=[];proposed=[]
    prior_folder=ROOT/'outputs/table2_stress_evaluation_v2'
    prior_plan=json.loads((prior_folder/'fit_plan.json').read_text())
    assert digest(prior_folder/'fit_plan.json')==json.loads((prior_folder/'verification.json').read_text())['fit_plan_sha256']
    for r in prior_plan['rows']:
        proposed.append(dict(pair_id=r['pair_id'],source_image_id=r['source_image_id'],duplicate_group_id=r['duplicate_group_id'],
            partition='train',table_use='train',training_eligible=False,planning_only=True,review_status='previously_accepted_with_recorded_concerns'))
    for row in data['sources']:
        name=row['source_id']
        if row['status']!='pending_review':continue
        ref=cv2.imread(str(folder/f'{name}_reference.png'));current=cv2.imread(str(folder/f'{name}_input.png'))
        rm=cv2.imread(str(folder/f'{name}_reference_mask.png'),0);im=cv2.imread(str(folder/f'{name}_input_mask.png'),0)
        for image,mask,report in [(ref,rm,row['reference_measurement']),(current,im,row['input_measurement'])]:
            assert set(np.unique(mask))<={0,255}
            stats=compute_masked_lab_statistics(image,mask,MIN_SKIN_PIXELS)
            assert stats['valid']
            features={k:float(stats[v]) for k,v in zip(FEATURES,FEATURE_KEYS)}
            assert features==report['features']
            assert int(np.count_nonzero(mask))==report['skin_pixels']
        assert lookup.label(row['reference_measurement']['features']['input_ita_degrees'])==row['reference_mst_estimate']
        assert lookup.label(row['input_features']['input_ita_degrees'])-1==row['input_features']['input_mst_index']
        selected=rm>0;rgb=cv2.cvtColor(ref,cv2.COLOR_BGR2RGB)
        transformed,_=composite_rgb(rgb,row['assigned_severity']);generated=rgb.copy();generated[selected]=transformed[selected]
        assert np.array_equal(generated,cv2.cvtColor(current,cv2.COLOR_BGR2RGB))
        _,clipping=composite_rgb(rgb[selected][:,None,:],row['assigned_severity']);assert clipping==row['clipping']
        fit=json.loads((folder/f'{name}_target_fit.json').read_text());assert fit==row['target_fit']
        support=(im>0)&selected;x=generated[support].astype(float)/255;y=rgb[support].astype(float)/255
        gamma,red,blue=fit['parameters'];predicted=np.clip(x**(1/gamma)*[red,1,blue],0,1)
        assert abs(float(np.sqrt(np.mean((predicted-y)**2)))-fit['float_rgb_rmse'])<1e-12
        checks.append(dict(source_id=name,reference_pixels=int(selected.sum()),intersection_pixels=int(support.sum()),
            reference_mask_retention=float(support.sum()/selected.sum()),clipping_fraction=clipping['clipped_pixels']/int(selected.sum())))
        for variant in ['identity','table2_'+row['assigned_severity']]:
            proposed.append(dict(pair_id=name+'__'+variant,source_image_id=row['image_id'],duplicate_group_id=row['duplicate_group_id'],
                partition='train',table_use='train',training_eligible=False,planning_only=True,review_status='pending'))
    folds=source_group_folds(proposed)
    assert len({r['source_image_id'] for r in proposed})==11 and len(proposed)==22 and len(folds)==11
    assert not any('51739' in r['pair_id'] for r in proposed)
    (folder/'provisional_combined_plan.json').write_text(json.dumps(dict(status='conditional_on_new_review_not_admission',
        rows=proposed,folds=folds,training_admitted=0,prior_plan_sha256=digest(prior_folder/'fit_plan.json'),
        limitation='Rebuild on actually accepted sources before fitting. Known source/duplicate groups do not prove person separation.'),indent=2))
    target.write_text(json.dumps(dict(status='pass',summary_sha256=digest(source),checks=checks,
        recomputed_measurements=12,reconstructed_distortions=6,recomputed_targets=6,
        hypothetical_combined_pairs=22,hypothetical_combined_folds=11,new_training_admissions=0),indent=2))
    print(json.dumps(dict(status='pass',checks=checks,provisional_combined_folds=len(folds)),indent=2))


if __name__=='__main__':main()
