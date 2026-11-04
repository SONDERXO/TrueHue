"""Join human reference reviews with technical, clipping and input-mask evidence."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.distortion_generation.table2_composite import composite_rgb
from src.evaluation.mask_support_quality import support_retention


def main():
    out=ROOT/'outputs/accepted_training_pair_audit_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    reviews_path=ROOT/'outputs/training_review36_import_v1/combined_original_mask_reviews60.json'
    reviews=read(reviews_path)
    imports=ROOT/'outputs/training_review36_import_v1'
    for name,sha in read(imports/'verification.json')['evidence_sha256'].items():assert digest(imports/name)==sha
    parent=ROOT/'outputs/correction_training_preparation_v1'
    prior={r['image_id']:r for r in (json.loads(x) for x in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    old=read(parent/'verification.json')['evidence_sha256']
    colors_path=ROOT/'outputs/training_reference_color_audit_v1/source_dispositions.json'
    colors={r['image_id']:r for r in read(colors_path)}
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    _,identity=contract(ROOT)
    assert identity==read(parent/'summary.json')['measurement_contract_sha256']
    lookup=DevelopmentMonotoneLookup(read(artifact),identity)
    reserved={r['image_id'] for r in read(ROOT/'outputs/focused_mask_review24_v1/reserved_training_check.json')['sources']}
    assert len(reviews)==len({r['image_id'] for r in reviews})==60 and not reserved&{r['image_id'] for r in reviews}
    paths=[Path(__file__),ROOT/'docs/accepted-reference-audit-protocol.md',reviews_path,colors_path,
        parent/'attempts.jsonl',artifact,ROOT/'src/evaluation/mask_support_quality.py',
        ROOT/'src/distortion_generation/table2_composite.py']
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_pair_audit',measurement_contract_sha256=identity,input_sha256=hashes,
        review_ids=[r['image_id'] for r in reviews],training_admissions=0,models_fitted=0))
    records=[];images_checked={};measurements=0
    def image(name,suffix,gray=False):
        relative=f'images/{name}_{suffix}.png';path=parent/relative
        sha=digest(path);assert sha==old[relative];images_checked[relative]=sha
        return cv2.imread(str(path),0 if gray else cv2.IMREAD_COLOR)
    def features(im,mask,report):
        nonlocal measurements
        stats=compute_masked_lab_statistics(im,mask,1000);assert stats['valid']
        for name,key in zip(FEATURES,FEATURE_KEYS):assert stats[key]==report['features'][name]
        measurements+=1
    for review in reviews:
        image_id=review['image_id'];s=prior[image_id];name=s['source_id']
        r=dict(image_id=image_id,source_id=name,decision=review['decision'],exact_notes=review['notes'],
            duplicate_group_id=s['duplicate_group_id'],training_eligible=False,primary_pair_eligible=False,
            identity_control_training_eligible=False,distorted_human_review='not_reviewed',
            status='excluded_human_reference_rejection',barriers=[])
        if review['decision']!='accept':r['barriers']=['human_reference_rejection'];records.append(r);continue
        if s['reference_measurement']['status']!='success':
            r.update(status='excluded_reference_pipeline_failure',barriers=['reference_pipeline_failure'],
                failure_reason=s['reference_measurement'].get('reason'));records.append(r);continue
        if colors.get(image_id,{}).get('status')!='requires_reference_review':
            r.update(status='excluded_reference_color_quality',barriers=['reference_color_quality']);records.append(r);continue
        ref=image(name,'reference');ref_mask=image(name,'reference_mask',True)
        features(ref,ref_mask,s['reference_measurement'])
        r.update(reference_technical_pass=True,identity_target=[1.,1.,1.],reference_review='accepted',
            identity_features=s['identity_features'],reference_mst_estimate=s['reference_mst_estimate'],
            assigned_severity=s['assigned_severity'],status='pending_distorted_input_review')
        if name=='16033':r['barriers'].append('accepted_reference_hair_concern_requires_assessment')
        assert s['identity_features']['input_mst_index']==lookup.label(s['reference_measurement']['features']['input_ita_degrees'])-1
        if s.get('input_measurement',{}).get('status')!='success':
            r.update(status='excluded_distorted_pipeline_failure');r['barriers'].append('distorted_pipeline_failure');records.append(r);continue
        current=image(name,'input');mask=image(name,'input_mask',True)
        features(current,mask,s['input_measurement'])
        assert s['input_features']['input_mst_index']==lookup.label(s['input_measurement']['features']['input_ita_degrees'])-1
        rgb=cv2.cvtColor(ref,cv2.COLOR_BGR2RGB);support=ref_mask>0
        transformed,_=composite_rgb(rgb,s['assigned_severity']);expected=rgb.copy();expected[support]=transformed[support]
        np.testing.assert_array_equal(expected,cv2.cvtColor(current,cv2.COLOR_BGR2RGB))
        _,clipping=composite_rgb(rgb[support][:,None,:],s['assigned_severity'])
        assert clipping==s['clipping']
        overlap=int(np.count_nonzero((mask>0)&support));added=int(np.count_nonzero((mask>0)&~support))
        lost=int(np.count_nonzero(support&(mask==0)))
        screen=support_retention(support,mask>0,mask>0)
        fit=s.get('target_fit',{});parameters=fit.get('parameters')
        target_valid=bool(parameters is not None and len(parameters)==3 and all(np.isfinite(x) and .25<=x<=4 for x in parameters))
        r.update(input_features=s['input_features'],target_parameters=parameters,target_available=target_valid,
            clipping=clipping,clipping_fraction=s['clipping_fraction'],input_mask_overlap_pixels=overlap,
            input_mask_added_pixels=added,input_mask_lost_pixels=lost,
            exploratory_support_screen=screen,input_mask_identical_to_reference=bool(np.array_equal(mask,ref_mask)),
            approximate_target_rgb_rmse=fit.get('float_rgb_rmse'),input_technical_pass=True)
        r['barriers'].append('distorted_mask_not_human_reviewed')
        if clipping['clipped_pixels']>0:
            r['barriers'].append('clipped_input_excluded_from_unclipped_primary')
            r['primary_route']='stress_only_pending_review'
        else:r['primary_route']='unclipped_candidate_pending_review'
        if not screen['screen_pass']:r['barriers'].append('exploratory_support_loss_flag')
        if not target_valid:r['barriers'].append('invalid_or_unavailable_target')
        records.append(r)
    accepted=[r for r in records if r['decision']=='accept'];paired=[r for r in accepted if r.get('input_technical_pass')]
    summary=dict(status='complete_no_training_admission',reviewed_sources=60,accepted_references=len(accepted),
        reference_statuses=dict(Counter(r['status'] for r in accepted)),technically_valid_accepted_pairs=len(paired),
        clipped_pairs=sum(r['clipping']['clipped_pixels']>0 for r in paired),
        unclipped_pairs=sum(r['clipping']['clipped_pixels']==0 for r in paired),
        support_screen_flagged_pairs=sum(not r['exploratory_support_screen']['screen_pass'] for r in paired),
        identical_input_reference_masks=sum(r['input_mask_identical_to_reference'] for r in paired),
        estimated_severity_counts=dict(Counter(r['assigned_severity'] for r in paired)),
        measurements_recomputed=measurements,table2_composites_reconstructed=len(paired),
        training_admissions=0,models_fitted=0,reserved_validation_test_access=False)
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
    write('source_pair_dispositions.json',records);write('summary.json',summary)
    write('verification.json',dict(status='pass',original_evidence_unchanged=True,images_sha256=images_checked,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
