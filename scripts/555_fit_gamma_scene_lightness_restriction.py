"""Exactly eleven fixed gamma fits; preserve saved gains, rows and features."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.gamma_scene_lightness_restriction import fit_restricted_gamma
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OUT=ROOT/'outputs/gamma_scene_lightness_models_v1'

def main():
    if OUT.exists():raise FileExistsError(OUT)
    S=ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json'
    F=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json'
    T=ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json'
    split=read(S);full=read(F);rows={r['case_id']:r for r in read(T)}
    paths=[S,F,T,Path(__file__),ROOT/'src/model_training/gamma_scene_lightness_restriction.py',
        ROOT/'src/model_training/development_build.py',ROOT/'src/model_training/portable_tree.py',
        ROOT/'docs/gamma-scene-lightness-protocol-2026-11-07.md']
    bindings={str(p):sha(p) for p in paths};folds=[]
    for f in split['folds']:
        assert all(rows[c]['subject_id']!=f['held_key'] for c in f['training_cases'])
        model=fit_restricted_gamma(f['model'],f['training_features'],[rows[c]['target'] for c in f['training_cases']])
        folds.append(dict(f,model=model))
    candidate=fit_restricted_gamma(full['split'],full['training_features'],[rows[c]['target'] for c in full['training_cases']])
    result=dict(folds=folds,full_model=candidate,full_training_cases=full['training_cases'],
        full_training_features=full['training_features'],input_sha256=bindings,new_gamma_fits=11,
        other_research_fits=0,production_adopted=False,admissions=0)
    OUT.mkdir();(OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    assert all(sha(p)==h for p,h in bindings.items())
    print('Saved exactly 11 gamma fits; original gain heads unchanged.')

if __name__=='__main__':main()
