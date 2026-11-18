"""Reuse independent pixel verifier with explicit expanded-model redirection."""
from pathlib import Path
import json,hashlib,runpy
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/expanded_correction_comparison_v1'
M=ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    legacy=ROOT/'outputs/face_local_action_models_v1/models_PRIVATE.json'
    def redirected(p):return read(M if Path(p)==legacy else p)
    ns=runpy.run_path(str(ROOT/'scripts/591_verify_face_local_outputs.py'));fn=ns['main'];fn.__globals__.update(OUT=OUT,read=redirected);fn()
    d=read(OUT/'results_PRIVATE.json');counts=0
    for cohort,layers in d['summary'].items():
        for layer,s in layers.items():
            rr=[r for r in d['records'] if r['cohort']==cohort and r['layer']==layer and r['reference_available']]
            for method in ('parent','candidate'):
                mm=s['methods'][method]
                expected=sum(r[method]['region_metrics']['relative_deltaE00_mean'] for r in rr)/len(rr)
                assert abs(expected-mm['region_CIEDE2000'])<1e-10
                assert mm['DE_harms']==sum(r[method]['region_metrics']['relative_deltaE00_mean']>r['input_region_metrics']['relative_deltaE00_mean'] for r in rr)
                assert mm['DE_benefits']==sum(r[method]['region_metrics']['relative_deltaE00_mean']<r['input_region_metrics']['relative_deltaE00_mean'] for r in rr);counts+=1
    for key,t in d['harm_benefit_transitions'].items():
        cohort,remaining=key.split('_',1)
        metric='relative_deltaE00_mean' if key.endswith('relative_deltaE00_mean') else 'rgb8_mae_codes'
        layer=remaining[:-(len(metric)+1)]
        rr=[r for r in d['records'] if r['cohort']==cohort and r['layer']==layer and r['reference_available']]
        ph={r['case_id'] for r in rr if r['parent']['region_metrics'][metric]>r['input_region_metrics'][metric]};ch={r['case_id'] for r in rr if r['candidate']['region_metrics'][metric]>r['input_region_metrics'][metric]}
        pb={r['case_id'] for r in rr if r['parent']['region_metrics'][metric]<r['input_region_metrics'][metric]};cb={r['case_id'] for r in rr if r['candidate']['region_metrics'][metric]<r['input_region_metrics'][metric]}
        assert t==dict(new_harms=sorted(ch-ph),removed_harms=sorted(ph-ch),lost_benefits=sorted(pb-cb),gained_benefits=sorted(cb-pb))
    p=OUT/'verification_PRIVATE.json';v=read(p);v.update(DE_summary_checks=counts,harm_transition_checks=len(d['harm_benefit_transitions']),wrapper_sha256=sha(Path(__file__)))
    p.write_text(json.dumps(v,indent=2),encoding='utf-8');print('PASS additional DE summaries and all harm/benefit transitions.')

if __name__=='__main__':main()
