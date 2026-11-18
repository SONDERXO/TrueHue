"""Verify diagnostic branch memberships from saved native leaf IDs, not feature re-routing."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'outputs/five_control_source_held_prediction_v1'
OUT=ROOT/'outputs/five_control_saved_route_diagnosis_v1'


def read(p):
    p=Path(p);assert p.suffix=='.json'
    return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compose(rows):
    return dict(rows=len(rows),roles=dict(Counter(r['role'] for r in rows)),sources=dict(Counter(r['source_id'] for r in rows)),
        neutral=sum(r['role'] in ['identity','colour_only'] for r in rows),exposure=sum(r['role'] not in ['identity','colour_only'] for r in rows))


def main():
    destination=OUT/'independent_verification_PRIVATE.json'
    if destination.exists():raise FileExistsError('Preserve independent proof')
    original=read(OUT/'verification_PRIVATE.json')
    for p,h in original['input_sha256'].items():assert sha(ROOT/p)==h
    cases=read(OUT/'routes_PRIVATE.json');summary=read(OUT/'summary_PRIVATE.json')
    cert=read(BASE/'models/all_fits_verified.json');models={m['held_source_id']:m for m in cert['models']}
    by_case={r['case_id']:r for r in read(BASE/'prepared_rows.json')}
    held={p['case_id']:p for p in read(BASE/'models/held_controls_sealed.json')}
    branches=0;unique=set();fit_errors=defaultdict(list);held_errors=defaultdict(list)
    for model in cert['models']:
        fit=read(model['fitting_rows_path']);replay=read(model['replay_path'])
        for row,p in zip(fit,replay['predictions']):fit_errors[row['role']].append([(a-b)**2 for a,b in zip(p,row['y'])])
    for p in held.values():held_errors[p['role']].append([(a-b)**2 for a,b in zip(p['controls'],by_case[p['case_id']]['y'])])
    for key,groups in [('fitting_control_errors',fit_errors),('held_control_errors',held_errors)]:
        for role,errors in groups.items():
            saved=summary[key][role];assert saved['occurrences']==len(errors)
            expected=[math.fsum(e[j] for e in errors)/len(errors) for j in range(5)]
            for a,b in zip(saved['mean_per_control_squared_error'],expected):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12)
            assert math.isclose(saved['mean_total_control_SSE'],math.fsum(expected),abs_tol=1e-12,rel_tol=1e-12)
    for case in cases:
        model=models[case['source_id']];tree=read(model['tree_path']);rows=read(model['fitting_rows_path']);native=read(model['replay_path'])
        parent={0:None}
        for i,node in enumerate(tree['nodes']):
            if node['kind']=='split':
                for child in [node['left'],node['right']]:assert child not in parent;parent[child]=i
        def ancestry(leaf):
            result=[]
            while leaf is not None:result.append(leaf);leaf=parent[leaf]
            return list(reversed(result))
        native_ancestors=[ancestry(leaf) for leaf in native['leaves']]
        for case_id,report in [(case['case_id'],case['route']),(case['paired_case_id'],case['paired_route'])]:
            unique.add(case_id);assert report['leaf']==held[case_id]['leaf']
            assert report['controls']==held[case_id]['controls']
            assert [p['node'] for p in report['path']]+[report['leaf']]==ancestry(report['leaf'])
            first=None
            for entry in report['path']:
                node=tree['nodes'][entry['node']];j=node['feature']
                assert entry['feature_index']==j and entry['feature_name']==tree['feature_names'][j]
                assert entry['threshold']==node['threshold'] and entry['held_value']==by_case[case_id]['x'][j]
                chosen=node['left'] if entry['held_value']<=node['threshold'] else node['right']
                assert chosen==entry['child']
                subsets={name:[r for r,a in zip(rows,native_ancestors) if index in a]
                    for name,index in [('parent',entry['node']),('left',node['left']),('right',node['right']),('chosen',chosen)]}
                for name,values in subsets.items():assert entry[name]==compose(values)
                if first is None and entry['parent']['neutral'] and not entry['chosen']['neutral'] and entry['chosen']['exposure']:first=entry
                for name,values in [('node_feature_range',subsets['parent']),('chosen_feature_range',subsets['chosen']),
                    ('node_neutral_feature_range',[r for r in subsets['parent'] if r['role'] in ['identity','colour_only']]),
                    ('node_exposure_feature_range',[r for r in subsets['parent'] if r['role'] not in ['identity','colour_only']])]:
                    saved=entry[name];assert saved['count']==len(values)
                    if values:
                        lo=min(r['x'][j] for r in values);hi=max(r['x'][j] for r in values)
                        assert saved['min']==lo and saved['max']==hi and saved['held_inside']==(lo<=entry['held_value']<=hi)
                    else:assert saved['min'] is None and saved['max'] is None
                branches+=1
            assert report['first_neutral_exclusion']==first
    assert len(cases)==4 and len(unique)==6
    result=dict(passed=True,verification_method='native_leaf_ancestry_memberships_independent_of_diagnostic_route_walker',
        selected_cases=4,paired_context_records=4,unique_source_role_contexts=6,existing_split_records_checked=branches,
        fitting_and_held_control_error_summaries_checked=True,
        metadata_only=True,pixel_or_NPZ_reads=0,new_fits=0,new_predictions=0,
        diagnosis_sha256={p.name:sha(p) for p in [OUT/'routes_PRIVATE.json',OUT/'summary_PRIVATE.json',OUT/'verification_PRIVATE.json']},
        verifier_sha256=sha(Path(__file__)))
    destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
