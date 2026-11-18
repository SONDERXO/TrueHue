"""Fixed1040actual distorted inputs and raw parent masks; no holdout or fits."""
from pathlib import Path
from collections import Counter
import json,hashlib,runpy,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2,numpy as np
from scipy.io import loadmat
from src.skin_masking.fixed_face_input_bridge import crop_face
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.model_training.photographic_target_diagnostic import distort
PLAN=ROOT/'outputs/expanded_correction_training_plan_v1'
OUT=ROOT/'outputs/expanded_correction_inputs_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve partial/completed preparation; no repeated forwards')
    assert read(PLAN/'verification_PRIVATE.json')['passed'];plan=read(PLAN/'plan_PRIVATE.json')
    clean=read(ROOT/'outputs/group_diversity_final_masks_v1/results_PRIVATE.json');cleanrows={r['case_id']:r for r in clean['records']}
    bound=read(ROOT/'outputs/group_diversity_final_masks_v1/final_input_sha256_PRIVATE.json')
    for p in (Path(__file__),PLAN/'plan_PRIVATE.json',PLAN/'verification_PRIVATE.json',ROOT/'docs/expanded-correction-training-protocol-2026-11-08.md',ROOT/'scripts/569_prepare_aligned_pipeline.py',ROOT/'scripts/609_run_expanded_faceocc.py'):
        bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    ns=runpy.run_path(str(ROOT/'scripts/569_prepare_aligned_pipeline.py'));detector,parent=ns['initialize']()
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    OUT.mkdir();(OUT/'cases').mkdir();(OUT/'references').mkdir();(OUT/'logits').mkdir()
    (OUT/'frozen_plan_PRIVATE.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    records=[];attempts=[];images={};parsercalls=0
    for i,item in enumerate(plan['pending_distortions'],1):
        source=item['source_case'];origin=cleanrows[source]
        assert origin['status']=='available' and item['subject_key'] not in plan['closed_holdout_keys']
        if source not in images:
            p=Path(item['source_path']);assert sha(p)==item['source_sha256'];bound[str(p)]=item['source_sha256']
            images[source]=cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
            assert cv2.imwrite(str(OUT/'references'/(source+'.png')),cv2.cvtColor(images[source],cv2.COLOR_RGB2BGR))
        scene,details,_=distort(images[source],np.ones(images[source].shape[:2]),item['recipe'])
        image=cv2.cvtColor(scene,cv2.COLOR_RGB2BGR);folder=OUT/'cases'/item['case_id'];folder.mkdir()
        path=folder/'scene_input.png';assert cv2.imwrite(str(path),image)
        r=dict(case_id=item['case_id'],case_index=i,source_case=source,subject_id=item['subject_key'],cohort='expanded_development',
            source_path=item['source_path'],source_sha256=item['source_sha256'],source_mst_exact_decimal=item['source_score'],
            recipe=item['recipe']['id'],layer=item['recipe']['layer'],distortion=details,status='failed',stage='actual_input_anchor',
            scene_path=str(path),reference_path=str(OUT/'references'/(source+'.png')),
            training_admitted=False,calibration_admitted=False,scientific_admission=False)
        try:
            boxes=detector(cv2.resize(image,(256,256),interpolation=cv2.INTER_LINEAR));r['anchor_face_count']=len(boxes)
            if len(boxes)!=1:raise ValueError('Exactly one actual-input anchor face required')
            native,bridge=crop_face(image,boxes[0]);r['input_bridge']=bridge;assert cv2.imwrite(str(folder/'native_input.png'),native)
            result,cache=parent(native);r.update(stage='parent_measurement',parent_report=result.report)
            if result.image is not None:assert cv2.imwrite(str(folder/'input.png'),result.image)
            if result.mask is not None:assert cv2.imwrite(str(folder/'parent_mask.png'),result.mask)
            if cache.get('points') is not None:np.save(folder/'landmarks.npy',cache['points'],allow_pickle=False)
            if 'categories' in cache:
                parsercalls+=1;assert cv2.imwrite(str(folder/'categories.png'),cache['categories'])
            if result.report['status']!='success':raise ValueError(result.report.get('reason','Parent measurement failed'))
            aligned,matrix,details=align_input(result.image,cache['points'],template)
            ap=folder/'aligned.png';assert cv2.imwrite(str(ap),aligned);bound[str(ap)]=sha(ap)
            r.update(status='inference_ready',stage='FaceOcc_pending',alignment=details,matrix=matrix.tolist())
            attempts.append(dict(image_id=r['case_id'],case_index=i,aligned_path=str(ap)))
        except (ValueError,RuntimeError,cv2.error) as e:r['reason']=str(e)
        (folder/'preparation_PRIVATE.json').write_text(json.dumps(r,indent=2),encoding='utf-8');records.append(r)
        if i%13==0:print(i,'/1040;',len(attempts),'FaceOcc-ready;',parsercalls,'parser forwards',flush=True)
    assert len(records)==1040 and len(images)==80 and all(sha(p)==h for p,h in bound.items())
    summary=dict(attempts=1040,source_originals=80,parser_forwards=parsercalls,FaceOcc_ready=len(attempts),
        failures_by_stage=dict(Counter(r['stage'] for r in records if r['status']!='inference_ready')),holdout_image_reads=0,new_fits=0)
    (OUT/'preparation_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records),indent=2),encoding='utf-8')
    (OUT/'inference_plan.json').write_text(json.dumps(dict(attempts=attempts,input_sha256=bound,new_fits=0),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
