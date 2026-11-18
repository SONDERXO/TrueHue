"""Fixed30 development originals, native-anchor preparation only; no fits."""
from pathlib import Path
import hashlib,importlib,json,sys,traceback
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2,numpy as np
from scipy.io import loadmat
from src.skin_masking.native_anchor_bridge import crop_native_anchor
from src.skin_masking.faceocc_mediapipe_bridge import align_input
OUT=ROOT/'outputs/scin_nine_support_screen_v1'
OLD=ROOT/'outputs/aligned_correction_preparation_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
def save(p,a):
    if not cv2.imwrite(str(p),a):raise IOError(str(p))

def main():
    if OUT.exists():raise FileExistsError('Preserve partial or completed preparation')
    policyroot=ROOT/'outputs/scin_exploratory_policy_v1'
    receipt=read(policyroot/'review_PRIVATE.json');assert receipt['passed']
    assert all(sha(p)==h for p,h in receipt['input_sha256'].items())
    roster=read(policyroot/'roster_PRIVATE.json');assert len(roster)==9
    OUT.mkdir();(OUT/'logits').mkdir()
    # Only already inventoried SCIN training-candidate aliases may be read.
    raw={};aliases=[];sources=[];images={}
    for index,r in enumerate(roster,1):
        hashes=[]
        for entry in r['local_alias_membership']:
            p=ROOT/entry['relative_path'];data=p.read_bytes();assert len(data)==entry['bytes']
            digest=hashlib.sha256(data).hexdigest();raw[entry['relative_path']]=data
            hashes.append(digest);aliases.append(dict(case_id=r['case_id'],path=entry['relative_path'],sha256=digest,bytes=len(data)))
        source=dict(source_case=f'scin_{index:02d}',source_path=str(ROOT/r['canonical_relative_path']),
            source_sha256=hashlib.sha256(raw[r['canonical_relative_path']]).hexdigest(),
            subject_id=r['case_group'],verified_person_id=None,case_id=r['case_id'],
            reference_labels=r['reference_labels'],condition='unknown_photographic',cohort='exploratory_development_readiness_only',
            identity_block=None)
        if len(set(hashes))!=1:source['identity_block']='local_alias_hash_conflict'
        sources.append(source)
    write(OUT/'alias_hashes_PRIVATE.json',dict(records=aliases,scope='New local baseline, not publisher authentication'))
    # Check existing locked metadata only. Never follow image paths from it.
    inventory=read(ROOT/'outputs/stellenbosch_received_data_v1/files_PRIVATE.json')
    groups=read(ROOT/'outputs/group_diversity_candidates_v1/plan_PRIVATE.json')['groups']
    lockedsubjects={r['subject_key'] for r in groups if r['role']=='closed_holdout_candidate'}
    lockedhashes={r['sha256'] for r in inventory if r['subject_key'] in lockedsubjects}
    import csv
    with (ROOT/'data/manifests/source_preparation_v1/source_audit_and_partitions.csv').open(encoding='utf-8-sig',newline='') as f:
        lockedpixels={r['decoded_pixel_sha256'] for r in csv.DictReader(f) if r['partition'] not in ('train','development_train','training') and r['decoded_pixel_sha256']}
    from src.model_training.whole_scene_features import scene_features
    decodedhashes={}
    for source,r in zip(sources,roster):
        folder=OUT/source['source_case'];folder.mkdir()
        if source['source_sha256'] in lockedhashes:source['identity_block']='known_locked_exact_file_overlap'
        if source['identity_block']:continue
        try:
            image=cv2.imdecode(np.frombuffer(raw[r['canonical_relative_path']],np.uint8),cv2.IMREAD_COLOR)
            if image is None:raise ValueError('Image decode failed')
            pixelhash=hashlib.sha256(image.tobytes()).hexdigest();source['decoded_BGR_sha256']=pixelhash
            source['duplicate_group']=decodedhashes.setdefault(pixelhash,source['source_case'])
            source['source_shape']=list(image.shape)
            if pixelhash in lockedpixels:source['identity_block']='known_locked_exact_decoded_overlap';continue
            save(folder/'source_full.png',image);images[source['source_case']]=image
            source['scene_features']=scene_features(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
        except (ValueError,cv2.error) as error:source['identity_block']=str(error)
    write(OUT/'identity_preflight_PRIVATE.json',dict(sources=sources,local_alias_files=len(aliases),
        canonical_cases=9,locked_comparison='Existing saved exact hash metadata only; absence is not cross-source person clearance.',
        exact_duplicate_groups=len(set(r.get('duplicate_group',r['source_case']) for r in sources)),
        blocked=sum(bool(r['identity_block']) for r in sources),image_hash_provenance='new_local_baseline'))
    helper=importlib.import_module('419_preview_object_protected_face');bound,inner=helper.dependencies()
    for p in [Path(__file__),ROOT/'scripts/782_run_scin_faceocc.py',ROOT/'scripts/369_run_faceocc_logits.py',
        ROOT/'scripts/783_finalize_scin_screen.py',ROOT/'src/skin_masking/native_anchor_bridge.py',
        ROOT/'src/model_training/whole_scene_features.py',ROOT/'docs/scin-exploratory-policy-2026-11-11.md',
        policyroot/'roster_PRIVATE.json',policyroot/'policy_PRIVATE.json',OUT/'identity_preflight_PRIVATE.json',OUT/'alias_hashes_PRIVATE.json']:
        bound[str(p)]=sha(p)
    contract=dict(version='scin_native_support_readiness_v1',inner_measurement_contract=inner,
        anchor='original_native_YuNet_0.85_NMS0.3_topK5000',bridge='native_anchor_square_context_1p5_v1',
        bridge_sha256=sha(ROOT/'src/skin_masking/native_anchor_bridge.py'),minimum_normalized_pixels=1000,
        colour='delivered_PNG_assumed_sRGB_no_new_calibration',parser='original_not_enhanced',
        FaceOcc='raw_aligned_strict_gt0',source_scores='both_annotators_metadata_only_not_inference')
    identity=hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert all(sha(p)==h for p,h in bound.items())
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
            folder=OUT/s['source_case'];image=images.get(s['source_case'])
            before=dict(counts);r=dict(s,status='unavailable',stage='anchor',measurement_contract_sha256=identity,
                training_admitted=False,calibration_admitted=False,case_index=index)
            try:
                if s['identity_block']:raise ValueError(s['identity_block'])
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
        assert counts['detector_forwards']<=18 and counts['parser_forwards']<=9
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
