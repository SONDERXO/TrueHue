"""Scalar matched-comparison verifier; imports no optimizer or target fitter."""
import math
import numpy as np
from . import affine_prepower_scalar as five
from .directional_recoverability_scalar import metrics

ROLES=('identity','colour_only','exposure_under','exposure_over','combined_under','combined_over')


def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10),(a,b)


def verify_case(case,record,output):
    image,reference,alpha,protected=[case[k] for k in ['image','reference','alpha','protected']]
    assert record['source_id']==case['source_id'] and record['role']==case['role']
    assert record['generated_fixture'] is case['generated_fixture']
    assert record['baseline_target']==case['baseline']['target']
    assert record['baseline_regions']==case['baseline']['regions']
    controls=case['baseline']['target']['parameters']+[1.,0.]
    old_float,old_objective=five.replay(image/255.,reference/255.,alpha,controls)
    old_rgb=np.rint(old_float*255).astype(np.uint8);old_rgb[alpha==0]=image[alpha==0]
    np.testing.assert_array_equal(old_rgb,case['baseline_output'])
    assert record['baseline_witness']['controls']==controls
    close(old_objective['float_mse'],record['baseline_witness']['float_mse'])
    close(old_objective['float_rmse'],case['baseline']['target'].get('float_rmse',0.))
    result=record['target']
    assert result['generated_fixture'] is case['generated_fixture'] and not result['model_ready']
    assert five.verify(image,reference,alpha,protected,result,rgb8=True)
    if result['parameters'] is None:
        assert output is None and record['float_mse_delta_to_baseline'] is None
    else:
        p=result['parameters']
        assert all(lo<=v<=hi for lo,v,hi in zip([.25,.25,.25,.5,-.3],p,[4,4,4,2,.3]))
        actual,_=five.replay(image/255.,reference/255.,alpha,p)
        rounded=np.rint(actual*255).astype(np.uint8);rounded[alpha==0]=image[alpha==0]
        np.testing.assert_array_equal(rounded,output)
        assert np.array_equal(output[protected],image[protected]) and np.array_equal(output[alpha==0],image[alpha==0])
        close(record['float_mse_delta_to_baseline'],result['float_mse']-old_objective['float_mse'])
        if case['role']=='identity':
            assert p==[1.,1.,1.,1.,0.] and result['evaluations']==0
            np.testing.assert_array_equal(output,reference)
        else:
            assert result['converged'] and result['jacobian_rank']==5
            singular=result['jacobian_singular_values']
            assert len(singular)==5 and all(math.isfinite(s) and s>0 for s in singular)
            assert min(singular)>max(singular)*max(int((alpha>0).sum())*3,5)*np.finfo(float).eps
            close(result['jacobian_condition_number'],max(singular)/min(singular))
            neutral_mse=math.fsum((float(a)-float(b))**2 for a,b in zip((image[alpha>0]/255.).flat,(reference[alpha>0]/255.).flat))/(int((alpha>0).sum())*3)
            close(result['identity_mse'],neutral_mse)
            assert result['float_mse']<=neutral_mse+1e-12
    for name,mask in {'primary':alpha>0,'core':alpha==1,'feather':(alpha>0)&(alpha<1),
                      'whole':np.ones(alpha.shape,bool)}.items():
        saved=record['regions'][name];assert saved['pixels']==int(mask.sum())
        old=metrics(case['baseline_output'],reference,mask)
        current=metrics(output,reference,mask) if output is not None else None
        if current is None:
            assert saved['output'] is None and saved['improvement_over_baseline'] is None
        else:
            for key in ['RGB','DE']:
                close(saved['output'][key],current[key])
                close(saved['improvement_over_baseline'][key],old[key]-current[key])
    return True


def verify_summary(records,summary):
    for role in ROLES:
        own=[r for r in records if r['role']==role]
        paired=[r for r in own if r['target']['parameters'] is not None]
        saved=summary['by_role'][role]
        assert saved['attempted']==len(own) and saved['available']==len(paired)
        assert saved['unavailable_sources']==[r['source_id'] for r in own if r['target']['parameters'] is None]
        for key in ['RGB','DE']:
            for label,block,field in [('baseline','baseline_regions','output'),('candidate','regions','output'),('improvement','regions','improvement_over_baseline')]:
                expected=math.fsum(r[block]['primary'][field][key] for r in paired)/len(paired) if paired else None
                if expected is None:assert saved['primary'][key][label] is None
                else:close(saved['primary'][key][label],expected)
        for key in ['RGB','DE']:
            assert saved[key+'_regressions']==[r['source_id'] for r in paired if r['regions']['primary']['improvement_over_baseline'][key]<-1e-10]
        assert saved['worse_float_objectives']==[r['source_id'] for r in paired if r['float_mse_delta_to_baseline']>1e-12]
    coverage=len(records)==66 and all(summary['by_role'][r]['attempted']==summary['by_role'][r]['available']==11 for r in ROLES)
    identity=coverage and all(r['target']['parameters']==[1.,1.,1.,1.,0.] and r['regions']['primary']['output']=={'RGB':0.,'DE':0.}
        for r in records if r['role']=='identity')
    nonworse=coverage and all(summary['by_role'][r]['primary'][k]['improvement']>=-1e-10 for r in ROLES if r!='identity' for k in ['RGB','DE'])
    improves=coverage and any(all(summary['by_role'][r]['primary'][k]['improvement']>1e-10 for k in ['RGB','DE'])
        for r in ['exposure_under','exposure_over','combined_under','combined_over'])
    assert summary['checks']==dict(coverage=coverage,identity=identity,each_role_RGB_and_DE_nonworse=nonworse,one_exposure_role_strictly_better=improves)
    assert summary['status']==('NUMERIC_CAPACITY_ELIGIBLE_ONLY' if coverage and identity and nonworse and improves else 'NOT_ADVANCED')
    assert not summary['model_ready'] and not summary['automatic_training_authorized']
    return True
