"""Prospective metadata-only single nearest-neighbour candidate."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.reiqa_frozen_features import sha
OUT=ROOT/'outputs/frozen_block_neighbour_design_v1'
def main():
    OUT.mkdir(exist_ok=False)
    parent=ROOT/'outputs/reiqa_added_feature_design_v1/plan_PRIVATE.json'
    plan=json.loads(parent.read_text(encoding='utf-8'))
    assert len(plan['feature_names'])==4377 and len(plan['rows'])==66
    assert json.loads((parent.parent/'verification_PRIVATE.json').read_text())['plan_sha256']==sha(parent)
    for p,h in plan['added_feature_bindings'].items():assert sha(ROOT/p)==h
    prior=ROOT/'outputs/reiqa_added_feature_prediction_v1/verification_PRIVATE.json'
    assert json.loads(prior.read_text())['numeric_status']=='NOT_ADVANCED'
    plan.update(predictor='fixed_equal_block_energy_1nn',k=1,block_weights=[1.,1.],
                settings=dict(k=1,blocks=[[0,281],[281,4377]],tie='lexical_case_id',
                    scale='fitting_only_centered_total_block_energy',distance='squared_euclidean'),
                protocol='docs/frozen-block-neighbour-correction-protocol-2026-11-15.md',
                maximum_index_constructions=11,tree_fits=0,baseline_refits=0,
                scope='user_authorized_exposed_development_predictor_assessment_not_paper_runtime_adoption')
    files=['docs/frozen-block-neighbour-correction-protocol-2026-11-15.md','scripts/specify_frozen_block_neighbour.py',
        'outputs/reiqa_added_feature_design_v1/plan_PRIVATE.json',
        'outputs/reiqa_added_feature_prediction_v1/verification_PRIVATE.json']
    plan['neighbour_bindings']={p:sha(ROOT/p) for p in files}
    (OUT/'plan_PRIVATE.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,plan_sha256=sha(OUT/'plan_PRIVATE.json'),
        sources=11,cases=66,indices=0,tree_fits=0,dimensions=4377),indent=2),encoding='utf-8')
    print('Fixed one4377two-block1NN design; no construction or scoring.')
if __name__=='__main__':main()
