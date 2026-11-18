"""Fixed clean regression and explicitly outcome-selected veto recovery losses."""
from pathlib import Path
import json,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/reserved_clean_veto_comparison_v1'
def main():
    target=OUT/'veto_attribution_review_PRIVATE.json'
    if target.exists():raise FileExistsError('Preserve attribution review')
    read=lambda p:json.loads(Path(p).read_text())
    final=read(OUT/'results_PRIVATE.json');pre=read(ROOT/'outputs/reserved_clean_veto_pre_comparison_v1/results_PRIVATE.json')
    before={r['case_id']:r for r in pre['records']};after={r['case_id']:r for r in final['records']}
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    selected=[dict(case_id='case_28__clean',selection='Fixed clean regression case from preceding experiment')];transitions={}
    for co in ('development','later'):
        rr=[r for r in final['records'] if r['cohort']==co and r['layer']=='core' and r['reference_available']]
        r=max(rr,key=lambda r:r['candidate']['region_metrics']['rgb8_mae_codes']-before[r['case_id']]['candidate']['region_metrics']['rgb8_mae_codes'])
        selected.append(dict(case_id=r['case_id'],selection='Outcome selected: largest veto-induced core RGB error increase in '+co))
        old={r['case_id'] for r in rr if before[r['case_id']]['candidate']['region_metrics']['rgb8_mae_codes']<r['input_region_metrics']['rgb8_mae_codes']}
        new={r['case_id'] for r in rr if r['candidate']['region_metrics']['rgb8_mae_codes']<r['input_region_metrics']['rgb8_mae_codes']}
        transitions[co]=dict(lost_benefits=sorted(old-new),gained_benefits=sorted(new-old))
    for i,s in enumerate(selected):
        cid=s['case_id'];p=prep[cid];paths=[p['reference_path'],p['scene_path'],before[cid]['output_path'],after[cid]['output_path']]
        title=np.full((28,896,3),255,np.uint8);cv2.putText(title,cid+' ref|input|reserved pre-veto|post-veto',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1)
        out=OUT/f'veto_attribution_{i:02d}.png';assert cv2.imwrite(str(out),np.vstack([title,np.hstack([cv2.imread(p) for p in paths])]))
        s.update(path=str(out),pre_error=before[cid]['candidate']['region_metrics']['rgb8_mae_codes'],post_error=after[cid]['candidate']['region_metrics']['rgb8_mae_codes'])
    target.write_text(json.dumps(dict(boards=selected,transitions=transitions,new_fits=0,holdout_image_reads=0),indent=2));print(json.dumps(selected,indent=2))
if __name__=='__main__':main()
