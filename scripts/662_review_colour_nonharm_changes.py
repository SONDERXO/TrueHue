"""Exhaustive changed-decision boards and unchanged-output parity against prior candidate."""
from pathlib import Path
import json
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/colour_nonharm_comparison_v1'
def main():
    target=OUT/'changes_PRIVATE.json'
    if target.exists():raise FileExistsError('Preserve review')
    read=lambda p:json.loads(Path(p).read_text())
    d=read(OUT/'results_PRIVATE.json');old={r['case_id']:r for r in read(ROOT/'outputs/facial_veto_exception_comparison_v1/results_PRIVATE.json')['records']}
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']};same=0;changes=[];boards=[]
    for r in d['records']:
        p=old[r['case_id']];a=cv2.imread(r['output_path']);b=cv2.imread(p['output_path'])
        if r['candidate']['parameters']==p['candidate']['parameters']:
            assert np.array_equal(a,b) and r['candidate']==p['candidate'];same+=1;continue
        cid=r['case_id'];q=prep[cid];changes.append(dict(case_id=cid,cohort=r['cohort'],layer=r['layer'],before=p['candidate']['region_metrics'],after=r['candidate']['region_metrics'],input=r['input_region_metrics']))
        title=np.full((28,896,3),255,np.uint8);cv2.putText(title,cid+' ref|input|previous|colour nonharm',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1)
        board=np.vstack([title,np.hstack([cv2.imread(q['reference_path']),cv2.imread(q['scene_path']),b,a])]);path=OUT/f'change_{len(boards):02d}.png';assert cv2.imwrite(str(path),board);boards.append(str(path))
    assert same==743 and len(changes)==13
    sheets=[]
    for start in range(0,len(boards),4):
        p=OUT/f'change_sheet_{start//4:02d}.png';assert cv2.imwrite(str(p),np.vstack([cv2.imread(b) for b in boards[start:start+4]]));sheets.append(str(p))
    target.write_text(json.dumps(dict(unchanged_outputs_and_metrics=same,changes=changes,boards=boards,sheets=sheets,selection='All13 changed decisions, not outcome-selected',new_fits=0,holdout_image_reads=0),indent=2))
    print('PASS743unchanged;13changeddecisionboards')
if __name__=='__main__':main()
