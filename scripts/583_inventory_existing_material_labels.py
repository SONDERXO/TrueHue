"""Audit completed reference labels for a material-learning plan; no training."""
from pathlib import Path
from collections import Counter
import hashlib,json
import cv2
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/material_label_inventory_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve inventory')
    bound={}
    def read(p):
        p=Path(p);bound[str(p)]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    points=read(ROOT/'outputs/stellenbosch_reference_points_import_v1/actual_export_PRIVATE.json')
    patches=read(ROOT/'outputs/stellenbosch_skin_patch_import_v2/actual_export_PRIVATE.json')
    bindings=read(ROOT/'outputs/stellenbosch_reference_points_v1/prediction_bindings_PRIVATE.json')
    source=read(ROOT/'outputs/stellenbosch_new_subjects_v1/results_PRIVATE.json')['records']
    records=[];totals=Counter();keys=set();conflicts=[]
    for row in points['rows']:
        key=row['review_id'];b=bindings[key]
        s=next(r for r in source if r['source_sha256']==b['source_sha256']);keys.add(s['subject_key'])
        p=ROOT/'outputs/stellenbosch_skin_patch_import_v2'/(key+'_patch.png');bound[str(p)]=sha(p)
        mask=cv2.imread(str(p),0);assert mask is not None
        patchrow=next(r for r in patches['rows'] if r['review_id']==key)
        assert row['image_sha256']==patchrow['image_sha256']
        counts=Counter(pt['label'] for pt in row['points']);inside=Counter()
        for pt in row['points']:
            if mask[pt['y'],pt['x']]>0:
                inside[pt['label']]+=1
                if pt['label'] in ('hair_or_beard','object_or_other'):
                    conflicts.append(dict(review_id=key,x=pt['x'],y=pt['y'],point_label=pt['label'],patch_label='selected_skin_patch'))
        totals.update(counts)
        records.append(dict(review_id=key,source_case=b['case_id'],publisher_group=s['subject_key'],
            points=dict(counts),points_inside_patches=dict(inside),polygons=len(patchrow['polygons']),
            patch_pixels=int((mask>0).sum())))
    result=dict(photos=len(records),publisher_groups=len(keys),point_counts=dict(totals),
        polygons=sum(r['polygons'] for r in records),patch_pixels=sum(r['patch_pixels'] for r in records),
        point_patch_conflicts=conflicts,records=records,
        separate_beard_labels=False,separate_glasses_frame_labels=False,separate_clear_lens_labels=False,
        dense_negative_masks=False,independent_unexposed_validation=False,
        new_fits=0,new_inference=0,new_annotations=0,training_admitted=False)
    assert result['photos']==6 and result['patch_pixels']==3156 and sum(totals.values())==238
    bound[str(Path(__file__))]=sha(Path(__file__))
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
    for r in records:print(r['review_id'],r['points'],r['points_inside_patches'])

if __name__=='__main__':main()
