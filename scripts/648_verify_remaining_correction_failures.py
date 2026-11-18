"""Independently reconcile taxonomy against frozen metric records and failures."""
from pathlib import Path
import json,hashlib
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/remaining_correction_failure_audit_v1'
def main():
    read=lambda p:json.loads(Path(p).read_text())
    d=read(OUT/'audit_PRIVATE.json');e=read(ROOT/'outputs/facial_veto_exception_comparison_v1/results_PRIVATE.json');pre={r['case_id']:r for r in read(ROOT/'outputs/reserved_clean_veto_pre_comparison_v1/results_PRIVATE.json')['records']}
    records={r['case_id']:r for r in d['records']};assert len(records)==len(e['records'])==756
    for r in e['records']:
        a=records[r['case_id']];assert a['mask_status']==r['mask_status'] and a['reference_available']==r['reference_available']
        for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
            x=a['metrics'][metric]
            if not r['reference_available']:assert x['category']=='no_reference_region';continue
            i=r['input_region_metrics'][metric];c=r['candidate']['region_metrics'][metric];p=r['parent']['region_metrics'][metric];b=pre[r['case_id']]['candidate']['region_metrics'][metric]
            useful=[k for k,v in [('aligned_parent',p),('reserved_pre_veto',b)] if v<i]
            assert x['useful_saved_alternatives']==sorted(useful) and x['input_error']==i and x['current_error']==c
            expected=('measurement_failed_no_op' if r['mask_status']!='available' else 'harmful_edit' if c>i else 'beneficial_edit' if c<i else 'clean_preserved' if r['layer']=='clean' else 'no_gain_but_saved_alternative_helped' if useful else 'no_gain_no_demonstrated_saved_alternative')
            assert x['category']==expected
            if expected=='measurement_failed_no_op':assert c==i and r['candidate']['changed_channels']==0
    for co in ('development','later'):
        for layer in ('clean','core','composite_stress_design'):
            rr=[r for r in d['records'] if r['cohort']==co and r['layer']==layer];s=d['summary'][co+'_'+layer]
            assert s['attempts']==len(rr)
            for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):assert s[metric]['counts']==dict(Counter(r['metrics'][metric]['category'] for r in rr))
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,attempts=756,metric_classification_checks=1512,new_fits=0,new_inference=0,new_renders=0,holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
