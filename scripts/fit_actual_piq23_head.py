"""Single approved real PIQ23 quality-head fit; no correction learner."""
from pathlib import Path
import sys,os,json,hashlib,math,time
os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.exposure_quality_training import SETTINGS,prepare,fit_head,score
from src.model_training.portrait_exposure_quality import ranking_pairs
F=ROOT/'outputs/piq23_actual_features_v1';OUT=ROOT/'outputs/piq23_actual_head_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
def softplus_negative(m):return math.log1p(math.exp(-abs(m)))+max(0.,-m)
def assess(rows,scores):
    pairs=ranking_pairs(rows);scene={}
    for s in sorted({r['scene'] for r in rows}):
        own=[(i,j) for i,j in pairs if rows[i]['scene']==s]
        margins=[scores[i]-scores[j] for i,j in own];assert margins
        scene[s]=dict(pairs=len(own),wins=sum(m>0 for m in margins),ties=sum(m==0 for m in margins),
                      accuracy=sum(m>0 for m in margins)/len(own),loss=math.fsum(softplus_negative(m) for m in margins)/len(own))
    margins=[scores[i]-scores[j] for i,j in pairs]
    return dict(images=len(rows),scenes=len(scene),pairs=len(pairs),per_scene=scene,
           pooled_accuracy=sum(m>0 for m in margins)/len(margins),pooled_loss=math.fsum(softplus_negative(m) for m in margins)/len(margins),
           scene_equal_accuracy=math.fsum(r['accuracy'] for r in scene.values())/len(scene),
           scene_equal_loss=math.fsum(r['loss'] for r in scene.values())/len(scene),tie_baseline_loss=math.log(2.))
def main():
    if OUT.exists():raise FileExistsError('Single real head attempt already exists')
    v=read(F/'verification.json');assert v['passed'] and v['vectors']==5116 and v['training_fits']==0
    for p,h in read(F/'bindings.json').items():assert sha(ROOT/p)==h
    for name,key in [('rows.json','rows_sha256'),('records.json','records_sha256'),('bindings.json','bindings_sha256')]:assert sha(F/name)==v[key]
    qa=read(ROOT/'outputs/piq23_training_engineering_v1/verification.json');assert qa['passed']
    for p,h in qa['code_sha256'].items():assert sha(ROOT/p)==h
    roster=read(F/'rows.json');records=read(F/'records.json');by_id={r['id']:r for r in records}
    assert len(by_id)==len(roster)==5116
    vectors=[]
    for r in roster:
        a=by_id[r['id']];assert a['partition']==r['partition'] and a['scene']==r['scene']
        p=ROOT/a['path'];assert sha(p)==a['sha256'];x=np.load(p,allow_pickle=False)
        assert x.dtype==np.float32 and x.shape==(4096,) and np.isfinite(x).all();vectors.append(x)
    x=np.stack(vectors);train_indices=[i for i,r in enumerate(roster) if r['partition']=='Train']
    test_indices=[i for i,r in enumerate(roster) if r['partition']=='Test']
    assert len(train_indices)==3630 and len(test_indices)==1486
    training=[roster[i] for i in train_indices];test=[roster[i] for i in test_indices]
    assert not {r['scene'] for r in training}&{r['scene'] for r in test}
    train_x=x[train_indices].copy();data=prepare(training,train_x,generated_fixture=False)
    assert len(data['pairs'])==71178 and len(ranking_pairs(test))==27981
    assert data['records']==sorted(training,key=lambda r:r['id']) and len(data['scene_pair_counts'])==35
    updates=50*math.ceil(71178/512);assert updates==7000
    bound={p.relative_to(ROOT).as_posix():sha(p) for p in [F/'verification.json',F/'records.json',F/'rows.json',F/'bindings.json',
       ROOT/'docs/piq23-real-head-evaluation-2026-11-18.md',Path(__file__),ROOT/'outputs/piq23_training_engineering_v1/verification.json']}
    bound.update(qa['code_sha256']);OUT.mkdir();write(OUT/'bindings.json',bound)
    write(OUT/'fit_accounting.json',dict(started=1,maximum=1,updates=updates,train_images=3630,training_scenes=35,test_images_in_fitter=0))
    start=time.monotonic();epoch_states=[]
    try:
        def observer(step,w,m,vv):
            assert np.isfinite(w).all() and np.isfinite(m).all() and np.isfinite(vv).all()
            if step%140==0:
                epoch=step//140;np.savez(OUT/f'epoch_{epoch:02d}.npz',weights=w,m=m,v=vv)
                epoch_states.append(dict(epoch=epoch,step=step,weight_norm=float(np.linalg.norm(w))))
                if epoch%5==0:print('Actual PIQ23 quality head epoch '+str(epoch)+'/50',flush=True)
        head,trace=fit_head(training,train_x,generated_fixture=False,observer=observer)
        assert head['optimizer_updates']==7000 and head['settings']==SETTINGS and head['generated_fixture'] is False
        assert head['mean']==data['mean'].tolist() and head['scale']==data['scale'].tolist()
        assert head['training_ids']==[r['id'] for r in data['records']] and not set(head['training_ids'])&{r['id'] for r in test}
        assert head['scene_pair_counts']==data['scene_pair_counts'] and head['eligible_pairs']==71178
        write(OUT/'head.json',head);write(OUT/'trace.json',trace);write(OUT/'epoch_states.json',epoch_states)
        write(OUT/'head_seal.json',dict(sha256=sha(OUT/'head.json'),real_fits=1,updates=7000,held_scores=0))
        w=head['weights'];mean=head['mean'];scale=head['scale'];scores=[];maximum=0.
        for r,vec in zip(roster,x):
            native=score(head,vec);independent=math.fsum(w[j]*((float(vec[j])-mean[j])/scale[j]) for j in range(4096))
            error=abs(native-independent);maximum=max(maximum,error)
            assert math.isclose(native,independent,rel_tol=1e-10,abs_tol=1e-10)
            scores.append(dict(id=r['id'],scene=r['scene'],partition=r['partition'],score=native,scalar_score=independent))
        write(OUT/'scores.json',scores)
        summaries={p:assess([roster[i] for i in ids],[scores[i]['scalar_score'] for i in ids]) for p,ids in [('Train',train_indices),('Test',test_indices)]}
        held=summaries['Test'];passed=held['scene_equal_accuracy']>.5 and held['scene_equal_loss']<math.log(2.)
        summaries.update(narrow_quality_screen_pass=passed,model_ready=False,correction_fit_selected=False)
        write(OUT/'summary.json',summaries)
        assert sha(OUT/'head.json')==read(OUT/'head_seal.json')['sha256']
        for p,h in bound.items():assert sha(ROOT/p)==h
        write(OUT/'verification.json',dict(passed=True,real_head_fits=1,optimizer_updates=7000,correction_fits=0,
            train_only_scaler_exact=True,train_only_ids_exact=True,head_sealed_before_held_scores=True,
            scalar_scores_verified=5116,max_scalar_error=maximum,narrow_quality_screen_pass=passed,
            model_ready=False,elapsed_seconds=time.monotonic()-start,
            artifacts={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()}))
        print('COMPLETE one real PIQ23 head; narrow_quality_screen_pass='+str(passed),flush=True)
        print(json.dumps(held,indent=2),flush=True)
    except Exception as exc:write(OUT/'failure.json',dict(error=repr(exc),real_fits_started=1,completed_epochs=len(epoch_states)));raise
if __name__=='__main__':main()
