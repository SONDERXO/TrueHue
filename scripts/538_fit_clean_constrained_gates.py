"""Eleven constrained gates; reuse all unconstrained specifications and labels."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.clean_constrained_gate import fit_clean_constrained_gate
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'outputs/clean_constrained_gate_models_v1'
def main():
    if OUT.exists():raise FileExistsError(OUT)
    M=ROOT/'outputs/signed_benefit_gate_models_v1/models_PRIVATE.json';S=ROOT/'outputs/split_benefit_gate_v1/results_PRIVATE.json';T=ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json';F=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json';base=read(M);nested=read(S);table={r['case_id']:r for r in read(T)};full=read(F)
    paths=[M,S,T,F,Path(__file__),ROOT/'src/model_training/clean_constrained_gate.py',ROOT/'docs/clean-constrained-gate-protocol-2026-11-07.md'];bindings={str(p):sha(p) for p in paths};folds=[]
    OUT.mkdir();(OUT/'plan_PRIVATE.json').write_text(json.dumps(dict(input_sha256=bindings,status='frozen_before_QP_fits',planned_gate_fits=11),indent=2),encoding='utf-8')
    for old,trace in zip(base['folds'],nested['folds']):
        assert old['held_key']==trace['held_key'];ids=old['training_cases'];x=[t['features'] for t in trace['training_trace']];idx=[i for i,c in enumerate(ids) if table[c]['case']['id']=='clean'];assert all(table[c]['subject_id']!=old['held_key'] for c in ids)
        candidate=fit_clean_constrained_gate(old['model'],x,old['training_signed_benefits'],idx);folds.append(dict(old,model=candidate));(OUT/f'fold_{len(folds):02d}_PRIVATE.json').write_text(json.dumps(folds[-1],indent=2),encoding='utf-8');print('constrained fold',len(folds),candidate['solver']['iterations'],'iterations',flush=True)
    ids=base['full_training_cases'];idx=[i for i,c in enumerate(ids) if table[c]['case']['id']=='clean'];assert len(idx)==29
    candidate=fit_clean_constrained_gate(base['full_signed'],full['gate_features'],base['full_training_signed_benefits'],idx)
    value=dict(base,folds=folds,full_signed=candidate,input_sha256=bindings,new_constrained_QP_fits=11,new_signed_fits=0,new_binary_fits=0,production_adopted=False,admissions=0)
    (OUT/'models_PRIVATE.json').write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8');assert all(sha(Path(p))==h for p,h in bindings.items());print('Saved11constrained gate fits; all fitting clean scores nonpositive.')
if __name__=='__main__':main()
