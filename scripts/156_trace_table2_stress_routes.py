"""Trace existing held predictions to fitting leaf members; no new fits."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import joblib
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.data_preparation.controlled_training_table import TARGETS


def main():
    folder=ROOT/'outputs/table2_stress_evaluation_v2';target=folder/'route_diagnosis.json'
    if target.exists():raise FileExistsError(target)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    summary_path=folder/'summary.json';verification=json.loads((folder/'verification.json').read_text())
    assert digest(summary_path)==verification['summary_sha256']
    plan_path=folder/'fit_plan.json';assert digest(plan_path)==verification['fit_plan_sha256']
    plan=json.loads(plan_path.read_text());summary=json.loads(summary_path.read_text());rows={r['pair_id']:r for r in plan['rows']}
    result=[]
    for record in summary['records']:
        fold=next(f for f in plan['folds'] if f['fold_id']==record['fold_id'])
        model=joblib.load(folder/f"fold_{fold['fold_id']}/decision_tree.joblib")
        row=rows[record['pair_id']];x=[row[k] for k in MST_FEATURES];leaf=int(model.apply([x])[0])
        members=[]
        for pair in fold['train_pair_ids']:
            fit=rows[pair]
            if int(model.apply([[fit[k] for k in MST_FEATURES]])[0])==leaf:
                members.append(dict(pair_id=pair,targets=[fit[k] for k in TARGETS]))
        path=[]
        # sklearn routes float32 inputs; use the exported evaluator's conversion.
        from src.model_training.portable_tree import float32
        node=0
        while model.tree_.children_left[node]!=-1:
            feature=int(model.tree_.feature[node]);value=float32(x[feature]);threshold=float(model.tree_.threshold[node])
            left=value<=threshold
            path.append(dict(feature=MST_FEATURES[feature],input_float32=value,threshold=threshold,branch='left' if left else 'right'))
            node=int(model.tree_.children_left[node] if left else model.tree_.children_right[node])
        assert node==leaf
        result.append(dict(pair_id=row['pair_id'],leaf=leaf,path=path,fitting_leaf_members=members,
            parameters=record['parameters'],learned_ciede2000=record['learned']['ciede2000_source_mask']))
    target.write_text(json.dumps(dict(status='saved_routes_verified',summary_sha256=digest(summary_path),records=result,
        limitation='Leaf membership explains this fixed tree, not an impossibility claim or justification for new thresholds.'),indent=2))
    print(json.dumps([r for r in result if r['pair_id'] in ['62331__identity','22454__table2_light','6236__table2_light']],indent=2))


if __name__=='__main__':main()
