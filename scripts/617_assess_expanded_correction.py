"""Exact predeclared acceptance and explicitly selected trade-off diagnostics."""
from pathlib import Path
from collections import Counter
import json,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/expanded_correction_comparison_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'results_PRIVATE.json');assert read(OUT/'verification_PRIVATE.json')['passed']
    m=read(ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json')
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    checks={};baseline={};scene_harms={};selected=[]
    for cohort,layers in d['summary'].items():
        checks[cohort+'_zero_clean']=layers['clean']['methods']['candidate']['changed']==0
        for layer in ('core','composite_stress_design'):
            methods=layers[layer]['methods']
            for metric in ('region_MAE','region_CIEDE2000','harms','DE_harms'):checks[cohort+'_'+layer+'_'+metric]=methods['candidate'][metric]<=methods['parent'][metric]
            for metric in ('benefits','DE_benefits'):checks[cohort+'_'+layer+'_'+metric]=methods['candidate'][metric]>=methods['parent'][metric]
        for layer in layers:
            rows=[r for r in d['records'] if r['cohort']==cohort and r['layer']==layer];rr=[r for r in rows if r['reference_available']]
            baseline[cohort+'_'+layer]=dict(region_scored=len(rr),input_RGB=float(np.mean([r['input_region_metrics']['rgb8_mae_codes'] for r in rr])),input_DE=float(np.mean([r['input_region_metrics']['relative_deltaE00_mean'] for r in rr])))
            scene_harms[cohort+'_'+layer]={method:sum(r[method]['scene_metrics']['rgb8_mae_codes']>prep[r['case_id']]['input_scene_metrics']['rgb8_mae_codes'] for r in rows) for method in ('parent','candidate')}
        rr=[r for r in d['records'] if r['cohort']==cohort and r['layer']=='core' and r['reference_available']]
        r=max(rr,key=lambda r:r['candidate']['region_metrics']['rgb8_mae_codes']-r['parent']['region_metrics']['rgb8_mae_codes'])
        selected.append(dict(case_id=r['case_id'],selection='Largest loss versus parent regional RGB MAE in '+cohort+' core'))
    stress=[r for r in d['records'] if r['layer']=='composite_stress_design' and r['reference_available']]
    r=max(stress,key=lambda r:r['candidate']['region_metrics']['rgb8_mae_codes']-r['input_region_metrics']['rgb8_mae_codes'])
    selected.append(dict(case_id=r['case_id'],selection='Largest remaining regional RGB harm versus input, stress'))
    candidates=[r for r in d['records'] if r['layer']=='core' and r['reference_available'] and r['candidate']['region_metrics']['rgb8_mae_codes']<r['input_region_metrics']['rgb8_mae_codes']]
    r=max(candidates,key=lambda r:r['parent']['region_metrics']['rgb8_mae_codes']-r['candidate']['region_metrics']['rgb8_mae_codes'])
    selected.append(dict(case_id=r['case_id'],selection='Largest gain versus parent among genuinely beneficial core candidate actions'))
    index={r['case_id']:r for r in d['records']}
    for i,item in enumerate(selected):
        r=index[item['case_id']];p=prep[r['case_id']];panels=[cv2.imread(p['reference_path']),cv2.imread(p['scene_path']),cv2.imread(r['parent_output_path']),cv2.imread(r['output_path'])]
        title=np.full((28,896,3),255,np.uint8);cv2.putText(title,'OUTCOME SELECTED '+r['case_id']+' ref|input|parent|expanded',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
        path=OUT/f'diagnostic_{i:02d}_OUTCOME_SELECTED.png';assert cv2.imwrite(str(path),np.vstack([title,np.hstack(panels)]));item['path']=str(path)
    splitcounts=Counter()
    for fit in m['folds']+[m['full']]:
        for n in fit['model']['tree']['nodes']:
            if n['kind']=='split':splitcounts[m['feature_names'][n['feature']]]+=1
    result=dict(acceptance=checks,all_requirements_pass=all(checks.values()),input_baselines=baseline,scene_RGB_harms=scene_harms,
        split_counts=dict(splitcounts),diagnostics=selected,changed_clean=[r['case_id'] for r in d['records'] if r['recipe']=='clean' and r['candidate']['changed_channels']>0],
        disposition='Rejected under fixed joint requirements' if not all(checks.values()) else 'Passes fixed development requirements; not final validation',
        holdout_opened=False,production_adopted=False,new_fits=0)
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    html='<!doctype html><meta charset="utf-8"><title>Private expanded correction comparison</title><h1>Private fixed comparison</h1><p>Reference, input, aligned parent, expanded fit. All fixed boards; no holdout.</p>'
    html+=''.join('<img style="max-width:100%" src="'+Path(p).relative_to(OUT).as_posix()+'">' for p in d['boards'])
    html+='<h2>Outcome-selected trade-off diagnostics</h2>'+''.join('<p>'+i['selection']+'</p><img style="max-width:100%" src="'+Path(i['path']).name+'">' for i in selected)
    (OUT/'review_PRIVATE.html').write_text(html,encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
