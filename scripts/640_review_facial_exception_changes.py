"""Exhaustive policy-change review and exact unchanged-output parity."""
from pathlib import Path
import json,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/facial_veto_exception_comparison_v1'
def main():
    target=OUT/'change_review_PRIVATE.json'
    if target.exists():raise FileExistsError('Preserve change review')
    read=lambda p:json.loads(Path(p).read_text())
    d=read(OUT/'results_PRIVATE.json');veto=read(ROOT/'outputs/reserved_clean_veto_comparison_v1/results_PRIVATE.json');pre=read(ROOT/'outputs/reserved_clean_veto_pre_comparison_v1/results_PRIVATE.json')
    old={r['case_id']:r for r in veto['records']};before={r['case_id']:r for r in pre['records']}
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    model=read(ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json');restored={r['case_id'] for r in model['exception_trace'] if r['restored']}
    boards=[];same=0;changes=[]
    for r in d['records']:
        cid=r['case_id'];a=cv2.imread(r['output_path']);b=cv2.imread(old[cid]['output_path'])
        if cid not in restored:
            assert np.array_equal(a,b) and r['candidate']==old[cid]['candidate'];same+=1;continue
        assert np.array_equal(a,cv2.imread(before[cid]['output_path']))
        changes.append(dict(case_id=cid,cohort=r['cohort'],layer=r['layer'],before=old[cid]['candidate']['region_metrics'],after=r['candidate']['region_metrics'],input=r['input_region_metrics']))
        paths=[prep[cid]['reference_path'],prep[cid]['scene_path'],old[cid]['output_path'],r['output_path']]
        title=np.full((28,896,3),255,np.uint8);cv2.putText(title,cid+' ref|input|veto|facial exception',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1)
        p=OUT/f'changed_{len(boards):02d}.png';assert cv2.imwrite(str(p),np.vstack([title,np.hstack([cv2.imread(path) for path in paths])]))
        boards.append(str(p))
    assert same==752 and len(changes)==4
    transitions={}
    for co in ('development','later'):
        rr=[r for r in d['records'] if r['cohort']==co and r['layer']=='core' and r['reference_available']]
        for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
            benefit=lambda row:row['candidate']['region_metrics'][metric]<row['input_region_metrics'][metric]
            previous={r['case_id'] for r in rr if benefit(old[r['case_id']])};current={r['case_id'] for r in rr if benefit(r)}
            transitions[co+'_'+metric]=dict(gained=sorted(current-previous),lost=sorted(previous-current))
    result=dict(unchanged_outputs_and_metrics=same,restored_pre_veto_output_parity=len(changes),changes=changes,boards=boards,transitions=transitions,
        review_selection='All four policy-restored conditions, not outcome-ranked; not independent validation',new_fits=0,holdout_image_reads=0)
    target.write_text(json.dumps(result,indent=2));print(json.dumps(dict(same=same,changes=[r['case_id'] for r in changes],transitions=transitions),indent=2))
if __name__=='__main__':main()
