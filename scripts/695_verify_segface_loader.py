"""Isolated CPU strict load and synthetic interface checks; no private images."""
from pathlib import Path
import sys,json,hashlib,shutil,importlib,importlib.metadata,traceback
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/segface_loader_check_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve loader check')
    selection_path=ROOT/'outputs/segface_route_selection_v1/selection_PRIVATE.json'
    s=json.loads(selection_path.read_text());weights=ROOT/'models/segface_mobilenet_candidate_v1/model_299.pt'
    assert sha(weights)==s['weight']['published_sha256']
    snap=selection_path.parent/'source_snapshot'
    for p,info in s['source_snapshots'].items():assert sha(snap/p)==info['sha256']
    OUT.mkdir();package=OUT/'source';(package/'network/models').mkdir(parents=True)
    (package/'network/__init__.py').write_text('')
    (package/'network/models/__init__.py').write_text('')
    src=(snap/'network/models/segface_celeb.py').read_text()
    assert src.count('mobilenet_v3_large(pretrained=True)')==1
    src=src.replace('mobilenet_v3_large(pretrained=True)','mobilenet_v3_large(weights=None)')
    (package/'network/models/segface_celeb.py').write_text(src)
    for p in ['transformer.py','utils_models.py']:
        shutil.copyfile(ROOT/'outputs/segface_loader_sources_v1/network/models'/p,package/'network/models'/p)
    shutil.copyfile(snap/'LICENSE',package/'LICENSE.SegFace-MIT.txt')
    shutil.copyfile(ROOT/'outputs/segface_loader_sources_v1/LICENSE.Meta-SAM-Apache-2.0.txt',package/'LICENSE.Meta-SAM-Apache-2.0.txt')
    try:
        import torch,torchvision,numpy as np
        from PIL import Image
        from torchvision import transforms
        from torchvision.transforms import InterpolationMode
        import urllib.request,socket
        network_attempts=[]
        def reject(*args,**kwargs):
            network_attempts.append('network_attempt');raise RuntimeError('Network disabled for isolated loader')
        urllib.request.urlopen=reject;torch.hub.download_url_to_file=reject;socket.socket.connect=reject
        torch.set_num_threads(2);torch.manual_seed(42)
        sys.path.insert(0,str(package))
        cls=importlib.import_module('network.models.segface_celeb').SegFaceCeleb
        model=cls(512,'mobilenet')
        checkpoint=torch.load(weights,map_location='cpu',weights_only=True)
        state=checkpoint['state_dict_backbone'];expected=model.state_dict()
        assert set(state)==set(expected)
        for key,value in state.items():assert value.shape==expected[key].shape and value.dtype==expected[key].dtype,(key,value.shape,expected[key].shape)
        status=model.load_state_dict(state,strict=True);assert not status.missing_keys and not status.unexpected_keys
        model.eval()
        pixels=np.arange(193*257*3,dtype=np.uint32).reshape(193,257,3)%256
        pil=Image.fromarray(pixels.astype(np.uint8))
        reference=transforms.Compose([transforms.Resize((512,512),interpolation=InterpolationMode.BICUBIC),transforms.ToTensor(),transforms.Normalize([.485,.456,.406],[.229,.224,.225])])(pil)
        array=np.asarray(pil.resize((512,512),Image.Resampling.BICUBIC)).copy()
        tensor=torch.from_numpy(array.transpose(2,0,1).copy()).float()/255.
        tensor=(tensor-torch.tensor([.485,.456,.406])[:,None,None])/torch.tensor([.229,.224,.225])[:,None,None]
        assert torch.equal(reference,tensor)
        with torch.inference_mode():
            logits=model(tensor[None],None,None);again=model(tensor[None],None,None)
        assert logits.shape==(1,19,512,512) and torch.isfinite(logits).all() and torch.equal(logits,again)
        decoded=logits.softmax(1).argmax(1)
        assert torch.equal(decoded,logits.argmax(1))
        synthetic=torch.zeros((1,19,1,19))
        for i in range(19):synthetic[0,i,0,i]=1
        assert synthetic.argmax(1).flatten().tolist()==list(range(19))
        assert not network_attempts
        output=dict(passed=True,checkpoint_sha256=sha(weights),state_entries=len(state),
            parameter_elements=sum(p.numel() for p in model.parameters()),missing_keys=[],unexpected_keys=[],
            key_shape_dtype_parity=True,weights_only=True,strict_load=True,input_shape=list(tensor[None].shape),
            output_shape=list(logits.shape),finite=True,synthetic_forwards=2,repeat_exact=True,
            preprocess_matches_author_torchvision_exact=True,class_ids_checked=19,class_names=s['class_names'],
            output_softmax_argmax_parity=True,network_attempts=0,
            source_patch='Only MobileNet constructor pretrained=True -> weights=None; minimal package initializers avoid unrelated model imports.',
            input_sha256={str(p):sha(p) for p in [selection_path,weights,Path(__file__)]},
            staged_source_sha256={str(p):sha(p) for p in package.rglob('*') if p.is_file() and '__pycache__' not in str(p)},
            executable=sys.executable,packages={p:importlib.metadata.version(p) for p in ['torch','torchvision','numpy','pillow']},
            private_image_reads=0,holdout_image_reads=0,adopted=False)
        (OUT/'verification_PRIVATE.json').write_text(json.dumps(output,indent=2));print(json.dumps({k:v for k,v in output.items() if 'sha256' not in k},indent=2))
    except Exception:
        (OUT/'failure_PRIVATE.json').write_text(json.dumps(dict(failure=traceback.format_exc()),indent=2));raise
if __name__=='__main__':main()
