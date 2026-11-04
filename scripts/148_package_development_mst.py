"""Package passed diagnostic recipe, retaining weak accuracy and development status."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from sklearn.isotonic import IsotonicRegression
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup


def main():
    folder=ROOT/'outputs/mst_monotone_square256_v1';target=folder/'development_lookup.json'
    if target.exists():raise FileExistsError(target)
    report=json.loads((folder/'summary.json').read_text())
    assert report['status']=='development_gate_passed_not_final_validation' and all(report['checks'].values())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in report['input_sha256'].items())
    original=json.loads((ROOT/'outputs/mst_square256_measurement_v1/summary.json').read_text())
    rows=[r for r in original['records'] if r['status']=='success']
    weights=[1/sum(s['subject_id']==r['subject_id'] for s in rows) for r in rows]
    model=IsotonicRegression(increasing=False,out_of_bounds='clip',y_min=1,y_max=10)
    x=[r['features']['input_ita_degrees'] for r in rows]
    model.fit(x,[r['source_mst_label'] for r in rows],sample_weight=weights)
    payload=dict(schema_version='truehue_development_monotone_mst_v1',status='experimental_not_final_validated',
        measurement_contract_sha256=report['measurement_contract_sha256'],ita_knots=model.X_thresholds_.tolist(),
        mst_knots=model.y_thresholds_.tolist(),rounding='floor_plus_half',outside_range='clip',
        calibration_subjects=sorted({r['subject_id'] for r in rows}),calibration_images=len(rows),
        validation_evidence='Exposed subject-held development evaluation; not independent final validation',
        evaluation_summary_sha256=hashlib.sha256((folder/'summary.json').read_bytes()).hexdigest(),
        quality=report['metrics']['overall'],scope_approval=report['scope_approval'],
        limitation='Weak exact accuracy, limited category support and photographed lighting dependence. Not a production lookup or calibrated complexion estimate.')
    portable=DevelopmentMonotoneLookup(payload,report['measurement_contract_sha256'])
    vectors=list(x)+model.X_thresholds_.tolist()+[(a+b)/2 for a,b in zip(model.X_thresholds_,model.X_thresholds_[1:])]+[-90,90]
    expected=model.predict(vectors)
    np.testing.assert_allclose([portable.continuous(v) for v in vectors],expected,rtol=0,atol=1e-12)
    assert [portable.label(v) for v in vectors]==np.floor(expected+.5).astype(int).tolist()
    target.write_text(json.dumps(payload,indent=2))
    result=dict(status='pass_experimental_artifact_parity',vectors_checked=len(vectors),new_full_data_mapping_fits=1,
        correction_tree_fits=0,runtime_activated=False,final_validated=False,
        lookup_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),fitted_label_range=[portable.label(90),portable.label(-90)])
    (folder/'artifact_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
