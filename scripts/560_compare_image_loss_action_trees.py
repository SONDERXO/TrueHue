"""Fixed saved-case evaluation of one joint tree; no external gate or guard."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/551_compare_joint_neutral_support.py').read_text(encoding='utf-8')

def replace(old,new):
    global source
    assert old in source,old
    source=source.replace(old,new)

replace('outputs/joint_neutral_support_v1','outputs/image_loss_action_tree_comparison_v1')
replace('from src.model_training.joint_neutral_support import prepare_policy,predict_policy',
    "from src.model_training.portable_tree import PortableTree\n"
    "def prepare_policy(model,features,clean):return dict(joint_action_tree=True)\n"
    "def predict_policy(model,policy,features):\n"
    "    tree=PortableTree(model['tree']);leaf=tree.leaf_id(features)\n"
    "    action=next(t['action'] for t in model['trace'] if t['node']==leaf)\n"
    "    return dict(parameters=tree.predict_one(features),supported=True,leaf=leaf,action=action)")
replace("    folds=read(S)['folds'];full=read(F);table=", "    M=ROOT/'outputs/image_loss_action_tree_models_v1/models_PRIVATE.json'\n"
    "    PREV=ROOT/'outputs/joint_neutral_support_v1/results_PRIVATE.json'\n"
    "    revised=read(M);assert all(sha(p)==h for p,h in revised['input_sha256'].items())\n"
    "    previous=read(PREV);previous_rows={(r['suite'],r['case_id']):r for r in previous['records']}\n"
    "    folds=revised['folds'];full=read(F);full['split']=revised['full_model'];table=")
replace("for p in [S,F,T,C,Path(__file__),", "for p in [S,F,T,C,M,PREV,ROOT/'scripts/551_compare_joint_neutral_support.py',ROOT/'src/model_training/image_loss_action_tree.py',Path(__file__),")
replace('docs/joint-neutral-support-protocol-2026-11-07.md','docs/image-loss-action-tree-protocol-2026-11-07.md')
replace("('input','retained','policy_ungated','policy_gated')", "('input','retained','previous_policy_gated','action_tree')")
replace('for x,flag in zip(features,flags):','for row_index,(x,flag) in enumerate(zip(features,flags)):')
replace("assert d['supported'] and d['parameters']==[1.,1.,1.]", "assert model['costs'][row_index][d['action']]==0")
replace("if vector is not None:assert predict_split(payloads[key],vector)==c['paths']['old_ungated']['parameters']", 'if vector is not None:assert len(d["parameters"])==3')
replace("        r['paths']['retained']=c['paths']['old_gated']", "        r['paths']['retained']=c['paths']['old_gated']\n"
    "        r['paths']['previous_policy_gated']=previous_rows[c['suite'],c['case_id']]['paths']['policy_gated']\n"
    "        if previous_rows[c['suite'],c['case_id']]['output_paths']:bind(previous_rows[c['suite'],c['case_id']]['output_paths']['policy_gated'])")
replace("[('policy_ungated',True),('policy_gated',bool(c['gate'] and c['gate']['apply_correction']))]", "[('action_tree',True)]")
replace("r['paths']['policy_gated']['changed_channels']", "r['paths']['action_tree']['changed_channels']")
replace("panels=[reference,image,rgb(c['old_output_paths']['old_gated']),images['policy_ungated'],images['policy_gated']]", "panels=[reference,image,rgb(previous_rows[c['suite'],c['case_id']]['output_paths']['policy_gated']),images['action_tree']]")
replace("image.shape[1]*5", "image.shape[1]*4")
replace('ref | input | retained | policy no gate | policy gated','ref | input | previous policy | joint action tree')
replace('new_fits=0,new_mask_forwards=0','new_fits=0,upstream_new_action_tree_fits=11,new_mask_forwards=0')
replace('Reference | input | retained | joint policy without gate | joint policy with retained gate','Reference | input | previous joint policy | learned joint action tree')
exec(compile(source,str(ROOT/'scripts/551_compare_joint_neutral_support.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
