"""One six-case parser replacement; original full-face scope and saved visibility."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from scipy.io import loadmat
from src.skin_masking.face_parsing_experiment import DenseFaceParser,facial_skin
from src.skin_masking.segmentation_appearance_probe import parser_input
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.faceocc_development import evaluate_parent
from src.evaluation.reference_point_review import compare_points
MODEL=ROOT/'models/face_parser_resnet34_candidate_v1'
SOURCE=ROOT/'outputs/stellenbosch_new_subjects_v1'
REVIEW=ROOT/'outputs/stellenbosch_reference_points_v1'
IMPORTED=ROOT/'outputs/stellenbosch_reference_points_import_v1'
OUT=ROOT/'outputs/resnet34_parser_comparison_v1'
EXPECTED='5b805bba7b5660ab7070b5a381dcf75e5b3e04199f1e9387232a77a00095102e'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    assert sha(MODEL/'resnet34.onnx')==EXPECTED
    bound=read(SOURCE/'inference_plan.json')['input_sha256']
    for root in [SOURCE,REVIEW,IMPORTED]:bound.update({str(root/p):h for p,h in read(root/'sha256.json').items()})
    for p in MODEL.iterdir():
        if p.is_file():bound[str(p)]=sha(p)
    for rel in ['scripts/468_compare_resnet34_parser.py','scripts/467_acquire_resnet34_parser.py','docs/resnet34-parser-comparison-protocol-2026-11-06.md']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    contract=dict(version='single_resnet34_swap_fullface_saved_visibility_v1',model_sha256=EXPECTED,
        parent_contract_sha256=read(SOURCE/'contract_PRIVATE.json')['sha256'],upper_face_candidate_used=False,dependency_sha256=bound)
    identity=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    (OUT/'contract_PRIVATE.json').write_text(json.dumps(dict(contract=contract,sha256=identity),indent=2),encoding='utf-8')
    net=DenseFaceParser(MODEL/'resnet34.onnx');template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    oldrows={r['case_id']:r for r in read(SOURCE/'results_PRIVATE.json')['records']}
    bindings=read(REVIEW/'prediction_bindings_PRIVATE.json');actual=read(IMPORTED/'actual_export_PRIVATE.json')
    records=[];predictions={};baselines={};boards=[];stages=[];forwards=0;replays=0
    for review_id,binding in bindings.items():
        old=oldrows[binding['case_id']];folder=SOURCE/binding['case_id'];target=OUT/review_id;target.mkdir()
        image=cv2.imread(str(folder/'input.png'));enhanced=parser_input(image)
        if (folder/'parser_input.png').exists():assert np.array_equal(enhanced,cv2.imread(str(folder/'parser_input.png')))
        assert cv2.imwrite(str(target/'parser_input.png'),enhanced)
        categories=net.categories_bgr(enhanced);forwards+=1
        assert cv2.imwrite(str(target/'categories.png'),categories)
        r=dict(review_id=review_id,case_id=binding['case_id'],status='failed',baseline_status=old['status'],calibration_admitted=False,training_admitted=False,MST=None)
        mask=None;parent_mask=None;stats=None
        if binding['native_grid_path'] is not None:
            x0,y0,x1,y1=binding['native_bounds'];baseline=cv2.imread(binding['native_grid_path'],0)[y0:y1,x0:x1]>0
        else:baseline=None
        baselines[review_id]=baseline;predictions[review_id]=None
        try:
            if not (folder/'landmarks.npy').exists():raise ValueError('Original required-landmark failure retained; no geometry/visibility fallback')
            points=np.load(folder/'landmarks.npy',allow_pickle=False)
            parent_mask=build_semantic_face_coverage(image,points,categories).mask.copy();parent_mask[nostril_guard((256,256),points)]=0
            assert cv2.imwrite(str(target/'parent_mask.png'),parent_mask)
            stats=compute_masked_lab_statistics(image,parent_mask,1000);r['parent_statistics']=stats
            if not stats['valid']:raise ValueError(stats['reason'])
            path=SOURCE/old['logits_path'];assert sha(path)==old['logits_sha256'];logits=np.load(path,allow_pickle=False)
            parent=SimpleNamespace(report=dict(status='success'),image=image,mask=parent_mask)
            predictor=lambda aligned:logits
            result=evaluate_parent(parent,points,template,predictor);again=evaluate_parent(parent,points,template,predictor)
            assert np.array_equal(result.aligned,cv2.imread(str(folder/'aligned_original.png')))
            assert result.report==again.report and np.array_equal(result.mask,again.mask);replays+=1
            r.update(status=result.report['status'],measurement_report=result.report);mask=result.mask
            if mask is not None:
                assert cv2.imwrite(str(target/'measurement_mask.png'),mask)
                native,account=native_projection(mask,old['input_bridge']);r['native_accounting']=account
                assert cv2.imwrite(str(target/'native_grid.png'),native)
                x0,y0,x1,y1=binding['native_bounds'];predictions[review_id]=native[y0:y1,x0:x1]>0
        except (ValueError,RuntimeError,cv2.error) as error:r['reason']=str(error)
        original_mask=cv2.imread(str(folder/'measurement_mask.png'),0) if (folder/'measurement_mask.png').exists() else np.zeros((256,256),np.uint8)
        shown=mask if mask is not None else np.zeros_like(original_mask)
        panels=[image]
        for m in [original_mask,shown]:
            overlay=image.copy();sel=m>0;overlay[sel]=np.rint(.6*image[sel]+.4*np.array([0,255,0])).astype(np.uint8);panels.append(overlay)
        delta=image.copy();a=(shown>0)&(original_mask==0);l=(original_mask>0)&(shown==0)
        delta[a]=np.rint(.6*image[a]+.4*np.array([255,0,255])).astype(np.uint8);delta[l]=np.rint(.6*image[l]+.4*np.array([255,255,0])).astype(np.uint8);panels.append(delta)
        label=np.full((26,1024,3),255,np.uint8)
        cv2.putText(label,review_id+' ResNet18 '+old['status']+' -> ResNet34 '+r['status'],(4,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        board=np.vstack([label,np.hstack(panels)]);boards.append((review_id,board));records.append(r)
        # Parser-only predictions include labels for case with unavailable geometry.
        side=old['input_bridge']['native_side'];alt_native=cv2.resize(facial_skin(categories).astype(np.uint8),(side,side),interpolation=cv2.INTER_NEAREST)>0
        oldcat=cv2.imread(str(folder/'categories.png'),0) if (folder/'categories.png').exists() else None
        old_native=None if oldcat is None else cv2.resize(facial_skin(oldcat).astype(np.uint8),(side,side),interpolation=cv2.INTER_NEAREST)>0
        userrow=next(x for x in actual['rows'] if x['review_id']==review_id)
        for p in userrow['points']:
            stages.append(dict(review_id=review_id,**p,baseline_parser_skin_nose=None if old_native is None else bool(old_native[p['y'],p['x']]),alternative_parser_skin_nose=bool(alt_native[p['y'],p['x']])))
        print(review_id+' '+r['status'],flush=True)
    oldpoints=compare_points(actual['rows'],baselines);newpoints=compare_points(actual['rows'],predictions)
    assert oldpoints['summary']==read(IMPORTED/'comparison_PRIVATE.json')['summary']
    paired=[r for r in actual['rows'] if baselines[r['review_id']] is not None and predictions[r['review_id']] is not None]
    paired_old=compare_points(paired,baselines);paired_new=compare_points(paired,predictions)
    transitions=Counter()
    for row in paired:
        rid=row['review_id']
        for p in row['points']:
            if p['label']=='uncertain':continue
            a=bool(baselines[rid][p['y'],p['x']]);b=bool(predictions[rid][p['y'],p['x']]);kind='skin' if p['label']=='skin' else 'unwanted'
            transitions[kind+('_retained' if a and b else '_gained' if b else '_lost' if a else '_still_excluded')]+=1
    summary=dict(attempts=6,parser_forwards=forwards,new_FaceOcc_forwards=0,saved_service_replays=replays,
        baseline_technical_successes=5,alternative_technical_successes=sum(r['status']=='success' for r in records),
        baseline_actual_points=oldpoints['summary'],alternative_actual_points=newpoints['summary'],
        paired_cases=len(paired),paired_baseline_points=paired_old['summary'],paired_alternative_points=paired_new['summary'],
        paired_point_transitions=dict(transitions),new_fits=0,admissions=0,independent_validation=False,effective_contract_sha256=identity)
    for name,value in [('results_PRIVATE.json',dict(summary=summary,records=records)),('actual_points_PRIVATE.json',newpoints),('parser_stage_points_PRIVATE.json',stages)]:
        (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    for name,board in boards:assert cv2.imwrite(str(OUT/(name+'.png')),board)
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private ResNet18 / ResNet34 single comparison</h1><p>Original; baseline whole-face mask; alternative whole-face mask; additions pink/losses cyan. Unavailable masks blank, not successful exclusions. Sparse exposed references, not accuracy. No redistribution.</p>'+''.join(f'<img style="max-width:100%" src="{n}.png">' for n,_ in boards),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'sha256.json').write_text(json.dumps({p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
