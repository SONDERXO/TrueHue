"""Independent routing/RGB8/metric replay of the facial-root comparison."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/562_verify_action_tree_outputs.py').read_text(encoding='utf-8')

def change(old,new):
    global source
    assert old in source,old
    source=source.replace(old,new)

change('outputs/image_loss_action_tree_comparison_v1','outputs/face_first_action_tree_comparison_v1')
change('outputs/image_loss_action_tree_models_v1','outputs/face_first_action_tree_models_v1')
change('outputs/joint_neutral_support_v1','outputs/image_loss_action_tree_comparison_v1')
change("assert r['paths']['previous_policy_gated']==prior['paths']['policy_gated']", "assert r['paths']['parent_action_tree']==prior['paths']['action_tree']")
start=source.index('    duplicate=0\n');end=source.index('    assert all(sha(p)==h for p,h in bound.items())',start)
source=source[:start]+'    duplicate=0  # Other native mask contexts intentionally not rerun.\n'+source[end:]
exec(compile(source,str(ROOT/'scripts/562_verify_action_tree_outputs.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
