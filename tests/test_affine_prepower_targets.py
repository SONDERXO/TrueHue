from types import SimpleNamespace
import numpy as np
import pytest
from src.model_training import affine_prepower_targets as target
from src.evaluation import affine_prepower_scalar as scalar
from src.model_training.blended_recovery_targets import render_rgb8 as old_render

CONTROLS=[ [.8,1.08,.92,.95,.03], [1.2,.95,1.05,1.05,-.02],
           [.7,1.,1.,1/1.08,(.08+35/255)/1.08],
           [1/.7,1.,1.,1/1.08,-35/255/1.08] ]


def fixture(spatial=False):
    image=np.random.default_rng(145).uniform(.2,.8,(12,12,3))
    alpha=np.ones((12,12),float);protected=np.zeros((12,12),bool)
    if spatial:
        alpha[[0,-1],:]=0;alpha[:,[0,-1]]=0;alpha[1,1:-1]=.25
        protected[5,5]=True;alpha[protected]=0
    return image,alpha,protected


@pytest.mark.parametrize('p',CONTROLS)
def test_known_noiseless_recovery(p):
    image,alpha,protected=fixture();before=image.copy()
    reference=target.render_float(image,alpha,protected,p)
    result=target.fit_float_target(image,reference,alpha,protected,generated_fixture=True)
    assert result['status']=='available_approximate_target'
    np.testing.assert_allclose(result['parameters'],p,atol=1e-3,rtol=0)
    assert result['float_rmse']<=1e-6 and result['jacobian_rank']==5
    assert scalar.verify(image,reference,alpha,protected,result,rgb8=False)
    np.testing.assert_array_equal(image,before)
    assert not result['training_admitted'] and not result['runtime_adopted']


def test_spatial_support_and_actual_rgb8_replay():
    image,alpha,protected=fixture(True)
    reference=target.render_float(image,alpha,protected,CONTROLS[0])
    result=target.fit_float_target(image,reference,alpha,protected,generated_fixture=True)
    assert result['float_rmse']<=1e-6
    assert scalar.verify(image,reference,alpha,protected,result,rgb8=False)
    actual=target.render_float(image,alpha,protected,result['parameters'])
    expected,_=scalar.replay(image,reference,alpha,result['parameters'])
    np.testing.assert_allclose(actual,expected,atol=1e-12,rtol=0)
    rgb=np.rint(image*255).astype(np.uint8)
    ref=target.render_rgb8(rgb,alpha,protected,CONTROLS[0])
    fit=target.fit_rgb8_target(rgb,ref,alpha,protected,generated_fixture=True)
    assert fit['parameters'] is not None
    assert scalar.verify(rgb,ref,alpha,protected,fit,rgb8=True)


def test_exact_three_control_nesting():
    image,alpha,protected=fixture(True);rgb=np.rint(image*255).astype(np.uint8)
    for p in [[1.,1.,1.],[.8,1.1,.9],[1.2,.9,1.1]]:
        np.testing.assert_array_equal(target.render_rgb8(rgb,alpha,protected,p+[1.,0.]),old_render(rgb,alpha,p))


def test_exact_neutral_and_no_optimization(monkeypatch):
    image,alpha,protected=fixture(True)
    monkeypatch.setattr(target,'least_squares',lambda *a,**k:pytest.fail('Identity must not fit'))
    result=target.fit_float_target(image,image,alpha,protected,generated_fixture=True)
    assert result['parameters']==[1.,1.,1.,1.,0.] and result['evaluations']==0
    np.testing.assert_array_equal(target.render_float(image,alpha,protected,result['parameters']),image)


def test_frozen_solver_settings_and_one_start(monkeypatch):
    image,alpha,protected=fixture();ref=target.render_float(image,alpha,protected,CONTROLS[0])
    original=target.least_squares;calls=[]
    def spy(fun,start,**kwargs):
        calls.append((start.copy(),kwargs.copy()));return original(fun,start,**kwargs)
    monkeypatch.setattr(target,'least_squares',spy)
    target.fit_float_target(image,ref,alpha,protected,generated_fixture=True)
    assert len(calls)==1
    start,kw=calls[0];np.testing.assert_array_equal(start,[1,1,1,1,0])
    np.testing.assert_array_equal(kw.pop('bounds'),[[.25,.25,.25,.5,-.3],[4,4,4,2,.3]])
    assert kw==dict(method='trf',loss='linear',ftol=1e-10,xtol=1e-10,gtol=1e-10,max_nfev=500)


