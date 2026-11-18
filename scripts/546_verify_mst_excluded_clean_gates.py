"""Independent free-coordinate KKT and inherited no-leak/action/RGB audit."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/540_verify_clean_constrained_gates.py').read_text()
source=source.replace('outputs/clean_constrained_gate_comparison_v1','outputs/mst_excluded_clean_gate_comparison_v1')
source=source.replace('outputs/clean_constrained_gate_models_v1','outputs/mst_excluded_clean_gate_models_v1')
source=source.replace('outputs/clean_constrained_gate_assessment_v1','outputs/mst_excluded_clean_gate_assessment_v1')
# 540 builds the constrained verifier source dynamically. Project its KKT
# stationarity onto free coordinates; the excluded coordinate has a free
# equality multiplier and must be exactly zero in every exported model.
old="    gradient=(d.T@(w*(d@theta-y))+reg@theta)/w.sum();active=np.abs(scores+margin)<=1e-6;assert active.any()"
new="    assert model['fixed_zero_coefficient_indices']==[4] and theta[4]==0.\n    free=np.array([i for i in range(len(theta)) if i!=4]);gradient=((d.T@(w*(d@theta-y))+reg@theta)/w.sum())[free];c=c[:,free];active=np.abs(scores+margin)<=1e-6;assert active.any()"
assert old in source
source=source.replace(old,new)
source=source.replace('constrained_KKT_checks=11','constrained_KKT_checks=11,zero_MST_coefficient_checks=11')
exec(compile(source,str(ROOT/'scripts/540_verify_clean_constrained_gates.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
