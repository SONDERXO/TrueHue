"""Reconstruct fixed mask stages from cached categories/landmarks, no forwards."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.semantic_face_coverage import select_face_skin
from src.skin_masking.full_face_support import nostril_guard
from src.skin_masking.fixed_face_input_bridge import native_projection
OUT=ROOT/'outputs/saved_parent_mask_trace_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve existing trace')
    bound={};boards=[]
    def bind(p):
        p=Path(p);bound[str(p)]=sha(p);return p
    def read(p):return json.loads(bind(p).read_text(encoding='utf-8'))
    def im(p):
        a=cv2.imread(str(bind(p)),cv2.IMREAD_UNCHANGED);assert a is not None;return a
    for rel in ('scripts/579_trace_saved_parent_masks.py','src/skin_masking/anatomical_face_coverage.py',
                'src/skin_masking/semantic_face_coverage.py','src/skin_masking/full_face_support.py',
                'src/skin_masking/fixed_face_input_bridge.py','src/skin_masking/face_parsing_experiment.py',
                'src/skin_masking/face_outline_experiment.py','src/skin_masking/landmark_exclusion.py',
                'src/skin_masking/mouth_exclusion.py'):bind(ROOT/rel)
    prep=read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']
    bindings=read(ROOT/'outputs/stellenbosch_reference_points_v1/prediction_bindings_PRIVATE.json')
    records=[]
    for key,b in bindings.items():
        r=next(r for r in prep if r['recipe']=='clean' and r['source_sha256']==b['source_sha256'])
        patch=im(ROOT/'outputs/stellenbosch_skin_patch_import_v2'/(key+'_patch.png'))>0
        full=np.zeros((224,224),bool);x0,y0,x1,y1=b['native_bounds'];full[y0:y1,x0:x1]=patch
        folder=Path(r['scene_path']).parent
        if not (folder/'categories.png').exists():
            records.append(dict(review_id=key,case_id=r['case_id'],status='unavailable',reason=r.get('reason'),patch_pixels=int(full.sum())))
            continue
        image=im(folder/'input.png');categories=im(folder/'categories.png')
        points=np.load(bind(folder/'landmarks.npy'),allow_pickle=False)
        geometry=build_face_coverage(image,points);allowed=np.isin(categories,[1,10])
        n,labels=cv2.connectedComponents(allowed.astype(np.uint8),connectivity=8)
        ids=set(np.unique(labels[allowed&(geometry.face_outline>0)]).tolist())-{0}
        associated=allowed&np.isin(labels,sorted(ids))
        anatomical=associated&~(geometry.exclusion_mask>0)
        selected,report=select_face_skin(categories,geometry.face_outline>0,geometry.exclusion_mask>0)
        assert np.array_equal(selected>0,anatomical)
        guarded=anatomical&~nostril_guard(anatomical.shape,points)
        assert np.array_equal(guarded,im(folder/'parent_mask.png')>0)
        stages=dict(parser=allowed,associated=associated,anatomical=anatomical,nostril=guarded,
                    final=im(folder/'measurement_mask.png')>0)
        projected={name:native_projection(a.astype(np.uint8)*255,r['input_bridge'])[0]>0 for name,a in stages.items()}
        counts={name:int((a&full).sum()) for name,a in projected.items()}
        for before,after in zip(list(projected),list(projected)[1:]):assert not (projected[after]&~projected[before]).any()
        bx0,by0,bx1,by1=r['input_bridge']['native_bounds'];inside=np.zeros_like(full);inside[by0:by1,bx0:bx1]=True
        losses=dict(outside_crop=int((full&~inside).sum()),parser_not_skin=int((full&inside&~projected['parser']).sum()))
        names=list(projected)
        for before,after in zip(names,names[1:]):losses[after]=counts[before]-counts[after]
        assert sum(losses.values())+counts['final']==int(full.sum())
        assert np.array_equal(projected['final'],im(r['measurement_native_path'])>0)
        native_categories=cv2.resize(categories,(bx1-bx0,by1-by0),interpolation=cv2.INTER_NEAREST)
        histogram=dict(Counter(map(int,native_categories[full[by0:by1,bx0:bx1]].tolist())))
        records.append(dict(review_id=key,case_id=r['case_id'],status='traced',measurement_status=r['status'],
            patch_pixels=int(full.sum()),overlap_by_stage=counts,disjoint_losses=losses,parser_classes_on_patch=histogram))
        scene=im(r['scene_path']);panels=[]
        for name,support in [('patches',full)]+list(projected.items()):
            panel=scene.copy();panel[support]=(panel[support]*.4+np.array([0,220,0])*.6).astype(np.uint8)
            panel=cv2.resize(panel,(224,224),interpolation=cv2.INTER_NEAREST)
            cv2.putText(panel,name,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.45,(255,255,255),1);panels.append(panel)
        title=np.full((27,1344,3),255,np.uint8);cv2.putText(title,key+' '+r['case_id']+' SAVED TRACE',(4,20),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack([title,np.hstack(panels)]))
    traced=[r for r in records if r['status']=='traced'];totals=Counter()
    for r in traced:totals.update(r['disjoint_losses'])
    result=dict(records=records,totals=dict(patch_pixels=sum(r['patch_pixels'] for r in traced),
        final_overlap=sum(r['overlap_by_stage']['final'] for r in traced),losses=dict(totals)),
        new_fits=0,new_inference=0,limitation='Selected patches include neck; losses describe this fixed pipeline, not validated skin classes or mask precision.')
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();assert cv2.imwrite(str(OUT/'all_trace_boards_PRIVATE.png'),np.vstack(boards))
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
