"""Assemble fixed review sheets and descriptive availability/support diagnostics."""
import json,hashlib
from pathlib import Path
from collections import Counter
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'outputs/input_derived_mask_check_v1';E=ROOT/'outputs/input_derived_correction_v1';O=ROOT/'outputs/input_derived_visuals_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if O.exists():raise FileExistsError(O)
    rows=read(E/'results_PRIVATE.json')['records'];masks=read(P/'results_PRIVATE.json')['records'];O.mkdir()
    for i in range(1,25):
        sid=f'eval_{i:02d}';boards=[cv2.imread(str(E/(sid+'__'+recipe)/'board.png')) for recipe in ['clean','combined_cool_under','stress_combined_over']];assert all(b is not None for b in boards)
        assert cv2.imwrite(str(O/(sid+'.png')),np.vstack(boards))
    diagnostic=dict(failure_reasons=dict(Counter(r.get('reason') or r.get('measurement_report',{}).get('reason') or r['status'] for r in masks if r['status']!='success')),layers={})
    for layer in ['clean','core','composite_stress_design']:
        rr=[r for r in rows if r['layer']==layer];paired=[r for r in rr if r['reference_available']]
        both=[r for r in paired if r['mask_status']=='success'];ious=[r['support_intersection']/r['support_union'] for r in both if r['support_union']]
        diagnostic['layers'][layer]=dict(attempts=len(rr),mask_success=sum(r['mask_status']=='success' for r in rr),gated_actions=sum(r['gate'] is not None and r['gate']['apply_correction'] for r in rr),
            mask_failure_fallbacks=sum(r['mask_status']!='success' for r in rr),clipped_mst=sum(r['mst_prediction'] is not None and r['mst_prediction']['raw']!=r['mst_prediction']['score'] for r in rr),
            paired_successful_masks=len(both),median_native_iou_on_paired_success=float(np.median(ious)) if ious else None,
            candidate_changed_outside_reference_cases=sum(r['paths']['input_gated']['changed_pixels_outside_reference']>0 for r in paired),
            candidate_changed_outside_reference_pixels=sum(r['paths']['input_gated']['changed_pixels_outside_reference'] for r in paired),
            useful_ungated_suppressed=sum(r['gate'] is not None and not r['gate']['apply_correction'] and r['paths']['input_ungated']['reference_metrics']['rgb8_mae_codes']<r['paths']['unchanged']['reference_metrics']['rgb8_mae_codes'] for r in paired))
    (O/'diagnostics_PRIVATE.json').write_text(json.dumps(diagnostic,indent=2),encoding='utf-8');(O/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in O.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(diagnostic,indent=2))
if __name__=='__main__':main()
