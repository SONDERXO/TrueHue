"""No-refit nested split-benefit label and retrained gate audit."""
from collections import Counter,defaultdict
import hashlib,json,math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.contextual_mst_experiment import FEATURES,predict
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import SCENE_FEATURES
from src.model_training.portable_tree import PortableTree
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
PARENT=ROOT/'outputs/whole_scene_correction_v1';CAND=ROOT/'outputs/split_benefit_gate_v1';OUT=ROOT/'outputs/split_benefit_gate_assessment_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    value=read(CAND/'results_PRIVATE.json');rows={r['case_id']:r for r in read(PARENT/'prepared_rows_PRIVATE.json')}
    original=read(ROOT/'outputs/stellenbosch_new_subjects_v1/results_PRIVATE.json');labels={r['subject_key']:float(r['source_mst_exact_decimal']) for r in original['records']}
    clean={r['source_case']:r for r in rows.values() if r['case']['id']=='clean' and r['features'] is not None}
    old_mst=read(ROOT/'outputs/nested_correction_diagnostic_v1/results_PRIVATE.json')['mapping_models'];cached_mst=read(ROOT/'outputs/benefit_aware_gate_v1/results_PRIVATE.json')['new_mst_models'];all_mst=dict(old_mst,**cached_mst)
    correctors=value['inner_correctors'];treecache={k:{h:PortableTree(v['model']['heads'][h]['tree']) for h in ['gamma','gains']} for k,v in correctors.items()}
    cache={}
    def pixels(r):
        if r['case_id'] not in cache:
            folder=PARENT/r['source_case'];pair=folder/r['case']['id']
            cache[r['case_id']]=(cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB),cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB),cv2.imread(str(folder/'mask.png'),0)>0)
        return cache[r['case_id']]
    def check_vector(r,vec,mid,excluded):
        model=all_mst[mid];assert set(model['excluded_keys'])==set(excluded) and not set(excluded)&set(model['training_keys'])
        p=predict(model['model'],r['features']);features=dict(r['features'],input_mst_score=p['score'])
        expected=[features[k] for k in CONTINUOUS_FEATURES]+[r['scene_features'][k] for k in SCENE_FEATURES]
        assert expected==vec
    ridgechecks=traces=labelchecks=logits=replays=0
    for mid,art in cached_mst.items():
        excluded=set(art['excluded_keys']);assert len(excluded)==3
        expected={k for k,r in clean.items() if r['subject_id'] not in excluded};assert set(art['training_cases'])==expected
        training=[clean[k] for k in art['training_cases']];counts=Counter(r['subject_id'] for r in training)
        weights=np.array([1/counts[r['subject_id']] for r in training]);x=np.array([[r['features'][k] for k in FEATURES] for r in training]);y=np.array([labels[r['subject_id']] for r in training])
        mean=np.average(x,axis=0,weights=weights);mean=np.where(np.ptp(x,axis=0)==0,x[0],mean);sd=np.sqrt(np.average((x-mean)**2,axis=0,weights=weights));sd=np.where(sd==0,1.,sd)
        m=art['model'];np.testing.assert_allclose(mean,m['mean'],atol=1e-12,rtol=0);np.testing.assert_allclose(sd,m['scale'],atol=1e-12,rtol=0)
        z=(x-mean)/sd;np.testing.assert_allclose((z.T@(weights[:,None]*z)+np.eye(len(FEATURES)))@np.array(m['coefficient']),z.T@(weights*(y-np.average(y,weights=weights))),atol=1e-10,rtol=0);ridgechecks+=1
    for cid,art in correctors.items():
        excluded=set(art['excluded_keys']);assert len(excluded)==2
        trace=art['training_trace'];expected={k for k,r in rows.items() if r['subject_id'] not in excluded and r['features'] is not None and r['target'] is not None}
        assert {t['case_id'] for t in trace}==expected
        targets=np.array([rows[t['case_id']]['target'] for t in trace])
        for t in trace:
            r=rows[t['case_id']];check_vector(r,t['features'],t['mapping_id'],excluded|{r['subject_id']});traces+=1
        for head,columns in [('gamma',[0]),('gains',[1,2])]:
            h=art['model']['heads'][head];yy=targets[:,columns]
            np.testing.assert_allclose(yy.mean(axis=0),h['normalization']['mean'],atol=1e-12,rtol=0)
            np.testing.assert_allclose(yy.std(axis=0),h['normalization']['population_std'],atol=1e-12,rtol=0)
            leafgroups=defaultdict(list)
            for i,t in enumerate(trace):leafgroups[treecache[cid][head].leaf_id(t['features'])].append(i)
            for leaf,indices in leafgroups.items():np.testing.assert_allclose(yy[indices].mean(axis=0),h['tree']['nodes'][leaf]['values'],atol=1e-12,rtol=0)
    folds={f['held_key']:f for f in value['folds']}
    for held,fold in folds.items():
        trace=fold['training_trace'];assert {t['case_id'] for t in trace}=={k for k,r in rows.items() if r['subject_id']!=held and r['features'] is not None}
        for t in trace:
            r=rows[t['case_id']];excluded={held,r['subject_id']};art=correctors[t['inner_corrector_id']];assert set(art['excluded_keys'])==excluded
            check_vector(r,t['features'],t['mapping_id'],excluded)
            controls=treecache[t['inner_corrector_id']]['gamma'].predict_one(t['features'])+treecache[t['inner_corrector_id']]['gains'].predict_one(t['features']);assert controls==t['predicted_parameters']
            image,ref,mask=pixels(r);output=render_rgb8(image,mask.astype(float),controls);mae=float(np.abs(output[mask].astype(float)-ref[mask]).mean())
            assert mae==t['inner_predicted_mae'] and t['input_mae']==r['input_metrics']['rgb8_mae_codes'] and t['label']==int(t['input_mae']>mae);labelchecks+=1
        if fold['model'] is not None:
            m=fold['model'];assert held not in m['training_keys'];w=np.array(m['weights']);x=np.array([t['features'] for t in trace]);mean=np.average(x,axis=0,weights=w);mean=np.where(np.ptp(x,axis=0)==0,x[0],mean);sd=np.sqrt(np.average((x-mean)**2,axis=0,weights=w));sd=np.where(sd==0,1.,sd)
            np.testing.assert_allclose(mean,m['mean'],atol=1e-12,rtol=0);np.testing.assert_allclose(sd,m['scale'],atol=1e-12,rtol=0)
            for key in m['training_keys']:
                for label in [0,1]:assert abs(sum(w[i] for i,t in enumerate(trace) if t['subject_id']==key and t['label']==label)-len(trace)/(2*len(m['training_keys'])))<1e-10
    outer=read(ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json');outerpreds={r['case_id']:r for r in outer['records']};boards=[]
    for r in value['records']:
        row=rows[r['case_id']];inspect=row['case']['id'] in ['clean','combined_cool_under','stress_combined_under']
        if r['status']=='unavailable_original':
            if inspect:
                scene=cv2.imread(str(PARENT/row['source_case']/row['case']['id']/'scene_input.png'));panel=np.full((188,800,3),255,np.uint8);panel[:160,:160]=cv2.resize(scene,(160,160));cv2.putText(panel,r['case_id']+' unavailable original',(168,30),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);boards.append(panel)
            continue
        image,ref,mask=pixels(row);prior=outerpreds[r['case_id']]['paths']['split_ungated'];assert r['features']==outerpreds[r['case_id']]['features']
        if r['gate'] is not None:
            m=folds[r['subject_id']]['model'];logit=math.fsum((float(x)-mu)/sd*c for x,mu,sd,c in zip(r['features'],m['mean'],m['scale'],m['coefficient']))+m['intercept'];assert abs(logit-r['gate']['logit'])<1e-12
            apply=logit>0;assert apply==r['gate']['apply_correction'];assert r['parameters']==(prior['parameters'] if apply else [1.,1.,1.]);logits+=1
        else:assert r['parameters']==[1.,1.,1.]
        output=render_rgb8(image,mask.astype(float),r['parameters']);saved=cv2.cvtColor(cv2.imread(str(CAND/(r['case_id']+'.png'))),cv2.COLOR_BGR2RGB)
        assert np.array_equal(output,saved) and np.array_equal(saved[~mask],image[~mask]) and metrics(saved,ref,mask)==r['metrics'];replays+=1
        if inspect:
            pair=PARENT/row['source_case']/row['case']['id'];ungated=cv2.cvtColor(cv2.imread(str(ROOT/'outputs/split_control_comparison_v1/split_ungated'/(r['case_id']+'.png'))),cv2.COLOR_BGR2RGB)
            oldgate=cv2.cvtColor(cv2.imread(str(ROOT/'outputs/split_control_comparison_v1/split_gated'/(r['case_id']+'.png'))),cv2.COLOR_BGR2RGB)
            panel=np.concatenate([cv2.resize(cv2.cvtColor(im,cv2.COLOR_RGB2BGR),(160,160),interpolation=cv2.INTER_NEAREST) for im in [ref,image,ungated,oldgate,saved]],axis=1)
            title=np.full((28,800,3),255,np.uint8);cv2.putText(title,r['case_id']+' ref/input/split/frozenGate/retrainedGate',(2,20),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);boards.append(np.concatenate([title,panel]))
    for path,h in read(CAND/'plan_PRIVATE.json')['input_sha256'].items():assert sha(Path(path))==h
    for path,h in read(CAND/'sha256.json').items():assert sha(CAND/path)==h
    OUT.mkdir(parents=True)
    for i in range(0,len(boards),10):cv2.imwrite(str(OUT/f'contact_{i//10+1:02d}_PRIVATE.png'),np.concatenate(boards[i:i+10]))
    report=dict(reused_three_key_excluded_ridge_equation_checks=ridgechecks,inner_corrector_training_trace_checks=traces,
        inner_held_benefit_label_replays=labelchecks,independent_outer_gate_logits=logits,outer_renderer_metric_replays=replays,
        preselected_boards=len(boards),refits=0,all_sources_unchanged=True)
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
