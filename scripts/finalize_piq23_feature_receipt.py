"""Finalize saved5116vectors after receipt-only versions-dict typo; no inference."""
from pathlib import Path
import json,hashlib,platform,importlib.metadata
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/piq23_actual_features_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dest=OUT/'verification.json'
    if dest.exists():raise FileExistsError(dest)
    failure=read(OUT/'failure.json');assert failure['completed_vectors']==5116 and failure['error']=="TypeError(\"'dict' object is not callable\")"
    rows=read(OUT/'rows.json');records=read(OUT/'records.json');assert records==read(OUT/'partial_records.json')
    assert len(rows)==len(records)==5116
    for row,record in zip(rows,records):
        assert all(row[k]==record[k] for k in ['id','scene','partition','generated_fixture'])
        p=ROOT/record['path'];assert sha(p)==record['sha256']
        x=np.load(p,allow_pickle=False);assert x.dtype==np.float32 and x.shape==(4096,) and np.isfinite(x).all()
    for p,h in read(OUT/'bindings.json').items():assert sha(ROOT/p)==h
    qa=read(ROOT/'outputs/piq23_training_engineering_v1/verification.json')
    versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','Pillow','torch','torchvision']})
    assert versions==qa['versions']
    result=dict(passed=True,vectors=5116,width=4096,actual_encoder_calls=5116,generated_contract_calls=1,
      records_sha256=sha(OUT/'records.json'),rows_sha256=sha(OUT/'rows.json'),bindings_sha256=sha(OUT/'bindings.json'),
      model_unchanged=True,input_immutable=True,training_fits=0,versions=versions,elapsed_seconds=None,
      finalization_only=True,original_failure_sha256=sha(OUT/'failure.json'),
      explanation='Original code completed encoder.verify_unchanged and all binding rehashes before receipt construction failed by calling local versions dictionary. All5116vectors and records already saved. No encoder/image replay.',
      new_encoder_calls=0,new_image_decodes=0,finalizer_sha256=sha(Path(__file__)))
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
    print('PASS finalized5116savedvectors; original receipt-only error preserved;0newencoder/imagecalls.')
if __name__=='__main__':main()
