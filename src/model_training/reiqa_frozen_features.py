"""Isolated frozen encoder; no photo loading, training, or download on import."""
import ast
import hashlib
from pathlib import Path
import numpy as np

CHECKPOINT_SHA = 'aef5e85843ba502206c726da78500ead5ff705da8b4a335d3b25466c93f1f2fb'
SOURCE_SHA = '3a6a98dd96d870df8e4ac291f5a4e3a4c0f82c9bd15cf61b0a85507e4212b278'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

class FrozenQualityEncoder:
    def __init__(self,root):
        import torch
        self.torch=torch
        torch.set_num_threads(2)
        torch.use_deterministic_algorithms(True)
        root=Path(root)
        checkpoint=root/'outputs/reiqa_checkpoint_pilot_v1/quality_aware_r50.pth'
        source=root/'outputs/reiqa_feature_feasibility_v1/source/networks/resnet.py'
        assert sha(checkpoint)==CHECKPOINT_SHA and sha(source)==SOURCE_SHA
        payload=torch.load(checkpoint,map_location='cpu',weights_only=True)
        state=payload['model']
        assert all(isinstance(v,torch.Tensor) and torch.isfinite(v).all() for v in state.values())
        assert all(k.startswith('module.encoder.') or k.startswith('module.head.') for k in state)
        nodes=[n for n in ast.parse(source.read_text(encoding='utf-8')).body
               if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['conv3x3','conv1x1','Bottleneck','ResNet']]
        assert len(nodes)==4
        namespace={'torch':torch,'nn':torch.nn}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),namespace)
        self.model=namespace['ResNet'](namespace['Bottleneck'],[3,4,6,3])
        self.model.load_state_dict({k[len('module.encoder.'):]:v for k,v in state.items() if k.startswith('module.encoder.')},strict=True)
        self.model.eval().requires_grad_(False)
        assert sum(p.numel() for p in self.model.parameters())==23508032
        self.initial_state=self.state_hash()

    def state_hash(self):
        h=hashlib.sha256()
        for key,value in self.model.state_dict().items():
            h.update(key.encode());h.update(value.detach().cpu().numpy().tobytes())
        return h.hexdigest()

    def encode(self,rgb):
        from PIL import Image
        if rgb.shape!=(256,256,3) or rgb.dtype!=np.uint8:
            raise ValueError('Exact256x256RGB8 input required; no resize fallback')
        image=Image.fromarray(rgb)
        images=[image,image.resize((128,128))]
        torch=self.torch
        with torch.inference_mode():
            values=[self.model(torch.from_numpy(np.asarray(i).copy()).permute(2,0,1).float().div(255).unsqueeze(0)) for i in images]
            result=torch.cat(values,dim=1).cpu().numpy().reshape(-1).copy()
        assert result.shape==(4096,) and result.dtype==np.float32 and np.isfinite(result).all()
        return result

    def verify_unchanged(self):
        assert not self.model.training and all(not p.requires_grad for p in self.model.parameters())
        assert self.state_hash()==self.initial_state

def generated_inputs():
    y,x=np.mgrid[0:256,0:256]
    base=np.stack([.1+.7*x/255,.15+.6*y/255,.2+.4*(x+y)/510+.05*np.sin(x/7)*np.cos(y/9)],axis=2)
    settings=[('identity',1.,1.,1.),('gamma_under',1.4,1.,1.),('gamma_over',.7,1.,1.),
              ('red',1.,1.1,1.),('blue',1.,1.,.9),('combined',1.4,1.1,.9)]
    return [(name,np.rint(np.clip(base**g*np.array([r,1,b]),0,1)*255).astype(np.uint8)) for name,g,r,b in settings]
