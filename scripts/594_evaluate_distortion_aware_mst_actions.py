"""Reuse frozen same-support evaluator, then label this comparison explicitly."""
from pathlib import Path
import runpy,json,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/distortion_aware_mst_action_comparison_v1'
M=ROOT/'outputs/distortion_aware_mst_action_models_v1/models_PRIVATE.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    # Reuse the unchanged native rendering/metrics implementation, not its old model.
    namespace=runpy.run_path(str(ROOT/'scripts/589_evaluate_face_local_action_trees.py'))
    fn=namespace['main'];fn.__globals__.update(M=M,OUT=OUT);fn()
    path=OUT/'results_PRIVATE.json';d=json.loads(path.read_text(encoding='utf-8'))
    model=json.loads(M.read_text(encoding='utf-8'));old=json.loads((ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json').read_text(encoding='utf-8'))
    prep={r['case_id']:r for r in json.loads((ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json').read_text(encoding='utf-8'))['records']}
    mst={}
    for name,source in [('parent',old),('candidate',model)]:
        predictions=source['predictions'];clean={prep[r['case_id']]['source_case']:r for r in predictions if prep[r['case_id']]['recipe']=='clean' and r['mst_prediction'] is not None}
        mst[name]={}
        for cohort in ('development','later'):
            for layer in ('clean','core','composite_stress_design'):
                rr=[r for r in predictions if r['cohort']==cohort and prep[r['case_id']]['layer']==layer and r['mst_prediction'] is not None]
                paired=[r for r in rr if prep[r['case_id']]['source_case'] in clean]
                errors=[abs(r['mst_prediction']['score']-float(prep[r['case_id']]['source_mst_exact_decimal'])) for r in rr]
                drift=[abs(r['mst_prediction']['score']-clean[prep[r['case_id']]['source_case']]['mst_prediction']['score']) for r in paired]
                bykey={k:[abs(r['mst_prediction']['score']-float(prep[r['case_id']]['source_mst_exact_decimal'])) for r in rr if r['subject_id']==k] for k in {r['subject_id'] for r in rr}}
                mst[name][cohort+'_'+layer]=dict(available=len(rr),score_MAE=float(np.mean(errors)),equal_key_MAE=float(np.mean([np.mean(v) for v in bykey.values()])),
                    paired=len(paired),mean_absolute_drift=float(np.mean(drift)),clipped=sum(r['mst_prediction']['raw']!=r['mst_prediction']['score'] for r in rr))
    # Both image metrics were already computed on identical scoring regions.
    for cohort,layers in d['summary'].items():
        for layer,s in layers.items():
            rr=[r for r in d['records'] if r['cohort']==cohort and r['layer']==layer and r['reference_available']]
            for method in ('parent','candidate'):
                s['methods'][method]['region_CIEDE2000']=float(np.mean([r[method]['region_metrics']['relative_deltaE00_mean'] for r in rr]))
    for p in d['boards']:
        im=cv2.imread(p);im[:28]=255
        cid=Path(p).parent.name
        cv2.putText(im,cid+' ref | input | aligned parent | paired-MST',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1)
        assert cv2.imwrite(p,im)
    for start in range(0,len(d['boards']),4):
        assert cv2.imwrite(str(OUT/'contact_sheets'/f'{start//4:02d}.png'),np.vstack([cv2.imread(p) for p in d['boards'][start:start+4]]))
    d.update(MST_comparison=mst,comparison='Distortion-trained MST supervision; unchanged aligned correction representation',
        implementation_note='face_local.png filename inherited from reused renderer; candidate is whole-scene aligned features with changed MST only')
    path.write_text(json.dumps(d,indent=2),encoding='utf-8')
    bp=OUT/'input_sha256_PRIVATE.json';bound=json.loads(bp.read_text(encoding='utf-8'));bound[str(Path(__file__))]=sha(Path(__file__));bp.write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print('MST errors/drift:',json.dumps(mst,indent=2))

if __name__=='__main__':main()
