"""Generated arithmetic end-to-end check; never loads real measurement rows."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.ita_estimation.contextual_mst_experiment import FEATURES,METHODS,evaluate_subject_held,predict

OUT=ROOT/'outputs/contextual_mst_generated_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    sources=[ROOT/p for p in ['src/ita_estimation/contextual_mst_experiment.py','tests/test_contextual_mst_experiment.py',
        'scripts/451_check_contextual_mst_generated.py','docs/contextual-mst-implementation-protocol-2026-11-05.md']]
    preserved=[ROOT/p for p in ['src/ita_estimation/mst_lookup.py','src/ita_estimation/threshold_calibration.py',
        'outputs/stellenbosch_faceocc_appearance_v1/sha256.json','outputs/stellenbosch_support_lighting_v1/sha256.json']]
    bindings={str(p):sha(p) for p in sources+preserved}
    rows=[]
    for s,score in enumerate(['1.2','2.8','4.1','6.3','8.0','9.7']):
        for c in range(3):
            rows.append(dict(case_id=f'generated_{s}_{c}',subject_id=f'generated_subject_{s}',condition=f'generated_condition_{c}',
                source_mst_exact_decimal=score,measurement_contract_sha256='a'*64,calibration_admitted=True,status='available',
                features=dict(zip(FEATURES,[float(50-8*s+4*c),float(70-6*s+3*c),float(3+s-c),float(10+2*c)]))))
    initial=json.dumps(rows,sort_keys=True);result=evaluate_subject_held(rows)
    # Exact replay from persisted/reloaded fixture representation, not real samples.
    replay=evaluate_subject_held(json.loads(initial));assert result==replay
    assert json.dumps(rows,sort_keys=True)==initial
    indexed={r['case_id']:r for r in rows};predictions={r['case_id']:r for r in result['records']};checks=0
    for fold in result['folds']:
        assert fold['held_subject'] not in fold['training_subjects']
        for case in fold['evaluation_cases']:
            for method,model in fold['models'].items():
                assert predict(model,indexed[case]['features'])==predictions[case]['predictions'][method];checks+=1
            assert predictions[case]['predictions']['subject_median']['score']==fold['median_baseline']
    for method in METHODS:assert result['metrics'][method]['attempts']==18 and result['metrics'][method]['available_predictions']==18
    assert all(sha(Path(p))==h for p,h in bindings.items())
    summary=dict(fixture_only=True,fictional_subjects=6,generated_rows=18,
        mapping_ridge_fits_first_run=result['mapping_ridge_fits'],mapping_ridge_fits_exact_repeat=replay['mapping_ridge_fits'],
        saved_linear_prediction_replays=checks,median_prediction_checks=18,
        real_rows_loaded=0,real_calibration_fits=0,correction_tree_fits=0,integer_category_exports=0,admissions=0,
        old_lookup_calibrator_and_parent_manifest_bytes_unchanged=True,scientific_accuracy_claim=False)
    OUT.mkdir()
    for name,value in [('generated_rows.json',rows),('results.json',result),('verification.json',summary),('input_sha256.json',bindings)]:
        (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
