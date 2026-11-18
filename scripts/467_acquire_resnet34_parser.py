"""Acquire one official, digest-pinned public model; no photo/model execution."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'models/face_parser_resnet34_candidate_v1'
REV='8a4729d95118d0e97c44185f9bdef3d6bfeaaf99'
EXPECTED='5b805bba7b5660ab7070b5a381dcf75e5b3e04199f1e9387232a77a00095102e'

def main():
    if OUT.exists() and any(OUT.iterdir()):raise FileExistsError('Acquisition artifacts exist; no overwrite')
    OUT.mkdir(exist_ok=True);session=requests.Session();session.headers['User-Agent']='TrueHue-research-model-acquisition'
    url='https://api.github.com/repos/yakhyo/face-parsing/releases/assets/328506789'
    response=session.get(url,timeout=45);response.raise_for_status();meta=response.json()
    (OUT/'asset_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    assert meta['id']==328506789 and meta['size']==93632554 and meta['digest']=='sha256:'+EXPECTED
    records={}
    for name,path in [('LICENSE','LICENSE'),('README.md','README.md'),('onnx_inference.py','onnx_inference.py'),('utils_common.py','utils/common.py')]:
        r=session.get(f'https://raw.githubusercontent.com/yakhyo/face-parsing/{REV}/{path}',timeout=45);r.raise_for_status()
        (OUT/('upstream_'+name)).write_bytes(r.content);records[path]=hashlib.sha256(r.content).hexdigest()
    target=OUT/'resnet34.onnx';digest=hashlib.sha256();count=0
    with session.get(meta['browser_download_url'],stream=True,timeout=(30,120)) as r:
        r.raise_for_status()
        with target.open('xb') as stream:
            for block in r.iter_content(1024*1024):
                if block:stream.write(block);digest.update(block);count+=len(block)
    assert count==93632554 and digest.hexdigest()==EXPECTED
    provenance=dict(asset_id=328506789,url=meta['browser_download_url'],bytes=count,sha256=digest.hexdigest(),source_revision=REV,
        source_sha256=records,research_only=True,photos_uploaded=0,model_executed=False,acquired_at_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    print(json.dumps(provenance,indent=2))

if __name__=='__main__':main()
