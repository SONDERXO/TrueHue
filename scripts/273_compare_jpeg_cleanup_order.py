"""Application-only morphology-order experiment with frozen measurement/model."""
import argparse
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.skin_mask import keep_largest_connected_component,create_candidate_mask_bgr
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors
h=importlib.import_module('256_compare_clean_control_tree_depth')
PARENT=ROOT/'outputs/endpoint_full_path_jpeg_v1';INPUTS=ROOT/'outputs/endpoint_jpeg_sensitivity_v1'
OUT=ROOT/'outputs/jpeg_cleanup_order_v1'


def support(image,box,points,operations):
    x,y,w,height=box;crop=image[y:y+height,x:x+w]
    hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV);yc=cv2.cvtColor(crop,cv2.COLOR_BGR2YCrCb)
    raw=cv2.inRange(hsv,np.array([0,48,0],np.uint8),np.array([20,255,255],np.uint8))
    raw&=cv2.inRange(yc,np.array([0,133,77],np.uint8),np.array([255,173,127],np.uint8))
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5));clean=raw.copy()
    for operation in operations:clean=cv2.morphologyEx(clean,operation,kernel)
    component=keep_largest_connected_component(clean)
    excluded=build_feature_exclusion_mask(crop,points,dilation=0)
    selected=cv2.bitwise_and(component,cv2.bitwise_not(excluded));selected,mouth=exclude_complete_mouth(selected,points)
    assert not np.any((selected>0)&((excluded>0)|(mouth>0)))
    full=np.zeros(image.shape[:2],np.uint8);full[y:y+height,x:x+w]=selected
    return full,raw,clean


def summarize(records):
    aggregate=[]
    for encoding in ('lossless','jpeg95','jpeg85'):
        part=[r for r in records if r['encoding']==encoding];valid=[r for r in part if r['status']=='success']
        aggregate.append(dict(encoding=encoding,attempts=len(part),successful=len(valid),failed=len(part)-len(valid),
            baseline_error=float(np.mean([r['baseline_metrics']['ciede2000_source_mask'] for r in valid])) if valid else None,
            candidate_error=float(np.mean([r['candidate_metrics']['ciede2000_source_mask'] for r in valid])) if valid else None,
            unchanged_error=float(np.mean([r['unchanged_metrics']['ciede2000_source_mask'] for r in valid])) if valid else None,
            added_pixels=sum(r['added_pixels'] for r in part),removed_pixels=sum(r['removed_pixels'] for r in part),
            baseline_missed_reference_pixels=sum(r['baseline_missed_reference_pixels'] for r in part),
            candidate_missed_reference_pixels=sum(r['candidate_missed_reference_pixels'] for r in part),
            candidate_pixels_outside_reference=sum(r['candidate_pixels_outside_reference'] for r in part),
            baseline_pixels_outside_reference=sum(r['baseline_pixels_outside_reference'] for r in part),
            clean_changed_ids=[r['pair_id'] for r in valid if r['variant']=='identity' and r['changed_input_pixels']]))
    return dict(aggregate=aggregate,scope='application support only; frozen measurement and parameters',models_fitted=0,
        active_demo_changed=False,new_human_approvals=0)


