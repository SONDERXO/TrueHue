"""Independent metadata-only prediction-roster/budget/target verification."""
from pathlib import Path
import json
import hashlib
import math
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/five_control_source_held_prediction_design_v1'


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    plan=json.loads((OUT/'plan_PRIVATE.json').read_text(encoding='utf-8'))
    rows=plan['rows'];ids={r['source_id'] for r in rows}
    roles={'identity','colour_only','exposure_under','exposure_over','combined_under','combined_over'}
    assert len(rows)==66 and len(ids)==11 and '29863' not in ids
    assert len({r['case_id'] for r in rows})==66
    assert {(r['source_id'],r['role']) for r in rows}=={(s,r) for s in ids for r in roles}
    by_id={r['case_id']:r for r in rows};held_counts=Counter();fit_counts=Counter()
    for fold in plan['folds']:
        s=fold['held_source_id'];f=fold['fitting_cases'];h=fold['evaluation_cases']
        assert len(f)==len(set(f))==60 and len(h)==len(set(h))==6
        assert set(f)|set(h)==set(by_id) and not set(f)&set(h)
        assert {by_id[c]['source_id'] for c in h}=={s}
        assert {by_id[c]['source_id'] for c in f}==ids-{s}
        assert set(fold['fitting_source_ids'])==ids-{s}
        assert {by_id[c]['role'] for c in h}==roles
        held_counts.update(h);fit_counts.update(f)
    assert len(plan['folds'])==11 and set(held_counts.values())=={1} and set(fit_counts.values())=={10}
    for r in rows:
        target=json.loads((ROOT/r['target_record']).read_text(encoding='utf-8'))['target']
        assert r['y']==target['parameters'] and len(r['y'])==5
        assert r['generated_fixture'] is False and not r['parent_training_admitted']
        assert r['official_tone_label'] is None
        assert r['allowed_input_key']=='input'
    assert len(plan['feature_names'])==len(set(plan['feature_names']))==281
    assert len(plan['feature_sources'])==11
    assert all(len(s['identity_saved_feature_vector'])==281 for s in plan['feature_sources'])
    assert plan['planned_tree_fits']==11 and plan['planned_fitting_route_replays']==11*60
    assert plan['planned_held_tree_predictions']==plan['planned_constant_held_renders']==11*6
    assert plan['planned_identity_feature_replays']==11 and plan['planned_new_nonidentity_feature_vectors']==55
    assert len(plan['bound_hit_cases_retained'])==6
    assert plan['settings']['max_depth']==4 and plan['settings']['random_state']==42
    for path,digest in plan['input_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    assert plan['real_arrays_read']==plan['new_features_computed']==plan['fits_executed']==plan['predictions_executed']==0
    result=dict(passed=True,scope='metadata_design_only_not_generated_workflow_QA',
        exact_cases=66,folds=11,fitting_route_budget=660,held_prediction_budget=66,
        target_refits=0,planned_tree_fits=11,bound_cases_preserved=6,
        gamma_raw_target_variance_fraction=plan['saved_target_root_SSE_fractions'][0],
        mapper_status='development_unvalidated_transfer_preserved',
        plan_sha256=hashlib.sha256((OUT/'plan_PRIVATE.json').read_bytes()).hexdigest(),
        arrays_read=0,fits=0,predictions=0,locked_access=False)
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
