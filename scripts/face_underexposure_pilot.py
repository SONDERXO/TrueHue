"""One approved frozen66input test; no fitting or correction rendering."""
from pathlib import Path
import sys,os,json,hashlib,math,platform,importlib.metadata,time
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'outputs/fiqa_tiny_runtime_v2/site'
sys.path.insert(0,str(SITE));sys.path.insert(0,str(ROOT))
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
import numpy as np
import torch
import timm
from PIL import Image
from torchvision import transforms
from src.model_training.reiqa_frozen_features import generated_inputs
from src.model_training.portrait_exposure_quality import exposure_probe
ASSET=ROOT/'outputs/fiqa_underexposure_source_review_v1'
QA=ROOT/'outputs/face_underexposure_native_v1'
DESIGN=ROOT/'outputs/face_underexposure_pilot_design_v1'
OUT=ROOT/'outputs/face_underexposure_pilot_v1'
ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']
FILES=['scripts/face_underexposure_pilot.py','docs/face-underexposure-pilot-protocol-2026-11-17.md',
       'docs/face-underexposure-runtime-compatibility-2026-11-17.md',
       'scripts/prepare_fiqa_tiny_runtime.py','scripts/prepare_fiqa_tiny_runtime_v2.py',
       'src/model_training/reiqa_frozen_features.py','src/model_training/portrait_exposure_quality.py']
PREPROCESS=transforms.Compose([transforms.Resize((224,224)),transforms.ToTensor(),
             transforms.Normalize([.485,.456,.406],[.229,.224,.225])])

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
def versions():return dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['torch','torchvision','Pillow','numpy','timm','huggingface-hub','safetensors','PyYAML']})
def state_hash(net):
    h=hashlib.sha256()
    for k,v in net.state_dict().items():h.update(k.encode());h.update(v.detach().cpu().numpy().tobytes())
    return h.hexdigest()

def preprocess(image):
    if not isinstance(image,np.ndarray) or image.shape!=(256,256,3) or image.dtype!=np.uint8:
        raise ValueError('Expected256x256RGB8cached input')
    crop=image[32:256,16:240,:].copy()
    assert crop.shape==(224,224,3)
    return PREPROCESS(Image.fromarray(crop)).unsqueeze(0),crop

def load_model():
    receipt=read(ASSET/'checkpoint_receipt.json');p=ASSET/'deit_tiny_checkpoint8.pth'
    assert sha(p)==receipt['sha256']
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    net=timm.create_model('deit_tiny_patch16_224',pretrained=False,num_classes=2)
    loaded=net.load_state_dict(torch.load(p,map_location='cpu',weights_only=True),strict=True)
    assert not loaded.missing_keys and not loaded.unexpected_keys
    net.eval().requires_grad_(False)
    assert len(net.state_dict())==152 and sum(p.numel() for p in net.parameters())==5524802
    return net

def infer(net,image):
    x,crop=preprocess(image)
    with torch.inference_mode():out=net(x)
    assert out.shape==(1,2) and out.dtype==torch.float32 and torch.isfinite(out).all()
    probs=torch.softmax(out,dim=1).reshape(-1).tolist();logits=out.reshape(-1).tolist()
    maximum=max(logits);exps=[math.exp(v-maximum) for v in logits];scalar=[v/math.fsum(exps) for v in exps]
    error=max(abs(a-b) for a,b in zip(probs,scalar));assert error<=2e-7
    klass=int(out.argmax(dim=1).item());assert klass==(1 if logits[1]>logits[0] else 0)
    return dict(logits=logits,probabilities=probs,under_probability=probs[1],predicted_class=klass,
                scalar_softmax=scalar,softmax_max_error=error,logit_margin=logits[1]-logits[0],
                crop_rgb_sha256=hashlib.sha256(crop.tobytes()).hexdigest())

