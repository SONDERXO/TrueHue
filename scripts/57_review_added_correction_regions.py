"""Prepare exact added/removed-support evidence for all38 YCrCb comparisons.

No new inference, masks, eligibility decisions or human labels are generated.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,image):
    if not cv2.imwrite(str(path),image):raise OSError(path)


def components(mask):
    count,labels,stats,_=cv2.connectedComponentsWithStats(mask.astype(np.uint8),8)
    result=[]
    for index in range(1,count):
        x,y,w,h,area=map(int,stats[index])
        component=(labels==index).astype(np.uint8)
        distance=cv2.distanceTransform(np.pad(component,1),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)[1:-1,1:-1]
        py,px=np.unravel_index(np.argmax(distance),mask.shape)
        result.append(dict(area=area,box=[x,y,w,h],interior_point=[int(px),int(py)]))
    return sorted(result,key=lambda r:(-r['area'],r['box']))


def main():
    ablation=ROOT/'outputs/ycrcb_estimation_ablation_v1'
    generation=ROOT/'outputs/hair_clean_generation_v1'
    output=ROOT/'outputs/added_correction_region_review_v1'
    if output.exists():raise FileExistsError(output)
    summary_path=ablation/'summary.json'
    rows=json.loads(summary_path.read_text())['square_pairs']
    tracked=[summary_path,Path(__file__)]
    for r in rows:
        pair=r['pair_id']
        tracked += [generation/(pair+'_input.png'),ablation/(pair+'_baseline_support.png'),ablation/(pair+'_ycrcb_support.png')]
    hashes={str(p):digest(p) for p in tracked}
    output.mkdir(parents=True)
    records=[];boards={}
    for row in rows:
        pair=row['pair_id'];source=pair.split('__',1)[1].rsplit('__',1)[0]
        variant=pair.rsplit('__',1)[1]
        image=cv2.imread(str(generation/(pair+'_input.png')))
        baseline=cv2.imread(str(ablation/(pair+'_baseline_support.png')),0)>0
        candidate=cv2.imread(str(ablation/(pair+'_ycrcb_support.png')),0)>0
        added=candidate&~baseline;removed=baseline&~candidate;retained=baseline&candidate
        assert image.shape[:2]==added.shape==(256,256)
        assert int(candidate.sum())==int(baseline.sum())+int(added.sum())-int(removed.sum())
        addition_components=components(added)
        assert sum(c['area'] for c in addition_components)==int(added.sum())
        records.append(dict(pair_id=pair,source=source,variant=variant,historical_table_use=row['historical_table_use'],
            baseline_pixels=int(baseline.sum()),candidate_pixels=int(candidate.sum()),
            added_pixels=int(added.sum()),removed_pixels=int(removed.sum()),retained_pixels=int(retained.sum()),
            addition_components=addition_components,
            warning='Connected components describe change geometry, not skin/material labels.'))
        for suffix,mask in [('added',added),('removed',removed)]:save(output/(pair+'_'+suffix+'.png'),mask.astype(np.uint8)*255)
        panels=[]
        for title,mask,color in [('Input',None,None),('ADDED only',added,[0,220,0]),('REMOVED only',removed,[0,0,255])]:
            panel=image.copy()
            if mask is not None:panel[mask]=np.rint(.35*panel[mask]+.65*np.array(color)).astype(np.uint8)
            panel=cv2.copyMakeBorder(panel,32,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(panel,variant+' '+title,(3,13),cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),1)
            cv2.putText(panel,f"+{added.sum()} / -{removed.sum()}",(3,27),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
            panels.append(panel)
        boards.setdefault(source,[]).append(np.hstack(panels))
    assert len(records)==38
    assert hashes=={p:digest(p) for p in hashes},'Inputs changed'
    (output/'change_geometry.json').write_text(json.dumps(dict(status='complete',pairs=records,input_sha256=hashes,
        warning='Review aid only; human annotations and production masks unchanged.'),indent=2),encoding='utf-8')
    links=[]
    for source,panels in boards.items():
        name=source+'_added_review.png';save(output/name,np.vstack(panels));links.append(f'- [{source}]({name})')
    (output/'review-index.md').write_text('# Added correction-region review\n\nGreen means newly selected, red means newly removed. Colors do not mean correct/incorrect.\n\n'+'\n'.join(links),encoding='utf-8')
    print(json.dumps(dict(pairs=len(records),sources=len(boards),added_pixels=sum(r['added_pixels'] for r in records),removed_pixels=sum(r['removed_pixels'] for r in records))))


if __name__=='__main__':main()