def run():
    if OUT.exists():raise FileExistsError(OUT)
    verified=h.read(PARENT/'verification.json');assert verified['status']=='pass'
    parent=h.read(PARENT/'plan.json');rows={r['pair_id']:r for r in parent['rows']}
    encoded={(r['pair_id'],r['encoding']):r for r in h.read(INPUTS/'predictions.json')}
    paths=[Path(__file__),Path(h.__file__),ROOT/'docs/jpeg-cleanup-order-protocol.md',PARENT/'verification.json',ROOT/'outputs/jpeg_mask_stage_trace_v1/verification.json']
    paths.extend(PARENT/path for path in verified['evidence_sha256'])
    hashes=dict(parent['input_sha256']);hashes.update({p.relative_to(ROOT).as_posix():h.digest(p) for p in paths})
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    OUT.mkdir();(OUT/'images').mkdir();h.write(OUT/'plan.json',dict(status='frozen_before_comparison',input_sha256=hashes,
        parent_rows=parent['rows'],baseline_order='open_close_close',candidate_order='close_open_close',measurement_features_changed=False))
    records=[]
    for prior in h.read(PARENT/'attempts.json'):
        assert prior['status']=='success'
        pair=prior['pair_id'];encoding=prior['encoding'];stem=pair+'_'+encoding;row=rows[pair]
        image=cv2.imread(str(INPUTS/encoded[(pair,encoding)]['encoded_input_path']))
        points=np.load(PARENT/'geometry'/(stem+'_landmarks.npy'));box=prior['measurement']['face_box']
        baseline,_,clean=support(image,box,points,(cv2.MORPH_OPEN,cv2.MORPH_CLOSE,cv2.MORPH_CLOSE))
        np.testing.assert_array_equal(baseline,cv2.imread(str(PARENT/'images'/(stem+'_mask.png')),0))
        x,y,w,height=box;np.testing.assert_array_equal(clean,create_candidate_mask_bgr(image[y:y+height,x:x+w]))
        candidate,_,_=support(image,box,points,(cv2.MORPH_CLOSE,cv2.MORPH_OPEN,cv2.MORPH_CLOSE))
        old=baseline>0;new=candidate>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        path=OUT/'images'/(stem+'_mask.png');assert cv2.imwrite(str(path),candidate)
        record=dict(pair_id=pair,encoding=encoding,variant=row['variant'],fold_id=prior['fold_id'],parameters=prior['parameters'],
            added_pixels=int((new&~old).sum()),removed_pixels=int((old&~new).sum()),candidate_pixels=int(new.sum()),
            baseline_missed_reference_pixels=int((score&~old).sum()),candidate_missed_reference_pixels=int((score&~new).sum()),
            baseline_pixels_outside_reference=int((old&~score).sum()),candidate_pixels_outside_reference=int((new&~score).sum()),
            candidate_mask_sha256=h.digest(path),baseline_metrics=prior['metrics'],status='insufficient_support')
        if new.sum()>=1000:
            rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
            output=rgb.copy();output[new]=np.rint(transform_rgb(rgb.astype(float)/255,*prior['parameters'])[new]*255).astype(np.uint8)
            assert np.array_equal(output[~new],rgb[~new]);result_path=OUT/'images'/(stem+'_result.png')
            assert cv2.imwrite(str(result_path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
            record.update(status='success',candidate_metrics=image_errors(reference,output,score),unchanged_metrics=image_errors(reference,rgb,score),
                changed_input_pixels=int(np.count_nonzero(np.any(output!=rgb,axis=2))),output_sha256=h.digest(result_path))
        records.append(record)
    h.write(OUT/'attempts.json',records);h.write(OUT/'summary.json',summarize(records))
    print(summarize(records))


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=h.read(OUT/'plan.json');rows={r['pair_id']:r for r in plan['parent_rows']}
    for path,sha in plan['input_sha256'].items():assert h.digest(ROOT/path)==sha
    originals={(r['pair_id'],r['encoding']):r for r in h.read(PARENT/'attempts.json')}
    encoded={(r['pair_id'],r['encoding']):r for r in h.read(INPUTS/'predictions.json')}
    records=h.read(OUT/'attempts.json');assert len(records)==141 and len({(r['pair_id'],r['encoding']) for r in records})==141
    for r in records:
        key=(r['pair_id'],r['encoding']);prior=originals[key];row=rows[r['pair_id']];stem=r['pair_id']+'_'+r['encoding']
        assert r['parameters']==prior['parameters'] and r['baseline_metrics']==prior['metrics']
        image=cv2.imread(str(INPUTS/encoded[key]['encoded_input_path']));x,y,w,height=prior['measurement']['face_box'];crop=image[y:y+height,x:x+w]
        points=np.load(PARENT/'geometry'/(stem+'_landmarks.npy'))
        hs=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV);yc=cv2.cvtColor(crop,cv2.COLOR_BGR2YCrCb)
        raw=((hs[:,:,0]<=20)&(hs[:,:,1]>=48)&(yc[:,:,1]>=133)&(yc[:,:,1]<=173)&(yc[:,:,2]>=77)&(yc[:,:,2]<=127)).astype(np.uint8)*255
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        cleaned=cv2.morphologyEx(cv2.morphologyEx(cv2.morphologyEx(raw,cv2.MORPH_CLOSE,kernel),cv2.MORPH_OPEN,kernel),cv2.MORPH_CLOSE,kernel)
        component=keep_largest_connected_component(cleaned);excluded=build_feature_exclusion_mask(crop,points,dilation=0)
        expected,_=exclude_complete_mouth(cv2.bitwise_and(component,cv2.bitwise_not(excluded)),points)
        full=np.zeros(image.shape[:2],np.uint8);full[y:y+height,x:x+w]=expected
        path=OUT/'images'/(stem+'_mask.png');assert h.digest(path)==r['candidate_mask_sha256'];np.testing.assert_array_equal(full,cv2.imread(str(path),0))
        new=full>0;old=cv2.imread(str(PARENT/'images'/(stem+'_mask.png')),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        for name,value in dict(added_pixels=(new&~old).sum(),removed_pixels=(old&~new).sum(),candidate_pixels=new.sum(),
            baseline_missed_reference_pixels=(score&~old).sum(),candidate_missed_reference_pixels=(score&~new).sum(),
            baseline_pixels_outside_reference=(old&~score).sum(),candidate_pixels_outside_reference=(new&~score).sum()).items():assert int(value)==r[name]
        if r['status']!='success':assert new.sum()<1000;continue
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        raw=np.clip((rgb.astype(float)/255)**r['parameters'][0]*[r['parameters'][1],1,r['parameters'][2]],0,1)
        expected=rgb.copy();expected[new]=np.rint(raw[new]*255).astype(np.uint8)
        path=OUT/'images'/(stem+'_result.png');assert h.digest(path)==r['output_sha256'];np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),expected)
        assert image_errors(reference,expected,score)==r['candidate_metrics'] and image_errors(reference,rgb,score)==r['unchanged_metrics']
        assert int(np.count_nonzero(np.any(expected!=rgb,axis=2)))==r['changed_input_pixels']
    assert summarize(records)==h.read(OUT/'summary.json')
    h.write(target,dict(status='pass',independently_reconstructed_candidates=141,parameters_unchanged=True,
        application_only=True,active_demo_changed=False,
        evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 141 independent support reconstructions, unchanged parameters and all available output/metric replays.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else run()
