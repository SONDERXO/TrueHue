"""Independent saved-output, feature, routing and metric replay; no fitting."""
import importlib.util,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.split_control_candidate import predict_split
from src.model_training.correction_gate_candidate import gate_decision
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
from src.model_training.whole_scene_features import scene_features,SCENE_FEATURES
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.contextual_mst_experiment import FEATURES,predict
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.portable_tree import PortableTree
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def main():
    P=ROOT/'outputs/frozen_split_subject_check_v1';E=ROOT/'outputs/frozen_split_subject_evaluation_v1';M=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json';O=ROOT/'outputs/frozen_split_subject_assessment_v1'
    if O.exists():raise FileExistsError(O)
    model=read(M);v=read(E/'results_PRIVATE.json');sources={r['case_id']:r for r in read(P/'results_PRIVATE.json')['records']}
    assert not set(model['training_keys'])&{r['subject_key'] for r in sources.values()}
    for package in [P,E]:
        assert all(sha(package/n)==h for n,h in read(package/'sha256.json').items())
    assert all(sha(Path(p))==h for p,h in model['input_sha256'].items())
    training={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')}
    prior={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/results_PRIVATE.json')['records']}
    for ids,vectors in [(model['training_cases'],model['training_features']),(model['gate_cases'],model['gate_features'])]:
        for cid,vector in zip(ids,vectors):assert vector==prior[cid]['methods']['face_plus_scene']['features']
    targets=np.array([training[c]['target'] for c in model['training_cases']]);leaf_checks=0
    for head,columns in [('gamma',[0]),('gains',[1,2])]:
        payload=model['split']['heads'][head];tree=PortableTree(payload['tree']);values=targets[:,columns]
        assert np.allclose(values.mean(axis=0),payload['normalization']['mean'],atol=1e-12,rtol=0)
        assert np.allclose(values.std(axis=0),payload['normalization']['population_std'],atol=1e-12,rtol=0)
        leaves=np.array([tree.leaf_id(x) for x in model['training_features']])
        for leaf in set(leaves.tolist()):
            assert np.allclose(values[leaves==leaf].mean(axis=0),payload['tree']['nodes'][leaf]['values'],atol=1e-12,rtol=0);leaf_checks+=1
    for cid,label in zip(model['gate_cases'],model['gate_labels']):
        assert label==int(training[cid]['input_metrics']['rgb8_mae_codes']>prior[cid]['methods']['face_plus_scene']['metrics']['rgb8_mae_codes'])
    gx=np.array(model['gate_features']);w=np.array(model['gate']['weights']);gm=np.average(gx,axis=0,weights=w)
    assert np.allclose(gm,model['gate']['mean'],atol=1e-12,rtol=0)
    assert np.allclose(np.sqrt(np.average((gx-gm)**2,axis=0,weights=w)),model['gate']['scale'],atol=1e-12,rtol=0)
    checks=0;vectors=0
    for r in v['records']:
        s=sources[r['source_case']];folder=E/r['source_case']/r['recipe']
        if 'paths' not in r:assert s['status']!='success';continue
        ref=rgb(P/r['source_case']/'input.png');mask=cv2.imread(str(P/r['source_case']/'measurement_mask.png'),0)>0
        scene=rgb(folder/'scene_input.png');x0,y0,x1,y1=s['input_bridge']['native_bounds'];image=cv2.resize(scene[y0:y1,x0:x1],(256,256),interpolation=cv2.INTER_LINEAR)
        assert np.array_equal(image,rgb(folder/'input.png'))
        stat=compute_masked_lab_statistics(cv2.cvtColor(image,cv2.COLOR_RGB2BGR),mask.astype(np.uint8)*255);assert stat==r['statistics']
        if r['features'] is not None:
            f=dict(zip(FEATURES,[stat['ita_degrees'],stat['mean_l_star'],stat['mean_a_star'],stat['mean_b_star']]));pred=predict(model['ridge'],f);assert pred==r['mst_prediction']
            sf=scene_features(scene);f['input_mst_score']=pred['score'];vector=[f[n] for n in CONTINUOUS_FEATURES]+[sf[n] for n in SCENE_FEATURES];assert vector==r['features'];assert gate_decision(model['gate'],vector)==r['gate'];assert predict_split(model['split'],vector)==r['paths']['split_ungated']['parameters'];vectors+=1
        for name,path in r['paths'].items():
            output=render_rgb8(image,mask.astype(float),path['parameters']) if path['parameters'] is not None else image
            assert np.array_equal(output,rgb(folder/(name+'.png')));assert np.array_equal(output[~mask],image[~mask]);assert metrics(output,ref,mask)==path['metrics'];assert int(np.count_nonzero(output!=image))==path['changed_channels'];checks+=1
    assert len(v['records'])==336
    O.mkdir();(O/'verification_PRIVATE.json').write_text(json.dumps(dict(attempts=336,feature_replays=vectors,render_metric_replays=checks,source_hashes_verified=True,key_disjointness=True,new_fits=0,visual_review='separate manual step'),indent=2),encoding='utf-8')
    print('Verified',vectors,'feature/prediction vectors and',checks,'render/metric outputs; no refits.')
if __name__=='__main__':main()
