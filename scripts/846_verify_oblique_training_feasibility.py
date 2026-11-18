"""Independent scalar replay; no trainer import, optimization or image access."""
from pathlib import Path
import hashlib
import json
import math
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]

def predict(model,row):
    x=[struct.unpack('!f',struct.pack('!f',float(v)))[0] for v in row]
    i=0
    while model['nodes'][i]['kind']=='split':
        n=model['nodes'][i]
        if 'weights' in n:
            right=math.fsum([n['intercept']]+[w*v for w,v in zip(n['weights'],x)])>0
        else:
            right=x[n['feature']]>n['threshold']
        i=n['right'] if right else n['left']
    return i,model['nodes'][i]['values']

def metrics(model,x,y,roles):
    errors=[];members={};identity=[]
    for k,(row,target,role) in enumerate(zip(x,y,roles)):
        leaf,values=predict(model,row);members.setdefault(leaf,[]).append(k)
        errors.append([(v-t)**2 for v,t in zip(values,target)])
        if role=='identity':
            identity.append([abs(v-1.) for v in values])
    return dict(SSE=math.fsum(v for row in errors for v in row),
        per_control=[math.fsum(row[j] for row in errors) for j in range(3)],
        per_role={r:math.fsum(v for k,row in enumerate(errors) if roles[k]==r for v in row) for r in sorted(set(roles))},
        members=members,identity_max_abs_control_deviation=[max((r[j] for r in identity),default=0.) for j in range(3)])

def verify_arrays(axis,initial,candidate,report,x,y,roles):
    assert len(x)==len(y)==len(roles)>0
    assert len(initial['nodes'])==len(candidate['nodes'])
    assert initial['feature_names']==candidate['feature_names']
    for a,b in zip(initial['nodes'],candidate['nodes']):
        assert a['kind']==b['kind']
        if a['kind']=='split':
            assert (a['left'],a['right'])==(b['left'],b['right'])
            assert len(b['weights'])==len(initial['feature_names'])
            assert all(math.isfinite(v) for v in b['weights']+[b['intercept']])
        else:assert len(b['values'])==3 and all(math.isfinite(v) and v>0 for v in b['values'])
    for row in x:
        assert predict(axis,row)[1]==predict(initial,row)[1]
    before=metrics(initial,x,y,roles);after=metrics(candidate,x,y,roles)
    for actual,recorded in [(before['SSE'],report['initial_SSE']),(after['SSE'],report['final_SSE'])]:
        assert math.isclose(actual,recorded,rel_tol=1e-12,abs_tol=1e-14)
    history=report['SSE_history']
    assert history[0]['SSE']==report['initial_SSE']
    assert history[-1]['SSE']==report['final_SSE']
    assert all(b['SSE']<=a['SSE'] for a,b in zip(history,history[1:]))
    assert after['SSE']<=before['SSE']
    # A cap can interrupt after a branch and before leaf refresh. Report residuals,
    # rather than incorrectly treating stale means as a correctness failure.
    residual=0.
    for leaf,ids in after['members'].items():
        means=[math.fsum(y[k][j] for k in ids)/len(ids) for j in range(3)]
        residual=max(residual,max(abs(a-b) for a,b in zip(means,candidate['nodes'][leaf]['values'])))
    if history[-1]['event']=='leaf_means':
        assert residual<=1e-12
    improved=before['SSE']-after['SSE']>1e-12*max(1.,before['SSE'])
    capped=report['status'] in ('time_cap','pass_cap','proposal_cap')
    return dict(passed=True,rows=len(x),initial=before,final=after,
        populated_leaf_mean_max_residual=residual,leaf_refresh_last=history[-1]['event']=='leaf_means',
        classification=('CAPPED_' if capped else 'VALID_')+('STRICT_FITTING_IMPROVEMENT' if improved else 'NO_STRICT_FITTING_IMPROVEMENT'),
        stored_nonzero_branch_coefficients=sum(w!=0 for n in candidate['nodes'] if n['kind']=='split' for w in n['weights']),
        empty_leaves=[i for i,n in enumerate(candidate['nodes']) if n['kind']=='leaf' and i not in after['members']],
        held_predictions=0,photo_reads=0,correction_quality_established=False)

def main():
    out=ROOT/'outputs/oblique_training_feasibility_v1'
    dest=out/'independent_verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve existing verification')
    read=lambda name:json.loads((out/name).read_text(encoding='utf-8'))
    receipt=read('execution_plan_PRIVATE.json')
    for key,name in [('runner_sha256','845_run_oblique_training_feasibility.py'),('verifier_sha256','846_verify_oblique_training_feasibility.py')]:
        assert hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest()==receipt[key]
    for name,digest in receipt['input_sha256'].items():
        path=(ROOT/name).resolve()
        assert path.is_relative_to(ROOT.resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
    assert read('run_status_PRIVATE.json')['fit_calls']==1
    inputs=read('fitting_inputs_PRIVATE.json')
    result=verify_arrays(read('initial_axis_PRIVATE.json'),read('initial_oblique_PRIVATE.json'),
        read('candidate_PRIVATE.json'),read('optimization_PRIVATE.json'),inputs['x'],inputs['y'],inputs['roles'])
    assert result['rows']==40
    result['artifact_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.json')}
    dest.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(result['classification'])

if __name__=='__main__':main()
