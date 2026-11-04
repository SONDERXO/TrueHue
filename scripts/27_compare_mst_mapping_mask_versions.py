"""Paired historical/current-V2/complete-mouth MST-E feasibility comparison.

Same reviewed sources, same subject-separated mapping rules, no final lookup
export, no calibration on FairFace, no changes to human reviews or raw images.
"""
import csv
import importlib
import json
from pathlib import Path
import random
import sys
import time
import argparse

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.mapping_feasibility import paired_cohorts,leave_subject_out


def measure(crop,result):
    statistics=compute_masked_lab_statistics(crop,result.mask,1000)
    status='success' if statistics['valid'] and result.landmarks_available else (
        'landmarks_unavailable' if not result.landmarks_available else statistics['reason'])
    return dict(status=status,ita=statistics['ita_degrees'],pixels=int(np.count_nonzero(result.mask)),
        mean_l_star=statistics['mean_l_star'],mean_a_star=statistics['mean_a_star'],
        mean_b_star=statistics['mean_b_star'])


def detect_comparison_boxes(image, detector, model, maximum_side=0):
    """Optional comparison-only detector resize; measurement pixels stay native."""
    h,w=image.shape[:2]
    ratio=min(1.,maximum_side/max(h,w)) if maximum_side else 1.
    detector_image=image if ratio==1 else cv2.resize(image,(max(1,round(w*ratio)),max(1,round(h*ratio))))
    dh,dw=detector_image.shape[:2]
    boxes=[]
    for x,y,bw,bh in detector(detector_image,model,.85):
        left=max(0,min(w,int(np.floor(x*w/dw))))
        top=max(0,min(h,int(np.floor(y*h/dh))))
        right=max(0,min(w,int(np.ceil((x+bw)*w/dw))))
        bottom=max(0,min(h,int(np.ceil((y+bh)*h/dh))))
        if right>left and bottom>top:
            boxes.append((left,top,right-left,bottom-top))
    return boxes,(dw,dh)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detector-max-side',type=int,default=0,
        help='Comparison-only detector resize; zero means native. Lab/mask pixels remain native.')
    args=parser.parse_args()
    if args.detector_max_side<0:
        parser.error('Detector side must be nonnegative')
    audit=importlib.import_module('26_audit_mst_mapping_feasibility')
    prepare=importlib.import_module('11_prepare_training_manifests')
    check=importlib.import_module('15_prepare_fairface_mask_review')
    previous=ROOT/'data/manifests/mst_mapping_feasibility_v1'
    source=previous/'reviewed_included_rows.csv'
    review=previous/'review_source_original.csv'
    records=sorted(audit.read(source),key=lambda r:r['image_id'])
    original={r['image_id']:r for r in audit.read(review)}
    if len(records)!=len({r['image_id'] for r in records}):
        raise ValueError('Duplicate reviewed image IDs')
    run_name='mst_mapping_mask_comparison_v1' if not args.detector_max_side else f'mst_mapping_mask_comparison_max{args.detector_max_side}_v1'
    output=ROOT/'data/manifests'/run_name
    figures=ROOT/'outputs'/run_name
    if output.exists() or figures.exists():
        raise FileExistsError('Comparison already exists; refusing overwrite')
    config=get_config()
    yunet,model=ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH
    inputs=[source,review,yunet,model,Path(__file__),ROOT/'scripts/11_prepare_training_manifests.py',
        ROOT/'src/skin_masking/skin_mask.py',ROOT/'src/skin_masking/landmark_exclusion.py',
        ROOT/'src/skin_masking/mouth_exclusion.py',ROOT/'src/ita_estimation/compute_ita.py',
        ROOT/'src/ita_estimation/mapping_feasibility.py']
    fingerprints={str(p):check.digest(p) for p in inputs}
    chosen=set(random.Random(42).sample([r['image_id'] for r in records],min(12,len(records))))
    output.mkdir();figures.mkdir()
    rows=[]
    fields=['image_id','subject_id','source_mst_label','source_lighting','historical_quality_review',
        'current_visual_review','source_sha256','historical_status','historical_ita','historical_pixels',
        'regenerated_v2_status','regenerated_v2_ita','regenerated_v2_pixels','regenerated_v2_mean_l_star',
        'regenerated_v2_mean_a_star','regenerated_v2_mean_b_star',
        'complete_mouth_status','complete_mouth_ita','complete_mouth_pixels','complete_mouth_mean_l_star',
        'complete_mouth_mean_a_star','complete_mouth_mean_b_star','historical_reproduced',
        'historical_to_v2_ita_delta','mouth_only_ita_delta','diagnostic_grid','error',
        'detector_width','detector_height','native_width','native_height','face_x','face_y','face_width','face_height']
    started=time.perf_counter()
    with (output/'image_measurement_comparison.csv').open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fields);writer.writeheader()
        for i,record in enumerate(records,1):
            image_id=record['image_id'];stored=original[image_id]
            row=dict.fromkeys(fields,'')
            row.update(image_id=image_id,subject_id=record['subject_id'],source_mst_label=int(record['source_mst_label']),
                source_lighting=record['source_lighting'],historical_quality_review=record['historical_quality_review'],
                current_visual_review='not_revalidated_for_this_version',historical_status='success',
                historical_ita=float(record['ita_degrees']),historical_pixels=int(float(stored['skin_pixels'])),
                regenerated_v2_status='not_processed',complete_mouth_status='not_processed')
            try:
                path=Path(record['image_path']);row['source_sha256']=check.digest(path)
                image=cv2.imread(str(path))
                if image is None:
                    raise ValueError('Source unreadable')
                boxes,detector_size=detect_comparison_boxes(image,prepare._detect_face_boxes,yunet,args.detector_max_side)
                row.update(detector_width=detector_size[0],detector_height=detector_size[1],
                    native_width=image.shape[1],native_height=image.shape[0])
                if len(boxes)!=1:
                    raise ValueError('single_face_required: detected '+str(len(boxes)))
                x,y,w,h=boxes[0];crop=image[y:y+h,x:x+w].copy()
                row.update(face_x=x,face_y=y,face_width=w,face_height=h)
                baseline=prepare.compute_v2_skin_mask_with_margin(crop,image,boxes[0],model)
                before=measure(crop,baseline)
                row.update({'regenerated_v2_'+key:value for key,value in before.items()})
                row['historical_reproduced']=bool(before['status']=='success' and
                    abs(before['ita']-row['historical_ita'])<=.00005 and before['pixels']==row['historical_pixels'])
                if before['ita'] is not None:
                    row['historical_to_v2_ita_delta']=before['ita']-row['historical_ita']
                current=prepare.compute_versioned_skin_mask(crop,image,boxes[0],model,'v2_complete_mouth_v1',baseline)
                after=measure(crop,current)
                if np.any((current.mask>0)&(baseline.mask==0)):
                    raise ValueError('Mouth restriction unexpectedly added pixels')
                row.update({'complete_mouth_'+key:value for key,value in after.items()})
                if before['ita'] is not None and after['ita'] is not None:
                    row['mouth_only_ita_delta']=after['ita']-before['ita']
                if image_id in chosen:
                    images=[crop,cv2.cvtColor(baseline.mask,cv2.COLOR_GRAY2BGR),cv2.cvtColor(current.mask,cv2.COLOR_GRAY2BGR)]
                    panels=[]
                    for label,panel in zip(('Original','Regenerated V2','Complete mouth'),images):
                        panel=cv2.resize(panel,(224,224),interpolation=cv2.INTER_NEAREST)
                        cv2.rectangle(panel,(0,0),(224,24),(0,0,0),-1)
                        cv2.putText(panel,label,(4,17),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,255,255),1)
                        panels.append(panel)
                    destination=figures/(image_id.replace('/','_')+'.png')
                    if not cv2.imwrite(str(destination),np.hstack(panels)):
                        raise OSError('Grid write failed')
                    row['diagnostic_grid']=destination.relative_to(ROOT).as_posix()
            except Exception as error:
                row['error']=str(error)
                if row['regenerated_v2_status']=='not_processed':row['regenerated_v2_status']='failed'
                if row['complete_mouth_status']=='not_processed':row['complete_mouth_status']='failed'
            writer.writerow(row);stream.flush();rows.append(row)
            if i%10==0:
                print(f'Compared {i}/{len(records)}; elapsed {time.perf_counter()-started:.0f}s',flush=True)
    cohorts=paired_cohorts(rows)
    summaries=[];predictions=[]
    for version,cohort in cohorts.items():
        result=leave_subject_out(cohort)
        predictions.extend(dict(r,measurement_version=version) for r in result)
        for method in sorted({r['method'] for r in result}):
            group=[r for r in result if r['method']==method]
            summaries.append(dict(measurement_version=version,method=method,view='paired_common_cohort',
                source_mst_label='',source_lighting='',**audit.metrics(group)))
            for label in range(1,11):
                subset=[r for r in group if r['source_mst_label']==label]
                if subset:
                    summaries.append(dict(measurement_version=version,method=method,view='by_label',
                        source_mst_label=label,source_lighting='',**audit.metrics(subset)))
            for lighting in sorted({r['source_lighting'] for r in group}):
                summaries.append(dict(measurement_version=version,method=method,view='by_lighting',
                    source_mst_label='',source_lighting=lighting,
                    **audit.metrics([r for r in group if r['source_lighting']==lighting])))
    audit.write(output/'paired_subject_heldout_predictions.csv',predictions)
    audit.write(output/'paired_mapping_metrics.csv',summaries)
    if any(check.digest(Path(p))!=value for p,value in fingerprints.items()):
        raise RuntimeError('Input/code/model changed during comparison')
    from collections import Counter
    report=dict(attempted_reviewed_sources=len(rows),common_sources=len(cohorts['historical']),
        common_subjects=len({r['subject_id'] for r in cohorts['historical']}),
        regenerated_v2_status=dict(Counter(r['regenerated_v2_status'] for r in rows)),
        complete_mouth_status=dict(Counter(r['complete_mouth_status'] for r in rows)),
        historical_reproduction_matches=sum(r['historical_reproduced'] is True for r in rows),
        detector_maximum_side=args.detector_max_side,measurement_resolution='native face crop; no mask/Lab resize',
        diagnostic_grid_count=sum(bool(r['diagnostic_grid']) for r in rows),
        elapsed_seconds=time.perf_counter()-started,input_sha256=fingerprints,
        overall_metrics=[r for r in summaries if r['view']=='paired_common_cohort'],
        caveat='Conditional paired comparison on historically reviewed development sources; current masks not newly human-reviewed; no final thresholds or group assignment exported.')
    (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':
    main()
