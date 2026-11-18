"""Five fixed parser forwards on current framing; cached geometry and visibility."""
from pathlib import Path
from collections import Counter
from types import SimpleNamespace
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from scipy.io import loadmat
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.segmentation_appearance_probe import parser_input
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.faceocc_development import evaluate_parent
P=ROOT/'outputs/aligned_correction_preparation_v1'
OUT=ROOT/'outputs/current_parser_appearance_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Do not repeat or overwrite forwards')
    bound={}
    def bind(p):p=Path(p);bound[str(p)]=sha(p);return p
    def read(p):return json.loads(bind(p).read_text(encoding='utf-8'))
    def im(p):
        a=cv2.imread(str(bind(p)),cv2.IMREAD_UNCHANGED);assert a is not None;return a
    model=bind(ROOT/'models/face_parser_experimental_v1/resnet18.onnx')
    assert sha(model)=='0d9bd318e46987c3bdbfacae9e2c0f461cae1c6ac6ea6d43bbe541a91727e33f'
    for rel in ('scripts/581_compare_current_parser_appearance.py','docs/current-parser-appearance-protocol-2026-11-08.md',
        'src/skin_masking/face_parsing_experiment.py','src/skin_masking/segmentation_appearance_probe.py',
        'src/skin_masking/semantic_face_coverage.py','src/skin_masking/anatomical_face_coverage.py',
        'src/skin_masking/full_face_support.py','src/skin_masking/fixed_face_input_bridge.py',
        'src/ita_estimation/faceocc_development.py','src/ita_estimation/faceocc_veto_candidate.py',
        'src/skin_masking/faceocc_coordinates.py','src/skin_masking/faceocc_mediapipe_bridge.py',
        'src/ita_estimation/compute_ita.py'):bind(ROOT/rel)
    rows=read(P/'results_PRIVATE.json')['records']
    bindings=read(ROOT/'outputs/stellenbosch_reference_points_v1/prediction_bindings_PRIVATE.json')
    actual=read(ROOT/'outputs/stellenbosch_reference_points_import_v1/actual_export_PRIVATE.json')
    inference={r['image_id']:r for r in read(P/'inference.json')['records']}
    template=loadmat(bind(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat'))['lm']
    OUT.mkdir();net=DenseFaceParser(model);records=[];boards=[];forwards=0
    for key,b in bindings.items():
        r=next(r for r in rows if r['recipe']=='clean' and r['source_sha256']==b['source_sha256'])
        folder=Path(r['scene_path']).parent;target=OUT/key;target.mkdir()
        record=dict(review_id=key,case_id=r['case_id'],baseline_status=r['status'],status='failed',points=[])
        if not (folder/'landmarks.npy').exists():
            record['reason']=r.get('reason');records.append(record);continue
        image=im(folder/'input.png');enhanced=parser_input(image);assert cv2.imwrite(str(target/'parser_input.png'),enhanced)
        categories=net.categories_bgr(enhanced);forwards+=1
        assert cv2.imwrite(str(target/'categories.png'),categories)
        points=np.load(bind(folder/'landmarks.npy'),allow_pickle=False)
        parent_mask=build_semantic_face_coverage(image,points,categories).mask
        parent_mask[nostril_guard((256,256),points)]=0
        assert cv2.imwrite(str(target/'parent_mask.png'),parent_mask)
        stats=compute_masked_lab_statistics(image,parent_mask,1000);record['parent_statistics']=stats
        final=None
        if stats['valid']:
            prediction=inference[r['case_id']];lp=bind(P/prediction['logits_path']);assert sha(lp)==prediction['logits_sha256']
            logits=np.load(lp,allow_pickle=False)
            def cached(aligned):
                assert np.array_equal(aligned,im(folder/'aligned.png'));return logits
            result=evaluate_parent(SimpleNamespace(report=dict(status='success'),image=image,mask=parent_mask),points,template,cached)
            record.update(status=result.report['status'],measurement_report=result.report);final=result.mask
        else:record['reason']=stats['reason']
        old=im(r['measurement_native_path'])>0
        alternative=np.zeros((224,224),np.uint8)
        if final is not None:
            assert cv2.imwrite(str(target/'measurement_mask.png'),final)
            alternative=native_projection(final,r['input_bridge'])[0]
        assert cv2.imwrite(str(target/'native_grid.png'),alternative)
        new=alternative>0
        patch=im(ROOT/'outputs/stellenbosch_skin_patch_import_v2'/(key+'_patch.png'))>0
        x0,y0,x1,y1=b['native_bounds'];full=np.zeros((224,224),bool);full[y0:y1,x0:x1]=patch
        record.update(patch_pixels=int(full.sum()),baseline_diagnostic_patch=int((old&full).sum()),
            candidate_diagnostic_patch=int((new&full).sum()),baseline_usable_patch=int((old&full).sum()) if r['status']=='available' else 0,
            candidate_usable_patch=int((new&full).sum()) if record['status']=='success' else 0)
        userrow=next(q for q in actual['rows'] if q['review_id']==key)
        for point in userrow['points']:
            xx=x0+point['x'];yy=y0+point['y']
            record['points'].append(dict(label=point['label'],x=xx,y=yy,
                baseline_diagnostic=bool(old[yy,xx]),candidate_diagnostic=bool(new[yy,xx]),
                baseline_usable=bool(old[yy,xx]) if r['status']=='available' else None,
                candidate_usable=bool(new[yy,xx]) if record['status']=='success' else None))
        scene=im(r['scene_path']);panels=[scene]
        for m in (old,new):
            panel=scene.copy();panel[m]=np.rint(panel[m]*.5+np.array([0,255,0])*.5).astype(np.uint8);panels.append(panel)
        delta=scene.copy();delta[new&~old]=(255,0,255);delta[old&~new]=(255,255,0);panels.append(delta)
        title=np.full((28,896,3),255,np.uint8)
        cv2.putText(title,key+' original | raw | enhanced | added pink / lost cyan',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1)
        board=np.vstack([title,np.hstack(panels)]);boards.append(board);assert cv2.imwrite(str(target/'board.png'),board)
        records.append(record);print(key,record['baseline_status'],'->',record['status'],flush=True)
    assert forwards==5
    summary=dict(attempts=6,parser_forwards=forwards,new_other_forwards=0,new_fits=0,
        baseline_successes=sum(r['baseline_status']=='available' for r in records),candidate_successes=sum(r['status']=='success' for r in records),
        diagnostic_patch_old=sum(r.get('baseline_diagnostic_patch',0) for r in records),diagnostic_patch_new=sum(r.get('candidate_diagnostic_patch',0) for r in records),
        usable_patch_old=sum(r.get('baseline_usable_patch',0) for r in records),usable_patch_new=sum(r.get('candidate_usable_patch',0) for r in records))
    summary['points']={}
    for scope in ('diagnostic','usable'):
        counts=Counter()
        for r in records:
            for point in r['points']:
                if point['label']=='uncertain':continue
                kind='skin' if point['label']=='skin' else 'unwanted'
                a=point['baseline_'+scope];b=point['candidate_'+scope]
                if a is None or b is None:continue
                counts[kind+'_paired']+=1;counts[kind+'_old']+=int(a);counts[kind+'_new']+=int(b)
        summary['points'][scope]=dict(counts)
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'results_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records,adopted=False),indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    assert cv2.imwrite(str(OUT/'all_boards_PRIVATE.png'),np.vstack(boards))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
