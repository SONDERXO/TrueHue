"""Assess the fixed facial-root candidate against its joint-tree parent."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/563_assess_image_loss_action_trees.py').read_text(encoding='utf-8')

def change(old,new):
    global source
    assert old in source,old
    source=source.replace(old,new)

change('outputs/image_loss_action_tree_comparison_v1','outputs/face_first_action_tree_comparison_v1')
change('outputs/image_loss_action_tree_models_v1','outputs/face_first_action_tree_models_v1')
change('outputs/joint_neutral_support_v1','outputs/image_loss_action_tree_comparison_v1')
change('previous_policy_gated','parent_action_tree')
change("p['output_paths']['policy_gated']", "p['output_paths']['action_tree']")
change('previous policy | action tree','parent joint tree | facial-root tree')
exec(compile(source,str(ROOT/'scripts/563_assess_image_loss_action_trees.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
