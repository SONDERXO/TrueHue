"""Frozen five coefficients on fixed66cached inputs; no external RGB output."""
from pathlib import Path
import sys,json,hashlib,platform,importlib.metadata
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from check_ppr_parameter_ready import ParametersOnly,state_hash
from src.model_training.reiqa_frozen_features import generated_inputs
ASSET=ROOT/'outputs/ppr_parameter_access_v1';OUT=ROOT/'outputs/ppr_parameter_features_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def main():
    if OUT.exists():raise FileExistsError(OUT)
    ready=read(ASSET/'readiness_verification.json');assert ready['passed']
    versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','Pillow','torch','torchvision']})
    assert versions==ready['versions']
    checkpoint=ASSET/'classifier_-1.pth';assert sha(checkpoint)==ready['checkpoint_sha256']
    plan_path=ROOT/'outputs/camera_halfstop_data_v1/plan_PRIVATE.json'
    plan=read(plan_path);done=read(plan_path.parent/'completion_PRIVATE.json');assert sha(plan_path)==done['plan_sha256']
    rows=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','input_pack','input_pack_sha256']} for r in plan['rows']]
    assert len(rows)==66 and len({r['case_id'] for r in rows})==66
    bound={p.relative_to(ROOT).as_posix():sha(p) for p in [checkpoint,ASSET/'readiness_verification.json',Path(__file__),ROOT/'scripts/check_ppr_parameter_ready.py',ROOT/'docs/ppr-parameter-correction-protocol-2026-11-17.md',plan_path]}
    for r in rows:
        assert r['generated_fixture'] is False
        p=(ROOT/r['input_pack']).resolve();p.relative_to(ROOT/'outputs/camera_halfstop_data_v1/cases')
        assert sha(p)==r['input_pack_sha256'];bound[p.relative_to(ROOT).as_posix()]=r['input_pack_sha256']
    OUT.mkdir();write(OUT/'bindings.json',bound)
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    net=ParametersOnly();net.load_state_dict(torch.load(checkpoint,map_location='cpu',weights_only=True),strict=True)
    net.eval().requires_grad_(False);before=state_hash(net);assert before==ready['state_sha256']
    def coefficients(image):
        x=torch.from_numpy((image.astype(np.float32)/255).transpose((2,0,1)).copy()).unsqueeze(0)
        with torch.inference_mode():v=net(x).cpu().numpy().reshape(-1).copy()
        assert v.shape==(5,) and v.dtype==np.float32 and np.isfinite(v).all()
        return v.astype(float).tolist()
    assert coefficients(generated_inputs()[0][1])==ready['records'][0]['output_coefficients']
    results=[];access=[]
    try:
        for r in rows:
            with np.load(ROOT/r['input_pack'],allow_pickle=False) as pack:image=pack['input'].copy()
            assert image.shape==(256,256,3) and image.dtype==np.uint8
            image_sha=hashlib.sha256(image.tobytes()).hexdigest();v=coefficients(image)
            assert hashlib.sha256(image.tobytes()).hexdigest()==image_sha
            results.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture']}|dict(coefficients=v,input_rgb_sha256=image_sha))
            access.append(dict(case_id=r['case_id'],keys=['input']))
            if len(results)%11==0:print('Portrait parameter features '+str(len(results))+'/66',flush=True)
        assert state_hash(net)==before
        for p,h in bound.items():assert sha(ROOT/p)==h
        write(OUT/'records.json',results);write(OUT/'access.json',access)
        write(OUT/'verification.json',dict(passed=True,cases=66,coefficients=330,actual_network_calls=66,generated_contract_calls=1,
             training_fits=0,external_RGB_outputs=0,parameter_model_unchanged=True,input_immutable=True,
             records_sha256=sha(OUT/'records.json'),checkpoint_sha256=ready['checkpoint_sha256'],versions=versions,model_ready=False))
        print('PASS66x5frozen coefficients;0training/0external correction pixels.',flush=True)
    except Exception as exc:
        write(OUT/'failure.json',dict(error=repr(exc),completed_cases=len(results),training_fits=0));raise
if __name__=='__main__':main()
