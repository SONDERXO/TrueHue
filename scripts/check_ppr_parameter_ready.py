"""Strict safe loading and six generated forwards only; no actual portraits."""
from pathlib import Path
import sys, json, hashlib, platform, importlib.metadata
import numpy as np
import torch
from torchvision.models import resnet18
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src.model_training.reiqa_frozen_features import generated_inputs
from src.model_training.portrait_exposure_quality import exposure_probe

OUT = ROOT / 'outputs/ppr_parameter_access_v1'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def state_hash(net):
    h = hashlib.sha256()
    for key, tensor in net.state_dict().items():
        h.update(key.encode()); h.update(tensor.detach().cpu().numpy().tobytes())
    return h.hexdigest()


class ParametersOnly(torch.nn.Module):
    """Own isolated equivalent of upstream resnet18_224(out_dim=5,aug_test=False)."""
    def __init__(self):
        super().__init__()
        self.upsample = torch.nn.Upsample(size=(224, 224), mode='bilinear', align_corners=False)
        self.model = resnet18(weights=None)  # NEVER download ImageNet weights.
        self.model.fc = torch.nn.Linear(512, 5)

    def forward(self, x):
        return self.model(self.upsample(x))


def main():
    result_path = OUT / 'readiness_verification.json'
    if result_path.exists(): raise FileExistsError(result_path)
    receipt = json.loads((OUT / 'checkpoint_receipt.json').read_text())
    checkpoint = OUT / 'classifier_-1.pth'
    assert sha(checkpoint) == receipt['checkpoint_sha256']
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    try:
        state = torch.load(checkpoint, map_location='cpu', weights_only=True)
        assert isinstance(state, dict) and state
        assert all(isinstance(k, str) and isinstance(v, torch.Tensor) and torch.isfinite(v).all()
                   for k, v in state.items())
        net = ParametersOnly()
        loaded = net.load_state_dict(state, strict=True)
        assert not loaded.missing_keys and not loaded.unexpected_keys
        assert net.model.fc.weight.shape == (5, 512)
        assert sum(p.numel() for p in net.parameters()) == 11179077
        net.eval().requires_grad_(False)
        before = state_hash(net)
        base = generated_inputs()[0][1]
        records = []
        for name, image in [('generated_base', base), ('generated_minus', exposure_probe(base, -.5)),
                            ('generated_plus', exposure_probe(base, .5))]:
            original = image.copy()
            # Upstream customto_tensor explicitly divides RGB8 by255 (RGB16 by65535).
            array = image.astype(np.float32) / 255
            x = torch.from_numpy(array.transpose((2, 0, 1)).copy()).unsqueeze(0)
            with torch.inference_mode():
                a = net(x); b = net(x)
            assert a.shape == (1, 5) and torch.isfinite(a).all() and torch.equal(a, b)
            assert np.array_equal(image, original)
            assert torch.equal(net.upsample(x), torch.nn.functional.interpolate(x, size=(224, 224),
                               mode='bilinear', align_corners=False))
            records.append(dict(name=name, output_coefficients=a.numpy().reshape(-1).tolist(),
                                repeat_exact=True, input_immutable=True))
        assert state_hash(net) == before
        result = dict(passed=True, status='CHECKPOINT_AND_GENERATED_MECHANICS_READY_ONLY',
            checkpoint_sha256=sha(checkpoint), checkpoint_bytes=checkpoint.stat().st_size,
            transferred_bytes=receipt['transferred'], safe_weights_only=True, strict_keys=True,
            tensors=len(state), parameters=11179077, outputs=5, generated_forward_calls=6,
            actual_portrait_calls=0, training_fits=0, correction_renders=0, records=records,
            weights_buffers_unchanged=True, no_ImageNet_download=True, no_trilinear_or_LUT=True,
            no_dependency_changes=True, author_runtime_parity_claim=False,
            preprocessing='RGB8 float32/255; NCHW; bilinear224 align_corners=False; no ImageNet normalization',
            source_revision='239490b8a8e917f2c29e3016ee2f6543c3c1bfba',
            source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in (OUT / 'source').rglob('*') if p.is_file()},
            code_sha256=sha(Path(__file__)), state_sha256=before,
            versions=dict(Python=platform.python_version(), **{p:importlib.metadata.version(p)
                          for p in ['numpy','Pillow','torch','torchvision']}),
            correction_quality_established=False, model_ready=False)
        with result_path.open('x', encoding='utf-8') as f:
            json.dump(result, f, indent=2); f.write('\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','records')}, indent=2))
    except Exception as exc:
        failure = OUT / 'readiness_failure.json'
        if not failure.exists(): failure.write_text(json.dumps({'error':repr(exc),'actual_portrait_calls':0,'training_fits':0})+'\n')
        raise


if __name__ == '__main__': main()
