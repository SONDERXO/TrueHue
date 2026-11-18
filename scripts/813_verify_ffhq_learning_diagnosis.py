"""Independent saved-routing/target-contribution diagnosis verifier; no fits."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'outputs/ffhq_learning_diagnosis_v1'
P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
M=ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    dest=D/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    assert all(sha(p)==h for p,h in read(D/'input_sha256_PRIVATE.json').items())
    rows={r['case_id']:r for r in read(P/'rows_PRIVATE.json')};models={r['definition']['held_publisher_group']:r for r in read(M/'models_PRIVATE.json')};preds={r['case_id']:r for r in read(M/'predictions_PRIVATE.json')};summary=read(D/'summary_PRIVATE.json')
    close=lambda a,b:math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-11)
    def route(f,r):
        nodes=f['tree']['nodes'];i=0
        while nodes[i]['kind']=='split':
            n=nodes[i];i=n['left'] if r['input_vector_float32'][n['feature']]<=n['threshold'] else n['right']
        return i
    def members(f,i):return [rows[c] for c in f['definition']['fitting_cases'] if route(f,rows[c])==i]
    for r in read(D/'held_contexts_PRIVATE.json'):
        f=models[r['held_group']];p=preds[r['case_id']];i=route(f,rows[r['case_id']]);group=members(f,i)
        assert i==r['leaf']==p['leaf_id'] and r['fitting_members']==[v['case_id'] for v in group]
        assert r['fitting_roles']==dict(Counter(v['experimental_role'] for v in group))
        for j in range(3):
            assert close(sum(v['nominal_controls'][j] for v in group)/len(group),r['control'][j])
            assert close(sum(r['drift_from_identity_by_role'][k][j] for k in r['drift_from_identity_by_role']),p['controls'][j]-1)
        assert r['control']==p['controls']
    fitting=read(D/'fitting_replays_PRIVATE.json');assert len(fitting)==440
    for r in fitting:
        f=models[r['held_group']];i=route(f,rows[r['case_id']]);assert i==r['leaf'] and r['control']==f['tree']['nodes'][i]['values']
        assert r['target']==rows[r['case_id']]['nominal_controls']
    assert sum(r['nonidentity_control'] for r in fitting if r['role']=='identity')==summary['fitting_identity_nonidentity_controls']==95
    budgets=read(D/'target_budgets_PRIVATE.json');totals=[0.,0.,0.]
    for b in budgets:
        f=models[b['held_group']];train=[rows[c] for c in f['definition']['fitting_cases']]
        assert dict(Counter(r['experimental_role'] for r in train))==b['fitting_role_counts']==dict(identity=10,exposure_under=10,exposure_over=10,colour_cool=10)
        for j in range(3):
            y=[Fraction(str(r['nominal_controls'][j])) for r in train]
            variance=float(sum((a-v)**2 for a in y for v in y)/(2*len(y)))
            assert close(variance,b['target_root_SSE'][j]);totals[j]+=variance
    assert all(close(a,b) for a,b in zip(totals,summary['target_root_SSE']))
    assert close(totals[0]/sum(totals),summary['gamma_fraction_of_raw_target_root_SSE'])
    pairs=read(D/'paired_paths_PRIVATE.json');assert sum(r['same_leaf'] for r in pairs)==9
    for r in pairs:
        f=models[r['group']];a=rows[r['identity_case']];b=rows[r['cool_case']]
        assert r['same_leaf']==(route(f,a)==route(f,b));assert len(r['unchanged_green_features'])==4
        assert all(a['features'][k]==b['features'][k] for k in r['unchanged_green_features'])
    contexts=read(D/'held_contexts_PRIVATE.json')
    for role,key,count in [('identity','held_identities_in_exposure_only_leaves',7),('colour_cool','held_cool_in_exposure_only_leaves',6)]:
        assert sum(set(r['fitting_roles'])<=set(['exposure_under','exposure_over']) for r in contexts if r['role']==role)==summary[key]==count
    dest.write_text(json.dumps(dict(passed=True,held_context_replays=44,fitting_control_replays=440,exact_fraction_pairwise_target_variance_folds=11,paired_paths=11,new_fits=0,image_reads=0,holdout_reads=0,summary_sha256=sha(D/'summary_PRIVATE.json'),verifier_sha256=sha(__file__)),indent=2)+'\n')
    print(dest.read_text())

if __name__=='__main__':main()
