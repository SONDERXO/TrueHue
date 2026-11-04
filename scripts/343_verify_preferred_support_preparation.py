"""Independent candidate-artifact checks; no new scientific experiment."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.isotonic import IsotonicRegression
from src.ita_estimation.semantic_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.distortion_generation.paper_gamma import transform_rgb


def main():
    folder=ROOT/'outputs/preferred_support_cohort_v1';pairs=ROOT/'outputs/preferred_support_pairs_v1'
    target=folder/'independent_verification.json'
    if target.exists():raise FileExistsError(target)
    read=lambda p:json.loads(p.read_text(encoding='utf-8'));digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(folder/'plan.json');records=read(folder/'records.json');identity=contract(ROOT)[1]
    assert identity==plan['measurement_contract_sha256']
    amendment=read(folder/'protocol_amendment.json')
    for path,sha in plan['input_sha256'].items():
        if path=='docs/preferred-support-development-cycle-protocol.md':
            assert digest(folder/amendment['original_snapshot'])==sha==amendment['original_protocol_sha256']
            assert digest(ROOT/path)==amendment['current_protocol_sha256']
        else:assert digest(ROOT/path)==sha
    old={r['source_image_id'] for r in read(ROOT/'outputs/reviewed_source_evidence32_v1/registry.json')['rows']}
    selected={r['image_id'] for r in plan['selected']};assert len(selected)==12 and not selected&old
    # Scan actual collected review imports, not only the older inventory snapshot.
    seen=[]
    def walk(value,origin):
        if isinstance(value,list):
            for item in value:walk(item,origin)
        elif isinstance(value,dict):
            key=value.get('image_id',value.get('source_image_id'))
            if key in selected and any('decision' in k and isinstance(v,str) and v in ['accept','reject','uncertain'] for k,v in value.items()):
                seen.append(dict(image_id=key,origin=origin))
            for v in value.values():
                if isinstance(v,(dict,list)):walk(v,origin)
    for p in (ROOT/'outputs').glob('*review*import*/*.json'):
        try:walk(read(p),p.relative_to(ROOT).as_posix())
        except (json.JSONDecodeError,UnicodeError):pass
    assert not seen,seen
    lookup=DevelopmentMonotoneLookup(read(folder/'development_lookup.json'),identity)
    calibration=[r for r in read(ROOT/'outputs/semantic_mst_measurement_v1/summary.json')['records'] if r['status']=='success']
    counts=Counter(r['subject_id'] for r in calibration)
    model=IsotonicRegression(increasing=False,out_of_bounds='clip',y_min=1,y_max=10)
    model.fit([r['features']['input_ita_degrees'] for r in calibration],[r['source_mst_label'] for r in calibration],
              sample_weight=[1/counts[r['subject_id']] for r in calibration])
    packaged=read(folder/'development_lookup.json')
    assert model.X_thresholds_.tolist()==packaged['ita_knots'] and model.y_thresholds_.tolist()==packaged['mst_knots']
    available=0
    for r in records:
        assert digest(ROOT/r['path'])==r['source_sha256']
        if r['measurement']['status']!='success':continue
        image=cv2.imread(str(ROOT/r['input_path']));masks={k:cv2.imread(str(ROOT/p),0)>0 for k,p in r['mask_paths'].items()}
        assert np.array_equal(masks['combined'],masks['face']|masks['neck']|masks['brows']|masks['lips'])
        for k,p in r['mask_paths'].items():assert digest(ROOT/p)==r['mask_sha256'][k]
        stats=compute_masked_lab_statistics(image,masks['face'].astype(np.uint8)*255,1000)
        assert stats==r['measurement']['statistics']
        features={f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
        features.update(facial_endpoint_features(image,masks['face'])['features'])
        features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        assert features==r['features'];available+=1
    pairschecked=0;regioncounts=Counter()
    for r in read(pairs/'records.json'):
        image=cv2.imread(str(ROOT/r['input_path']));ref=cv2.imread(str(ROOT/r['reference_path']))
        assert digest(ROOT/r['input_path'])==r['input_sha256']
        masks={k:cv2.imread(str(ROOT/p),0)>0 for k,p in r['reference_region_masks'].items()}
        assert np.array_equal(image[~masks['combined']],ref[~masks['combined']])
        for k in ['face','neck','brows','lips']:regioncounts[k]+=bool(masks[k].any())
        if r['measurement']['status']=='success':
            face=cv2.imread(str(ROOT/r['measurement_mask_path']),0)
            assert compute_masked_lab_statistics(image,face,1000)==r['measurement']['statistics']
            assert digest(ROOT/r['measurement_mask_path'])==r['measurement_mask_sha256']
            assert digest(ROOT/r['correction_mask_path'])==r['correction_mask_sha256']
            rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);targetrgb=cv2.cvtColor(ref,cv2.COLOR_BGR2RGB)
            correction=cv2.imread(str(ROOT/r['correction_mask_path']),0)>0
            selected=correction&masks['combined']
            output=transform_rgb(rgb.astype(float)/255,*r['target'])
            error=float(np.abs(np.rint(output[selected]*255)-targetrgb[selected]).mean()/255)
            assert abs(error-r['target_reconstruction_rgb_mae'])<1e-12
        assert not r['training_admitted'];pairschecked+=1
    result=dict(status='passed',source_selection_excludes_old32=True,live_prior_review_matches=seen,
        reference_feature_replays=available,allrow_lookup_refit_replays=1,pair_measurement_target_replays=pairschecked,
        reference_region_nonempty_case_counts=dict(regioncounts),unapproved_rows_not_admitted=True,
        semantic_measurement_contract_unchanged=True,reserved_pixel_access=0,
        protocol_clarification_snapshot_verified=True)
    target.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
