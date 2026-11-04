"""Strict checkpoint load and synthetic forwards in isolated inference env."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import torch
import segmentation_models_pytorch as smp
from safetensors.torch import load_file

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT / 'outputs/faceocc_loading_v1'
    if out.exists():
        raise FileExistsError(out)
    weights = ROOT / 'models/faceocc_candidate_v1/model.safetensors'
    expected = '5d6d27a9cb221692425840a80eb4efc07e6245670b233e2eb618e83fd9b7caf6'
    assert hashlib.sha256(weights.read_bytes()).hexdigest() == expected
    torch.set_num_threads(2)
    model = smp.Unet(encoder_name='resnet18', encoder_depth=5, encoder_weights=None,
        decoder_use_norm='batchnorm', decoder_channels=(256,128,64,32,16),
        decoder_attention_type=None, decoder_interpolation='nearest',
        in_channels=3, classes=1, activation=None)
    result = model.load_state_dict(load_file(str(weights), device='cpu'), strict=True)
    assert not result.missing_keys and not result.unexpected_keys
    model.eval()
    image = torch.zeros((1,3,256,256), dtype=torch.float32)
    mean = torch.tensor([.485,.456,.406]).view(1,3,1,1)
    std = torch.tensor([.229,.224,.225]).view(1,3,1,1)
    normalized = (image-mean)/std
    with torch.inference_mode():
        logits = model(normalized)
        replay = model(normalized)
    assert logits.shape == (1,1,256,256) and torch.isfinite(logits).all()
    assert torch.equal(logits,replay)
    report = dict(status='strict_load_and_synthetic_forward_passed', executable=sys.executable,
        python=platform.python_version(), packages={k:importlib.metadata.version(k) for k in
            ['torch','torchvision','segmentation-models-pytorch','safetensors','numpy']},
        weight_sha256=expected, missing_keys=[], unexpected_keys=[],
        input_shape=list(image.shape),output_shape=list(logits.shape),
        finite=True, repeat_exact=True, photos_processed=0, model_adopted=False,
        source_runtime='architecture reproduced from pinned source; not imported training/dataset scripts',
        remaining='TrueHue landmark correspondence and gallery input adaptation not established; no image inference')
    out.mkdir()
    (out/'verification.json').write_text(json.dumps(report,indent=2))
    (out/'environment-freeze.txt').write_text('\n'.join(sorted(
        str(d.metadata['Name'])+'=='+str(d.version) for d in importlib.metadata.distributions())),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
