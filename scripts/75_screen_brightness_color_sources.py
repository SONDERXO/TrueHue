"""Screen18 unused TRAIN sources across recorded brightness/color; never fit.

Selection uses three native-L* rank bins, three native-b* ranks within each,
two per cell by fixed hash ordering. This is not MST sampling or independent final evaluation.
"""
import csv
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter,hair_veto_support
from src.data_preparation.controlled_training_table import FEATURES


def read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,image):
    if not cv2.imwrite(str(path),image):raise OSError(path)


def main():
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    version='brightness_color_source_screen_v1';output=ROOT/config.OUTPUTS_ROOT/version;tables=ROOT/'data/manifests'/version
    if output.exists() or tables.exists():raise FileExistsError('Audit exists')
    audit_path=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    current_path=ROOT/'data/manifests/controlled_expansion31_v1/staged_train.csv'
    fold_path=current_path.with_name('source_group_folds.json')
    prior=read(audit_path);current=read(current_path)
    train=[r for r in prior if r['partition']=='train']
    pool=[r for r in train if r['source_suitability']=='hold_unreviewed_source' and r['processing_status']=='success'
          and r['known_pipeline_development_exposure']=='False' and r['original_visual_decision']=='pending'
          and r['controlled_source_decision']=='not_assessed_in_this_pass']
    # Include exposure added after the historical master snapshot.
    exposure_path=ROOT/'data/manifests/development_exposure_additions.jsonl'
    existing_exposure=[]
    if exposure_path.exists():existing_exposure=[json.loads(line) for line in exposure_path.read_text(encoding='utf-8').splitlines() if line]
    exposed_ids={r['image_id'] for r in existing_exposure}
    pool=[r for r in pool if r['image_id'] not in exposed_ids]
    if len(pool)<18:raise ValueError('Insufficient unexposed training candidates')
    current_groups={r['duplicate_group_id'] for r in current}
    pool=[r for r in pool if r['duplicate_group_id'] not in current_groups and r['duplicate_group_size']=='1']
    ordered=sorted(pool,key=lambda r:(float(r['mean_l_star']),r['image_id']))
    selected=[];bin_info=[]
    for light_index,indices in enumerate(np.array_split(np.arange(len(ordered)),3),1):
        light_bucket=[ordered[int(i)] for i in indices]
        color_sorted=sorted(light_bucket,key=lambda r:(float(r['mean_b_star']),r['image_id']))
        for color_index,color_indices in enumerate(np.array_split(np.arange(len(color_sorted)),3),1):
            bucket=[color_sorted[int(i)] for i in color_indices]
            if len(bucket)<2:raise ValueError('Insufficient candidates in fixed cell')
            index=(light_index-1)*3+color_index
            chosen=sorted(bucket,key=lambda r:hashlib.sha256(('brightness_color_seed42/'+r['image_id']).encode()).hexdigest())[:2]
            bin_info.append(dict(bin=index,light_rank=light_index,color_rank=color_index,pool_size=len(bucket),
                native_l_range=[min(float(r['mean_l_star']) for r in bucket),max(float(r['mean_l_star']) for r in bucket)],
                native_b_range=[min(float(r['mean_b_star']) for r in bucket),max(float(r['mean_b_star']) for r in bucket)]))
            selected += [dict(r,sampling_bin=index) for r in chosen]
    assert len(selected)==len({r['image_id'] for r in selected})==18
    assert all(r['partition']=='train' for r in selected)
    tracked=[Path(__file__),audit_path,current_path,fold_path,
             ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,
             ROOT/config.SELFIE_SEGMENTER_MODEL_PATH,ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,
             ROOT/'scripts/11_prepare_training_manifests.py',ROOT/'src/ita_estimation/compute_ita.py',
             ROOT/'src/skin_masking/skin_mask.py',ROOT/'src/skin_masking/mouth_exclusion.py',
             ROOT/'src/skin_masking/landmark_exclusion.py',ROOT/'src/skin_masking/selfie_material_segmenter.py']
    tracked += [Path(r['image_path']) for r in selected]
    brightness=importlib.import_module('72_audit_brightness_features')
    frozen_schema=ROOT/'outputs/brightness_feature_audit_v1/feature_schema.json'
    tracked += [frozen_schema,ROOT/'scripts/72_audit_brightness_features.py']
    hashes={str(p):digest(p) for p in tracked}
    model=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    assert digest(model)==json.loads(model.with_suffix('.provenance.json').read_text())['sha256']
    output.mkdir(parents=True);tables.mkdir(parents=True);(output/'images').mkdir()
    policy=dict(version=version,status='Pre-fit development suitability audit, not source acceptance',
        selection='TRAIN only; historicalunreviewed/computationsuccess/no recorded exposure; exclude newexposure ledger/current groups; three native L* rank bins,three native b* rank bins within each,two per cell by brightness_color_seed42 SHA256',
        bins=bin_info,notes='L*/b* are photo-dependent appearance proxies, not MST or intrinsic skin tone; b* samples one color axis only. Native bins are only sampling proxies; fresh256measurements below.',
        next_use='No distortion pairs or models generated. Human reviews remain pending. Newly inspected IDs are development-exposed, never a fresh holdout.')
    (tables/'selection_policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    (tables/'selected_source_ids.json').write_text(json.dumps([dict(image_id=r['image_id'],sampling_bin=r['sampling_bin'],partition='train',duplicate_group_id=r['duplicate_group_id']) for r in selected],indent=2),encoding='utf-8')
    (tables/'prior_exposure_snapshot.json').write_text(json.dumps(existing_exposure,indent=2),encoding='utf-8')
    # Record exposure before image processing, including any failed attempt.
    with exposure_path.open('a',encoding='utf-8') as f:
        for r in selected:f.write(json.dumps(dict(image_id=r['image_id'],partition='train',reason='brightness_color_source_screen_v1 source/mask development inspection',date='2026-10-24',source_manifest=str(audit_path.relative_to(ROOT))))+'\n')
    (output/'run_status.json').write_text('{"status":"running"}',encoding='utf-8')
    segmenter=SelfieMaterialSegmenter(model);attempts=[];boards={}
    try:
        for r in selected:
            image=cv2.imread(r['image_path'])
            if image is None:raise ValueError('Unreadable selected image')
            square=cv2.resize(image,(config.IMAGE_SIZE,config.IMAGE_SIZE),interpolation=cv2.INTER_LINEAR)
            stem=r['image_id'].replace('/','_');mask=np.zeros(square.shape[:2],bool);cleaned=np.zeros_like(mask)
            record=dict(image_id=r['image_id'],source_path=r['image_path'],partition='train',sampling_bin=r['sampling_bin'],
                        previous_source_suitability=r['source_suitability'],original_human_decision=r['original_visual_decision'],
                        newly_development_exposed=True,training_eligible=False,source_assessment='pending_source_suitability_review')
            boxes=prepare._detect_face_boxes(square,ROOT/config.FACE_MODEL_PATH,.85)
            record.update(face_count=len(boxes),status='expected_single_face',face_boxes=[[int(v) for v in box] for box in boxes])
            if len(boxes)==1:
                x,y,w,h=boxes[0];crop=square[y:y+h,x:x+w]
                result=prepare.compute_versioned_skin_mask(crop,square,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
                mask[y:y+h,x:x+w]=result.mask>0
                stats=compute_masked_lab_statistics(crop,result.mask,1000)
                record.update(**stats,landmarks_available=bool(result.landmarks_available),
                    status='success' if result.landmarks_available and stats['valid'] else 'landmarks_unavailable' if not result.landmarks_available else stats['reason'])
                if record['status']=='success':cleaned=hair_veto_support(segmenter.categories_bgr(square),mask)
                record['hair_clean_generation_pixels']=int(cleaned.sum())
                record['predicted_hair_removed']=int((mask&~cleaned).sum())
            record['brightness_audit']=brightness.brightness_features(square,mask)
            attempts.append(record)
            for suffix,pixels in [('input',square),('estimation',mask.astype(np.uint8)*255),('hairclean',cleaned.astype(np.uint8)*255)]:save(output/'images'/(stem+'_'+suffix+'.png'),pixels)
            panels=[]
            for title,shown in [('Input',None),('Estimation',mask),('Hair-clean source',cleaned)]:
                panel=square.copy()
                if shown is not None:panel[shown]=np.rint(.55*panel[shown]+.45*np.array([0,220,0])).astype(np.uint8)
                panel=cv2.copyMakeBorder(panel,32,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(panel,Path(r['image_path']).stem+' '+title,(3,14),cv2.FONT_HERSHEY_SIMPLEX,.38,(255,255,255),1)
                cv2.putText(panel,record['status'][:36],(3,28),cv2.FONT_HERSHEY_SIMPLEX,.3,(255,255,255),1);panels.append(panel)
            boards.setdefault(r['sampling_bin'],[]).append(np.hstack(panels))
            with (output/'attempts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
            print(r['image_id']+': '+record['status'],flush=True)
        assert hashes=={p:digest(p) for p in hashes},'Tracked inputs changed'
        report=dict(status='complete',current_training_pairs=31,current_sources=8,current_variants=dict(Counter(r['variant'] for r in current)),
            total_training_pool_rows=len(train),training_suitability_counts=dict(Counter(r['source_suitability'] for r in train)),
            unexposed_unreviewed_training_pool=len(pool),selected_new_sources=18,
            new_status_counts=dict(Counter(r['status'] for r in attempts)),new_source_attempts=attempts,
            frozen_brightness_schema_sha256=digest(frozen_schema),input_sha256=hashes,
            caveat='All current source photos already have processing exposure; no recorded prior development exposure is not proof of never being seen. Marginal feature bounds do not establish joint coverage.')
        (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        links=[]
        for index,panels in sorted(boards.items()):
            name=f'sampling_bin_{index}.png';save(output/name,np.vstack(panels));links.append(f'- [Brightness/color sampling cell {index}]({name})')
        (output/'review-index.md').write_text('# Training-source coverage screening\n\n18new TRAIN-pool sources, not accepted or assigned MST. Green is selected support, not quality approval.\n\n'+'\n'.join(links),encoding='utf-8')
        (output/'run_status.json').write_text('{"status":"complete"}',encoding='utf-8')
        print(json.dumps(dict(pool=len(pool),statuses=report['new_status_counts'],brightness_available=sum(r['brightness_audit']['valid'] for r in attempts))))
    finally:segmenter.close()


if __name__=='__main__':main()