@pytest.mark.parametrize('kind',['constant','near_flat'])
def test_degenerate_input_unavailable_without_optimization(monkeypatch,kind):
    image,alpha,protected=fixture()
    image[:]=.4
    if kind=='near_flat': image[::2]+=.001
    ref=np.full_like(image,.5)
    monkeypatch.setattr(target,'least_squares',lambda *a,**k:pytest.fail('Degenerate case must not fit'))
    result=target.fit_float_target(image,ref,alpha,protected,generated_fixture=True)
    assert result['parameters'] is None and result['status']=='unavailable_degenerate_input'


@pytest.mark.parametrize('failure',['rank','convergence','worse','bounds','nonfinite_jac'])
def test_unsuccessful_solution_never_falls_back(failure,monkeypatch):
    image,alpha,protected=fixture();ref=target.render_float(image,alpha,protected,CONTROLS[0])
    original=target.least_squares
    def altered(*args,**kwargs):
        result=original(*args,**kwargs)
        if failure=='rank': result.jac[:]=0
        if failure=='convergence': result.success=False
        if failure=='worse': result.x=np.array([4.,.25,.25,.5,-.3])
        if failure=='bounds': result.x=np.array([1.,1.,1.,3.,0.])
        if failure=='nonfinite_jac': result.jac[:]=np.nan
        return result
    monkeypatch.setattr(target,'least_squares',altered)
    result=target.fit_float_target(image,ref,alpha,protected,generated_fixture=True)
    assert result['parameters'] is None and result['status'].startswith('unavailable_')


@pytest.mark.parametrize('p',[[0,1,1,1,0],[1,0,1,1,0],[1,1,1,-1,0],
                            [1,1,1,1,float('nan')],[True,1,1,1,0],['1',1,1,1,0],[1,1,1]])
def test_invalid_controls_rejected(p):
    image,alpha,protected=fixture()
    with pytest.raises(ValueError): target.render_float(image,alpha,protected,p)


@pytest.mark.parametrize('kind',['protection','alpha_nan','empty','range','image','shape'])
def test_invalid_data_rejected(kind):
    image,alpha,protected=fixture();ref=image.copy()
    if kind=='protection': protected[0,0]=True
    if kind=='alpha_nan': alpha[0,0]=np.nan
    if kind=='empty': alpha[:]=0
    if kind=='range': alpha[0,0]=1.01
    if kind=='image': image[0,0,0]=1.1
    if kind=='shape': ref=ref[:2]
    with pytest.raises(ValueError): target.fit_float_target(image,ref,alpha,protected,generated_fixture=True)


def test_nonfinite_extreme_extrapolation_raises():
    image,alpha,protected=fixture()
    with pytest.raises(FloatingPointError): target.render_float(image,alpha,protected,[4,1,1,1e300,0])


def test_prepower_floor_and_high_intermediate_not_prematurely_clipped():
    image=np.array([[[0.,.4,1.],[.1,.5,.9]]]);alpha=np.ones((1,2));protected=np.zeros((1,2),bool)
    p=[1.,.5,.5,2.,-.2]
    output=target.render_float(image,alpha,protected,p)
    assert output[0,0,2]==.9  # Intermediate1.8 is reduced by blue gain rather than clipped to1first.
    assert output[0,0,0]==0
    expected,_=scalar.replay(image,image,alpha,p)
    np.testing.assert_allclose(output,expected,atol=1e-12,rtol=0)


def test_generated_output_refuses_overwrite_and_preserves_failure(tmp_path):
    import importlib.util
    import json
    from pathlib import Path
    path=Path(__file__).resolve().parents[1]/'scripts/check_affine_prepower_targets_generated.py'
    spec=importlib.util.spec_from_file_location('generated_affine_probe',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    dest=tmp_path/'partial'
    module.create_output(dest)
    sentinel=dest/'completed_case.txt';sentinel.write_text('preserve')
    module.record_failure(dest,RuntimeError('injected failure'))
    with pytest.raises(FileExistsError):module.create_output(dest)
    assert sentinel.read_text()=='preserve'
    assert json.loads((dest/'failure_PRIVATE.json').read_text())['status']=='failed_preserved'
