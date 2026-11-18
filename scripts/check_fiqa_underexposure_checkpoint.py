"""One selected external checkpoint readiness; no photos/inference/dependency changes."""
from pathlib import Path
import json,re,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/fiqa_underexposure_source_review_v1'
NAME='deit_tiny_checkpoint8.pth'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)

def download():
    import requests
    p=OUT/NAME
    if p.exists():raise FileExistsError(p)
    password=re.search(r'\*\*Password\*\*:\s*([^\n]+)',(OUT/'README.md').read_text(encoding='utf-8')).group(1).strip()
    url='https://cloud.h-da.de/public.php/webdav/additional_models/tiny_model_checkpoints/'+NAME
    total=0
    try:
        with requests.get(url,auth=('8of8Aotr7F5Hy5z',password),timeout=(7,25),stream=True) as r:
            r.raise_for_status()
            assert int(r.headers['Content-Length'])==22155985
            with p.open('xb') as f:
                for chunk in r.iter_content(65536):
                    total+=len(chunk)
                    if total>24*1024**2:raise ValueError('Selected asset ceiling exceeded')
                    f.write(chunk)
        assert total==22155985
        write(OUT/'checkpoint_receipt.json',dict(bytes=total,sha256=sha(p),url=url,
              selected_before_inference=True,variants_downloaded=0,photos_downloaded=0,
              code_ref='f776d0d8a071f5c70dde4f408f8f86ecd07e27db',
              scope_contract_sha256=sha(ROOT/'docs/face-underexposure-next-step-2026-11-17.md')))
        print('PASS one selected22.2MBcheckpoint downloaded; zero photos/other models.')
    except Exception as exc:
        write(OUT/'download_failure.json',dict(error=repr(exc),bytes_received=total));raise

def inspect():
    import torch
    p=OUT/NAME;receipt=json.loads((OUT/'checkpoint_receipt.json').read_text(encoding='utf-8'))
    assert sha(p)==receipt['sha256'] and p.stat().st_size==receipt['bytes']
    state=torch.load(p,map_location='cpu',weights_only=True)
    assert isinstance(state,dict) and state and all(isinstance(k,str) and isinstance(v,torch.Tensor) for k,v in state.items())
    assert all(torch.isfinite(v).all().item() for v in state.values())
    assert tuple(state['head.weight'].shape)==(2,192) and tuple(state['head.bias'].shape)==(2,)
    assert tuple(state['patch_embed.proj.weight'].shape)==(192,3,16,16)
    assert tuple(state['pos_embed'].shape)==(1,197,192) and tuple(state['cls_token'].shape)==(1,1,192)
    assert sorted({int(k.split('.')[1]) for k in state if k.startswith('blocks.')})==list(range(12))
    write(OUT/'checkpoint_inspection.json',dict(passed=True,safe_weights_only=True,finite=True,
          checkpoint_sha256=receipt['sha256'],tensors=len(state),tensor_elements=sum(v.numel() for v in state.values()),
          shapes={k:list(v.shape) for k,v in state.items()},native_model_loaded=False,generated_calls=0,
          portrait_calls=0,training_fits=0,model_ready=False))
    print('PASS safe finite tiny-DeiT shaped state; native inference remains unverified.')

if __name__=='__main__':
    {'download':download,'inspect':inspect}[sys.argv[1]]()
