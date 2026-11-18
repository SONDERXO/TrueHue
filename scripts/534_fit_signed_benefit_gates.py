"""Fixed signed-benefit fits on saved nested labels; no photographic inference."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.signed_benefit_gate import fit_signed_benefit
from src.model_training.correction_gate_candidate import fit_gate
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'outputs/signed_benefit_gate_models_v1'
def main():
    if OUT.exists():raise FileExistsError(OUT)
    S=ROOT/'outputs/split_benefit_gate_v1/results_PRIVATE.json';F=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json';P=ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json';T=ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json';old=read(S);full=read(F);pred={r['case_id']:r for r in read(P)['records']};rows={r['case_id']:r for r in read(T)}
    paths=[S,F,P,T,Path(__file__),ROOT/'src/model_training/signed_benefit_gate.py',ROOT/'src/model_training/correction_gate_candidate.py',ROOT/'docs/signed-benefit-gate-protocol-2026-11-07.md',ROOT/'outputs/correction_action_cost_audit_v1/audit_PRIVATE.json']
    bindings={str(p):sha(p) for p in paths};folds=[]
    for f in old['folds']:
        trace=f['training_trace'];x=[t['features'] for t in trace];gain=[t['input_mae']-t['inner_predicted_mae'] for t in trace];keys=[t['subject_id'] for t in trace];assert all(k!=f['held_key'] for k in keys)
        model=fit_signed_benefit(x,gain,keys);np.testing.assert_allclose(model['mean'],f['model']['mean'],rtol=0,atol=1e-12);assert model['weights']==f['model']['weights']
        folds.append(dict(held_key=f['held_key'],model=model,held_cases=f['held_cases'],training_cases=[t['case_id'] for t in trace],training_signed_benefits=gain))
    cases=full['gate_cases'];x=full['gate_features'];keys=[rows[c]['subject_id'] for c in cases];gain=[]
    for cid,vec in zip(cases,x):
        p=pred[cid];assert vec==p['features'];gain.append(p['input_metrics']['rgb8_mae_codes']-p['paths']['split_ungated']['metrics']['rgb8_mae_codes'])
    assert len(cases)==397
    signed=fit_signed_benefit(x,gain,keys);binary,_=fit_gate(x,[int(g>0) for g in gain],keys);assert signed['weights']==binary['weights'];np.testing.assert_allclose(signed['mean'],binary['mean'],atol=1e-12,rtol=0)
    OUT.mkdir();v=dict(folds=folds,full_signed=signed,full_matched_binary=binary,full_training_cases=cases,full_training_signed_benefits=gain,input_sha256=bindings,new_signed_fits=11,new_binary_fits=1,other_photographic_fits=0,production_adopted=False,admissions=0)
    (OUT/'models_PRIVATE.json').write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8');assert all(sha(Path(p))==h for p,h in bindings.items());print('Saved10nested signed gates +1full signed gate +1matched full binary comparator; no other fits.')
if __name__=='__main__':main()
