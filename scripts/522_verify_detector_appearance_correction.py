"""No-fit audit of mixed cached/recovered mask paths and corrected outputs."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/516_verify_input_derived_correction.py').read_text()
source=source.replace('outputs/input_derived_mask_check_v1','outputs/detector_appearance_merged_v1').replace('outputs/input_derived_correction_v1','outputs/detector_appearance_correction_v1').replace('outputs/input_derived_assessment_v1','outputs/detector_appearance_assessment_v1')
source=source.replace('P/cid',"Path(s['artifact_root'])")
source=source.replace("if r['recipe']=='clean':","if r['recipe']=='clean' and not s['detector_fallback_target']:")
exec(compile(source,str(ROOT/'scripts/516_verify_input_derived_correction.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