def native():
    if QA.exists():raise FileExistsError(QA)
    installation=read(SITE.parent/'installation.json');assert installation['passed']
    for p,h in installation['site_files'].items():assert sha(SITE/p)==h
    source=read(ASSET/'verification.json');assert source['passed']
    for p,h in source['bindings'].items():assert sha(ROOT/p)==h
    QA.mkdir();records=[]
    try:
        net=load_model();before=state_hash(net);base=generated_inputs()[0][1]
        for name,image in [('base',base),('minus',exposure_probe(base,-.5)),('plus',exposure_probe(base,.5))]:
            saved=image.copy();x,crop=preprocess(image)
            expected=(crop.astype(np.float32)/np.float32(255)-np.array([.485,.456,.406],np.float32))/np.array([.229,.224,.225],np.float32)
            assert np.array_equal(x.numpy()[0],expected.transpose(2,0,1))
            a=infer(net,image);b=infer(net,image);assert a==b and np.array_equal(image,saved)
            records.append(dict(name=name,**a))
        for bad in [np.zeros((255,256,3),np.uint8),np.zeros((256,256,3),np.float32),np.zeros((256,256,4),np.uint8)]:
            try:preprocess(bad)
            except ValueError:pass
            else:raise AssertionError('Invalid input accepted')
        assert state_hash(net)==before
        write(QA/'verification.json',dict(passed=True,strict_native_loaded=True,generated_calls=6,portrait_calls=0,
              state_sha256=before,repeat_exact=True,input_immutable=True,model_unchanged=True,
              preprocessing_exact=True,invalid_before_forward=3,versions=versions(),records=records,
              checkpoint_sha256=sha(ASSET/'deit_tiny_checkpoint8.pth'),
              code_sha256={p:sha(ROOT/p) for p in FILES},
              installation_sha256=sha(SITE.parent/'installation.json')))
        print('PASS native tiny-DeiT/strict152tensors/6generatedrepeat/preprocess/softmax/immutable checks; zero portraits.')
    except Exception as exc:write(QA/'failure.json',dict(error=repr(exc),completed_generated_images=len(records),portrait_calls=0));raise

def prepare():
    if DESIGN.exists():raise FileExistsError(DESIGN)
    q=read(QA/'verification.json');assert q['passed'] and q['versions']==versions()
    for p,h in q['code_sha256'].items():assert sha(ROOT/p)==h
    assert sha(SITE.parent/'installation.json')==q['installation_sha256']
    data=ROOT/'outputs/camera_halfstop_data_v1';plan=read(data/'plan_PRIVATE.json')
    assert sha(data/'plan_PRIVATE.json')==read(data/'completion_PRIVATE.json')['plan_sha256']
    rows=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','input_pack','input_pack_sha256']} for r in plan['rows']]
    assert len(rows)==len({r['case_id'] for r in rows})==66 and len({r['source_id'] for r in rows})==11
    assert set(r['role'] for r in rows)==set(ROLES)
    previous=read(ROOT/'outputs/ppr_parameter_features_v1/verification.json');assert previous['passed']
    previous_records=ROOT/'outputs/ppr_parameter_features_v1/records.json';assert sha(previous_records)==previous['records_sha256']
    pixel_hashes={r['case_id']:r['input_rgb_sha256'] for r in read(previous_records)}
    assert set(pixel_hashes)=={r['case_id'] for r in rows}
    bound=dict(q['code_sha256'])
    for r in rows:
        assert r['generated_fixture'] is False
        assert sum(x['source_id']==r['source_id'] and x['role']==r['role'] for x in rows)==1
        p=(ROOT/r['input_pack']).resolve();p.relative_to(data/'cases');assert sha(p)==r['input_pack_sha256']
        bound[p.relative_to(ROOT).as_posix()]=r['input_pack_sha256'];r['input_rgb_sha256']=pixel_hashes[r['case_id']]
    for p in [QA/'verification.json',ASSET/'deit_tiny_checkpoint8.pth',ASSET/'verification.json',
              SITE.parent/'installation.json',SITE.parent/'wheel_receipt.json',data/'plan_PRIVATE.json',previous_records]:
        bound[p.relative_to(ROOT).as_posix()]=sha(p)
    DESIGN.mkdir();write(DESIGN/'roster.json',rows);write(DESIGN/'bindings.json',bound)
    write(DESIGN/'authorization.json',dict(exact_user_reply='Okay lets do that',scope='one frozen66existinginput pilot; no correction training',protocol_sha256=sha(ROOT/FILES[1])))
    write(DESIGN/'verification.json',dict(passed=True,cases=66,sources=11,classes=['normal_exposure','under_exposure'],
          crop=[16,32,240,256],native_qa_sha256=sha(QA/'verification.json'),roster_sha256=sha(DESIGN/'roster.json'),
          bindings_sha256=sha(DESIGN/'bindings.json'),authorization_sha256=sha(DESIGN/'authorization.json'),portrait_calls=0,versions=versions()))
    print('PASS bound66input-only roster and fixed protocol; zero portraits/fits.')

