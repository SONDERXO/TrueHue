"""Independent exhaustive fitting verification with facial root eligibility."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    parent=read(ROOT/'outputs/image_loss_action_tree_models_v1/models_PRIVATE.json')
    revised=read(ROOT/'outputs/face_first_action_tree_models_v1/models_PRIVATE.json')
    for old,new in zip(parent['folds'],revised['folds']):
        assert old['held_key']==new['held_key'] and old['training_cases']==new['training_cases'] and old['training_features']==new['training_features']
        for k in ('costs','clean','actions','action_recipes'):assert old['model'][k]==new['model'][k]
    for k in ('costs','clean','actions','action_recipes'):assert parent['full_model'][k]==revised['full_model'][k]
    source=(ROOT/'scripts/561_verify_action_tree_training.py').read_text(encoding='utf-8')
    assert source.count("OUT=ROOT/'outputs/image_loss_action_tree_models_v1'")==1
    source=source.replace("OUT=ROOT/'outputs/image_loss_action_tree_models_v1'", "OUT=ROOT/'outputs/face_first_action_tree_models_v1'")
    assert source.count('for f in range(x.shape[1]):')==1
    source=source.replace('for f in range(x.shape[1]):', "for f in range(x.shape[1]):\n                    if depth==0 and tree['feature_names'][f] not in ('input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees','input_mst_score'):continue")
    exec(compile(source,str(ROOT/'scripts/561_verify_action_tree_training.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
    out=ROOT/'outputs/face_first_action_tree_models_v1/verification_PRIVATE.json';v=read(out)
    v.update(parent_actions_and_costs_unchanged=True,training_verifier_source_sha256=sha(ROOT/'scripts/561_verify_action_tree_training.py'))
    out.write_text(json.dumps(v,indent=2),encoding='utf-8')

if __name__=='__main__':main()
