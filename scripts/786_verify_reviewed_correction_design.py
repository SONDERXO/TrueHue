"""Independent metadata-only verification of the correction comparison design."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/reviewed_correction_comparison_design_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    bound=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    plan=read(OUT/'plan_PRIVATE.json');rows=read(OUT/'rows_PRIVATE.json');folds=read(OUT/'folds_PRIVATE.json')
    original=read(ROOT/'outputs/shared_core_mst_features_v1/complete_development_rows_PRIVATE.json')
    assert rows==original and len(rows)==14 and len(folds)==8
    indexed={r['case_id']:r for r in rows};names=plan['candidate']['feature_names'];actions=plan['candidate']['actions']
    assert len(names)==16 and len(actions)==14 and plan['candidate']['maximum_depth']==4
    assert len({r['features']['input_mst_score'] for r in rows})==1
    assert sum(r['role']=='source' for r in rows)==sum(r['role']=='target' for r in rows)==7
    evaluated=[];missing=[];fitting_count=0
    for f in folds:
        held=f['held_publisher_group'];tests=f['evaluation_cases'];missing+=f['unavailable_evaluation_roles']
        assert len(f['attempted_evaluation_roles'])==2
        if held=='904':
            assert f['fit_required'] is False and f['fitting_cases']==tests==[]
            assert len(f['unavailable_evaluation_roles'])==2
            continue
        fitting_count+=1;assert f['fit_required'] and len(tests)==2 and len(f['fitting_cases'])==12
        assert set(tests)=={c for c,r in indexed.items() if r['publisher_group']==held}
        assert set(f['fitting_cases'])==set(indexed)-set(tests)
        assert {indexed[c]['publisher_group'] for c in f['fitting_cases']}=={r['publisher_group'] for r in rows}-{held}
        assert all(v==1. for v in f['fitting_role_weights'].values())
        evaluated+=tests
    assert fitting_count==7 and len(evaluated)==len(set(evaluated))==14 and len(missing)==2
    assert set(evaluated)==set(indexed)
    for r in rows:
        assert r['clean_identity_constraint']==(r['role']=='target')
        if r['role']=='target':assert r['action_costs'][0]==0
        assert r['training_admitted'] is False and r['calibration_admitted'] is False
    bounds=plan['execution_bounds'];assert bounds['tree_fits']==7 and bounds['held_role_predictions']==14
    assert not bounds['all_data_fit'] and bounds['new_MST_fits']==bounds['new_MST_predictions']==bounds['new_image_model_calls']==0
    assert not plan['execution_authorized_by_this_preparation'] and plan['new_fits']==plan['new_predictions']==0
    result=dict(passed=True,exact_existing_rows=14,source_roles=7,identity_roles=7,attempted_roles=16,
        fitting_folds=7,unavailable_only_fold_skipped=True,unique_held_predictions_planned=14,
        same_pair_never_split=True,old_features_actions_mapping_preserved=True,new_fits=0,new_predictions=0,image_reads=0,
        input_sha256={str(p):sha(p) for p in OUT.iterdir() if p.is_file()},verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:14unchangedrows/16attempts/7disjoint12fit-2evalfolds;904no fit;frozen features/actions/mapping;zero execution.')


if __name__=='__main__':main()