def summarize(records):
    assert len(records)==66 and len({r['case_id'] for r in records})==66
    by_role={}
    for role in ROLES:
        rows=[r for r in records if r['role']==role];assert len(rows)==11
        by_role[role]=dict(count=11,flagged_under=sum(r['predicted_class']==1 for r in rows),
              mean_under_probability=math.fsum(r['under_probability'] for r in rows)/11,
              min_under_probability=min(r['under_probability'] for r in rows),max_under_probability=max(r['under_probability'] for r in rows))
    pairs={}
    for family,reference,target in [('pure','identity','exposure_under'),('combined','colour_only','combined_under')]:
        values=[]
        for source in sorted({r['source_id'] for r in records}):
            a=next(r for r in records if r['source_id']==source and r['role']==reference)
            b=next(r for r in records if r['source_id']==source and r['role']==target)
            values.append(dict(source_id=source,reference_case=a['case_id'],under_case=b['case_id'],
                   probability_margin=b['under_probability']-a['under_probability'],logit_margin_change=b['logit_margin']-a['logit_margin']))
        pairs[family]=dict(wins=sum(v['probability_margin']>0 for v in values),ties=sum(v['probability_margin']==0 for v in values),
                           losses=sum(v['probability_margin']<0 for v in values),records=values)
    gates=dict(original_false_flags_zero=by_role['identity']['flagged_under']==0,
               colour_false_flags_zero=by_role['colour_only']['flagged_under']==0,
               pure_under_majority=by_role['exposure_under']['flagged_under']>=6,
               combined_under_majority=by_role['combined_under']['flagged_under']>=6,
               pure_ordering_majority=pairs['pure']['wins']>=6,combined_ordering_majority=pairs['combined']['wins']>=6)
    return dict(by_role=by_role,pairs=pairs,gates=gates,narrow_pilot_pass=all(gates.values()),model_ready=False,
                training_fits=0,calibrated_probabilities=False,official_tone_qualification=False)

def run():
    if OUT.exists():raise FileExistsError(OUT)
    design=read(DESIGN/'verification.json');assert design['passed'] and design['versions']==versions()
    for name,key in [('roster.json','roster_sha256'),('bindings.json','bindings_sha256'),('authorization.json','authorization_sha256')]:
        assert sha(DESIGN/name)==design[key]
    bound=read(DESIGN/'bindings.json')
    for p,h in bound.items():assert sha(ROOT/p)==h
    installation=read(SITE.parent/'installation.json')
    for p,h in installation['site_files'].items():assert sha(SITE/p)==h
    q=read(QA/'verification.json');rows=read(DESIGN/'roster.json')
    OUT.mkdir();records=[];access=[];started=time.monotonic()
    write(OUT/'bindings.json',bound)
    try:
        net=load_model();before=state_hash(net);assert before==q['state_sha256']
        assert infer(net,generated_inputs()[0][1])=={k:v for k,v in q['records'][0].items() if k!='name'}
        for r in rows:
            with np.load(ROOT/r['input_pack'],allow_pickle=False) as pack:image=pack['input'].copy()
            image_hash=hashlib.sha256(image.tobytes()).hexdigest();assert image_hash==r['input_rgb_sha256']
            result=infer(net,image);assert hashlib.sha256(image.tobytes()).hexdigest()==image_hash
            records.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture']}|dict(input_rgb_sha256=image_hash,**result))
            access.append(dict(case_id=r['case_id'],keys=['input']))
            if len(records)%11==0:print('Frozen underexposure scores '+str(len(records))+'/66',flush=True)
        assert state_hash(net)==before
        for p,h in bound.items():assert sha(ROOT/p)==h
        write(OUT/'records.json',records);write(OUT/'score_seal.json',dict(cases=66,records_sha256=sha(OUT/'records.json')))
        summary=summarize(records);write(OUT/'summary.json',summary);write(OUT/'access.json',access)
        write(OUT/'verification.json',dict(passed=True,portrait_calls=66,generated_contract_calls=1,training_fits=0,
              correction_renders=0,input_immutable=True,model_unchanged=True,model_state_sha256=before,
              scores_sealed_before_metrics=True,softmax_max_error=max(r['softmax_max_error'] for r in records),
              narrow_pilot_pass=summary['narrow_pilot_pass'],model_ready=False,versions=versions(),elapsed_seconds=time.monotonic()-started,
              artifacts={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.iterdir()) if p.is_file()}))
        print('COMPLETE66scores; narrow_pilot_pass='+str(summary['narrow_pilot_pass'])+'; zero fits/renders.',flush=True)
    except Exception as exc:
        write(OUT/'failure.json',dict(error=repr(exc),completed_portrait_calls=len(records)));raise

if __name__=='__main__':{'native':native,'prepare':prepare,'run':run}[sys.argv[1]]()
