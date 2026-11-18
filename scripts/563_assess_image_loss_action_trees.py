"""Saved training/evaluation assessment and explicitly outcome-selected boards."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/image_loss_action_tree_comparison_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    data=read(OUT/'results_PRIVATE.json');rows=data['records']
    models=read(ROOT/'outputs/image_loss_action_tree_models_v1/models_PRIVATE.json');training=[]
    for key,model,features in [(f['held_key'],f['model'],f['training_features']) for f in models['folds']]+[('full',models['full_model'],models['full_training_features'])]:
        tree=PortableTree(model['tree']);costs=np.array(model['costs']);selected=[model['trace'][tree.leaf_id(x)]['action'] for x in features]
        actual=costs[np.arange(len(costs)),selected];clean=np.array(model['clean'])
        assert np.all(actual[clean]==0)
        training.append(dict(fit=key,rows=len(features),clean_rows=int(clean.sum()),input_mean_mae=float(costs[:,0].mean()),
            learned_mean_mae=float(actual.mean()),evaluation_only_best_library_mean_mae=float(costs.min(axis=1).mean()),
            changed_control_rows=sum(model['actions'][a]!=[1.,1.,1.] for a in selected),clean_constraint_pass=True))
    context={(r['suite'],r['case_id']):r for r in read(ROOT/'outputs/gamma_scene_chroma_comparison_v3/results_PRIVATE.json')['records']}
    previous={(r['suite'],r['case_id']):r for r in read(ROOT/'outputs/joint_neutral_support_v1/results_PRIVATE.json')['records']}
    selected=[];extra=OUT/'selected_diagnostics';extra.mkdir(exist_ok=True)
    for suite in ('fold_working256','fallback_native224'):
        for layer in ('clean','core'):
            rr=[r for r in rows if r['suite']==suite and r['layer']==layer and r['reference_available']]
            harmful=[r for r in rr if r['paths']['action_tree']['reference_metrics']['rgb8_mae_codes']>r['input_reference_metrics']['rgb8_mae_codes']]
            if not harmful:continue
            q=sorted(harmful,key=lambda r:(-(r['paths']['action_tree']['reference_metrics']['rgb8_mae_codes']-r['input_reference_metrics']['rgb8_mae_codes']),r['case_id']))[0]
            c=context[suite,q['case_id']];p=previous[suite,q['case_id']]
            paths=[q['reference_path'],q['image_path'],c['old_output_paths']['old_gated'],p['output_paths']['policy_gated'],q['output_paths']['action_tree']]
            panels=[rgb(path) for path in paths];title=np.full((30,panels[0].shape[1]*5,3),255,np.uint8)
            cv2.putText(title,'OUTCOME SELECTED '+suite+' '+q['case_id']+' ref | input | retained | previous policy | action tree',(2,19),cv2.FONT_HERSHEY_SIMPLEX,.33,(0,0,0),1)
            board=extra/(suite+'_'+layer+'.png');assert cv2.imwrite(str(board),cv2.cvtColor(np.vstack([title,np.hstack(panels)]),cv2.COLOR_RGB2BGR))
            selected.append(dict(suite=suite,layer=layer,case_id=q['case_id'],excess_rgb_mae=q['paths']['action_tree']['reference_metrics']['rgb8_mae_codes']-q['input_reference_metrics']['rgb8_mae_codes'],path=str(board),source_sha256={path:sha(path) for path in paths}))
    gain_changes={}
    for suite in ('fold_working256','fallback_native224'):
        gain_changes[suite]={}
        for layer in ('clean','core','composite_stress_design'):
            rr=[r for r in rows if r['suite']==suite and r['layer']==layer and r['reference_available']]
            gain_changes[suite][layer]=dict(scored=len(rr),beneficial=sum(r['paths']['action_tree']['reference_metrics']['rgb8_mae_codes']<r['input_reference_metrics']['rgb8_mae_codes'] for r in rr),
                prior_benefits_lost=sum(r['paths']['previous_policy_gated']['reference_metrics']['rgb8_mae_codes']<r['input_reference_metrics']['rgb8_mae_codes'] and r['paths']['action_tree']['changed_channels']==0 for r in rr))
    focal=[r for r in rows if (r['suite'],r['case_id']) in [('fold_working256','case_28__clean'),('fallback_native224','eval_02__clean'),('fallback_native224','eval_22__colour_warm')]]
    result=dict(training=training,selected_diagnostics=selected,selection='Worst excess RGB MAE versus input per main context and clean/core layer, outcome-selected',
        gain_counts=gain_changes,focal_records=focal,result_sha256=sha(OUT/'results_PRIVATE.json'),assessor_sha256=sha(Path(__file__)),new_fits=0)
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(dict(full_training=training[-1],gains=gain_changes,selected_diagnostics=[{k:v for k,v in r.items() if k!='source_sha256'} for r in selected]),indent=2))

if __name__=='__main__':main()
