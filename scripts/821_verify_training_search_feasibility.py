"""Independent fitting-only route/leaf/exact-objective verification; no refit."""
from pathlib import Path
from fractions import Fraction
from collections import Counter,defaultdict
import json,hashlib,struct,math
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/training_search_feasibility_v1'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]

def main():
    dest=O/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve independent verification')
    execution=read(O/'execution_plan_PRIVATE.json');assert all(sha(p)==h for p,h in execution['input_sha256'].items())
    rows=read(O/'fitting_inputs_PRIVATE.json');old=read(O/'incumbent_PRIVATE.json');new=read(O/'candidate_PRIVATE.json');stats=read(O/'search_PRIVATE.json')
    assert len(rows)==40 and [r['case_id'] for r in rows]==execution['training_cases']
    assert all('16061' not in r['case_id'] for r in rows)
    assert Counter(r['role'] for r in rows)==dict(identity=10,exposure_under=10,exposure_over=10,colour_cool=10)
    assert old['feature_names']==new['feature_names'] and len(new['feature_names'])==16
    def evaluate(payload):
        nodes=payload['nodes'];members=defaultdict(list);routing=[];seen=set();stack=[(0,0)]
        while stack:
            index,depth=stack.pop();assert index not in seen and depth<=4;seen.add(index);n=nodes[index]
            if n['kind']=='split':stack.extend([(n['left'],depth+1),(n['right'],depth+1)])
            else:assert len(n['values'])==3 and all(v>0 and math.isfinite(v) for v in n['values'])
        assert len(seen)==len(nodes)
        for r in rows:
            x=[f32(v) for v in r['input_vector_float32']];i=0
            while nodes[i]['kind']=='split':
                n=nodes[i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
            members[i].append(r);routing.append(dict(case_id=r['case_id'],leaf=i,controls=nodes[i]['values'],target=r['nominal_controls']))
        exact=Fraction();exported=Fraction()
        for i,n in enumerate(nodes):
            if n['kind']=='leaf':
                own=members[i];assert own
                for j in range(3):
                    y=[Fraction.from_float(float(r['nominal_controls'][j])) for r in own];mean=sum(y,Fraction())/len(y)
                    assert math.isclose(float(mean),n['values'][j],abs_tol=1e-12,rel_tol=1e-12)
                    exact+=sum(((v-mean)**2 for v in y),Fraction())
                    exported+=sum(((v-Fraction.from_float(float(n['values'][j])))**2 for v in y),Fraction())
        return exact,exported,routing
    before,before_float,old_routes=evaluate(old);after,after_float,new_routes=evaluate(new)
    for a,b in [(float(before),stats['initial_SSE']),(float(after),stats['selected_SSE']),(float(after_float),stats['exported_float_SSE'])]:assert math.isclose(a,b,abs_tol=1e-11,rel_tol=1e-11)
    assert after<=before and stats['expanded_states']<=5000 and stats['partial_states_cached']==0
    assert stats['global_lower_bound']<=stats['best_found_SSE']<=stats['initial_SSE']
    if stats['status']=='budget_limited':assert not stats['optimality_certified'] and stats['global_lower_bound']==0
    if stats['optimality_certified'] and stats['best_found_SSE']!=0:
        certificate='completion_reported_by_verified_algorithm_not_independently_exhausted_on_real_data'
    else:certificate='nonnegative_SSE_zero_bound_verified' if stats['best_found_SSE']==0 else 'budget_limited_no_global_optimality_claim'
    improved=float(before-after)>stats['numerical_improvement_tolerance'];assert improved==stats['strict_improvement']
    identity_counts={name:sum(any(abs(v-1)>1e-12 for v in r['controls']) for r in records if r['case_id'].endswith('__identity')) for name,records in [('incumbent',old_routes),('candidate',new_routes)]}
    (O/'fitting_routes_PRIVATE.json').write_text(json.dumps(dict(incumbent=old_routes,candidate=new_routes),indent=2)+'\n')
    result=dict(passed=True,fitting_routes_checked=80,exact_mean_SSE_before=float(before),exact_mean_SSE_after=float(after),serialized_float_SSE_before=float(before_float),serialized_float_SSE_after=float(after_float),training_identity_nonidentity_controls=identity_counts,strict_training_improvement=improved,certificate_scope=certificate,held_predictions=0,image_reads=0,new_fits=0,holdout_reads=0,summary_sha256=sha(O/'summary_PRIVATE.json'),candidate_sha256=sha(O/'candidate_PRIVATE.json'),verifier_sha256=sha(__file__))
    dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
