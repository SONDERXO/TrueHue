"""Coverage, mask diagnostics and explicitly selected end-to-end failures."""
from pathlib import Path
from collections import Counter
import json,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'outputs/aligned_correction_preparation_v1';OUT=ROOT/'outputs/aligned_action_tree_comparison_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    data=read(OUT/'results_PRIVATE.json');prep=read(P/'results_PRIVATE.json');rows=data['records'];masks={r['case_id']:r for r in prep['records']}
    selected=[];extra=OUT/'selected_diagnostics';extra.mkdir(exist_ok=True)
    for cohort in ('development','later'):
        for layer in ('clean','core'):
            rr=[r for r in rows if r['cohort']==cohort and r['layer']==layer and r['reference_available']]
            harmful=[r for r in rr if r['paths']['aligned_tree']['region_metrics']['rgb8_mae_codes']>r['input_region_metrics']['rgb8_mae_codes']]
            if not harmful:continue
            q=sorted(harmful,key=lambda r:(-(r['paths']['aligned_tree']['region_metrics']['rgb8_mae_codes']-r['input_region_metrics']['rgb8_mae_codes']),r['case_id']))[0]
            paths=[q['reference_path'],q['image_path'],q['output_paths']['parent_controls_new_alpha'],q['output_paths']['aligned_tree']]
            panels=[rgb(p) for p in paths];title=np.full((30,panels[0].shape[1]*4,3),255,np.uint8)
            cv2.putText(title,'OUTCOME SELECTED '+cohort+' '+q['case_id']+' ref|input|old controls new alpha|aligned',(2,19),cv2.FONT_HERSHEY_SIMPLEX,.35,(0,0,0),1)
            board=extra/(cohort+'_'+layer+'.png');assert cv2.imwrite(str(board),cv2.cvtColor(np.vstack([title,np.hstack(panels)]),cv2.COLOR_RGB2BGR))
            selected.append(dict(cohort=cohort,layer=layer,case_id=q['case_id'],excess_rgb_mae=q['paths']['aligned_tree']['region_metrics']['rgb8_mae_codes']-q['input_region_metrics']['rgb8_mae_codes'],path=str(board),source_sha256={p:sha(p) for p in paths}))
    coverage={}
    for cohort in ('development','later'):
        rr=[r for r in prep['records'] if r['cohort']==cohort]
        coverage[cohort]=dict(attempts=len(rr),failures_by_stage=dict(Counter(r['stage'] for r in rr if r['status']!='available')),
            failures_by_reason=dict(Counter(r.get('reason','unspecified') for r in rr if r['status']!='available')),
            requires_glasses_choice=sum(bool(r.get('requires_glasses_choice')) for r in rr),
            available_by_recipe={recipe:sum(r['status']=='available' for r in rr if r['recipe']==recipe) for recipe in sorted({r['recipe'] for r in rr})})
    clean=[dict(case_id=r['case_id'],cohort=r['cohort'],measurement_available=r['mask_status']=='available',prediction_available=r['paths']['aligned_tree']['prediction_available'],changed=r['paths']['aligned_tree']['changed_channels']>0,region_mae=r['paths']['aligned_tree']['region_metrics']['rgb8_mae_codes'] if r['reference_available'] else None) for r in rows if r['recipe']=='clean']
    full=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')['full'];model=full['model'];features=model['tree']['feature_names']
    split_counts=dict(Counter(features[n['feature']] for n in model['tree']['nodes'] if n['kind']=='split'))
    focal=[r for r in rows if r['case_id'] in ('case_28__clean','eval_02__clean','eval_22__colour_warm')]
    result=dict(coverage=coverage,clean_records=clean,selected_diagnostics=selected,selection='Worst positive excess native-region RGB MAE versus input per cohort and clean/core layer; outcome-selected',full_model_split_counts=split_counts,
        full_fitting_rows=len(full['training_cases']),full_fitting_clean=sum(model['clean']),focal_records=focal,result_sha256=sha(OUT/'results_PRIVATE.json'),new_fits=0)
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('Clean outcomes:',json.dumps([r for r in clean if r['changed']],indent=2));print('Clean MST MAE:',data['clean_MST_mae']);print('Full split features:',split_counts)
    print('Diagnostics:',json.dumps([{k:v for k,v in d.items() if k!='source_sha256'} for d in selected],indent=2))

if __name__=='__main__':main()
