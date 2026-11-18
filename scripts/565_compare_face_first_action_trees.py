"""Reuse joint-tree evaluation for two frozen nonduplicate principal contexts."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/560_compare_image_loss_action_trees.py').read_text(encoding='utf-8')

def change(old,new):
    global source
    assert old in source,old
    source=source.replace(old,new)

change('outputs/image_loss_action_tree_models_v1','outputs/face_first_action_tree_models_v1')
change('outputs/image_loss_action_tree_comparison_v1','outputs/face_first_action_tree_comparison_v1')
change("PREV=ROOT/'outputs/joint_neutral_support_v1/results_PRIVATE.json'", "PREV=ROOT/'outputs/image_loss_action_tree_comparison_v1/results_PRIVATE.json'")
change("previous_rows[c['suite'],c['case_id']]['paths']['policy_gated']", "previous_rows[c['suite'],c['case_id']]['paths']['action_tree']")
change("previous_rows[c['suite'],c['case_id']]['output_paths']['policy_gated']", "previous_rows[c['suite'],c['case_id']]['output_paths']['action_tree']")
change('previous_policy_gated','parent_action_tree')
change('docs/image-loss-action-tree-protocol-2026-11-07.md','docs/face-first-action-tree-protocol-2026-11-07.md')
change("ROOT/'src/model_training/image_loss_action_tree.py',Path(__file__)", "ROOT/'src/model_training/image_loss_action_tree.py',ROOT/'src/model_training/face_first_action_tree.py',ROOT/'scripts/560_compare_image_loss_action_trees.py',Path(__file__)")
change('exec(compile(source',
    'replace("context=read(C)[\'records\']", "context=[r for r in read(C)[\'records\'] if r[\'suite\'] in (\'fold_working256\',\'fallback_native224\')]")\n'
    'replace("assert len(records)==1428", "assert len(records)==756")\n'
    'exec(compile(source')
exec(compile(source,str(ROOT/'scripts/560_compare_image_loss_action_trees.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
