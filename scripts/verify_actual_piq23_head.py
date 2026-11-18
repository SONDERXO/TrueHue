"""No fitting or encoder calls; recount actual split/scaler/scores/held metrics."""
from pathlib import Path
import sys,json,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portrait_exposure_quality import ranking_pairs
OUT=ROOT/'outputs/piq23_actual_head_v1';FEATURES=ROOT/'outputs/piq23_actual_features_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dest=OUT/'independent_audit.json'
    if dest.exists():raise FileExistsError(dest)
    v=read(OUT/'verification.json');assert v['passed'] and v['real_head_fits']==1 and v['optimizer_updates']==7000
    for p,h in v['artifacts'].items():assert sha(OUT/p)==h
    for p,h in read(OUT/'bindings.json').items():assert sha(ROOT/p)==h
    head=read(OUT/'head.json');assert sha(OUT/'head.json')==read(OUT/'head_seal.json')['sha256']
    assert head['generated_fixture'] is False and head['bias']==0
    roster=read(FEATURES/'rows.json');records=read(FEATURES/'records.json');features={r['id']:r for r in records}
    training=sorted([r for r in roster if r['partition']=='Train'],key=lambda r:r['id'])
    test=[r for r in roster if r['partition']=='Test'];assert len(training)==3630 and len(test)==1486
    assert head['training_ids']==[r['id'] for r in training] and not {r['scene'] for r in training}&{r['scene'] for r in test}
    matrix=np.stack([np.load(ROOT/features[r['id']]['path'],allow_pickle=False) for r in training]).astype(np.float64)
    mean=matrix.mean(0);scale=matrix.std(0);scale[scale==0]=1
    assert mean.tolist()==head['mean'] and scale.tolist()==head['scale']
    pair=ranking_pairs(training);pair.sort(key=lambda p:(training[p[0]]['id'],training[p[1]]['id']))
    assert len(pair)==71178
    pairids=[(training[i]['id'],training[j]['id']) for i,j in pair]
    assert hashlib.sha256(json.dumps(pairids,separators=(',',':')).encode()).hexdigest()==head['pair_ids_sha256']
    rng=np.random.default_rng(42);batchhashes=[]
    for epoch in range(50):
        perm=rng.permutation(len(pair))
        batchhashes.extend(hashlib.sha256(perm[i:i+512].tobytes()).hexdigest() for i in range(0,len(perm),512))
    assert batchhashes==head['epoch_batch_index_sha256'] and len(batchhashes)==7000
    trace=read(OUT/'trace.json');assert len(trace)==7000 and all(math.isfinite(r['loss']) for r in trace)
    saved=read(OUT/'scores.json');scores={r['id']:r for r in saved};assert len(scores)==len(saved)==5116
    summary=read(OUT/'summary.json');checks=0
    for partition,rows in [('Train',training),('Test',test)]:
        pairs=ranking_pairs(rows);assert len(pairs)==(71178 if partition=='Train' else 27981)
        scene={}
        for i,j in pairs:
            a=rows[i];b=rows[j];assert a['scene']==b['scene']
            margin=scores[a['id']]['scalar_score']-scores[b['id']]['scalar_score']
            scene.setdefault(a['scene'],[]).append(margin)
        for name,values in scene.items():
            r=summary[partition]['per_scene'][name]
            accuracy=sum(m>0 for m in values)/len(values)
            loss=math.fsum(math.log1p(math.exp(-abs(m)))+max(0.,-m) for m in values)/len(values)
            assert r['pairs']==len(values) and r['wins']==sum(m>0 for m in values) and r['ties']==sum(m==0 for m in values)
            assert math.isclose(r['accuracy'],accuracy,abs_tol=1e-12) and math.isclose(r['loss'],loss,abs_tol=1e-12)
            checks+=1
        equal_accuracy=math.fsum(summary[partition]['per_scene'][s]['accuracy'] for s in scene)/len(scene)
        equal_loss=math.fsum(summary[partition]['per_scene'][s]['loss'] for s in scene)/len(scene)
        assert equal_accuracy==summary[partition]['scene_equal_accuracy'] and equal_loss==summary[partition]['scene_equal_loss']
    passed=summary['Test']['scene_equal_accuracy']>.5 and summary['Test']['scene_equal_loss']<math.log(2.)
    assert passed==summary['narrow_quality_screen_pass']==v['narrow_quality_screen_pass']
    result=dict(passed=True,real_fits_verified=1,train_images=3630,test_images=1486,training_pair_ids=71178,
      test_pairs=27981,scaler_values_verified=8192,batch_index_hashes_verified=7000,scene_results_verified=checks,
      original_artifact_hashes=len(v['artifacts']),narrow_quality_screen_pass=passed,new_fits=0,new_encoder_calls=0,
      test_scene_equal_accuracy=summary['Test']['scene_equal_accuracy'],test_scene_equal_loss=summary['Test']['scene_equal_loss'],model_ready=False)
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
    print(result)
if __name__=='__main__':main()
