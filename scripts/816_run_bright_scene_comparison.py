"""One fixed18-input bright-scene comparison against saved16-input results; no parameter search."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from sklearn.tree import DecisionTreeRegressor
from skimage.color import rgb2lab,deltaE_ciede2000
from src.model_training.portable_tree import export_tree,PortableTree
P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1';OUT=ROOT/'outputs/bright_scene_cue_comparison_v1'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')

def main():
    if OUT.exists():raise FileExistsError('Preserve completed or partial comparison')
    design_path=ROOT/'outputs/bright_scene_cue_comparison_design_v1/plan_PRIVATE.json';frozen=read(design_path)
    assert all(sha(p)==h for p,h in frozen['input_sha256'].items())
    receipt=read(ROOT/'outputs/bright_scene_cue_readiness_v1/review_PRIVATE.json');assert receipt['passed'];bound=receipt['input_sha256'];assert all(sha(p)==h for p,h in bound.items())
    rows={r['case_id']:r for r in read(P/'rows_PRIVATE.json')};folds=read(P/'folds_PRIVATE.json');plan=read(ROOT/'outputs/reviewed_ffhq_restoration_design_v1/plan_PRIVATE.json')
    plan['feature_names']=frozen['feature_names']
    additions=read(ROOT/'outputs/bright_scene_cue_readiness_v1/records_PRIVATE.json');assert len(additions)==44
    for a in additions:
        r=rows[a['case_id']];assert r['input_vector_float32']==a['input_vector_float32_18'][:16];r['input_vector_float32']=a['input_vector_float32_18']
    bound.update(frozen['input_sha256']);bound[str(design_path)]=sha(design_path)
    for rel in ['src/model_training/portable_tree.py','scripts/817_verify_bright_scene_comparison.py']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    for r in rows.values():assert sha(r['pixels_file'])==r['pixels_sha256'];bound[r['pixels_file']]=r['pixels_sha256']
    bound[str(Path(__file__))]=sha(__file__);OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(planned_fits=11,planned_predictions=44,input_sha256=bound,all_data_fit=False,holdout_reads=0))
    models=[];preds=[]
    for f in folds:
        train=[rows[c] for c in f['fitting_cases']];assert len(train)==40 and all(r['publisher_group']!=f['held_publisher_group'] for r in train)
        est=DecisionTreeRegressor(max_depth=4,random_state=42,min_samples_leaf=1,criterion='squared_error',splitter='best')
        est.fit(np.array([r['input_vector_float32'] for r in train],np.float32),[r['nominal_controls'] for r in train])
        payload=export_tree(est,plan['feature_names'],['gamma','red_gain','blue_gain'],dict(objective='unweighted_nominal_direct_control_squared_error',runtime_adopted=False));tree=PortableTree(payload)
        models.append(dict(definition=f,tree=payload));write(OUT/'models_PRIVATE.json',models);boards=[]
        for case in f['evaluation_cases']:
            r=rows[case];control=tree.predict_one(r['input_vector_float32']);np.testing.assert_array_equal(control,est.predict([r['input_vector_float32']])[0])
            with np.load(r['pixels_file'],allow_pickle=False) as pack:
                image=pack['input_rgb8'];ref=pack['reference_rgb8'];a=pack['alpha'];mask=pack['scoring_mask'];protect=pack['protected'];u=image/255.
                output=np.rint(255*(u*(1-a[:,:,None])+np.clip(u**control[0]*[control[1],1.,control[2]],0,1)*a[:,:,None])).astype(np.uint8)
                metrics={}
                for prefix,data in [('input',image),('output',output)]:
                    metrics[prefix+'_RGB']=float(np.abs(data[mask].astype(float)-ref[mask]).mean());metrics[prefix+'_DE']=float(deltaE_ciede2000(rgb2lab(data[mask]/255.),rgb2lab(ref[mask]/255.)).mean())
                dest=OUT/case;dest.mkdir();assert cv2.imwrite(str(dest/'output.png'),output[:,:,::-1]);head=np.full((32,768,3),255,np.uint8)
                cv2.putText(head,case+' | input / held output / original',(3,21),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
                board=np.vstack([head,np.hstack([image,output,ref])[:,:,::-1]]);assert cv2.imwrite(str(dest/'board.png'),board);boards.append(board)
                preds.append(dict(case_id=case,held_publisher_group=f['held_publisher_group'],experimental_role=r['experimental_role'],controls=control,leaf_id=tree.leaf_id(r['input_vector_float32']),changed_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),protected_unchanged=bool(np.array_equal(output[protect],image[protect])),zero_alpha_unchanged=bool(np.array_equal(output[a==0],image[a==0])),output_sha256=sha(dest/'output.png'),**metrics))
            write(OUT/'predictions_PRIVATE.json',preds)
        assert cv2.imwrite(str(OUT/(f['held_publisher_group']+'_board.png')),np.vstack(boards))
    by_role={}
    for role in ['identity','exposure_under','exposure_over','colour_cool']:
        own=[p for p in preds if p['experimental_role']==role]
        by_role[role]={k:float(np.mean([p[k] for p in own])) for k in ['input_RGB','output_RGB','input_DE','output_DE']}
        by_role[role].update(cases=len(own),edited=sum(p['changed_pixels']>0 for p in own),RGB_harms=sum(p['output_RGB']>p['input_RGB']+1e-12 for p in own),DE_harms=sum(p['output_DE']>p['input_DE']+1e-12 for p in own))
    checks=dict(coverage=len(preds)==44,all_recipe_RGB_means_improve=all(by_role[k]['output_RGB']<by_role[k]['input_RGB'] for k in by_role if k!='identity'),all_recipe_DE_means_improve=all(by_role[k]['output_DE']<by_role[k]['input_DE'] for k in by_role if k!='identity'),identity_unchanged=by_role['identity']['edited']==0,protection_preserved=all(p['protected_unchanged'] and p['zero_alpha_unchanged'] for p in preds))
    parent=read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/summary_PRIVATE.json')
    checks['each_recipe_RGB_nonworse_saved_parent']=all(by_role[k]['output_RGB']<=parent['by_role'][k]['output_RGB']+1e-12 for k in by_role if k!='identity')
    checks['each_recipe_DE_nonworse_saved_parent']=all(by_role[k]['output_DE']<=parent['by_role'][k]['output_DE']+1e-12 for k in by_role if k!='identity')
    summary=dict(parent_by_role=parent['by_role'],fits=11,predictions=44,attempted_roles=48,by_role=by_role,checks=checks,development_checks_passed=all(checks.values()),parameter_MAE=np.mean([np.abs(np.array(p['controls'])-rows[p['case_id']]['nominal_controls']) for p in preds],axis=0).tolist(),runtime_adopted=False,all_data_fit=False,original_photo_reads=0,image_model_calls=0,MST_fits=0,holdout_reads=0)
    assert all(sha(p)==h for p,h in bound.items());write(OUT/'summary_PRIVATE.json',summary);print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
