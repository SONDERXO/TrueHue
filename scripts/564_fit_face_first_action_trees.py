"""Eleven facial-root fits using immutable parent actions and supervision costs."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.face_first_action_tree import fit_face_first_tree
OUT=ROOT/'outputs/face_first_action_tree_models_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    P=ROOT/'outputs/image_loss_action_tree_models_v1/models_PRIVATE.json';parent=read(P)
    V=ROOT/'outputs/image_loss_action_tree_models_v1/verification_PRIVATE.json';assert read(V)['passed']
    assert all(sha(p)==h for p,h in parent['input_sha256'].items())
    paths=[P,V,Path(__file__),ROOT/'src/model_training/face_first_action_tree.py',ROOT/'src/model_training/image_loss_action_tree.py',ROOT/'src/model_training/portable_tree.py',ROOT/'docs/face-first-action-tree-protocol-2026-11-07.md']
    bound=dict(parent['input_sha256']);bound.update({str(p):sha(p) for p in paths})
    OUT.mkdir();folds=[]
    items=[(f['held_key'],f['model'],f['training_cases'],f['training_features'],f['held_cases']) for f in parent['folds']]+[('full',parent['full_model'],parent['full_training_cases'],parent['full_training_features'],[])]
    for key,prior,cases,features,held in items:
        model=fit_face_first_tree(features,prior['costs'],prior['clean'],prior['actions'],prior['tree']['feature_names'],max_depth=3)
        for k in ('costs','clean','action_recipes'):model[k]=prior[k]
        record=dict(held_key=key,model=model,training_cases=cases,training_features=features,held_cases=held)
        (OUT/(key+'_PRIVATE.json')).write_text(json.dumps(record,indent=2,allow_nan=False),encoding='utf-8')
        if key=='full':full=model
        else:folds.append(record)
        print('Saved facial-root tree:',key,flush=True)
    result=dict(folds=folds,full_model=full,full_training_cases=parent['full_training_cases'],full_training_features=parent['full_training_features'],input_sha256=bound,new_action_tree_fits=11,new_cost_renders=0,other_research_fits=0,production_adopted=False,admissions=0)
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())

if __name__=='__main__':main()
