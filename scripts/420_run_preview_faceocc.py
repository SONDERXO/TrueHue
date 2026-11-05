"""One fixed CPU FaceOcc pass for a frozen development-preview request."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
WEIGHT_SHA = '5d6d27a9cb221692425840a80eb4efc07e6245670b233e2eb618e83fd9b7caf6'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--request',required=True,type=Path)
    request=parser.parse_args().request.resolve()
    if not request.is_relative_to((ROOT/'outputs').resolve()):
        raise ValueError('Preview request must be under project outputs')
    folder=request.parent
    if (folder/'faceocc_logits.npy').exists() or (folder/'inference.json').exists():
        raise FileExistsError('Prediction exists; no repeat pass')
    plan=json.loads(request.read_text(encoding='utf-8'))
    if not all(sha(p)==h for p,h in plan['input_sha256'].items()):
        raise ValueError('Frozen preview input changed')
    weights=ROOT/'models/faceocc_candidate_v1/model.safetensors'
    if sha(weights)!=WEIGHT_SHA:
        raise ValueError('Pinned FaceOcc weights required')
    # A failed/partial forward is retained; do not silently retry it.
    with (folder/'inference_started.json').open('x',encoding='utf-8') as stream:
        json.dump(dict(request_sha256=sha(request)),stream)
    import numpy as np
    from PIL import Image
    import torch
    import segmentation_models_pytorch as smp
    from safetensors.torch import load_file
    torch.set_num_threads(2)
    model=smp.Unet(encoder_name='resnet18',encoder_depth=5,encoder_weights=None,
        decoder_use_norm='batchnorm',decoder_channels=(256,128,64,32,16),
        decoder_attention_type=None,decoder_interpolation='nearest',in_channels=3,classes=1,activation=None)
    model.load_state_dict(load_file(str(weights),device='cpu'),strict=True);model.eval()
    image=np.asarray(Image.open(plan['aligned_path']).convert('RGB'),dtype=np.float32)
    if image.shape!=(256,256,3):raise ValueError('Aligned RGB256 input required')
    mean=np.array([.485,.456,.406],np.float32);std=np.array([.229,.224,.225],np.float32)
    tensor=torch.from_numpy(np.ascontiguousarray(((image/255-mean)/std).transpose(2,0,1)[None]))
    with torch.inference_mode():logits=model(tensor).cpu().numpy()
    if logits.shape!=(1,1,256,256) or not np.isfinite(logits).all():
        raise ValueError('Finite1x1x256x256 output required')
    if not all(sha(p)==h for p,h in plan['input_sha256'].items()):
        raise ValueError('Preview inputs changed during inference')
    np.save(folder/'faceocc_logits.npy',logits[0,0])
    (folder/'inference.json').write_text(json.dumps(dict(forwards=1,fits=0,
        request_sha256=sha(request),logits_sha256=sha(folder/'faceocc_logits.npy')),indent=2))


if __name__=='__main__':main()
