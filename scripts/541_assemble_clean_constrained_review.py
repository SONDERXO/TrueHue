"""Fixed/outcome-labelled visual comparison; reuse prior signed outputs."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/537_assemble_signed_benefit_review.py').read_text()
source=source.replace('outputs/signed_benefit_gate_comparison_v1','outputs/clean_constrained_gate_comparison_v1').replace('outputs/signed_benefit_gate_review_v1','outputs/clean_constrained_gate_review_v1')
source=source.replace("cv2.imread(str(E/suite/cid/'matched_binary.png'))","cv2.imread(str(ROOT/'outputs/signed_benefit_gate_comparison_v1'/suite/cid/'signed.png'))")
exec(compile(source,str(ROOT/'scripts/537_assemble_signed_benefit_review.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
