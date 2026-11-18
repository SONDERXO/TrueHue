"""Bounded saved-JSON diagnosis, never reads images/NPZ/masks or fits models."""
from pathlib import Path
from collections import Counter,defaultdict
import sys
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.evaluation.five_control_saved_route_diagnosis import trace,detailed_path,errors,summarize_errors,composition,NEUTRAL

BASE=ROOT/'outputs/five_control_source_held_prediction_v1'
OUT=ROOT/'outputs/five_control_saved_route_diagnosis_v1'
SELECTED=[('29617','colour_only'),('48879','colour_only'),('49131','colour_only'),('48879','identity')]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def main():
    if OUT.exists():raise FileExistsError('Preserve diagnosis')
    verification=json.loads((BASE/'verification_PRIVATE.json').read_text(encoding='utf-8'))
    receipt=json.loads((BASE/'assessment_PRIVATE.json').read_text(encoding='utf-8'))
    assert verification['passed'] and receipt['verification_sha256']==sha(BASE/'verification_PRIVATE.json')
    bindings={str((BASE/'verification_PRIVATE.json').relative_to(ROOT)):sha(BASE/'verification_PRIVATE.json'),
              str((BASE/'assessment_PRIVATE.json').relative_to(ROOT)):sha(BASE/'assessment_PRIVATE.json')}
    def read(path):
        path=Path(path).resolve()
        assert path.suffix=='.json' and path.is_relative_to(BASE)
        rel=str(path.relative_to(BASE));expected=verification['artifact_sha256'][rel]
        assert sha(path)==expected
        bindings[str(path.relative_to(ROOT))]=expected
        return json.loads(path.read_text(encoding='utf-8'))
    rows=read(BASE/'prepared_rows.json');by_case={r['case_id']:r for r in rows}
    sealed=read(BASE/'models/held_controls_sealed.json');held={r['case_id']:r for r in sealed}
    cert=read(BASE/'models/all_fits_verified.json');plan=read(BASE/'execution_plan.json')
    assert len(rows)==len(sealed)==66 and cert['fit_calls']==11
    fitting_errors=defaultdict(list);held_errors=defaultdict(list);mixed=Counter();pooled=Counter();pure=Counter()
    contexts={};fit_routes=held_routes=0;used=Counter();fit_mix_examples=[]
    for fold,m in zip(plan['folds'],cert['models']):
        assert m['held_source_id']==fold['held_source_id']
        tree=read(m['tree_path']);fit=read(m['fitting_rows_path']);native=read(m['replay_path'])
        assert len(fit)==60 and [r['case_id'] for r in fit]==fold['fitting_cases']
        assert fold['held_source_id'] not in {r['source_id'] for r in fit}
        routes=[trace(tree,r['x']) for r in fit];members=defaultdict(list)
        assert [r['leaf'] for r in routes]==native['leaves']
        assert [r['controls'] for r in routes]==native['predictions']
        for r,route in zip(fit,routes):
            assert r=={k:by_case[r['case_id']][k] for k in ['case_id','source_id','role','generated_fixture','x','y']}
            members[route['leaf']].append(r);fitting_errors[r['role']].append(errors(route['controls'],r['y']))
        for leaf,own in members.items():
            for j in range(5):assert math.isclose(tree['nodes'][leaf]['values'][j],math.fsum(r['y'][j] for r in own)/len(own),abs_tol=1e-12,rel_tol=1e-12)
        for r,route in zip(fit,routes):
            types=composition(members[route['leaf']]);labels=types['roles']
            if r['role'] in NEUTRAL and types['exposure']:
                mixed[r['role']]+=1;fit_mix_examples.append(dict(held_source_id=fold['held_source_id'],case_id=r['case_id'],leaf=route['leaf'],composition=types))
            if r['role'] in NEUTRAL and 'identity' in labels and 'colour_only' in labels:pooled[r['role']]+=1
        for case_id in fold['evaluation_cases']:
            r=by_case[case_id];route=trace(tree,r['x']);p=held[case_id]
            assert route['controls']==p['controls'] and route['leaf']==p['leaf']
            held_errors[r['role']].append(errors(p['controls'],r['y']))
            types=composition(members[route['leaf']])
            if r['role'] in NEUTRAL and types['neutral']==0 and types['exposure']>0:pure[r['role']]+=1
            held_routes+=1
        contexts[fold['held_source_id']]=(tree,fit,routes,members)
        for node in tree['nodes']:
            if node['kind']=='split':used[tree['feature_names'][node['feature']]]+=1
        fit_routes+=len(routes)
    selected=[]
    for source_id,role in SELECTED:
        case_id=f'five_prediction_ffhq_{source_id}__{role}';r=by_case[case_id]
        tree,fit,routes,members=contexts[source_id]
        report=detailed_path(tree,r['x'],fit,routes)
        metric=read(BASE/'evaluation'/(case_id+'.json'))
        paired_role='identity' if role=='colour_only' else 'colour_only'
        paired_id=f'five_prediction_ffhq_{source_id}__{paired_role}'
        paired=detailed_path(tree,by_case[paired_id]['x'],fit,routes)
        assert report['controls']==metric['controls'] and report['first_neutral_exclusion'] is not None
        selected.append(dict(case_id=case_id,source_id=source_id,role=role,
            diagnostic_selection='four_predeclared_known_failures_not_independent_evidence',
            saved_primary_metrics=metric['regions']['primary'],route=report,
            paired_case_id=paired_id,paired_route=paired,reference_pair_is_not_available_at_inference=True))
    roles=list(plan['rows'][i]['role'] for i in range(6))
    assert len(set(roles))==6 and fit_routes==660 and held_routes==66
    summary=dict(fitting_control_errors={r:summarize_errors(fitting_errors[r]) for r in roles},
        held_control_errors={r:summarize_errors(held_errors[r]) for r in roles},
        fitting_neutral_occurrences_in_exposure_mixed_leaves={r:mixed[r] for r in ['identity','colour_only']},
        fitting_neutral_occurrences_in_identity_colour_mixed_leaves={r:pooled[r] for r in ['identity','colour_only']},
        held_neutral_cases_in_exposure_only_leaves={r:pure[r] for r in ['identity','colour_only']},
        saved_split_feature_counts=dict(used),selected_first_exclusions=[dict(case_id=r['case_id'],
            feature=r['route']['first_neutral_exclusion']['feature_name'],
            threshold=r['route']['first_neutral_exclusion']['threshold'],
            held_value=r['route']['first_neutral_exclusion']['held_value'],
            node=r['route']['first_neutral_exclusion']['node'],
            held_inside_node_fitting_range=r['route']['first_neutral_exclusion']['node_feature_range']['held_inside']) for r in selected],
        scope='saved_control_and_route_descriptions_not_new_predictions_or_fit_image_metrics',
        next_training_recipe_qualified=False,candidate_status='NOT_ADVANCED_UNCHANGED',
        new_fits=0,new_feature_computations=0,new_correction_renders=0,new_ratings=0,image_or_NPZ_reads=0)
    for relative in ['docs/five-control-saved-route-diagnosis-protocol-2026-11-15.md',
        'src/evaluation/five_control_saved_route_diagnosis.py','scripts/diagnose_five_control_saved_routes.py',
        'tests/test_five_control_saved_route_diagnosis.py']:
        bindings[relative]=sha(ROOT/relative)
    OUT.mkdir()
    write(OUT/'routes_PRIVATE.json',selected);write(OUT/'summary_PRIVATE.json',summary)
    write(OUT/'fitting_mixed_leaf_occurrences_PRIVATE.json',fit_mix_examples)
    assert all(sha(ROOT/p)==h for p,h in bindings.items())
    write(OUT/'verification_PRIVATE.json',dict(passed=True,metadata_JSON_only=True,
        saved_fitting_route_replays=660,saved_held_route_replays=66,selected_complete_paths=4,
        paired_context_paths=4,leaf_means_replayed=True,input_sha256=bindings,
        original_metadata_unchanged=True,new_fits=0,new_candidate_predictions=0,pixel_or_NPZ_reads=0))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
