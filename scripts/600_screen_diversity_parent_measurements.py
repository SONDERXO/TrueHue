"""Exactly96development photos, unchanged parent pipeline, closedholdout untouched."""
from pathlib import Path
import json,hashlib,runpy,sys
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.skin_masking.fixed_face_input_bridge import crop_face,native_projection
P=ROOT/'outputs/group_diversity_candidates_v1';OUT=ROOT/'outputs/group_diversity_parent_screen_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve partial/completed screen; do not repeat forwards')
    assert read(P/'verification_PRIVATE.json')['passed'];plan=read(P/'plan_PRIVATE.json')
    rows=[r for r in plan['selection'] if r['role']=='development_candidate'];assert len(rows)==96
    hold={r['source_sha256'] for r in plan['selection'] if r['role']=='closed_holdout_candidate'}
    assert not hold&{r['source_sha256'] for r in rows}
    oldplan=read(ROOT/'outputs/aligned_correction_preparation_v1/plan_PRIVATE.json')
    bound={p:h for p,h in oldplan['input_sha256'].items() if not p.lower().endswith(('.jpeg','.jpg','.png'))}
    for p in (Path(__file__),P/'plan_PRIVATE.json',P/'verification_PRIVATE.json',ROOT/'scripts/569_prepare_aligned_pipeline.py',ROOT/'docs/group-diversity-parent-screen-protocol-2026-11-08.md'):bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    ns=runpy.run_path(str(ROOT/'scripts/569_prepare_aligned_pipeline.py'));detector,parent=ns['initialize']()
    OUT.mkdir();(OUT/'plan_PRIVATE.json').write_text(json.dumps(dict(selection=rows,heldout_image_reads=0,contract=oldplan['contract'],input_sha256=bound),indent=2),encoding='utf-8')
    records=[];parser_calls=0
    for i,source in enumerate(rows,1):
        cid=f'diversity_{i:03d}';folder=OUT/cid;folder.mkdir()
        p=Path(source['source_path']);assert sha(p)==source['source_sha256'];bound[str(p)]=source['source_sha256']
        image=cv2.imread(str(p));assert image is not None
        r=dict(source,case_id=cid,status='failed',stage='actual_input_anchor',parent_only=True)
        assert cv2.imwrite(str(folder/'scene_input.png'),image)
        try:
            boxes=detector(cv2.resize(image,(256,256),interpolation=cv2.INTER_LINEAR));r['anchor_face_count']=len(boxes)
            if len(boxes)!=1:raise ValueError('Exactly one actual-input anchor face required')
            native,bridge=crop_face(image,boxes[0]);r['input_bridge']=bridge
            assert cv2.imwrite(str(folder/'native_input.png'),native)
            result,cache=parent(native);r.update(stage='parent_measurement',parent_report=result.report)
            if result.image is not None:assert cv2.imwrite(str(folder/'input.png'),result.image)
            if result.mask is not None:
                assert cv2.imwrite(str(folder/'parent_mask.png'),result.mask)
                projected,account=native_projection(result.mask,bridge);r['native_accounting']=account
                assert cv2.imwrite(str(folder/'parent_native.png'),projected)
            if cache.get('points') is not None:np.save(folder/'landmarks.npy',cache['points'],allow_pickle=False)
            if 'categories' in cache:
                parser_calls+=1;assert cv2.imwrite(str(folder/'categories.png'),cache['categories'])
            if result.report['status']!='success':raise ValueError(result.report.get('reason','Parent measurement failed'))
            r['status']='parent_available'
        except (ValueError,RuntimeError,cv2.error) as e:r['reason']=str(e)
        (folder/'report_PRIVATE.json').write_text(json.dumps(r,indent=2),encoding='utf-8');records.append(r)
        print(i,'/96',r['status'],flush=True)
    summary=dict(attempts=96,parent_available=sum(r['status']=='parent_available' for r in records),
        parser_forwards=parser_calls,failures_by_reason=dict(Counter(r.get('reason') for r in records if r['status']!='parent_available')),
        groups_with_all_three_parent_passes=sum(all(r['status']=='parent_available' for r in records if r['subject_key']==key) for key in {r['subject_key'] for r in records}),
        FaceOcc_forwards=0,new_fits=0,holdout_image_reads=0,scientific_admissions=0,
        parent_pass_is_final_mask_availability=False)
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'results_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records),indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
