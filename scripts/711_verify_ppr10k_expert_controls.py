"""Cached target-mask verification and descriptive source/target readiness joins."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np,tifffile
from src.ita_estimation.faceocc_veto_candidate import combine_saved
from src.skin_masking.correction_preview import render_preview
OUT=ROOT/'outputs/ppr10k_expert_control_readiness_v1'
SOURCE=ROOT/'outputs/ppr10k_native_pipeline_diagnostic_v1'
BASE=ROOT/'outputs/ppr10k_new_group_comparison_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    d=read(OUT/'results_PRIVATE.json');old=read(SOURCE/'results_PRIVATE.json')
    ov=read(SOURCE/'verification_PRIVATE.json');assert ov['passed'] and ov['results_sha256']==sha(SOURCE/'results_PRIVATE.json')
    sources={r['frame']:r for r in old['records']};regions=read(BASE/'source_regions.json')
    artifacts=read(OUT/'artifact_sha256_PRIVATE.json')
    assert all(sha(OUT/p)==h for p,h in artifacts.items())
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    assert len(d['records'])==8
    joins=[];verified=0;cropped=0
    for r in d['records']:
        frame=r['frame'];folder=OUT/frame;source=sources[frame]
        image=cv2.imread(str(folder/'target_rgb8.png'))
        assert image is not None
        boxes=r['target_native_anchors'];shown=image.copy()
        cv2.polylines(shown,[np.array(regions[frame]['polygon'],np.int32)],True,(0,255,0),1)
        for b in boxes:
            x,y,w,h=b;cv2.rectangle(shown,(x,y),(x+w,y+h),(0,255,255),2)
        assert cv2.imwrite(str(folder/'target_anchor_overlay.png'),shown)
        row=dict(frame=frame,source_status=source['status'],target_status=r['status'],
            source_historical_face_match=source['historical_face_match'],
            target_anchor_count=len(boxes),source_measurement_native_pixels=source.get('measurement_native_pixels'),
            source_correction_native_pixels=source.get('correction_native_pixels'),
            target_measurement_native_pixels=r.get('measurement_native_pixels'),
            target_correction_native_pixels=r.get('correction_native_pixels'),training_admitted=False,
            target_selected_person_review='pending_visual_review',mask_comparison='unavailable')
        if 'input_bridge' in r:
            b=r['input_bridge'];l,t,rr,bb=b['native_bounds'];side=rr-l
            assert b['anchor_coordinate_space']=='original_native_pixels'
            numeric=tifffile.imread(BASE/'originals/target_a'/f'{frame}.tif')
            assert numeric.dtype==np.uint8
            np.testing.assert_array_equal(cv2.cvtColor(numeric,cv2.COLOR_RGB2BGR),image)
            np.testing.assert_array_equal(image[t:bb,l:rr],cv2.imread(str(folder/'native_input.png')));cropped+=1
        if r['status']=='available':
            im=cv2.imread(str(folder/'input.png'));parent=cv2.imread(str(folder/'parent_mask.png'),0)
            logits=np.load(folder/'faceocc_logits.npy',allow_pickle=False)
            matrix=np.array(read(folder/'matrix.json'))
            mask,_,report=combine_saved(im,parent,logits,matrix);assert report['status']=='success'
            np.testing.assert_array_equal(mask,cv2.imread(str(folder/'measurement_mask.png'),0))
            idx=np.floor(np.arange(side)*256/side).astype(int)
            native=np.zeros(image.shape[:2],np.uint8);native[t:bb,l:rr]=mask[idx[:,None],idx[None,:]]
            np.testing.assert_array_equal(native,cv2.imread(str(folder/'measurement_native.png'),0))
            alpha=np.load(folder/'alpha_normalized.npy',allow_pickle=False)
            protected=cv2.imread(str(folder/'protected_normalized.png'),0)>0
            local=cv2.resize(alpha,(side,side),interpolation=cv2.INTER_LINEAR)
            veto=cv2.resize(protected.astype(np.float32),(side,side),interpolation=cv2.INTER_AREA)>0
            local[veto]=0;expected=np.zeros(image.shape[:2],float);expected[t:bb,l:rr]=local
            np.testing.assert_array_equal(expected,np.load(folder/'alpha_native.npy',allow_pickle=False))
            guard=np.zeros(image.shape[:2],bool);guard[t:bb,l:rr]=veto
            np.testing.assert_array_equal(guard,cv2.imread(str(folder/'protected_native.png'),0)>0)
            assert not expected[guard].any()
            preview=render_preview(im,parent,cv2.imread(str(folder/'categories.png'),0),
                np.load(folder/'landmarks.npy',allow_pickle=False),cv2.imread(str(folder/'visible_face.png'),0),
                glasses='uncertain',parameters=(1.,1.,1.))
            np.testing.assert_array_equal(preview.output,im);np.testing.assert_array_equal(preview.alpha,alpha)
            sm=cv2.imread(str(SOURCE/frame/'measurement_native.png'),0)>0;tm=native>0
            intersection=int((sm&tm).sum());union=int((sm|tm).sum())
            a=source['measurement_report']['statistics'];z=r['measurement_report']['statistics']
            keys=['mean_l_star','mean_a_star','mean_b_star','ita_degrees']
            row.update(mask_comparison='descriptive_native_overlap_no_warp',measurement_intersection=intersection,
                measurement_union=union,measurement_iou=intersection/union if union else None,
                source_statistics={k:a[k] for k in keys},target_statistics={k:z[k] for k in keys},
                target_minus_source={k:z[k]-a[k] for k in keys})
            verified+=1
        else:
            assert len(boxes)!=1 and r['calls']['FaceOcc_forwards']==0
        joins.append(row)
    assert verified==cropped==7
    assert all(sha(OUT/p)==h for p,h in artifacts.items())
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    result=dict(passed=True,target_attempts=8,technical_available=verified,exact_target_crops=cropped,
        paired_records=joins,results_sha256=sha(OUT/'results_PRIVATE.json'),
        source_results_sha256=sha(SOURCE/'results_PRIVATE.json'),verifier_sha256=sha(Path(__file__)),
        artifact_manifest_sha256=sha(OUT/'artifact_sha256_PRIVATE.json'),new_forwards=0,new_fits=0,holdout_reads=0,
        limitations='IoU is between two predictions, not accuracy; input photos/masks/crops vary; no intrinsic colour, calibration or clean-preservation validation.')
    dest.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('PASS: 7 exact target slices/mask/native/alpha/protection/identity replays, 8 roles retained, hashes unchanged.')
    for r in joins:print(r['frame'],'target_faces',r['target_anchor_count'],'target_pixels',r['target_measurement_native_pixels'],'source_pixels',r['source_measurement_native_pixels'],'IoU',r.get('measurement_iou'))
if __name__=='__main__':main()
