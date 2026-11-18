"""Generated algebra, scalar parity, protection and two local target rehearsals."""
from pathlib import Path
import sys,json,platform,importlib.metadata
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.luminance_chroma_operator import transform,render_float,render_rgb8,fit_target,decode,encode
from src.evaluation.luminance_chroma_scalar import pixel,replay
from src.model_training.reiqa_frozen_features import sha
OUT=ROOT/'outputs/luminance_chroma_generated_v1'
def write(p,v):Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
def main():
    if OUT.exists():raise FileExistsError(OUT)
    OUT.mkdir();checks=[];fits=[]
    try:
        rng=np.random.default_rng(77491)
        palette=np.vstack([rng.integers(0,256,(1024,3),dtype=np.uint8),np.repeat(np.arange(256,dtype=np.uint8)[:,None],3,axis=1),
            np.array([[0,0,0],[255,255,255],[128,0,64],[200,255,180],[1,0,0]],np.uint8)])
        identity=transform(palette/255.,[1]*5)
        assert np.array_equal(np.rint(identity*255).astype(np.uint8),palette)
        assert np.array_equal(np.rint(encode(decode(palette/255.))*255).astype(np.uint8),palette)
        probes=[[1]*5,[.7,1.3,1.02,.98,.6],[1.4,.8,.98,1.03,.9],[.25,4.,4.,.25,1.5],[4.,.25,.25,4.,.25]]
        scalar_values=0;maximum=0.;lum_error=0.
        for p in probes:
            actual,detail=transform(palette/255.,p,details=True)
            independent=np.array([pixel(rgb,p) for rgb in palette/255.])
            difference=float(np.abs(actual-independent).max());maximum=max(maximum,difference)
            assert difference<2e-12 and np.isfinite(actual).all() and np.all(actual>=0) and np.all(actual<=1)
            lum_error=max(lum_error,float(np.abs(detail['linear']@np.array([.2126,.7152,.0722])-detail['luminance']).max()))
            assert np.all(actual[np.all(palette==0,axis=1)]==0)
            scalar_values+=actual.size
        assert lum_error<2e-14
        # Strictly positive arbitrarily dark values participate, not thresholded away.
        near=transform(np.array([[1e-14,2e-14,1e-14]]),[.7,1.2,1,1,.5]);assert np.all(near>0)
        filled=transform(np.array([[.5,0,.2],[0,0,0]]),[.7,1.2,1,1,.5])
        assert filled[0,1]>0 and np.all(filled[1]==0)
        dimmed=transform(np.array([[.8,1,.7]]),[1,.5,1,1,1]);assert dimmed[0,1]<1
        neutral=transform(np.repeat(np.linspace(0,1,256)[:,None],3,axis=1),[.8,1.2,1,1,.6])
        assert np.max(np.abs(neutral-neutral[:,0,None]))<1e-14
        checks.extend(['RGB8identity_exact','sRGBroundtrip_exact','black_exact','nearblack_positive','zeroGreen_filled_without_black_fill',
                       'saturatedGreen_can_dim','neutral_preserved','finite_in_gamut','scalar_formula_parity','linear_luminance_preserved'])
        image=rng.integers(8,230,(16,24,3),dtype=np.uint8)
        alpha=np.ones((16,24),float);alpha[0]=0;alpha[1]=.5;protected=np.zeros((16,24),bool);protected[8,10]=True;alpha[protected]=0
        original=image.copy();original_alpha=alpha.copy()
        for i,p in enumerate(probes[1:3]):
            target=render_rgb8(image,alpha,protected,p)
            scalar,mse=replay(image,target,alpha,protected,p)
            assert np.array_equal(target,scalar)
            assert np.array_equal(target[alpha==0],image[alpha==0]) and np.array_equal(target[protected],image[protected])
            fitted=fit_target(image,target,alpha,protected);fits.append(fitted)
            assert fitted['solver_calls']==1 and fitted['status']=='available_local_diagnostic'
            actual=render_rgb8(image,alpha,protected,fitted['parameters'])
            independent,objective=replay(image,target,alpha,protected,fitted['parameters'])
            assert np.array_equal(actual,independent)
            assert abs(objective-fitted['float_mse'])<1e-12
            assert fitted['float_mse']<=mse+1e-10
            np.savez(OUT/f'generated_{i}.npz',input=image,reference=target,alpha=alpha,protected=protected,output=actual)
        assert np.array_equal(image,original) and np.array_equal(alpha,original_alpha)
        assert fit_target(image,image,alpha,protected)['solver_calls']==0
        assert fit_target(image,image,np.zeros_like(alpha),protected)['solver_calls']==0
        black=np.zeros_like(image);assert fit_target(black,image,alpha,protected)['solver_calls']==0
        for bad in [[float('nan'),1,1,1,1],[0,1,1,1,1],[1,1,1,1,2],[1,1]]:
            try:transform(image/255.,bad)
            except ValueError:pass
            else:raise AssertionError('Invalid controls accepted')
        bad_alpha=alpha.copy();bad_alpha[protected]=1
        try:render_rgb8(image,bad_alpha,protected,[1]*5)
        except ValueError:pass
        else:raise AssertionError('Protected alpha accepted')
        assert np.array_equal(transform(np.zeros((2,3)),[.7,1.2,1,1,.5])[0],transform(np.zeros((2,3)),[.7,1.2,1,1,.5])[1])
        checks.extend(['two_generated_local_fits','known_parameter_witness_not_worse','scalar_fitted_render_objective',
                       'outside_protection_exact','inputs_not_mutated','identity_empty_black_skip_solver','invalid_controls_support_rejected','clipped_collision_not_recovered'])
        # Loader rehearsal: both hashes checked before first decode; poison unused NPZkey.
        from run_luminance_chroma_two_case import load_bound
        loader_rows=[]
        for i in range(2):
            p=OUT/f'loader_{i}.npz'
            np.savez(p,input=image,reference=image,alpha=alpha,protected=protected,forbidden=np.array([object()],dtype=object))
            loader_rows.append(dict(case_id=f'generated_loader_{i}',pack=p.name,sha256=sha(p)))
        access=[];loaded=load_bound(OUT,loader_rows,access)
        assert len(loaded)==len(access)==2 and all(r['keys']==['input','reference','alpha','protected'] for r in access)
        corrupted=[dict(r) for r in loader_rows];corrupted[1]['sha256']='0'*64;blocked=[]
        try:load_bound(OUT,corrupted,blocked)
        except AssertionError:pass
        else:raise AssertionError('Corrupted hash accepted')
        assert not blocked
        checks.append('all_hash_barrier_before_decode_and_unused_pickle_key_unread')
        files=['src/model_training/luminance_chroma_operator.py','src/evaluation/luminance_chroma_scalar.py',
            'scripts/check_luminance_chroma_generated.py','scripts/run_luminance_chroma_two_case.py',
            'scripts/verify_luminance_chroma_two_case.py','docs/luminance-chroma-feasibility-protocol-2026-11-15.md']
        result=dict(passed=True,status='GENERATED_OPERATOR_FITTER_ONLY',checks=checks,generated_solver_calls=2,
            generated_fits=fits,scalar_values=scalar_values,max_scalar_difference=maximum,max_linear_luminance_error=lum_error,
            real_photos=0,real_fits=0,predictor_fits=0,loader_hash_barrier_poison_pass=True,
            versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-image']}),
            input_sha256={p:sha(ROOT/p) for p in files},artifact_sha256={p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
        write(OUT/'verification_PRIVATE.json',result)
        print(json.dumps({k:v for k,v in result.items() if k not in ['generated_fits','input_sha256','artifact_sha256']},indent=2))
    except Exception as e:
        write(OUT/'failure_PRIVATE.json',dict(error_type=type(e).__name__,error=str(e),completed_generated_fits=len(fits)));raise
if __name__=='__main__':main()
