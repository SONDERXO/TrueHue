"""Saved action-cost decomposition; retrospective best action is diagnostic only."""
import json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/correction_action_cost_audit_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if OUT.exists():raise FileExistsError(OUT)
    S=ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json';B=ROOT/'outputs/split_benefit_gate_v1/results_PRIVATE.json';split=read(S);matched={r['case_id']:r for r in read(B)['records']};records=[]
    for r in split['records']:
        if 'paths' not in r:continue
        inp=r['input_metrics']['rgb8_mae_codes'];ungated=r['paths']['split_ungated']['metrics']['rgb8_mae_codes'];gain=inp-ungated
        for method,output in [('frozen_joint_gate',r['paths']['split_gated']['metrics']['rgb8_mae_codes']),('matched_binary_gate',matched[r['case_id']]['metrics']['rgb8_mae_codes'])]:
            apply=(r['gate'] is not None and r['gate']['apply_correction']) if method=='frozen_joint_gate' else (matched[r['case_id']]['gate'] is not None and matched[r['case_id']]['gate']['apply_correction'])
            records.append(dict(case_id=r['case_id'],subject_id=r['subject_id'],layer=r['layer'],method=method,input_mae=inp,ungated_mae=ungated,signed_gain=gain,apply=apply,output_mae=output,harmful_action_cost=max(-gain,0.) if apply else 0.,missed_benefit=max(gain,0.) if not apply else 0.,regret=output-min(inp,ungated)))
    summary={}
    for method in ['frozen_joint_gate','matched_binary_gate']:
        summary[method]={}
        for layer in ['clean','core','composite_stress_design']:
            rr=[r for r in records if r['method']==method and r['layer']==layer]
            for r in rr:assert abs(r['regret']-r['harmful_action_cost']-r['missed_benefit'])<1e-10
            summary[method][layer]=dict(scored=len(rr),harmful_actions=sum(r['harmful_action_cost']>0 for r in rr),missed_useful=sum(r['missed_benefit']>0 for r in rr),mean_harm_cost=float(np.mean([r['harmful_action_cost'] for r in rr])),mean_missed_benefit=float(np.mean([r['missed_benefit'] for r in rr])),mean_regret=float(np.mean([r['regret'] for r in rr])))
    OUT.mkdir();(OUT/'audit_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records,input_sha256={str(p):sha(p) for p in [S,B,Path(__file__)]},new_fits=0),indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
