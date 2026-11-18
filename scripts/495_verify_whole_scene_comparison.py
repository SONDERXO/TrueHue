"""No-refit whole-scene synthesis, nested feature and paired renderer audit."""
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.photographic_target_diagnostic import distort,metrics
from src.model_training.blended_recovery_targets import render_rgb8
from src.ita_estimation.contextual_mst_experiment import predict
from src.model_training.whole_scene_features import SCENE_FEATURES
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
PARENT=ROOT/'outputs/whole_scene_correction_v1';OUT=ROOT/'outputs/whole_scene_assessment_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def quantile(values,q):
    x=np.sort(values.ravel()).astype(float);at=(len(x)-1)*q;i=int(at);return float(x[i]+(x[min(i+1,len(x)-1)]-x[i])*(at-i))


def main():
    if OUT.exists():raise FileExistsError(OUT)
    plan=read(PARENT/'plan_PRIVATE.json');v=read(PARENT/'results_PRIVATE.json');rows={r['case_id']:r for r in read(PARENT/'prepared_rows_PRIVATE.json')}
    sources={r['case_id']:r for r in read(ROOT/'outputs/stellenbosch_new_subjects_v1/results_PRIVATE.json')['records']}
    mappings=read(ROOT/'outputs/nested_correction_diagnostic_v1/results_PRIVATE.json')['mapping_models'];folds={f['held_key']:f for f in v['folds']}
    traces=0;norms=0
    for held,f in folds.items():
        targets=np.array([rows[k]['target'] for k in f['training_cases']])
        assert all(rows[k]['subject_id']!=held for k in f['training_cases'])
        for art in f['models'].values():
            np.testing.assert_allclose(targets.mean(axis=0),art['normalization']['fitting_target_mean'],atol=1e-12,rtol=0)
            np.testing.assert_allclose(targets.std(axis=0),art['normalization']['fitting_population_std'],atol=1e-12,rtol=0);norms+=1
        for t in f['training_feature_trace']:
            r=rows[t['case_id']];m=mappings[t['mapping_id']]
            assert not {held,r['subject_id']}&set(m['training_keys'])
            mst=predict(m['model'],r['features']);assert mst==t['mst_prediction']
            expected=dict(r['features'],input_mst_score=mst['score']);assert t['features']==[expected[k] for k in CONTINUOUS_FEATURES];traces+=1
    byprediction={r['case_id']:r for r in v['records']};scenes=features=replays=0;boards=[]
    for key,r in rows.items():
        original=sources[r['source_case']];folder=PARENT/r['source_case'];pair=folder/r['case']['id'];source=cv2.cvtColor(cv2.imread(original['source_path']),cv2.COLOR_BGR2RGB)
        replay,_,_=distort(source,np.ones(source.shape[:2],float),r['case']);scene=cv2.cvtColor(cv2.imread(str(pair/'scene_input.png')),cv2.COLOR_BGR2RGB)
        assert np.array_equal(replay,scene);scenes+=1
        mean=scene.astype(float).mean(axis=(0,1));lab=cv2.cvtColor(cv2.cvtColor(scene,cv2.COLOR_RGB2BGR),cv2.COLOR_BGR2LAB);l=lab[:,:,0].astype(np.float32)*(100/255)
        expected=[float(np.log((mean[0]+1)/(mean[1]+1))),float(np.log((mean[2]+1)/(mean[1]+1))),quantile(l,.1),quantile(l,.5),quantile(l,.9),float(np.any(scene==0,axis=2).mean()),float(np.any(scene==255,axis=2).mean())]
        np.testing.assert_allclose(expected,[r['scene_features'][k] for k in SCENE_FEATURES],atol=1e-10,rtol=0);features+=1
        inspect=r['case']['id'] in ['clean','combined_cool_under','stress_combined_under'];p=byprediction[key]
        if r['status']=='unavailable_original':
            if inspect:
                panel=np.full((160,768,3),255,np.uint8);panel[:128,:128]=cv2.resize(cv2.cvtColor(scene,cv2.COLOR_RGB2BGR),(128,128))
                cv2.putText(panel,key+' unavailable original landmarks',(135,30),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);boards.append((key,panel))
            continue
        x0,y0,x1,y1=original['input_bridge']['native_bounds'];image=cv2.resize(scene[y0:y1,x0:x1],(256,256),interpolation=cv2.INTER_LINEAR)
        saved=cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB);assert np.array_equal(image,saved)
        reference=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
        assert metrics(image,reference,mask)==p['input_metrics'];outputs=[]
        for method,art in folds[r['subject_id']]['models'].items():
            m=p['methods'][method]
            if m['features'] is not None:
                mst=predict(mappings[r['subject_id']]['model'],r['features']);expected=dict(r['features'],input_mst_score=mst['score']);vec=[expected[k] for k in CONTINUOUS_FEATURES]
                if method=='face_plus_scene':vec += [r['scene_features'][k] for k in SCENE_FEATURES]
                assert vec==m['features'] and PortableTree(art['tree']).predict_one(vec)==m['parameters']
            output=render_rgb8(image,mask.astype(float),m['parameters']) if m['parameters'] is not None else image.copy()
            stored=cv2.cvtColor(cv2.imread(str(pair/(method+'.png'))),cv2.COLOR_BGR2RGB)
            assert np.array_equal(output,stored) and np.array_equal(output[~mask],image[~mask]);assert metrics(output,reference,mask)==m['metrics'];replays+=1;outputs.append(output)
        if inspect:
            oracle=cv2.cvtColor(cv2.imread(str(pair/'oracle.png')),cv2.COLOR_BGR2RGB)
            board=np.concatenate([cv2.resize(cv2.cvtColor(im,cv2.COLOR_RGB2BGR),(128,128),interpolation=cv2.INTER_NEAREST) for im in [scene,reference,image,*outputs,oracle]],axis=1)
            label=np.full((32,768,3),255,np.uint8);cv2.putText(label,key+' scene/ref/input/face/+scene/target',(3,22),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1);boards.append((key,np.concatenate([label,board])))
    for path,h in plan['input_sha256'].items():assert sha(Path(path))==h
    for path,h in read(PARENT/'sha256.json').items():assert sha(PARENT/path)==h
    assert scenes==features==420 and replays==812 and len(boards)==90
    OUT.mkdir(parents=True)
    for i in range(0,len(boards),10):cv2.imwrite(str(OUT/f'contact_{i//10+1:02d}_PRIVATE.png'),np.concatenate([b for _,b in boards[i:i+10]]))
    summary=dict(scene_synthesis_replays=scenes,independent_scene_feature_checks=features,nested_training_feature_checks=traces,
        paired_fitting_normalizations=norms,paired_renderer_metric_checks=replays,preselected_inspection_boards=len(boards),refits=0,all_bound_sources_unchanged=True)
    (OUT/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
