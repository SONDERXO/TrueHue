"""Fixed30 development originals, native-anchor preparation only; no fits."""
from pathlib import Path
import hashlib,importlib,json,sys,traceback
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2,numpy as np
from scipy.io import loadmat
from src.skin_masking.native_anchor_bridge import crop_native_anchor
from src.skin_masking.faceocc_mediapipe_bridge import align_input
OUT=ROOT/'outputs/labelled_brightness_screen_v1'
OLD=ROOT/'outputs/aligned_correction_preparation_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
def save(p,a):
    if not cv2.imwrite(str(p),a):raise IOError(str(p))

def main():
    if OUT.exists():raise FileExistsError('Preserve partial or completed preparation')
    roster=read(ROOT/'outputs/labelled_brightness_coverage_review_v1/candidate_roster_PRIVATE.json')
    groups=read(ROOT/'outputs/group_diversity_candidates_v1/plan_PRIVATE.json')['groups']
    locked={r['subject_key'] for r in groups if r['role']=='closed_holdout_candidate'}
    sources=[dict(source_case=f"bright_{i:02d}", source_path=r['source_path'], source_sha256=r['sha256'],
        subject_id=r['subject_key'],condition=r['condition'],source_mst_exact_decimal=r['source_mst_exact_decimal'],
        cohort='development_brightness_screen') for i,r in enumerate(roster,1)]
    assert len(sources)==30 and len({r['subject_id'] for r in sources})==10
    assert not ({r['subject_id'] for r in sources}&locked)
    helper=importlib.import_module('419_preview_object_protected_face');bound,inner=helper.dependencies()
    for r in sources:
        assert sha(r['source_path'])==r['source_sha256'];bound[r['source_path']]=r['source_sha256']
    for p in [Path(__file__),ROOT/'scripts/757_run_brightness_faceocc.py',ROOT/'scripts/369_run_faceocc_logits.py',
        ROOT/'scripts/758_finalize_brightness_screen.py',ROOT/'src/skin_masking/native_anchor_bridge.py',
        ROOT/'docs/labelled-brightness-screen-protocol-2026-11-10.md',
        ROOT/'outputs/labelled_brightness_coverage_review_v1/candidate_roster_PRIVATE.json',
        ROOT/'outputs/group_diversity_candidates_v1/plan_PRIVATE.json']:
        bound[str(p)]=sha(p)
    contract=dict(version='native_anchor_brightness_screen_v1',inner_measurement_contract=inner,
        anchor='original_native_YuNet_0.85_NMS0.3_topK5000',bridge='native_anchor_square_context_1p5_v1',
        bridge_sha256=sha(ROOT/'src/skin_masking/native_anchor_bridge.py'),minimum_normalized_pixels=1000,
        colour='source_JPEG_assumed_sRGB_no_new_calibration',parser='original_not_enhanced',
        FaceOcc='raw_aligned_strict_gt0',source_scores='original_exact_decimal_reporting_only')
    identity=hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'logits').mkdir()
    write(OUT/'plan_PRIVATE.json',dict(sources=sources,contract=contract,measurement_contract_sha256=identity,input_sha256=bound))
    old=importlib.import_module('11_prepare_training_manifests');module=importlib.import_module('569_prepare_aligned_pipeline')
    counts=dict(detector_forwards=0,landmarker_helper_calls=0,parser_forwards=0)
    od=old._detect_face_boxes;ol=old.detect_face_landmarks;op=module.DenseFaceParser.categories_bgr
    def detector_count(*a,**kw):counts['detector_forwards']+=1;return od(*a,**kw)
    def landmark_count(*a,**kw):counts['landmarker_helper_calls']+=1;return ol(*a,**kw)
    def parser_count(self,*a,**kw):counts['parser_forwards']+=1;return op(self,*a,**kw)
    old._detect_face_boxes=detector_count;old.detect_face_landmarks=landmark_count;module.DenseFaceParser.categories_bgr=parser_count
    rows=[];attempts=[]
    try:
        detector,parent=module.initialize();template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
        for index,s in enumerate(sources,1):
            folder=OUT/s['source_case'];folder.mkdir();image=cv2.imread(s['source_path']);assert image is not None
            before=dict(counts);r=dict(s,status='unavailable',stage='anchor',measurement_contract_sha256=identity,
                training_admitted=False,calibration_admitted=False,case_index=index)
            try:
                boxes=detector(image);r['native_anchor_boxes']=[list(map(int,b)) for b in boxes]
                if len(boxes)!=1:raise ValueError('Exactly one native anchor required')
                crop,bridge=crop_native_anchor(image,native_box=boxes[0]);r['input_bridge']=bridge;save(folder/'native_input.png',crop)
                result,cache=parent(crop);r.update(stage='parent',parent_report=result.report,landmark_details=cache.get('landmark_details'))
                if result.image is not None:save(folder/'input.png',result.image)
                if result.mask is not None:save(folder/'parent_mask.png',result.mask)
                if cache.get('points') is not None:np.save(folder/'landmarks.npy',cache['points'],allow_pickle=False)
                if 'categories' in cache:save(folder/'categories.png',cache['categories'])
                if result.report['status']!='success':raise ValueError(result.report.get('reason','Parent failed'))
                aligned,matrix,details=align_input(result.image,cache['points'],template)
                save(folder/'aligned.png',aligned);write(folder/'matrix.json',matrix.tolist())
                r.update(status='inference_ready',stage='FaceOcc_pending',alignment=details)
                attempts.append(dict(image_id=s['source_case'],case_index=index,aligned_path=str(folder/'aligned.png')))
            except (ValueError,RuntimeError,cv2.error) as error:r['reason']=str(error)
            r['calls']={k:counts[k]-before[k] for k in counts};write(folder/'preparation_PRIVATE.json',r);rows.append(r)
            print(s['source_case'],r['status'],r.get('reason',''),flush=True)
        assert counts['detector_forwards']<=60 and counts['parser_forwards']<=30
        assert all(sha(p)==h for p,h in bound.items())
        write(OUT/'preparation_PRIVATE.json',dict(records=rows,counts=counts,inference_ready=len(attempts)))
        batchbound=dict(bound)
        for r in attempts:batchbound[r['aligned_path']]=sha(r['aligned_path'])
        batchbound[str(OUT/'preparation_PRIVATE.json')]=sha(OUT/'preparation_PRIVATE.json')
        write(OUT/'inference_plan.json',dict(attempts=attempts,input_sha256=batchbound))
        print('Prepared',len(rows),'FaceOcc-ready',len(attempts),'counts',counts,flush=True)
    except Exception:
        write(OUT/'failure_prepare_PRIVATE.json',dict(completed=len(rows),traceback=traceback.format_exc()));raise
    finally:
        old._detect_face_boxes=od;old.detect_face_landmarks=ol;module.DenseFaceParser.categories_bgr=op
if __name__=='__main__':main()
