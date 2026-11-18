"""Generated-only, frozen quality encoder mechanics. No project-photo loader."""
import ast
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import pickletools
import platform
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/reiqa_frozen_generated_v1'
SOURCE = ROOT / 'outputs/reiqa_feature_feasibility_v1/source'
CHECKPOINT = ROOT / 'outputs/reiqa_checkpoint_pilot_v1/quality_aware_r50.pth'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def peak_working_set():
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (x, ctypes.c_size_t) for x in ['PeakWorkingSetSize', 'WorkingSetSize',
            'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage',
            'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage',
            'PagefileUsage', 'PeakPagefileUsage']]
    value = Counters()
    value.cb = ctypes.sizeof(value)
    kernel = ctypes.WinDLL('kernel32')
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL('psapi')
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(value), value.cb):
        raise OSError('GetProcessMemoryInfo failed')
    return value.PeakWorkingSetSize

def main():
    OUT.mkdir(exist_ok=False)
    result = {'status': 'STARTED', 'dataset_reads': 0, 'correction_tree_fits': 0,
              'python': platform.python_version(), 'checkpoint_sha256': digest(CHECKPOINT)}
    try:
        receipt = json.loads((ROOT / 'outputs/reiqa_checkpoint_pilot_v1/transfer_PRIVATE.json').read_text())
        assert result['checkpoint_sha256'] == receipt['sha256']
        with zipfile.ZipFile(CHECKPOINT) as z:
            metadata = [i for i in z.infolist() if i.filename.endswith('/data.pkl')]
            assert len(metadata) == 1 and metadata[0].file_size < 1024*1024
            data = z.read(metadata[0])
            result['archive_members'] = len(z.infolist())
            result['pickle_globals'] = sorted({str(a) for o,a,_ in pickletools.genops(data) if o.name == 'GLOBAL'})
        import torch
        import numpy as np
        import PIL
        from PIL import Image
        import torchvision
        from torchvision.models import resnet50
        torch.set_num_threads(2)
        torch.use_deterministic_algorithms(True)
        result['versions'] = {'torch': torch.__version__, 'torchvision': torchvision.__version__,
                              'numpy': np.__version__, 'pillow': PIL.__version__}
        checkpoint = torch.load(CHECKPOINT, map_location='cpu', weights_only=True)
        result['top_keys'] = list(checkpoint)
        assert isinstance(checkpoint, dict) and isinstance(checkpoint['model'], dict)
        state = checkpoint['model']
        assert all(isinstance(k, str) and isinstance(v, torch.Tensor) for k,v in state.items())
        assert all(torch.isfinite(v).all().item() for v in state.values())
        result['state_inventory'] = {k: {'shape': list(v.shape), 'dtype': str(v.dtype)} for k,v in state.items()}
        prefix = 'module.encoder.'
        weights = {k[len(prefix):]: v for k,v in state.items() if k.startswith(prefix)}
        assert weights and all(k.startswith(prefix) or k.startswith('module.head.') for k in state)
        # Execute only audited architecture definitions from the previously pinned source.
        source_file = SOURCE / 'networks/resnet.py'
        tree = ast.parse(source_file.read_text(encoding='utf-8'))
        selected = ['conv3x3', 'conv1x1', 'Bottleneck', 'ResNet']
        nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in selected]
        assert sorted(n.name for n in nodes) == sorted(selected)
        namespace = {'torch': torch, 'nn': torch.nn}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source_file), 'exec'), namespace)
        model = namespace['ResNet'](namespace['Bottleneck'], [3,4,6,3])
        model.load_state_dict(weights, strict=True)
        model.eval().requires_grad_(False)
        result['encoder_parameters'] = sum(p.numel() for p in model.parameters())
        assert result['encoder_parameters'] == 23508032
        before = {k:v.clone() for k,v in model.state_dict().items()}
        # Independent installed topology comparison; never download ImageNet weights.
        comparison = resnet50(weights=None)
        comparison.fc = torch.nn.Identity()
        comparison.load_state_dict(weights, strict=True)
        comparison.eval().requires_grad_(False)
        y,x = np.mgrid[0:256,0:256]
        base = np.stack([.1+.7*x/255, .15+.6*y/255,
                         .2+.4*(x+y)/510+.05*np.sin(x/7)*np.cos(y/9)], axis=2)
        settings = [('identity',1.,1.,1.), ('gamma_under',1.4,1.,1.),
                    ('gamma_over',.7,1.,1.), ('red',1.,1.1,1.),
                    ('blue',1.,1.,.9), ('combined',1.4,1.1,.9)]
        result['generated_settings'] = settings
        result['preprocessing'] = 'RGB8 round clip(base**gamma*[r,1,b]*255); Pillow default RGB resize256->128; float32/255; no normalization'
        def tensors(rgb):
            image = Image.fromarray(rgb)
            half = image.resize((128,128))
            return [torch.from_numpy(np.asarray(i).copy()).permute(2,0,1).float().div(255).unsqueeze(0) for i in (image,half)]
        def features(m, ts):
            with torch.inference_mode():
                return torch.cat([m(t) for t in ts], dim=1)
        base_rgb = np.rint(np.clip(base,0,1)*255).astype(np.uint8)
        ts = tensors(base_rgb)
        start = time.perf_counter()
        reference = features(model,ts)
        result['first_inference_seconds'] = time.perf_counter()-start
        other = features(comparison,ts)
        result['independent_topology_max_abs_diff'] = (reference-other).abs().max().item()
        assert torch.equal(reference,other)
        records = []
        arrays = {}
        for name,gamma,r,b in settings:
            rgb = np.rint(np.clip(base**gamma*np.array([r,1,b]),0,1)*255).astype(np.uint8)
            ts = tensors(rgb)
            start = time.perf_counter()
            f = features(model,ts)
            elapsed = time.perf_counter()-start
            assert f.shape == (1,4096) and torch.isfinite(f).all()
            arrays[name] = f.numpy()
            records.append({'case':name,'seconds':elapsed,
                'feature_l2_change':(f-reference).norm().item(),
                'max_abs_change':(f-reference).abs().max().item(),
                'input_sha256':hashlib.sha256(rgb.tobytes()).hexdigest()})
            if name == 'identity':
                assert torch.equal(f,reference)
        result['records'] = records
        result['repeat_identity_exact'] = True
        result['weights_and_buffers_unchanged'] = all(torch.equal(v,before[k]) for k,v in model.state_dict().items())
        assert result['weights_and_buffers_unchanged']
        result['peak_process_working_set_bytes'] = peak_working_set()
        np.savez(OUT/'generated_features.npz', **arrays)
        result['generated_features_sha256'] = digest(OUT/'generated_features.npz')
        result['source_bindings'] = {str(p.relative_to(ROOT)):digest(p) for p in [source_file,SOURCE/'demo_quality_aware_feats.py',SOURCE/'LICENSE',Path(__file__)]}
        result['status'] = 'GENERATED_MECHANICS_PASS_ONLY'
    except Exception as exc:
        result.update(status='STOPPED', error=f'{type(exc).__name__}: {exc}')
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['state_inventory','source_bindings']},indent=2))

if __name__ == '__main__':
    main()
