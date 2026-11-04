"""Trace held-source control predictions to actual fitted leaves; no fitting."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.train_model import load_model
from src.data_preparation.controlled_training_table import FEATURES,TARGETS


def main():
    output=ROOT/'outputs/correction_controls_sourcecv_v1'
    destination=output/'control_failure_traces.json'
    if destination.exists():raise FileExistsError(destination)
    summary_path=output/'summary.json';summary=json.loads(summary_path.read_text())
    table=ROOT/'data/manifests/correction_controls_sourcecv_v1/development_train.csv'
    with table.open(encoding='utf-8',newline='') as stream:rows={r['pair_id']:r for r in csv.DictReader(stream)}
    audits={(a['fold_id'],a['method']):a for a in summary['fit_audits']}
    comparisons={(p['pair_id'],p['method']):p for p in summary['predictions']}
    results=[]
    for prediction in summary['predictions']:
        if prediction['method']!='controls_tree' or prediction['variant'] not in ['identity_control','mild_bright_exposure']:continue
        audit=audits[(prediction['fold_id'],'controls_tree')]
        path=output/'fold_models'/f"fold{prediction['fold_id']}_controls_tree.joblib"
        assert hashlib.sha256(path.read_bytes()).hexdigest()==summary['fold_model_sha256'][path.name]
        learner=load_model(str(path));x=np.asarray(prediction['features'],float)[None,:]
        leaf=int(learner.apply(x)[0]);fitting=[rows[p] for p in audit['fit_pair_ids']]
        train_x=np.asarray([[float(r[k]) for k in FEATURES] for r in fitting])
        members=[r for r,node in zip(fitting,learner.apply(train_x)) if int(node)==leaf]
        assert members
        assert prediction['source_image_id'] not in {r['source_image_id'] for r in members}
        mean=np.mean([[float(r[k]) for k in TARGETS] for r in members],axis=0)
        np.testing.assert_allclose(mean,prediction['predicted_parameters'],atol=1e-12,rtol=0)
        no_correction=comparisons[(prediction['pair_id'],'no_correction')]
        results.append(dict(pair_id=prediction['pair_id'],source_image_id=prediction['source_image_id'],variant=prediction['variant'],
            fold_id=prediction['fold_id'],leaf_id=leaf,predicted_parameters=prediction['predicted_parameters'],
            target_parameters=prediction['target_parameters'],mean_leaf_targets=mean.tolist(),
            fitted_leaf_members=[dict(pair_id=r['pair_id'],source_image_id=r['source_image_id'],variant=r['variant'],
                target_parameters=[float(r[k]) for k in TARGETS]) for r in members],
            corrected_error=prediction['ciede2000_source_mask'],no_correction_error=no_correction['ciede2000_source_mask'],
            worsens_vs_no_correction=prediction['ciede2000_source_mask']>no_correction['ciede2000_source_mask']))
    assert len(results)==12
    destination.write_text(json.dumps(dict(status='complete',traces=results,
        limitation='Describes fitted training branches under fixed fold models; does not establish causal physical skin/exposure identifiability or generalization.',
        source_summary_sha256=hashlib.sha256(summary_path.read_bytes()).hexdigest(),
        source_table_sha256=hashlib.sha256(table.read_bytes()).hexdigest()),indent=2),encoding='utf-8')
    print(json.dumps(dict(control_traces=12,worsened_identity=sum(r['variant']=='identity_control' and r['worsens_vs_no_correction'] for r in results),
        worsened_mild=sum(r['variant']=='mild_bright_exposure' and r['worsens_vs_no_correction'] for r in results))))


if __name__=='__main__':main()
