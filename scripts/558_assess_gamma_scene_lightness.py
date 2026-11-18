"""Saved-result action ledger and aggregate checks; no fits or new renders."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/gamma_scene_lightness_comparison_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    data=read(OUT/'results_PRIVATE.json');records=data['records'];ledgers={}
    for suite,layers in data['summary'].items():
        ledgers[suite]={}
        for layer,summary in layers.items():
            rr=[r for r in records if r['suite']==suite and r['layer']==layer]
            scored=[r for r in rr if r['reference_available']];stages=Counter()
            for r in scored:
                p=r['policy']
                stage=('missing_features' if p is None else 'outside_leaf_ranges' if not p['supported']
                    else 'neutral_supported_controls' if p['parameters']==[1.,1.,1.]
                    else 'nonneutral_gate_off' if not r['gate']['apply_correction'] else 'nonneutral_gate_on')
                stages[stage]+=1
            assert sum(stages.values())==len(scored)==summary['methods']['input']['reference_scored']
            previous_benefits=[r for r in scored if r['paths']['previous_policy_gated']['reference_metrics']['rgb8_mae_codes']<r['input_reference_metrics']['rgb8_mae_codes']]
            lost=[r for r in previous_benefits if r['paths']['policy_gated']['changed_channels']==0]
            ledgers[suite][layer]=dict(reference_scored=len(scored),reference_scored_stages=dict(stages),
                previous_policy_beneficial_actions=len(previous_benefits),previous_policy_beneficial_actions_now_unchanged=len(lost))
            assert summary['support_abstentions']==sum(r['policy'] is not None and not r['policy']['supported'] for r in rr)
            for name,m in summary['methods'].items():
                values=[r for r in rr if r['paths'].get(name,{}).get('reference_metrics') is not None]
                assert m['reference_harms']==sum(r['paths'][name]['reference_metrics']['rgb8_mae_codes']>r['input_reference_metrics']['rgb8_mae_codes'] for r in values)
                for region in ('reference_metrics','scene_metrics'):
                    eligible=[r for r in rr if r['paths'].get(name,{}).get(region) is not None]
                    for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
                        keys={r['subject_id'] for r in eligible}
                        mean=float(np.mean([np.mean([r['paths'][name][region][metric] for r in eligible if r['subject_id']==k]) for k in keys])) if keys else None
                        actual=m['equal_key_'+region+'_'+metric]
                        assert actual is None if mean is None else abs(mean-actual)<1e-12
    native_duplicates=0
    for r in records:
        if r['suite']=='fallback_native224' and r['recipe']=='clean' and r['reference_available']:
            for suite in ('borrowed_native224','input_native224'):
                other=next(x for x in records if x['suite']==suite and x['case_id']==r['case_id'])
                for name in ('policy_ungated','policy_gated'):assert Path(r['output_paths'][name]).read_bytes()==Path(other['output_paths'][name]).read_bytes()
            native_duplicates+=1
    models=read(ROOT/'outputs/gamma_scene_lightness_models_v1/models_PRIVATE.json')
    table={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')}
    tree=models['full_model']['heads']['gamma']['tree'];portable=PortableTree(tree);leaves={}
    for cid,x in zip(models['full_training_cases'],models['full_training_features']):leaves.setdefault(portable.leaf_id(x),[]).append(cid)
    leaf_summary={str(leaf):dict(rows=len(cases),clean_rows=sum(table[c]['case']['id']=='clean' for c in cases),raw_gamma=tree['nodes'][leaf]['values'][0],recipes=dict(Counter(table[c]['case']['id'] for c in cases))) for leaf,cases in leaves.items()}
    focal=[r for r in records if (r['suite'],r['case_id']) in [('fallback_native224','eval_02__clean'),('fold_working256','case_28__clean'),('fallback_native224','eval_22__colour_warm')]]
    result=dict(action_ledgers=ledgers,full_gamma_leaf_summary=leaf_summary,focal_records=focal,
        aggregate_checks_passed=True,native_clean_duplicate_checks=native_duplicates,
        assessed_result_sha256=sha(OUT/'results_PRIVATE.json'),assessor_sha256=sha(Path(__file__)),new_fits=0,new_correction_renders=0)
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    for suite in ('fold_working256','fallback_native224'):
        print(suite,json.dumps(ledgers[suite],indent=2))
    print('Full gamma leaves:',json.dumps(leaf_summary,indent=2))

if __name__=='__main__':main()
