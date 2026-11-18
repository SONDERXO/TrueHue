"""Saved single-case diagnosis; no inference, fitting or target optimization."""
import json,hashlib,sys
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.split_control_candidate import predict_split
from src.model_training.correction_gate_candidate import gate_decision
from src.ita_estimation.contextual_mst_experiment import FEATURES,predict
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import scene_features,SCENE_FEATURES
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
OUT=ROOT/'outputs/recovered_false_correction_diagnosis_v1';CID='eval_22__colour_warm'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def save(p,a):assert cv2.imwrite(str(p),cv2.cvtColor(a,cv2.COLOR_RGB2BGR))
def main():
    if OUT.exists():raise FileExistsError(OUT)
    M=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json';E=ROOT/'outputs/detector_appearance_correction_v1';P=ROOT/'outputs/detector_appearance_merged_v1';T=ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json'
    model=read(M);records=read(E/'results_PRIVATE.json')['records'];row=next(r for r in records if r['case_id']==CID);source=next(r for r in read(P/'results_PRIVATE.json')['records'] if r['case_id']==CID);folder=Path(source['artifact_root'])
    referencepath=ROOT/'outputs/frozen_split_subject_check_v1/eval_22/source.jpeg';assert not row['reference_available'];assert source['subject_key'] not in model['training_keys']
    paths=[M,T,E/'results_PRIVATE.json',P/'results_PRIVATE.json',referencepath,Path(source['source_path']),Path(__file__),ROOT/'docs/recovered-false-correction-diagnosis-protocol-2026-11-07.md']
    paths+=[folder/n for n in ['input.png','measurement_mask.png','native_grid.png','native_crop.png']]
    paths+=[ROOT/p for p in ['src/model_training/portable_tree.py','src/model_training/split_control_candidate.py','src/model_training/correction_gate_candidate.py','src/model_training/blended_recovery_targets.py','src/model_training/photographic_target_diagnostic.py','src/ita_estimation/contextual_mst_experiment.py','src/ita_estimation/compute_ita.py','src/model_training/whole_scene_features.py']]
    bindings={str(p):sha(p) for p in paths};assert all(sha(Path(p))==h for p,h in model['input_sha256'].items())
    image=rgb(Path(source['source_path']));reference=rgb(referencepath);working=cv2.imread(str(folder/'input.png'));rawmask=cv2.imread(str(folder/'measurement_mask.png'),0);mask=cv2.imread(str(folder/'native_grid.png'),0)>0
    stat=compute_masked_lab_statistics(working,rawmask);assert stat['valid'];f=dict(zip(FEATURES,[stat['ita_degrees'],stat['mean_l_star'],stat['mean_a_star'],stat['mean_b_star']]));mst=predict(model['ridge'],f);sf=scene_features(image);joined=dict(f,input_mst_score=mst['score']);vector=[joined[n] for n in CONTINUOUS_FEATURES]+[sf[n] for n in SCENE_FEATURES];assert vector==row['features'] and mst==row['mst_prediction']
    gate=model['gate'];x=np.array(vector);z=(x-np.array(gate['mean']))/np.array(gate['scale']);terms=z*np.array(gate['coefficient']);logit=float(terms.sum()+gate['intercept']);assert abs(logit-row['gate']['logit'])<1e-12;assert gate_decision(gate,vector)==row['gate']
    contributions=[dict(feature=n,value=float(x[i]),standardized=float(z[i]),coefficient=gate['coefficient'][i],logit_term=float(terms[i])) for i,n in enumerate(model['feature_names'])]
    train={r['case_id']:r for r in read(T)};targets=np.array([train[c]['target'] for c in model['training_cases']]);tx=np.array(model['training_features']);heads={}
    for name,cols in [('gamma',[0]),('gains',[1,2])]:
        tree=model['split']['heads'][name]['tree'];nodes=tree['nodes'];route=[];node=0
        while nodes[node]['kind']=='split':
            split=nodes[node];value=float(np.float32(vector[split['feature']]));left=value<=split['threshold'];route.append(dict(node=node,feature=model['feature_names'][split['feature']],input_float32=value,threshold=split['threshold'],branch='left' if left else 'right'));node=split['left'] if left else split['right']
        portable=PortableTree(tree);assert portable.leaf_id(vector)==node;members=[i for i,t in enumerate(tx) if portable.leaf_id(t.tolist())==node];values=targets[members][:,cols];mean=values.mean(axis=0);assert np.allclose(mean,nodes[node]['values'],rtol=0,atol=1e-12)
        heads[name]=dict(route=route,leaf=node,prediction=nodes[node]['values'],fitting_rows=len(members),distinct_publisher_keys=len({train[model['training_cases'][i]]['subject_id'] for i in members}),layer_counts=dict(Counter(train[model['training_cases'][i]]['case']['layer'] for i in members)),recipe_counts=dict(Counter(train[model['training_cases'][i]]['case']['id'] for i in members)),target_mean=mean.tolist(),target_range_min=values.min(axis=0).tolist(),target_range_max=values.max(axis=0).tolist(),members=[model['training_cases'][i] for i in members])
    gx=np.array(model['gate_features']);dist=np.linalg.norm((gx-x)/np.array(gate['scale']),axis=1);nearest=[dict(case_id=model['gate_cases'][i],distance=float(dist[i]),saved_joint_benefit_label=model['gate_labels'][i],recipe=train[model['gate_cases'][i]]['case']['id']) for i in np.argsort(dist)[:5]]
    ranges=[dict(feature=n,value=float(x[i]),head_min=float(tx[:,i].min()),head_max=float(tx[:,i].max()),outside_head_range=bool(x[i]<tx[:,i].min() or x[i]>tx[:,i].max()),gate_min=float(gx[:,i].min()),gate_max=float(gx[:,i].max()),outside_gate_range=bool(x[i]<gx[:,i].min() or x[i]>gx[:,i].max())) for i,n in enumerate(model['feature_names'])]
    params=predict_split(model['split'],vector);assert params==row['paths']['input_gated']['parameters'];controls=dict(neutral=[1.,1.,1.],gamma_only=[params[0],1.,1.],gains_only=[1.,params[1],params[2]],full=params)
    OUT.mkdir();component={};outputs={}
    for name,p in controls.items():
        result=render_rgb8(image,mask.astype(float),p);assert np.array_equal(result[~mask],image[~mask]);save(OUT/(name+'.png'),result);outputs[name]=result
        component[name]=dict(parameters=p,own_predicted_region_NOTskin_truth=metrics(result,reference,mask),full_scene=metrics(result,reference,np.ones(mask.shape,bool)),changed_channels=int(np.count_nonzero(result!=image)))
    assert np.array_equal(outputs['neutral'],image);assert np.array_equal(outputs['full'],rgb(E/CID/'input_gated.png'));assert component['full']['full_scene']==row['paths']['input_gated']['scene_metrics']
    overlay=image.copy();overlay[mask]=np.rint(.6*image[mask]+.4*np.array([0,255,0])).astype(np.uint8)
    panels=[reference,image,overlay,outputs['gamma_only'],outputs['gains_only'],outputs['full']];label='Original | input | predicted mask | gamma only | gains only | full'
    title=np.full((26,1344,3),255,np.uint8);cv2.putText(title,label,(4,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1);save(OUT/'scene_board.png',np.vstack([title,np.hstack(panels)]))
    x0,y0,x1,y1=source['input_bridge']['native_bounds'];zoom=[cv2.resize(a[y0:y1,x0:x1],(256,256),interpolation=cv2.INTER_NEAREST) for a in panels];title=np.full((26,1536,3),255,np.uint8);cv2.putText(title,label+' (native nearest zoom)',(4,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1);save(OUT/'native_board.png',np.vstack([title,np.hstack(zoom)]))
    context=[dict(case_id=r['case_id'],mask_status=r['mask_status'],features_available=r['features'] is not None,gate=r['gate'],parameters=r['paths']['input_gated']['parameters'],scene_mae=r['paths']['input_gated']['scene_metrics']['rgb8_mae_codes']) for r in records if r['source_case']=='eval_22'];assert len(context)==14
    result=dict(case_id=CID,features=joined,scene_features=sf,mst_prediction=mst,gate=dict(intercept=gate['intercept'],facial_terms_sum=float(terms[:5].sum()),scene_terms_sum=float(terms[5:].sum()),logit=logit,contributions=contributions),heads=heads,feature_ranges=ranges,nearest_gate_training_vectors=nearest,component_replays=component,same_source_context=context,native_selected_pixels=int(mask.sum()),reference_mask_available=False,new_fits=0,new_inference=0,new_targets=0,production_adopted=False)
    (OUT/'diagnosis_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8');assert all(sha(Path(p))==h for p,h in bindings.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(dict(gate={k:result['gate'][k] for k in ['intercept','facial_terms_sum','scene_terms_sum','logit']},heads={n:{k:v for k,v in h.items() if k not in ['members']} for n,h in heads.items()},components=component,outside_training_ranges=[r['feature'] for r in ranges if r['outside_head_range'] or r['outside_gate_range']]),indent=2))
if __name__=='__main__':main()
