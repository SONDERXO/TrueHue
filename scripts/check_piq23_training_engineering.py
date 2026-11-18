"""Generated full-width trainer/Adam replay and frozen encoder integration only."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['MKL_NUM_THREADS']='2'
from pathlib import Path
import sys,json,math,hashlib,copy,itertools,platform
from collections import Counter
import importlib.metadata
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training import exposure_quality_training as training
from src.model_training.exposure_quality_inference import preprocess_roi,probe_features
from src.model_training.reiqa_frozen_features import FrozenQualityEncoder,generated_inputs,sha

OUT=ROOT/'outputs/piq23_training_engineering_v1'


def scalar_batch(w,z,pairs,weights,indices):
    factor=len(pairs)/len(indices);losses=[];contributions=[[] for _ in w]
    for i in indices:
        a,b=pairs[i];difference=[float(u)-float(v) for u,v in zip(z[a],z[b])]
        margin=math.fsum(u*v for u,v in zip(w,difference))
        sigmoid=(math.exp(-margin)/(1+math.exp(-margin))) if margin>=0 else 1/(1+math.exp(margin))
        losses.append(factor*float(weights[i])*(max(0,-margin)+math.log1p(math.exp(-abs(margin)))))
        for j,d in enumerate(difference):contributions[j].append(-factor*float(weights[i])*sigmoid*d)
    return (math.fsum(losses)+.0005*math.fsum(v*v for v in w),
            [math.fsum(c)+.001*v for c,v in zip(contributions,w)])


def main():
    if OUT.exists():raise FileExistsError(OUT)
    records=[];x=np.zeros((72,4096),dtype=np.float32)
    for s in range(3):
        for i in range(24):
            records.append(dict(id=f's{s}_{i:03d}',scene=f's{s}',partition='Train',generated_fixture=True,low=i-.1,score=float(i),high=i+.1))
            x[s*24+i,:5]=[i/23,s/2,math.sin(i),math.cos(i/3),(i%5)/4]
    original=x.copy();raw=copy.deepcopy(records);observed=[]
    def observe(step,w,m,v):
        assert np.count_nonzero(w[5:])==np.count_nonzero(m[5:])==np.count_nonzero(v[5:])==0
        observed.append((w[:5].copy(),m[:5].copy(),v[:5].copy()))
    head,trace=training.fit_head(records,x,generated_fixture=True,observer=observe)
    assert np.array_equal(x,original) and records==raw
    assert head['eligible_pairs']==828 and head['optimizer_updates']==len(trace)==len(observed)==100
    # Independent canonical pair construction and fitting-only scalar standardization.
    ordered=sorted(range(len(raw)),key=lambda i:raw[i]['id']);r=[raw[i] for i in ordered];xx=x[ordered].astype(float)
    pairs=[]
    for a,b in itertools.combinations(range(72),2):
        if r[a]['scene']!=r[b]['scene']:continue
        if r[a]['low']>r[b]['high']:pairs.append((a,b))
        elif r[b]['low']>r[a]['high']:pairs.append((b,a))
    pairs.sort(key=lambda p:(r[p[0]]['id'],r[p[1]]['id']))
    counts=Counter(r[a]['scene'] for a,b in pairs)
    weights=[1/(3*counts[r[a]['scene']]) for a,b in pairs]
    means=[math.fsum(row[j] for row in xx)/72 for j in range(5)]
    scales=[math.sqrt(math.fsum((row[j]-means[j])**2 for row in xx)/72) for j in range(5)]
    scales=[v if v else 1 for v in scales]
    z=[[(float(row[j])-means[j])/scales[j] for j in range(5)] for row in xx]
    for a,b in zip(head['mean'][:5],means):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12)
    for a,b in zip(head['scale'][:5],scales):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12)
    assert head['scale'][5:]==[1.]*4091
    rng=np.random.default_rng(42);w=[0.]*5;m=[0.]*5;v=[0.]*5;step=0;max_adam_error=0.;max_loss_error=0.
    for epoch in range(50):
        order=rng.permutation(828);assert sorted(order.tolist())==list(range(828))
        for start in range(0,828,512):
            ids=order[start:start+512]
            loss,g=scalar_batch(w,z,pairs,weights,ids)
            step+=1
            max_loss_error=max(max_loss_error,abs(loss-trace[step-1]['loss']))
            assert hashlib.sha256(ids.tobytes()).hexdigest()==head['epoch_batch_index_sha256'][step-1]
            for j in range(5):
                m[j]=.9*m[j]+.1*g[j];v[j]=.999*v[j]+.001*g[j]*g[j]
                w[j]-=.01*(m[j]/(1-.9**step))/(math.sqrt(v[j]/(1-.999**step))+1e-8)
            for reference,actual in zip([w,m,v],observed[step-1]):max_adam_error=max(max_adam_error,max(abs(a-b) for a,b in zip(reference,actual)))
    assert max_adam_error<1e-10 and max_loss_error<1e-10
    assert max(abs(a-b) for a,b in zip(w,head['weights'][:5]))<1e-10
    print('PASS100independent scalar Adam updates/full4096state/uneven batches.',flush=True)
    # Unequal numbers of eligible pairs across scenes expose batch renormalization errors.
    imbalanced=copy.deepcopy(records)
    for k,row in enumerate(imbalanced):
        level=(k%24)//(1 if k<24 else 2 if k<48 else 4)
        row.update(low=level-.1,score=float(level),high=level+.1)
    data=training.prepare(imbalanced,x,generated_fixture=True);n=len(data['pairs']);assert n==780
    assert sorted(data['scene_pair_counts'].values())==[240,264,276]
    for scene in data['scene_pair_counts']:
        total=math.fsum(float(a) for (i,j),a in zip(data['pairs'],data['pair_weights']) if data['records'][i]['scene']==scene)
        assert math.isclose(total,1/3,abs_tol=1e-14)
    ww=np.zeros(4096);ww[:5]=[.2,-.3,.1,.4,-.2]
    full_loss,full_grad=training.batch_objective(ww,data['z'],data['pairs'],data['pair_weights'],np.arange(n))
    losses=[];gradients=[];max_balance_error=0.
    for start in range(0,n,512):
        ids=np.arange(n)[start:start+512]
        loss,g=training.batch_objective(ww,data['z'],data['pairs'],data['pair_weights'],ids)
        sl,sg=scalar_batch(ww[:5].tolist(),data['z'][:,:5].tolist(),data['pairs'].tolist(),data['pair_weights'].tolist(),ids)
        max_balance_error=max(max_balance_error,abs(loss-sl),max(abs(a-b) for a,b in zip(g[:5],sg)))
        losses.append(len(ids)/n*loss);gradients.append(len(ids)/n*g)
    assert abs(math.fsum(losses)-full_loss)<1e-12
    assert np.max(np.abs(sum(gradients)-full_grad))<1e-12 and max_balance_error<1e-12
    # Dense4096 gradient checks, independent scalar score and finite differences.
    dense=np.random.default_rng(9).normal(0,.1,(4,4096));dp=np.array([[1,0],[2,0],[3,1]])
    da=np.array([.2,.3,.5]);dw=np.random.default_rng(10).normal(0,.01,4096)
    dl,dg=training.batch_objective(dw,dense,dp,da,np.arange(3))
    sl,sg=scalar_batch(dw.tolist(),dense.tolist(),dp.tolist(),da.tolist(),range(3))
    assert abs(dl-sl)<1e-12 and np.max(np.abs(dg-sg))<1e-12
    max_fd=0.
    for j in [0,1,17,281,1024,2048,4095]:
        d=np.zeros(4096);d[j]=1e-6
        fd=(training.batch_objective(dw+d,dense,dp,da,np.arange(3))[0]-training.batch_objective(dw-d,dense,dp,da,np.arange(3))[0])/2e-6
        max_fd=max(max_fd,abs(fd-dg[j]))
    assert max_fd<1e-8
    repeat,retrace=training.fit_head(records,x,generated_fixture=True)
    assert head==repeat and trace==retrace
    for invalid in ['test','provenance','duplicate','width','nonfinite']:
        rr=copy.deepcopy(records);fx=x.copy()
        if invalid=='test':rr[-1]['partition']='Test'
        elif invalid=='provenance':rr[-1]['generated_fixture']=False
        elif invalid=='duplicate':rr[-1]['id']=rr[0]['id']
        elif invalid=='width':fx=fx[:,:-1]
        elif invalid=='nonfinite':fx[-1,0]=float('nan')
        try:training.prepare(rr,fx,generated_fixture=True)
        except ValueError:pass
        else:raise AssertionError('Invalid training input accepted:'+invalid)
    zeros=training.prepare(records,np.zeros_like(x),generated_fixture=True)
    zl,zg=training.batch_objective(np.zeros(4096),zeros['z'],zeros['pairs'],zeros['pair_weights'],np.arange(828))
    assert abs(zl-math.log(2))<1e-12 and np.count_nonzero(zg)==0
    OUT.mkdir();(OUT/'generated_head.json').write_text(json.dumps(head,indent=2)+'\n',encoding='utf-8')
    reloaded=json.loads((OUT/'generated_head.json').read_text())
    q=dense[0];scalar_score=math.fsum(float(wi)*((float(qi)-mi)/si) for wi,qi,mi,si in zip(head['weights'],q,head['mean'],head['scale']))
    assert math.isclose(training.score(reloaded,q),scalar_score,abs_tol=1e-12,rel_tol=1e-12)
    # Real frozen encoder, generated pixels only. No image/model download or photo loader.
    encoder=FrozenQualityEncoder(ROOT);state=encoder.initial_state;encoder_cases=[]
    class RecordingEncoder:
        def __init__(self,actual):self.actual=actual;self.values=[]
        def encode(self,rgb):
            result=self.actual.encode(rgb);self.values.append(result.copy());return result
    for name,rgb in generated_inputs()[:3]:
        before=rgb.copy();capture=RecordingEncoder(encoder)
        cues,scores=probe_features(reloaded,capture,rgb)
        again,again_scores=probe_features(reloaded,capture,rgb)
        assert cues==again and scores==again_scores and np.array_equal(rgb,before)
        assert all(np.array_equal(a,b) for a,b in zip(capture.values[:3],capture.values[3:]))
        scalar=[math.fsum(w*((float(v)-m)/s) for w,v,m,s in zip(head['weights'],vector,head['mean'],head['scale'])) for vector in capture.values[:3]]
        for actual,expected in zip([scores['base'],scores['minus'],scores['plus']],scalar):assert math.isclose(actual,expected,abs_tol=1e-10,rel_tol=1e-10)
        assert np.allclose(cues,[scalar[1]-scalar[0],scalar[2]-scalar[0]],atol=1e-10,rtol=1e-10)
        encoder_cases.append(dict(name=name,repeat_exact=True,scalar_score_parity=True,temporary_probe_features=cues))
    roi=Image.fromarray(generated_inputs()[0][1][:31,:17]);roi_before=roi.tobytes()
    assert np.array_equal(preprocess_roi(roi),np.asarray(roi.convert('RGB').resize((256,256),Image.Resampling.BICUBIC)))
    assert roi.tobytes()==roi_before
    encoder.verify_unchanged();assert encoder.state_hash()==state
    files=['src/model_training/exposure_quality_training.py','src/model_training/exposure_quality_inference.py','src/model_training/portrait_exposure_quality.py','src/model_training/reiqa_frozen_features.py','scripts/check_piq23_training_engineering.py','docs/piq23-trainer-engineering-protocol-2026-11-17.md']
    report=dict(passed=True,generated_training_runs=2,real_head_fits=0,correction_fits=0,actual_portrait_reads=0,
        full_width=4096,generated_training_images=72,generated_pairs=828,epochs=50,updates_each=100,
        scalar_adam_max_error=max_adam_error,scalar_minibatch_loss_max_error=max_loss_error,
        unequal_scene_pair_counts=data['scene_pair_counts'],scene_balance_scalar_error=max_balance_error,
        dense_gradient_finite_difference_max_error=max_fd,deterministic_repeat='EXACT',
        invalid_training_test_provenance_id_width_finite='PASS',identical_feature_ambiguity='RETAINED_UNSOLVED',
        generated_encoder_calls=18,encoder_cases=encoder_cases,encoder_unchanged=True,model_state_sha256=state,
        checkpoint_sha256=sha(ROOT/'outputs/reiqa_checkpoint_pilot_v1/quality_aware_r50.pth'),
        versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','Pillow','torch','torchvision']}),
        blas_threads=2,code_sha256={p:sha(ROOT/p) for p in files},generated_head_sha256=sha(OUT/'generated_head.json'),
        scientific_status='ENGINEERING_ONLY_PHOTOGRAPHIC_USEFULNESS_NOT_ESTABLISHED')
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
