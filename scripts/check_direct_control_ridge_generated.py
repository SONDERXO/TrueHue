"""Fixed generated-only QA before the one real ridge comparison."""
import copy
import platform
import numpy as np
from direct_control_ridge_workflow import ROOT,fit_and_seal,read,write,sha,select
from direct_control_ridge_verify import scalar_predict,verify_fit,close
from src.model_training.direct_control_ridge import fit,predict
from src.model_training.luminance_chroma_operator import render_rgb8,parameters
from src.evaluation.luminance_chroma_scalar import replay

ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']
CODE=['src/model_training/direct_control_ridge.py','scripts/direct_control_ridge_verify.py',
      'scripts/direct_control_ridge_workflow.py','scripts/check_direct_control_ridge_generated.py',
      'src/model_training/luminance_chroma_operator.py','src/evaluation/luminance_chroma_scalar.py',
      'docs/direct-control-ridge-protocol-2026-11-16.md']


def main():
    out=ROOT/'outputs/direct_control_ridge_generated_v1'
    if out.exists():raise FileExistsError(out)
    rng=np.random.default_rng(42);rows=[]
    for s in range(11):
        for role in ROLES:
            g=2**(.5 if role.endswith('under') else -.5 if role.endswith('over') else 0)
            colour=role=='colour_only' or role.startswith('combined')
            y=[1.,g,1/.85 if colour else 1.,1/1.15 if colour else 1.,1.]
            x=rng.normal(0,.001,314);x[:3]=y[1:4];x[3]=s/10;x[-1]=0
            rows.append(dict(case_id=str(s)+'_'+role,source_id=str(s),role=role,generated_fixture=True,
                             x314=np.asarray(x,np.float32).astype(float).tolist(),y=y))
    folds=[dict(held_source_id=str(s),fitting_cases=[r['case_id'] for r in rows if r['source_id']!=str(s)],
                evaluation_cases=[r['case_id'] for r in rows if r['source_id']==str(s)]) for s in range(11)]
    plan=dict(folds=folds,generated_fixture=True)
    # Fit payload construction must not touch excluded feature/target values.
    class Poison(dict):
        def __getitem__(self,key):
            if key in ['x314','y']:raise AssertionError('Excluded payload accessed')
            return super().__getitem__(key)
    poison=[Poison(r) if r['source_id']=='0' else r for r in rows]
    assert len(select(poison,folds[0]))==60
    original=copy.deepcopy(rows)
    predictions=fit_and_seal(plan,rows,out)
    assert rows==original
    # Verify serialized models; scalar prediction does not use fitting labels.
    cert=read(out/'all_fits_verified.json');normal_max=0
    for entry in cert['models']:
        model=read(out/entry['path']);f=next(v for v in folds if v['held_source_id']==entry['source'])
        proof=verify_fit(model,select(rows,f),f);normal_max=max(normal_max,proof['max_normal_residual'])
        assert model['scale'][-1]==1 and all(v==0 for v in model['slopes'][-1])
        assert all(v[0]==0 and v[4]==0 for v in model['slopes'])
    image=rng.integers(0,256,(12,13,3),dtype=np.uint8);ref=image.copy()
    alpha=rng.choice([0.,.25,1.],(12,13));protected=np.zeros(alpha.shape,bool)
    protected[0,:]=True;alpha[protected]=0
    for p in predictions:
        q=render_rgb8(image,alpha,protected,p['controls'])
        expected,_=replay(image,ref,alpha,protected,p['controls'])
        assert np.array_equal(q,expected) and np.array_equal(q[protected],image[protected])
    try:fit_and_seal(plan,rows,out)
    except FileExistsError:pass
    else:raise AssertionError('Output overwritten')
    # Nonfinite/width and out-of-bounds predictions must fail explicitly.
    bad=copy.deepcopy(select(rows,folds[0]));bad[0]['x314'][0]=float('nan')
    try:fit(bad)
    except ValueError:pass
    else:raise AssertionError('Nonfinite fit accepted')
    model=read(out/cert['models'][0]['path'])
    try:predict(model,[0.])
    except ValueError:pass
    else:raise AssertionError('Bad width accepted')
    try:parameters([-1.,1.,1.,1.,1.])
    except ValueError:pass
    else:raise AssertionError('Invalid control accepted')
    # Identical-feature ambiguity is not solved by regularization.
    ambiguous=copy.deepcopy(select(rows,folds[0]))
    for r in ambiguous:r['x314']=[0.]*314
    am=fit(ambiguous)
    for row in ambiguous:
        assert predict(am,row['x314'])==am['intercept']
    report=dict(passed=True,generated_models=12,main_models=11,fitting_predictions=660,
                held_predictions=66,independent_scalar_renders=66,max_normal_residual=normal_max,
                excluded_payload_poison='PASS',input_immutable=True,no_overwrite='PASS',
                identical_feature_ambiguity='RETAINED_NOT_SOLVED',
                real_portraits=0,real_fits=0,versions=dict(python=platform.python_version(),numpy=np.__version__),
                code_sha256={p:sha(ROOT/p) for p in CODE})
    write(out/'verification.json',report);print(report)


if __name__=='__main__':main()
