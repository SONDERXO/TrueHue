"""Eleven fixed gamma fits; every other head and model stays frozen."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.gamma_scene_chroma_restriction import fit_restricted_gamma
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'outputs/gamma_scene_chroma_models_v1'
def main():
    if OUT.exists():raise FileExistsError(OUT)
    S=ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json';M=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json';T=ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json';rows={r['case_id']:r for r in read(T)};old=read(S);full=read(M)
    paths=[S,M,T,Path(__file__),ROOT/'src/model_training/gamma_scene_chroma_restriction.py',ROOT/'docs/gamma-scene-chroma-restriction-protocol-2026-11-07.md',ROOT/'src/model_training/development_build.py']
    bindings={str(p):sha(p) for p in paths};folds=[]
    for fold in old['folds']:
        model=fit_restricted_gamma(fold['model'],fold['training_features'],[rows[c]['target'] for c in fold['training_cases']]);folds.append(dict(fold,model=model))
    candidate=fit_restricted_gamma(full['split'],full['training_features'],[rows[c]['target'] for c in full['training_cases']])
    result=dict(folds=folds,full_model=candidate,full_training_cases=full['training_cases'],full_training_features=full['training_features'],input_sha256=bindings,new_gamma_fits=11,other_fits=0,production_adopted=False,admissions=0)
    OUT.mkdir();(OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');assert all(sha(Path(p))==h for p,h in bindings.items());print('Saved10fold gamma fits +1full-training gamma fit; gains unchanged.')
if __name__=='__main__':main()
