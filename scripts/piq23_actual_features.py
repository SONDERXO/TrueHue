"""One immutable frozen vector per admitted Exposure input; no training."""
from pathlib import Path
import sys,json,hashlib,time,platform,importlib.metadata
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.reiqa_frozen_features import FrozenQualityEncoder,generated_inputs,sha
ADMIT=ROOT/'outputs/piq23_actual_admission_v1';OUT=ROOT/'outputs/piq23_actual_features_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
    if OUT.exists():raise FileExistsError(OUT)
    v=read(ADMIT/'verification.json');assert v['passed'] and v['admitted_images']==5116
    assert sha(ADMIT/'roster.json')==v['roster_sha256']
    qa=read(ROOT/'outputs/piq23_training_engineering_v1/verification.json');assert qa['passed']
    versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','Pillow','torch','torchvision']})
    assert versions==qa['versions']
    for p,h in qa['code_sha256'].items():assert sha(ROOT/p)==h
    rows=read(ADMIT/'roster.json');bound=dict(qa['code_sha256'])
    for p in [ADMIT/'roster.json',ADMIT/'verification.json',ADMIT/'source.json',ADMIT/'duplicate_audit.json',
              Path(__file__),ROOT/'docs/piq23-real-head-evaluation-2026-11-18.md',ROOT/'outputs/piq23_training_engineering_v1/verification.json']:
        bound[p.relative_to(ROOT).as_posix()]=sha(p)
    for r in rows:assert sha(ROOT/r['rgb256_path'])==r['rgb256_file_sha256']
    OUT.mkdir();(OUT/'vectors').mkdir();write(OUT/'bindings.json',bound);write(OUT/'rows.json',rows)
    records=[];start=time.monotonic()
    try:
        encoder=FrozenQualityEncoder(ROOT);assert encoder.initial_state==qa['model_state_sha256']
        generated=encoder.encode(generated_inputs()[0][1])
        with np.load(ROOT/'outputs/reiqa_frozen_generated_v1/generated_features.npz',allow_pickle=False) as old:
            assert np.array_equal(generated,old['identity'].reshape(-1))
        for i,r in enumerate(rows):
            image=np.load(ROOT/r['rgb256_path'],allow_pickle=False);before=hashlib.sha256(image.tobytes()).hexdigest()
            assert image.shape==(256,256,3) and image.dtype==np.uint8 and before==r['rgb256_sha256']
            feature=encoder.encode(image);assert hashlib.sha256(image.tobytes()).hexdigest()==before
            p=OUT/'vectors'/f'{i:05d}.npy';np.save(p,feature,allow_pickle=False)
            records.append(dict(id=r['id'],scene=r['scene'],partition=r['partition'],generated_fixture=False,
                 input_rgb_sha256=before,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
            if (i+1)%128==0:print('Actual frozen PIQ23 vectors '+str(i+1)+'/5116 elapsed='+str(round(time.monotonic()-start))+'s',flush=True)
        encoder.verify_unchanged()
        for p,h in bound.items():assert sha(ROOT/p)==h
        write(OUT/'records.json',records)
        write(OUT/'verification.json',dict(passed=True,vectors=5116,width=4096,actual_encoder_calls=5116,generated_contract_calls=1,
            records_sha256=sha(OUT/'records.json'),rows_sha256=sha(OUT/'rows.json'),bindings_sha256=sha(OUT/'bindings.json'),
            model_unchanged=True,input_immutable=True,training_fits=0,versions=versions(),elapsed_seconds=time.monotonic()-start))
        print('COMPLETE5116actual Exposure vectors; zero fits.',flush=True)
    except Exception as exc:
        write(OUT/'partial_records.json',records);write(OUT/'failure.json',dict(error=repr(exc),completed_vectors=len(records)));raise
if __name__=='__main__':main()
