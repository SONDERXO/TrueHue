"""Metadata-only fixed comparison design; no photo or feature extraction."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training.reiqa_frozen_features import sha
OUT=ROOT/'outputs/reiqa_added_feature_design_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    OUT.mkdir(exist_ok=False)
    parent=ROOT/'outputs/five_control_source_held_prediction_design_v1/plan_PRIVATE.json'
    plan=read(parent);assert read(parent.parent/'verification_PRIVATE.json')['plan_sha256']==sha(parent)
    rep=ROOT/'outputs/reiqa_development_representation_v1'
    assert read(rep/'independent_verification_PRIVATE.json')['passed']
    assert sha(rep/'features.npz')==read(rep/'completion_PRIVATE.json')['feature_sha256']
    prepared=ROOT/'outputs/five_control_real_feature_preparation_v1'
    assert read(prepared/'verification_PRIVATE.json')['passed']
    assert read(prepared/'completion_PRIVATE.json')['identity_vectors_exact']==11
    feature_rows=read(prepared/'rows_PRIVATE.json');rep_rows=read(rep/'rows_PRIVATE.json')
    assert [(r['case_id'],r['source_id'],r['role']) for r in feature_rows]==[(r['case_id'],r['source_id'],r['role']) for r in rep_rows]
    assert len(feature_rows)==66 and all(len(r['x'])==281 and r['generated_fixture'] is False for r in feature_rows)
    assert all(a['y']==b['y'] for a,b in zip(feature_rows,plan['rows']))
    plan.update(feature_names=plan['feature_names']+[f'reiqa_quality_{i:04d}' for i in range(4096)],
        generated_fixture=False,execution_role='exposed_development_added_frozen_features_not_final_admission',
        added_dimensions=4096,total_dimensions=4377,baseline_refits=0,feature_recomputations=0,
        protocol='docs/reiqa-added-feature-prediction-protocol-2026-11-15.md',
        saved_baseline='outputs/five_control_source_held_prediction_v1',
        representation_root=str(rep.relative_to(ROOT)))
    files=['docs/reiqa-added-feature-prediction-protocol-2026-11-15.md',
           'scripts/specify_reiqa_added_feature_test.py',
           'outputs/five_control_source_held_prediction_design_v1/plan_PRIVATE.json',
           'outputs/five_control_real_feature_preparation_v1/rows_PRIVATE.json',
           'outputs/five_control_real_feature_preparation_v1/verification_PRIVATE.json',
           'outputs/reiqa_development_representation_v1/features.npz',
           'outputs/reiqa_development_representation_v1/completion_PRIVATE.json',
           'outputs/reiqa_development_representation_v1/independent_verification_PRIVATE.json',
           'outputs/five_control_source_held_prediction_v1/verification_PRIVATE.json',
           'outputs/five_control_source_held_prediction_v1/evaluation/summary.json']
    plan['added_feature_bindings']={p:sha(ROOT/p) for p in files}
    (OUT/'plan_PRIVATE.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    result=dict(passed=True,plan_sha256=sha(OUT/'plan_PRIVATE.json'),rows=66,dimensions=4377,
                real_fits=0,source_held_folds=11,maximum_real_fits=11)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()
