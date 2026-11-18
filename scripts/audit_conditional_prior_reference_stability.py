"""Fixed eleven exposed identity references; statistical stability, no correction."""
from pathlib import Path
import hashlib,json,math,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.reference_prior_stability_audit import summarize,table_for_fold,residual

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def scalar_summary(rgb):
    groups=[[] for _ in range(8)];positive=0
    for r,g,b in rgb.reshape(-1,3).tolist():
        if min(r,g,b)==0:continue
        positive+=1;k=min(7,math.floor(8*g/255));groups[k].append([math.log(r/g),math.log(b/g)])
    return dict(total=65536,positive=positive,bins=[dict(count=len(v),mean=[math.fsum(p[j] for p in v)/len(v) for j in [0,1]] if v else None) for v in groups])

def main():
    if sys.argv[1:]!=['--execute-reference-audit']:raise SystemExit('Explicit reference-audit flag required')
    sourceplan=ROOT/'outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json';refs=read(sourceplan)['source_references']
    assert len(refs)==len({r['source'] for r in refs})==11 and all('29863' not in r['identity_case'] for r in refs)
    files=['docs/conditional-prior-reference-audit-protocol-2026-11-14.md','src/model_training/reference_prior_stability_audit.py','tests/test_reference_prior_stability_audit.py','scripts/audit_conditional_prior_reference_stability.py','outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json']
    bindings={n:sha(ROOT/n) for n in files};out=ROOT/'outputs/conditional_prior_reference_stability_v1';out.mkdir()
    write(out/'execution.json',dict(stage='DESCRIPTIVE_EXPOSED_REFERENCE_STATISTICS_NOT_CORRECTION',references=refs,input_sha256=bindings,correction_tree_fits=0,new_candidate_predictions=0,decoded_key_only='input_rgb8',archive_hash_covers_all_keys=True))
    try:
        test=subprocess.run([sys.executable,'-m','pytest','tests/test_reference_prior_stability_audit.py','-q','-p','no:cacheprovider','--junitxml='+str(out/'generated_tests.xml')],cwd=ROOT,capture_output=True,text=True)
        (out/'generated_tests.txt').write_text(test.stdout+test.stderr,encoding='utf-8')
        if test.returncode:raise RuntimeError('Generated leakage/accounting tests failed; no reference decode allowed')
        arrays={};stats={};scalar={};checks=0;worst=0.
        def close(a,b):
            nonlocal checks,worst
            assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12);checks+=1;worst=max(worst,abs(a-b))
        for ref in refs:
            path=Path(ref['identity_container']);expected=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'/ref['identity_case']/'paired_pixels.npz'
            assert path.resolve()==expected.resolve() and ref['allowed_key']=='input_rgb8' and sha(path)==ref['identity_sha256']
            with np.load(path,allow_pickle=False) as pack:rgb=pack['input_rgb8']
            source=ref['source'];arrays[source]=rgb;stats[source]=summarize(rgb);scalar[source]=scalar_summary(rgb)
            assert stats[source]['positive']>0 and stats[source]['positive']==scalar[source]['positive']
            for a,b in zip(stats[source]['bins'],scalar[source]['bins']):
                assert a['count']==b['count']
                if a['mean']:
                    for x,y in zip(a['mean'],b['mean']):close(x,y)
        write(out/'reference_statistics.json',stats)
        tables={};others={}
        for held in sorted(stats):
            fitting=sorted(set(stats)-{held});tables[held]=table_for_fold(stats,fitting,held);other=[]
            for k in range(8):
                ids=[s for s in fitting if scalar[s]['bins'][k]['count']];mu=[math.fsum(scalar[s]['bins'][k]['mean'][j] for s in ids)/len(ids) for j in [0,1]] if ids else None
                assert tables[held][k]['contributors']==ids and held not in ids
                if mu:
                    for a,b in zip(tables[held][k]['mean'],mu):close(a,b)
                else:assert tables[held][k]['mean'] is None
                other.append(mu)
            others[held]=other
        write(out/'tables.json',tables);write(out/'tables_sealed.json',dict(passed=True,diagnostic_tables=11,each_excludes_own_source=True))
        rows=[]
        for held in sorted(stats):
            d=residual(stats[held],tables[held]);pairs=[]
            for r,g,b in arrays[held].reshape(-1,3).tolist():
                if min(r,g,b)==0:continue
                mu=others[held][min(7,math.floor(8*g/255))]
                if mu is not None:pairs.append([math.log(r/g)-mu[0],math.log(b/g)-mu[1]])
            assert len(pairs)==d['supported_pixels']
            if pairs:
                for j,k in enumerate(['red_residual','blue_residual']):close(math.fsum(p[j] for p in pairs)/len(pairs),d[k])
            else:assert d['red_residual'] is None and d['blue_residual'] is None
            rows.append(dict(source=held,descriptor=d,bin_contributor_counts=[len(t['contributors']) for t in tables[held]],absolute_residual_to_existing_edit_scale=[abs(d[k])/abs(math.log(245/255)) if d[k] is not None else None for k in ['red_residual','blue_residual']],comparison_not_acceptance_threshold=True))
        summarize_axis=lambda key:dict(signed_min=min(r['descriptor'][key] for r in rows if r['descriptor'][key] is not None),signed_max=max(r['descriptor'][key] for r in rows if r['descriptor'][key] is not None),median_absolute=float(np.median([abs(r['descriptor'][key]) for r in rows if r['descriptor'][key] is not None])),maximum_absolute=max(abs(r['descriptor'][key]) for r in rows if r['descriptor'][key] is not None))
        result=dict(passed=True,diagnostic_tables=11,held_references=rows,red=summarize_axis('red_residual'),blue=summarize_axis('blue_residual'),existing_edit_abs_log_scale=abs(math.log(245/255)),scalar_values_checked=checks,max_abs_difference=worst,decoded_identity_input_arrays=11,decoded_other_NPZ_keys=0,correction_tree_fits=0,new_candidate_predictions=0,new_renders=0,new_ratings=0,model_adopted=False)
        for ref in refs:assert sha(Path(ref['identity_container']))==ref['identity_sha256']
        assert all(sha(ROOT/n)==h for n,h in bindings.items())
        write(out/'results.json',result);write(out/'verification.json',dict(passed=True,results_sha256=sha(out/'results.json'),table_sha256=sha(out/'tables.json'),input_sha256=bindings,scalar_values_checked=checks,held_reference_excluded=True,correction_tree_fits=0,new_candidate_predictions=0))
        print(test.stdout);print(json.dumps(dict(red=result['red'],blue=result['blue'],edit_scale=result['existing_edit_abs_log_scale'],scalar_values=checks,maxdifference=worst,coverage=[r['descriptor']['supported_fraction'] for r in rows]),indent=2))
    except BaseException as error:write(out/'failure.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise
if __name__=='__main__':main()
