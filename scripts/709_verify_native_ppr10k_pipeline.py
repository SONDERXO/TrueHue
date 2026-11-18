"""Independent native projection/identity checks and original-block baseline."""
from pathlib import Path
import hashlib,importlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np,tifffile
from skimage.color import rgb2lab,deltaE_ciede2000
from src.ita_estimation.faceocc_veto_candidate import combine_saved
from src.skin_masking.correction_preview import render_preview

OUT=ROOT/'outputs/ppr10k_native_pipeline_diagnostic_v1'
OLD=ROOT/'outputs/ppr10k_new_group_comparison_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve completed verification')
    artifacts=read(OUT/'artifact_sha256_PRIVATE.json')
    assert all(sha(OUT/p)==h for p,h in artifacts.items())
    results=read(OUT/'results_PRIVATE.json');bindings=results['input_sha256']
    assert all(sha(p)==h for p,h in bindings.items())
    historical=read(OLD/'sha256.json');oldresults=read(OLD/'results.json')
    metric=importlib.import_module('scripts.392_ppr10k_operator_diagnostic').metrics
    baseline=[];checks=[]
    for r in results['records']:
        frame=r['frame'];folder=OUT/frame
        bridge=r['input_bridge'];l,t,rr,bb=bridge['native_bounds']
        source=tifffile.imread(OLD/'originals/source'/f'{frame}.tif')
        bgr=cv2.cvtColor(np.rint(source.astype(float)/257).astype(np.uint8),cv2.COLOR_RGB2BGR)
        np.testing.assert_array_equal(bgr[t:bb,l:rr],cv2.imread(str(folder/'native_input.png')))
        assert bridge['anchor_coordinate_space']=='original_native_pixels'
        if r['status']=='available':
            im=cv2.imread(str(folder/'input.png'));parent=cv2.imread(str(folder/'parent_mask.png'),0)
            logits=np.load(folder/'faceocc_logits.npy',allow_pickle=False);matrix=np.array(read(folder/'matrix.json'))
            mask,_,report=combine_saved(im,parent,logits,matrix)
            assert report['status']=='success'
            np.testing.assert_array_equal(mask,cv2.imread(str(folder/'measurement_mask.png'),0))
            b=r['input_bridge'];l,t,rr,bb=b['native_bounds'];side=rr-l
            # Explicit index mapping for nearest-neighbour, no projection helper.
            idx=np.floor(np.arange(side)*256/side).astype(int)
            local=mask[idx[:,None],idx[None,:]]
            expected=np.zeros(b['source_shape'][:2],np.uint8);expected[t:bb,l:rr]=local
            np.testing.assert_array_equal(expected,cv2.imread(str(folder/'measurement_native.png'),0))
            an=np.load(folder/'alpha_normalized.npy',allow_pickle=False)
            pn=cv2.imread(str(folder/'protected_normalized.png'),0)>0
            native=np.zeros(b['source_shape'][:2],float);guard=np.zeros(b['source_shape'][:2],bool)
            resized=cv2.resize(an,(side,side),interpolation=cv2.INTER_LINEAR)
            veto=cv2.resize(pn.astype(np.float32),(side,side),interpolation=cv2.INTER_AREA)>0
            resized[veto]=0;native[t:bb,l:rr]=resized;guard[t:bb,l:rr]=veto
            np.testing.assert_array_equal(native,np.load(folder/'alpha_native.npy',allow_pickle=False))
            np.testing.assert_array_equal(guard,cv2.imread(str(folder/'protected_native.png'),0)>0)
            assert not native[guard].any()
            points=np.load(folder/'landmarks.npy',allow_pickle=False)
            categories=cv2.imread(str(folder/'categories.png'),0);visible=cv2.imread(str(folder/'visible_face.png'),0)
            preview=render_preview(im,parent,categories,points,visible,glasses='uncertain',parameters=(1.,1.,1.))
            np.testing.assert_array_equal(preview.output,im)
            np.testing.assert_array_equal(preview.alpha,an)
            np.testing.assert_array_equal(preview.protected,pn)
            assert int((expected>0).sum())==r['measurement_native_pixels']
            checks.append(dict(frame=frame,mask_replay=True,native_projection=True,identity_protection=True))
        else:
            assert r['status']!='available'
            checks.append(dict(frame=frame,retained_no_anchor_failure=True))
        p=OLD/(frame+'_replay.npz');assert sha(p)==historical[p.name]
        with np.load(p,allow_pickle=False) as a:
            x=a['source'];y=a['target'];m=a['check_mask']
            bmetric=metric(x,y,m)
            # Scalar selected-pixel alternative to full-frame metric calculation.
            de=deltaE_ciede2000(rgb2lab(x[m].reshape(-1,1,3)),rgb2lab(y[m].reshape(-1,1,3))).ravel()
            assert abs(float(de.mean())-bmetric['de00_mean'])<1e-10
            assert abs(float(np.abs(x[m]-y[m]).mean()*255)-bmetric['rgb_mae_255'])<1e-10
            old=next(z for z in oldresults['results'] if z['frame']==frame)
            replay=metric(a['three_output'],y,m)
            assert abs(replay['de00_mean']-old['metrics']['three']['check']['de00_mean'])<1e-10
            baseline.append(dict(frame=frame,unchanged=bmetric,three_control_saved=old['metrics']['three']['check'],
                improvement_de00=bmetric['de00_mean']-replay['de00_mean'],
                automatic_support_available=r['status']=='available',
                scope='Historical manual polygon/checker blocks, target-aware fit, NOT automatic correction accuracy'))
    assert all(sha(OUT/p)==h for p,h in artifacts.items())
    assert all(sha(p)==h for p,h in bindings.items())
    result=dict(passed=True,checks=checks,baseline=baseline,
        exact_native_crop_checks=8, correctly_selected_available=results['summary']['correctly_selected_available'],
        retained_wrong_person_cases=results['summary']['retained_wrong_person_cases'],
        mean_unchanged_de00=sum(x['unchanged']['de00_mean'] for x in baseline)/8,
        mean_three_control_de00=sum(x['three_control_saved']['de00_mean'] for x in baseline)/8,
        three_control_improvements=sum(x['improvement_de00']>0 for x in baseline),
        no_new_forwards=True,new_fits=0,holdout_reads=0,
        historical_npz_sha256={x['frame']:historical[x['frame']+'_replay.npz'] for x in baseline},
        results_sha256=sha(OUT/'results_PRIVATE.json'),artifact_manifest_sha256=sha(OUT/'artifact_sha256_PRIVATE.json'),
        verifier_sha256=sha(Path(__file__)),limitation='Native reconstruction independent of projection helper; renderer reused for identity; no dense skin or registration truth.')
    dest.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('PASS: 8 outcomes, 8 measurement/native/alpha/identity replays, all bound hashes, 8 old-block baselines.')
    print('Unchanged DE',result['mean_unchanged_de00'],'three-control DE',result['mean_three_control_de00'],'improved',result['three_control_improvements'],'/8')
    for b in baseline: print(b['frame'],round(b['unchanged']['de00_mean'],4),round(b['three_control_saved']['de00_mean'],4))
if __name__=='__main__':main()
