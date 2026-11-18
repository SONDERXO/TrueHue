"""Exhaustive saved-outcome taxonomy; no causal mask attribution or new fits."""
from pathlib import Path
from collections import Counter
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/remaining_correction_failure_audit_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve completed audit')
    bound={}
    def read(p):
        p=ROOT/p;b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
    d=read('outputs/facial_veto_exception_comparison_v1/results_PRIVATE.json')
    assert read('outputs/facial_veto_exception_comparison_v1/verification_PRIVATE.json')['passed']
    pre={r['case_id']:r for r in read('outputs/reserved_clean_veto_pre_comparison_v1/results_PRIVATE.json')['records']}
    model=read('outputs/facial_veto_exception_models_v1/models_PRIVATE.json');pred={p['case_id']:p for p in model['predictions']}
    prep={r['case_id']:r for r in read('outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    fits={f['held_key']:f for f in model['folds']+[model['full']]};records=[]
    for r in d['records']:
        cid=r['case_id'];p=pred[cid];q=prep[cid];ready=r['mask_status']=='available';scored=r['reference_available']
        key=p['subject_id'] if p['cohort']=='development' else 'full';leaf=None;veto=False
        if p['features'] is not None:
            import struct
            x=[struct.unpack('f',struct.pack('f',v))[0] for v in p['features']];tree=fits[key]['model']['tree'];leaf=0
            while tree['nodes'][leaf]['kind']=='split':
                n=tree['nodes'][leaf];leaf=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
            veto=str(leaf) in fits[key]['vetoed_leaves']
        metrics={}
        for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
            if not scored:metrics[metric]=dict(category='no_reference_region');continue
            inp=r['input_region_metrics'][metric];current=r['candidate']['region_metrics'][metric]
            alternatives={'aligned_parent':r['parent']['region_metrics'][metric],'reserved_pre_veto':pre[cid]['candidate']['region_metrics'][metric]}
            proven={k:v for k,v in alternatives.items() if v<inp}
            if not ready:category='measurement_failed_no_op'
            elif current>inp:category='harmful_edit'
            elif current<inp:category='beneficial_edit'
            elif r['layer']=='clean':category='clean_preserved'
            elif proven:category='no_gain_but_saved_alternative_helped'
            else:category='no_gain_no_demonstrated_saved_alternative'
            metrics[metric]=dict(category=category,input_error=inp,current_error=current,saved_alternative_errors=alternatives,
                useful_saved_alternatives=sorted(proven),best_saved_error=min([current]+list(alternatives.values())),
                candidate_excess_over_best_saved=current-min([current]+list(alternatives.values())))
        records.append(dict(case_id=cid,source_case=q['source_case'],publisher_group=r['subject_id'],cohort=r['cohort'],layer=r['layer'],recipe=r['recipe'],
            mask_status=r['mask_status'],failure_stage=q.get('stage'),failure_reason=q.get('reason'),reference_available=scored,
            changed_channels=r['candidate']['changed_channels'],identity_controls=p['parameters']==[1.,1.,1.],fit_key=key,leaf=leaf,explicitly_vetoed_leaf=veto,metrics=metrics))
    summaries={}
    for co in ('development','later'):
        for layer in ('clean','core','composite_stress_design'):
            rr=[r for r in records if r['cohort']==co and r['layer']==layer]
            item=dict(attempts=len(rr),available=sum(r['mask_status']=='available' for r in rr),scored=sum(r['reference_available'] for r in rr))
            for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
                counts=Counter(r['metrics'][metric]['category'] for r in rr)
                actionable=[r for r in rr if r['metrics'][metric]['category']=='no_gain_but_saved_alternative_helped']
                item[metric]=dict(counts=dict(counts),missed_useful_by_recipe=dict(Counter(r['recipe'] for r in actionable)),missed_useful_in_veto_leaf=sum(r['explicitly_vetoed_leaf'] for r in actionable))
            summaries[co+'_'+layer]=item
    assert len(records)==756
    for p,h in bound.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    bound[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    OUT.mkdir();result=dict(summary=summaries,records=records,input_sha256=bound,new_fits=0,new_inference=0,new_renders=0,holdout_image_reads=0,
        limitation='Saved alternatives use identical existing alpha/scoring support. They demonstrate a decision opportunity, not a deployable selector. No mask truth or causal residual-error partition is available. No useful saved alternative does not prove no useful action exists.')
    (OUT/'audit_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(summaries,indent=2))
if __name__=='__main__':main()
