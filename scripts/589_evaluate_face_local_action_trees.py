"""Same-support native comparison against saved aligned parent outputs."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
P=ROOT/'outputs/aligned_correction_preparation_v1'
M=ROOT/'outputs/face_local_action_models_v1/models_PRIVATE.json'
OUT=ROOT/'outputs/face_local_action_comparison_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    if OUT.exists():raise FileExistsError('Preserve completed comparison')
    model=read(M);pred={r['case_id']:r for r in model['predictions']}
    parent_path=ROOT/'outputs/aligned_action_tree_comparison_v1/results_PRIVATE.json'
    parent=read(parent_path);old={r['case_id']:r for r in parent['records']}
    prep=read(P/'results_PRIVATE.json')['records'];bound=dict(model['input_sha256'])
    for p in (M,parent_path,Path(__file__),ROOT/'src/model_training/blended_recovery_targets.py',ROOT/'src/model_training/photographic_target_diagnostic.py'):bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();records=[];boards=[];parentboards={str(Path(p).parent) for p in parent['boards']}
    for r in prep:
        cid=r['case_id'];q=pred[cid];baseline=old[cid];im=rgb(r['scene_path']);ref=rgb(r['reference_path'])
        ready=r['status']=='available';alpha=np.load(r['alpha_path'],allow_pickle=False) if ready else np.zeros(im.shape[:2],float)
        output=render_rgb8(im,alpha,q['parameters']) if ready else im.copy()
        protected=cv2.imread(r['protected_path'],0)>0 if r.get('protected_path') else np.zeros(alpha.shape,bool)
        assert np.array_equal(output[alpha==0],im[alpha==0]) and np.array_equal(output[protected],im[protected])
        folder=OUT/cid;folder.mkdir();path=folder/'face_local.png';assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
        scoring=cv2.imread(r['scoring_path'],0)>0 if r['reference_support_available'] else None
        item=dict(parameters=q['parameters'],prediction_available=ready,changed_channels=int(np.count_nonzero(output!=im)),
            region_metrics=metrics(output,ref,scoring) if scoring is not None else None,
            scene_metrics=metrics(output,ref,np.ones(alpha.shape,bool)))
        record=dict(case_id=cid,cohort=r['cohort'],subject_id=r['subject_id'],recipe=r['recipe'],layer=r['layer'],
            mask_status=r['status'],reference_available=scoring is not None,input_region_metrics=r['input_region_metrics'],
            parent=baseline['paths']['aligned_tree'],candidate=item,output_path=str(path),
            parent_output_path=baseline['output_paths']['aligned_tree'])
        records.append(record)
        if cid in parentboards:
            parentim=rgb(record['parent_output_path']);bound[record['parent_output_path']]=sha(record['parent_output_path'])
            title=np.full((28,896,3),255,np.uint8);cv2.putText(title,cid+' ref | input | aligned parent | face-local',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1)
            board=np.vstack([title,np.hstack([ref,im,parentim,output])]);bp=folder/'board.png'
            assert cv2.imwrite(str(bp),cv2.cvtColor(board,cv2.COLOR_RGB2BGR));boards.append(str(bp))
    summary={}
    for cohort in ('development','later'):
        summary[cohort]={}
        for layer in ('clean','core','composite_stress_design'):
            rows=[r for r in records if r['cohort']==cohort and r['layer']==layer];scored=[r for r in rows if r['reference_available']]
            ss=dict(attempts=len(rows),available=sum(r['mask_status']=='available' for r in rows),scored=len(scored),methods={})
            for method in ('parent','candidate'):
                ss['methods'][method]=dict(changed=sum(r[method]['changed_channels']>0 for r in rows),
                    region_MAE=float(np.mean([r[method]['region_metrics']['rgb8_mae_codes'] for r in scored])),
                    harms=sum(r[method]['region_metrics']['rgb8_mae_codes']>r['input_region_metrics']['rgb8_mae_codes'] for r in scored),
                    benefits=sum(r[method]['region_metrics']['rgb8_mae_codes']<r['input_region_metrics']['rgb8_mae_codes'] for r in scored),
                    worst_excess=max(r[method]['region_metrics']['rgb8_mae_codes']-r['input_region_metrics']['rgb8_mae_codes'] for r in scored),
                    equal_key_MAE=float(np.mean([np.mean([r[method]['region_metrics']['rgb8_mae_codes'] for r in scored if r['subject_id']==k]) for k in sorted({r['subject_id'] for r in scored})])))
            summary[cohort][layer]=ss
    result=dict(summary=summary,records=records,boards=boards,new_fits=0,production_adopted=False)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    sheets=OUT/'contact_sheets';sheets.mkdir()
    for start in range(0,len(boards),4):assert cv2.imwrite(str(sheets/f'{start//4:02d}.png'),np.vstack([cv2.imread(p) for p in boards[start:start+4]]))
    assert all(sha(p)==h for p,h in bound.items());print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
