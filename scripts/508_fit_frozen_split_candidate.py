"""Single frozen experimental fit; no evaluation pixels or targets."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.ita_estimation.contextual_mst_experiment import _ridge
from src.model_training.split_control_candidate import fit_split_predictors
from src.model_training.correction_gate_candidate import fit_gate
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import SCENE_FEATURES
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'outputs/frozen_split_candidate_v1'
def main():
    if OUT.exists():raise FileExistsError(OUT)
    E=ROOT/'outputs/frozen_split_subject_check_v1';assert not (E/'preparation_PRIVATE.json').exists()
    P=ROOT/'outputs/whole_scene_correction_v1';S=ROOT/'outputs/stellenbosch_new_subjects_v1'
    rows=read(P/'prepared_rows_PRIVATE.json');pred={r['case_id']:r for r in read(P/'results_PRIVATE.json')['records']}
    originals=read(S/'results_PRIVATE.json')['records'];keys={r['subject_key'] for r in originals}
    assert not keys & set(read(E/'plan_PRIVATE.json')['selected_keys_PRIVATE'])
    clean=[dict(subject_id=r['subject_key'],features=r['measurement_report']['features'],source_mst_exact_decimal=r['source_mst_exact_decimal']) for r in originals if r['status']=='success']
    ridge=_ridge(clean,('input_ita_degrees','input_mean_l_star','input_mean_a_star','input_mean_b_star'))
    train=[r for r in rows if r['target'] is not None and r['features'] is not None]
    vector=lambda r:pred[r['case_id']]['methods']['face_plus_scene']['features']
    split,_=fit_split_predictors([vector(r) for r in train],[r['target'] for r in train],CONTINUOUS_FEATURES+SCENE_FEATURES)
    gate_rows=[r for r in rows if r['features'] is not None]
    labels=[int(r['input_metrics']['rgb8_mae_codes']>pred[r['case_id']]['methods']['face_plus_scene']['metrics']['rgb8_mae_codes']) for r in gate_rows]
    gate,_=fit_gate([vector(r) for r in gate_rows],labels,[r['subject_id'] for r in gate_rows])
    assert (len(clean),len(train),len(gate_rows))==(29,357,397)
    paths=[P/'prepared_rows_PRIVATE.json',P/'results_PRIVATE.json',S/'results_PRIVATE.json',E/'plan_PRIVATE.json']
    paths+=list((ROOT/'src/model_training').glob('*candidate.py'))+[Path(__file__),ROOT/'docs/frozen-split-subject-check-protocol-2026-11-06.md']
    payload=dict(ridge=ridge,split=split,gate=gate,feature_names=list(CONTINUOUS_FEATURES+SCENE_FEATURES),training_keys=sorted(keys),
        training_cases=[r['case_id'] for r in train],training_features=[vector(r) for r in train],gate_cases=[r['case_id'] for r in gate_rows],gate_features=[vector(r) for r in gate_rows],gate_labels=labels,
        upstream_training_features='saved own-key-held MST predictions',gate_labels_provenance='saved own-key-held joint corrector benefit; transferred to split heads',
        new_fits=dict(ridge=1,head_trees=2,gate=1,target=0),production_adopted=False,calibration_admitted=False,training_admitted=False,
        input_sha256={str(p):sha(p) for p in paths})
    OUT.mkdir();(OUT/'model_PRIVATE.json').write_text(json.dumps(payload,indent=2,allow_nan=False),encoding='utf-8')
    print('Frozen one ridge, two split heads and one gate; 29/357/397 fitting rows, zero evaluation pixels.')
if __name__=='__main__':main()
