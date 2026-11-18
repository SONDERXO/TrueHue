"""Frozen756attempt comparison using unchanged native evaluator and extra DE accounting."""
from pathlib import Path
import json,hashlib,runpy
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/expanded_correction_comparison_v1';M=ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ns=runpy.run_path(str(ROOT/'scripts/589_evaluate_face_local_action_trees.py'));fn=ns['main'];fn.__globals__.update(M=M,OUT=OUT);fn()
    d=read(OUT/'results_PRIVATE.json');transitions={}
    for cohort,layers in d['summary'].items():
        for layer,s in layers.items():
            rr=[r for r in d['records'] if r['cohort']==cohort and r['layer']==layer and r['reference_available']]
            for method in ('parent','candidate'):
                s['methods'][method].update(region_CIEDE2000=float(np.mean([r[method]['region_metrics']['relative_deltaE00_mean'] for r in rr])),
                    DE_harms=sum(r[method]['region_metrics']['relative_deltaE00_mean']>r['input_region_metrics']['relative_deltaE00_mean'] for r in rr),
                    DE_benefits=sum(r[method]['region_metrics']['relative_deltaE00_mean']<r['input_region_metrics']['relative_deltaE00_mean'] for r in rr))
            for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
                def ids(method,sign):return {r['case_id'] for r in rr if sign*(r[method]['region_metrics'][metric]-r['input_region_metrics'][metric])>0}
                ph=ids('parent',1);ch=ids('candidate',1);pb=ids('parent',-1);cb=ids('candidate',-1)
                transitions[cohort+'_'+layer+'_'+metric]=dict(new_harms=sorted(ch-ph),removed_harms=sorted(ph-ch),lost_benefits=sorted(pb-cb),gained_benefits=sorted(cb-pb))
    for p in d['boards']:
        image=cv2.imread(p);image[:28]=255;cv2.putText(image,Path(p).parent.name+' ref|input|aligned parent|expanded fit',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1);assert cv2.imwrite(p,image)
    for start in range(0,len(d['boards']),4):assert cv2.imwrite(str(OUT/'contact_sheets'/f'{start//4:02d}.png'),np.vstack([cv2.imread(p) for p in d['boards'][start:start+4]]))
    d.update(comparison='Expanded correction fitting sources only; frozen MST and aligned12features',harm_benefit_transitions=transitions,
        implementation_note='face_local.png is inherited evaluator filename; features and model are expanded whole-scene aligned pipeline')
    (OUT/'results_PRIVATE.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
    bp=OUT/'input_sha256_PRIVATE.json';bound=read(bp);bound[str(Path(__file__))]=sha(Path(__file__));bp.write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print('Complete CIEDE2000/RGB summaries:',json.dumps(d['summary'],indent=2))

if __name__=='__main__':main()
