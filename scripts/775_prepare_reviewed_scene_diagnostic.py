"""Exact-sixty existing scene summaries, diagnostic only; zero model calls."""
from pathlib import Path
import hashlib,json,sys
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training.whole_scene_features import SCENE_FEATURES,scene_features
OUT=ROOT/'outputs/reviewed_scene_diagnostic_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve previous or partial diagnostic')
    bound={}
    def read(p):
        p=Path(p);raw=p.read_bytes();bound[str(p)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    rows=read(ROOT/'outputs/combined_reviewed_mst_design_v1/rows_PRIVATE.json')
    meta=read(ROOT/'outputs/existing_illumination_cue_readiness_v1/exact60_metadata_PRIVATE.json')
    root=Path(read(ROOT/'outputs/stellenbosch_received_data_v1/protocol.json')['dataset_location'])
    groups=read(ROOT/'outputs/group_diversity_candidates_v1/plan_PRIVATE.json')['groups']
    locked={r['subject_key'] for r in groups if r['role']=='closed_holdout_candidate'}
    assert len(rows)==len(meta)==60 and not ({r['subject_id'] for r in rows}&locked)
    bycase={r['case_id']:r for r in rows}
    # Read only the whitelist, once per source. Verify all hashes before any decode.
    payloads={}
    for m in meta:
        assert m['subject_id']==bycase[m['case_id']]['subject_id'] and m['source_sha256']==bycase[m['case_id']]['source_sha256']
        p=root/m['inherited_relative_path'];raw=p.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==m['source_sha256']
        payloads[m['case_id']]=raw
    OUT.mkdir();(OUT/'frames').mkdir()
    def write(name,d):(OUT/name).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
    write('execution_plan_PRIVATE.json',dict(status='hash_preflight_passed',sources=meta,input_sha256=bound,
        scene_feature_names=list(SCENE_FEATURES),image_reads=60,model_calls=0,fits=0,holdout_reads=0))
    records=[]
    for row in rows:
        r=dict(row,scene_status='unavailable',scene_features=None)
        try:
            bgr=cv2.imdecode(np.frombuffer(payloads[row['case_id']],np.uint8),cv2.IMREAD_COLOR)
            assert bgr is not None and bgr.shape==(224,224,3)
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            features=scene_features(rgb)
            assert all(np.isfinite(v) for v in features.values())
            path=OUT/'frames'/(row['case_id']+'.npy');np.save(path,rgb,allow_pickle=False)
            r.update(scene_status='available',scene_features=features,frame_file=str(path.relative_to(OUT)),
                frame_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        except Exception as error:r['scene_reason']=str(error)
        records.append(r)
        write('records_PRIVATE.json',records)
    assert len(records)==60
    photo=read(ROOT/'outputs/reviewed_feature_control_contract_v1/partial_features_and_targets_PRIVATE.json')
    available=[r for r in records if r['scene_status']=='available']
    ranges={f:[min(r['scene_features'][f] for r in available),max(r['scene_features'][f] for r in available)] for f in SCENE_FEATURES}
    photo_support=[]
    for r in photo:
        photo_support.append(dict(case_id=r['case_id'],outside_scene_marginals=[f for f in SCENE_FEATURES if not ranges[f][0]<=r['features_partial'][f]<=ranges[f][1]]))
    index={(r['subject_id'],r['condition']):r for r in records}
    pairs=[]
    for subject in sorted({r['subject_id'] for r in rows}):
        for family in ('F_cool','H_warm','L_warm'):
            a,b=index[(subject,family+'_600')],index[(subject,family+'_1200')]
            pairs.append(dict(subject_id=subject,family=family,available=a['scene_status']==b['scene_status']=='available',
                delta={f:b['scene_features'][f]-a['scene_features'][f] for f in SCENE_FEATURES} if a['scene_status']==b['scene_status']=='available' else None))
    paired={f:dict(mean_delta=float(np.mean([p['delta'][f] for p in pairs if p['available']])),
        positive=sum(p['delta'][f]>0 for p in pairs if p['available']),negative=sum(p['delta'][f]<0 for p in pairs if p['available']),
        zero=sum(p['delta'][f]==0 for p in pairs if p['available'])) for f in SCENE_FEATURES}
    spreads={c:{f:float(np.ptp([r['scene_features'][f] for r in available if r['condition']==c])) for f in SCENE_FEATURES} for c in sorted({r['condition'] for r in available})}
    write('summary_PRIVATE.json',dict(attempts=60,available=len(available),unavailable=60-len(available),subjects=10,
        scene_ranges=ranges,paired_changes=paired,within_condition_across_subject_ranges=spreads,photographic_support=photo_support,
        photographic_outside_any_scene_marginal=sum(bool(r['outside_scene_marginals']) for r in photo_support),
        calibrated_illumination_truth=False,feature_selection=False,calibration_admitted=False,runtime_adopted=False,
        image_reads=60,source_decodes=60,model_calls=0,fits=0,new_predictions=0,holdout_reads=0))
    write('pairs_PRIVATE.json',pairs);write('input_sha256_PRIVATE.json',bound)
    print(json.dumps(dict(available=len(available),paired_changes=paired,photographic_support=photo_support),indent=2))


if __name__=='__main__':main()
