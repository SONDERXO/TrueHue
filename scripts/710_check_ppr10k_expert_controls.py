"""Expert target identity-control readiness; own measurements, no fitting."""
from pathlib import Path
from types import SimpleNamespace
import hashlib, importlib, json, subprocess, sys, traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
import tifffile
from PIL import ImageCms
from io import BytesIO
from scipy.io import loadmat
from src.utilities.config import get_config
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.skin_masking.native_anchor_bridge import crop_native_anchor
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.ita_estimation.faceocc_development import evaluate_parent
from src.skin_masking.correction_preview import render_preview
from src.model_training.aligned_correction_support import project_alpha

BASE=ROOT/'outputs/ppr10k_new_group_comparison_v1'
OUT=ROOT/'outputs/ppr10k_expert_control_readiness_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
def save(p,a):
    if not cv2.imwrite(str(p),a):raise IOError(str(p))

def main():
    if OUT.exists():raise FileExistsError('Preserve screen/partial artifacts; no repeat inference')
    helper=importlib.import_module('419_preview_object_protected_face')
    bound,identity=helper.dependencies()
    sample=read(BASE/'frozen_sample.json');audit=read(BASE/'image_audit.json')
    historical=read(BASE/'sha256.json');regions=read(BASE/'source_regions.json')
    assets={}
    # Entire original image/hash/profile preflight completes before any forward.
    for r in audit:
        p=BASE/r['file'];assert sha(p)==r['sha256']==historical[r['file']]
        bound[str(p)]=r['sha256'];im=tifffile.imread(p)
        assert list(im.shape)==r['shape'] and str(im.dtype)==r['dtype']
        with tifffile.TiffFile(p) as tf:icc=tf.pages[0].tags[34675].value
        assert hashlib.sha256(icc).hexdigest()==r['icc_sha256']
        assert 'sRGB' in ImageCms.getProfileDescription(ImageCms.ImageCmsProfile(BytesIO(icc)))
        assets[(r['frame'],r['role'])]=im
    cfg=get_config();worker=ROOT/'outputs/faceocc_inference_env_v1/Scripts/python.exe'
    assert worker.is_file()
    deps=['scripts/710_check_ppr10k_expert_controls.py','scripts/569_prepare_aligned_pipeline.py',
          'src/skin_masking/fixed_face_input_bridge.py','src/model_training/aligned_correction_support.py',
          'docs/ppr10k-expert-control-readiness-protocol-2026-11-09.md',
          'outputs/ppr10k_native_pipeline_diagnostic_v1/results_PRIVATE.json',
          'outputs/ppr10k_native_pipeline_diagnostic_v1/verification_PRIVATE.json',
          'src/skin_masking/native_anchor_bridge.py',
          'outputs/ppr10k_native_anchor_comparison_v1/results_PRIVATE.json',
          'outputs/ppr10k_native_anchor_comparison_v1/verification_PRIVATE.json',
          'outputs/ppr10k_saved_readiness_v1/readiness_PRIVATE.json']
    for p in [*(ROOT/x for x in deps),*(BASE/x for x in ['frozen_sample.json','image_audit.json','sha256.json','source_regions.json'])]:bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    cached=read(ROOT/'outputs/ppr10k_native_anchor_comparison_v1/results_PRIVATE.json')
    checked=read(ROOT/'outputs/ppr10k_native_anchor_comparison_v1/verification_PRIVATE.json')
    assert checked['passed'] and checked['results_sha256']==sha(ROOT/'outputs/ppr10k_native_anchor_comparison_v1/results_PRIVATE.json')
    anchors_by_frame={r['frame']:r for r in cached['records']}
    selection_by_frame={r['frame']:r['visual_match_to_historical_face'] for r in checked['checks']}
    OUT.mkdir();write(OUT/'plan_PRIVATE.json',dict(frames=sample['frames'],input_sha256=bound,
        measurement_contract=identity,scope='8 expert-target inputs only; no source inference or tree fit',
        bridge='native_anchor_square_context_1p5_v1',glasses='uncertain',identity_only=True))
    # Instrument helper invocations without changing returned values or policy.
    old=importlib.import_module('11_prepare_training_manifests')
    module=importlib.import_module('569_prepare_aligned_pipeline')
    counts=dict(detector_forwards=0,landmarker_helper_calls=0,parser_forwards=0,FaceOcc_forwards=0)
    original_detect=old._detect_face_boxes;original_lm=old.detect_face_landmarks
    parser_cls=module.DenseFaceParser;original_parser=parser_cls.categories_bgr
    def detect(*a,**kw):counts['detector_forwards']+=1;return original_detect(*a,**kw)
    def lm(*a,**kw):counts['landmarker_helper_calls']+=1;return original_lm(*a,**kw)
    def parse(self,*a,**kw):counts['parser_forwards']+=1;return original_parser(self,*a,**kw)
    old._detect_face_boxes=detect;old.detect_face_landmarks=lm;parser_cls.categories_bgr=parse
    rows=[]
    try:
        detector,parent=module.initialize()
        template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
        for frame in sample['frames']:
            folder=OUT/frame;folder.mkdir();before=dict(counts)
            src=assets[(frame,'target_a')];target=assets[(frame,'target_a')]
            assert src.shape==target.shape
            assert src.dtype==np.uint8
            rgb=src.copy();bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
            save(folder/'target_rgb8.png',bgr)
            # Target-only identity display, not a new source-target correspondence review.
            target_bgr=cv2.cvtColor(target,cv2.COLOR_RGB2BGR)
            edges=cv2.Canny(cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY),80,160)>0
            contour=target_bgr.copy();contour[edges]=(0,255,0)
            save(folder/'pair_board.png',np.hstack([bgr,target_bgr,contour]))
            poly=np.array(regions[frame]['polygon'],np.int32)
            bx,by,bw,bh=cv2.boundingRect(poly);pad=15
            x0=max(0,bx-pad);y0=max(0,by-pad);x1=min(rgb.shape[1],bx+bw+pad);y1=min(rgb.shape[0],by+bh+pad)
            save(folder/'pair_detail.png',np.hstack([bgr[y0:y1,x0:x1],target_bgr[y0:y1,x0:x1],contour[y0:y1,x0:x1]]))
            r=dict(frame=frame,status='failed',stage='anchor',training_admitted=False,mst=None)
            try:
                boxes=[list(map(int,b)) for b in detector(bgr)]
                r['target_native_anchors']=boxes
                r['source_historical_face_match']=selection_by_frame[frame]
                r['target_person_review']='pending'
                r['source_selection_status']='source_matches_historical_face' if selection_by_frame[frame] else 'SOURCE_WRONG_PERSON_RETAINED_FAILURE'
                if len(boxes)!=1:raise ValueError('Exactly one native target anchor required')
                native,bridge=crop_native_anchor(bgr,native_box=boxes[0]);r['input_bridge']=bridge
                save(folder/'native_input.png',native)
                result,cache=parent(native);r.update(stage='parent',parent_report=result.report,landmark_details=cache.get('landmark_details'))
                if result.image is not None:save(folder/'input.png',result.image)
                if result.mask is not None:save(folder/'parent_mask.png',result.mask)
                if cache.get('points') is not None:np.save(folder/'landmarks.npy',cache['points'],allow_pickle=False)
                if 'categories' in cache:save(folder/'categories.png',cache['categories'])
                if result.report['status']!='success':raise ValueError(result.report.get('reason','Parent unavailable'))
                aligned,matrix,details=align_input(result.image,cache['points'],template)
                save(folder/'aligned.png',aligned);write(folder/'matrix.json',matrix.tolist());r['alignment']=details
                request=dict(aligned_path=str(folder/'aligned.png'),input_sha256=dict(bound,**{str(folder/'aligned.png'):sha(folder/'aligned.png')}))
                write(folder/'inference_request.json',request);r['stage']='FaceOcc'
                subprocess.run([str(worker),'-B',str(ROOT/'scripts/420_run_preview_faceocc.py'),'--request',str(folder/'inference_request.json')],cwd=ROOT,check=True)
                pred=read(folder/'inference.json');assert pred['request_sha256']==sha(folder/'inference_request.json')
                assert pred['logits_sha256']==sha(folder/'faceocc_logits.npy')
                counts['FaceOcc_forwards']+=pred['forwards'];assert counts['FaceOcc_forwards']<=8
                logits=np.load(folder/'faceocc_logits.npy',allow_pickle=False)
                measurement=evaluate_parent(result,cache['points'],template,lambda _:logits)
                r['measurement_report']=measurement.report
                if measurement.mask is not None:
                    save(folder/'measurement_mask.png',measurement.mask)
                    projected,_=native_projection(measurement.mask,bridge);save(folder/'measurement_native.png',projected)
                visible=map_visible_mask((logits>0).astype(np.uint8)*255,result.image.shape[:2],matrix)
                save(folder/'visible_face.png',visible)
                preview=render_preview(result.image,result.mask,cache['categories'],cache['points'],visible,glasses='uncertain',parameters=(1.,1.,1.))
                assert np.array_equal(preview.output,result.image)
                alpha,protected=project_alpha(preview.alpha,preview.protected,bridge)
                np.save(folder/'alpha_normalized.npy',preview.alpha,allow_pickle=False)
                np.save(folder/'alpha_native.npy',alpha,allow_pickle=False)
                save(folder/'protected_normalized.png',preview.protected.astype(np.uint8)*255)
                save(folder/'protected_native.png',protected.astype(np.uint8)*255)
                save(folder/'correction_native.png',(alpha>0).astype(np.uint8)*255)
                assert not alpha[protected].any()
                r.update(preview_report=preview.report,correction_native_pixels=int((alpha>0).sum()),
                    measurement_native_pixels=int((projected>0).sum()) if measurement.mask is not None else 0,
                    status='available' if measurement.report['status']=='success' and alpha.any() else 'measurement_or_support_failed',stage='complete')
                measured=result.image.copy()
                if measurement.mask is not None:measured[measurement.mask==0]=35
                overlay=result.image.copy();sel=preview.alpha>0;overlay[sel]=np.rint(.6*overlay[sel]+.4*np.array([0,255,0])).astype(np.uint8)
                guard=result.image.copy();guard[preview.protected]=[255,0,255]
                save(folder/'mask_board.png',np.hstack([result.image,measured,overlay,guard]))
            except (ValueError,RuntimeError,cv2.error,subprocess.CalledProcessError) as e:
                r['reason']=str(e)
            r['calls']={k:counts[k]-before[k] for k in counts}
            write(folder/'report_PRIVATE.json',r);rows.append(r)
            write(OUT/'progress_PRIVATE.json',dict(completed=len(rows),counts=counts))
            print(frame,r['status'],r.get('reason',''),r['calls'],flush=True)
        assert all(sha(p)==h for p,h in bound.items())
        assert counts['detector_forwards']<=16 and counts['parser_forwards']<=8 and counts['FaceOcc_forwards']<=8
        summary=dict(attempts=8,available=sum(r['status']=='available' for r in rows),
            source_matched_target_technically_available=sum(r['status']=='available' and r.get('source_historical_face_match',False) for r in rows),
            retained_source_wrong_person_cases=[r['frame'] for r in rows if not r.get('source_historical_face_match',False)],
            target_anchor_forwards=8,calls=counts,
            landmarker_count_semantics='detect_face_landmarks helper invocations including intrinsic margin fallbacks; not MediaPipe internal subnetwork count',
            new_fits=0,expert_target_inputs=8,source_inputs_inferred=0,holdout_reads=0,training_admitted=False)
        write(OUT/'results_PRIVATE.json',dict(summary=summary,records=rows,input_sha256=bound))
        write(OUT/'artifact_sha256_PRIVATE.json',{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
        print(json.dumps(summary),flush=True)
    except Exception:
        write(OUT/'failure_PRIVATE.json',dict(traceback=traceback.format_exc(),completed=len(rows),counts=counts));raise
    finally:
        old._detect_face_boxes=original_detect;old.detect_face_landmarks=original_lm;parser_cls.categories_bgr=original_parser

if __name__=='__main__':main()
