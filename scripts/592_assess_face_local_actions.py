"""Predeclared acceptance, fixed gallery and outcome-selected worst diagnostics."""
from pathlib import Path
from collections import Counter
import json,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/face_local_action_comparison_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'results_PRIVATE.json');assert read(OUT/'verification_PRIVATE.json')['passed']
    m=read(ROOT/'outputs/face_local_action_models_v1/models_PRIVATE.json')
    tests={};selected=[]
    for cohort,layers in d['summary'].items():
        tests[cohort+'_zero_clean']=layers['clean']['methods']['candidate']['changed']==0
        for layer in ('core','composite_stress_design'):
            for metric in ('region_MAE','harms'):
                methods=layers[layer]['methods'];tests[cohort+'_'+layer+'_'+metric]=methods['candidate'][metric]<=methods['parent'][metric]
        for layer in ('clean','core'):
            rr=[r for r in d['records'] if r['cohort']==cohort and r['layer']==layer and r['reference_available']]
            r=max(rr,key=lambda r:r['candidate']['region_metrics']['rgb8_mae_codes']-r['input_region_metrics']['rgb8_mae_codes'])
            path=OUT/(cohort+'_'+layer+'_OUTCOME_SELECTED.png')
            prep=next(p for p in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records'] if p['case_id']==r['case_id'])
            panels=[cv2.imread(prep['reference_path']),cv2.imread(prep['scene_path']),cv2.imread(r['parent_output_path']),cv2.imread(r['output_path'])]
            title=np.full((28,896,3),255,np.uint8);cv2.putText(title,'OUTCOME SELECTED '+r['case_id']+' ref|input|parent|local',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1)
            assert cv2.imwrite(str(path),np.vstack([title,np.hstack(panels)]))
            selected.append(dict(case_id=r['case_id'],path=str(path),selection='Worst candidate excess RGB MAE versus input per cohort clean/core',
                excess=r['candidate']['region_metrics']['rgb8_mae_codes']-r['input_region_metrics']['rgb8_mae_codes']))
    splits=Counter()
    for fit in m['folds']+[m['full']]:
        tree=fit['model']['tree']
        for n in tree['nodes']:
            if n['kind']=='split':splits[tree['feature_names'][n['feature']]]+=1
    errors=[dict(case_id=r['case_id'],error=r['candidate']['region_metrics']['rgb8_mae_codes']) for r in d['records'] if r['recipe']=='clean' and r['candidate']['changed_channels']>0]
    result=dict(acceptance=tests,all_requirements_pass=all(tests.values()),changed_clean=errors,split_counts=dict(splits),diagnostics=selected,new_fits=0,production_adopted=False)
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    html='<!doctype html><meta charset="utf-8"><title>Private face-local comparison</title><h1>Private face-local action comparison</h1><p>All fixed boards. Ref, input, aligned parent, face-local candidate. Research only; do not redistribute.</p>'
    html+=''.join('<img style="max-width:100%" src="'+Path(p).relative_to(OUT).as_posix()+'">' for p in d['boards'])
    html+='<h2>Outcome-selected worst cases</h2>'+''.join('<img style="max-width:100%" src="'+Path(p['path']).name+'">' for p in selected)
    (OUT/'review_PRIVATE.html').write_text(html,encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
