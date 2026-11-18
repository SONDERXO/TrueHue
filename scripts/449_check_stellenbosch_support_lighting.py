"""Original-colour full versus shared-location support diagnostic; no inference."""
from collections import defaultdict,Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.shared_aligned_support_probe import common_support
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

BASE=ROOT/'outputs/stellenbosch_face_crop_v1'
PARENT=ROOT/'outputs/stellenbosch_faceocc_appearance_v1'
OUT=ROOT/'outputs/stellenbosch_support_lighting_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
def save(p,v):
    if not cv2.imwrite(str(p),v):raise IOError(str(p))

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    for rel in ['scripts/449_check_stellenbosch_support_lighting.py','src/skin_masking/shared_aligned_support_probe.py',
        'tests/test_shared_aligned_support_probe.py','docs/stellenbosch-support-lighting-protocol-2026-11-05.md']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();write(OUT/'input_sha256_PRIVATE.json',bound)
    rows=read(PARENT/'results_PRIVATE.json')['records'];groups=defaultdict(list)
    for row in rows:groups[row['subject_key']].append(row)
    assert len(rows)==30 and len(groups)==10 and all(len(g)==3 for g in groups.values())
    records=[];subjects=[];signs=defaultdict(Counter);full_ranges=[];shared_ranges=[];boards=[]
    for key,group in groups.items():
        complete=all(r['status']=='success' for r in group)
        shared=None;common_pixels=None
        if complete:
            masks=[cv2.imread(str(PARENT/r['case_id']/'measurement_mask.png'),0) for r in group]
            matrices=[np.array(read(PARENT/r['case_id']/'matrix.json')) for r in group]
            aligned,shared=common_support(masks,matrices);common_pixels=int(np.count_nonzero(aligned))
            save(OUT/(str(group[0]['subject_index'])+'_aligned_shared.png'),aligned)
        triplet=[];cards=[]
        for i,r in enumerate(group):
            image=cv2.imread(str(BASE/r['case_id']/'input.png'));empty=np.zeros(image.shape[:2],np.uint8)
            mask=cv2.imread(str(PARENT/r['case_id']/'measurement_mask.png'),0) if (PARENT/r['case_id']/'measurement_mask.png').exists() else empty
            rec={k:r[k] for k in ['case_id','subject_index','subject_key','condition','source_mst_exact_decimal','source_mst_raw_type','source_mst_raw_value']}
            rec.update(status=r['status'],complete_subject=complete,admitted=False,full_statistics=None,shared_statistics=None)
            if r['status']=='success':
                stats=compute_masked_lab_statistics(image,mask,1000);assert stats==r['measurement_report']['statistics']
                rec['full_statistics']=stats
                b=stats['mean_b_star'];signs[r['condition']]['negative' if b<0 else 'positive' if b>0 else 'zero']+=1
            common=shared[i] if complete else empty
            if complete:
                assert not common[mask==0].any();save(OUT/(r['case_id']+'_shared.png'),common)
                rec['shared_statistics']=compute_masked_lab_statistics(image,common,1000)
            panels=[image]
            for sel,color in [(mask>0,[0,255,0]),(common>0,[0,255,0]),((mask>0)&(common==0),[0,0,255])]:
                overlay=image.copy();overlay[sel]=np.rint(.6*image[sel]+.4*np.array(color)).astype(np.uint8);panels.append(overlay)
            label=np.full((26,1024,3),255,np.uint8)
            text=r['case_id']+' '+r['condition']+' '+r['status']+' / '+('shared probe' if complete else 'shared UNAVAILABLE incomplete subject')
            cv2.putText(label,text,(4,18),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
            cards.append(np.vstack([label,np.hstack(panels)]));triplet.append(rec);records.append(rec)
        available=complete and all(r['shared_statistics']['valid'] for r in triplet)
        subject=dict(subject_key=key,subject_index=group[0]['subject_index'],complete=complete,shared_available=available,aligned_common_pixels=common_pixels)
        if complete:
            subject['full_ITA_range']=max(r['full_statistics']['ita_degrees'] for r in triplet)-min(r['full_statistics']['ita_degrees'] for r in triplet)
        if available:
            for field in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']:
                for name in ['full','shared']:
                    values=[r[name+'_statistics'][field] for r in triplet];subject[name+'_'+field+'_range']=max(values)-min(values)
            full_ranges.append(subject['full_ita_degrees_range']);shared_ranges.append(subject['shared_ita_degrees_range'])
        subjects.append(subject);boards.append(np.vstack(cards))
    for i,board in enumerate(boards,1):save(OUT/f'contact_{i:02d}.png',board)
    def extent(values):return [min(values),float(np.median(values)),max(values)] if values else None
    summary=dict(attempts=30,subject_keys=10,full_measurements=sum(r['full_statistics'] is not None for r in records),
        complete_subjects=sum(s['complete'] for s in subjects),shared_measured_cases=sum(r['shared_statistics'] is not None for r in records),
        shared_valid_cases=sum(r['shared_statistics'] is not None and r['shared_statistics']['valid'] for r in records),
        paired_subjects=len(full_ranges),full_ITA_range_on_paired_keys_min_median_max=extent(full_ranges),
        shared_ITA_range_on_same_keys_min_median_max=extent(shared_ranges),
        paired_subjects_shared_ITA_range_smaller=sum(a<b for a,b in zip(shared_ranges,full_ranges)),
        full_b_sign_by_condition={k:dict(v) for k,v in signs.items()},
        common_region_is_skin_truth_or_dense_correspondence=False,causal_lighting_isolation=False,
        new_forwards=0,new_fits=0,admissions=0)
    write(OUT/'results_PRIVATE.json',dict(summary=summary,records=records,subjects=subjects))
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private support / lighting check</h1><p>Original; full mask green; common aligned-location probe green; selected region outside common probe red. Common probe is not skin truth or dense correspondence. Incomplete subjects have no common probe. No redistribution.</p>'+''.join(f'<img style="max-width:100%" src="contact_{i:02d}.png">' for i in range(1,11)),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    write(OUT/'sha256.json',{p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
