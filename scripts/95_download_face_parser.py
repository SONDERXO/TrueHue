"""Fetch one published ONNX asset and pinned author sources; never execute them."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TrueHue-thesis-development'}),timeout=60)


def main():
    output=ROOT/get_config().MODELS_ROOT/'face_parser_experimental_v1'
    output.mkdir(exist_ok=True)
    model=output/'resnet18.onnx';metadata=output/'resnet18.provenance.json'
    if model.exists() or metadata.exists():raise FileExistsError('Preserve existing model/provenance')
    with fetch('https://api.github.com/repos/yakhyo/face-parsing/releases/tags/weights') as response:release=json.load(response)
    with fetch('https://api.github.com/repos/yakhyo/face-parsing/commits/main') as response:revision=json.load(response)['sha']
    asset=next(a for a in release['assets'] if a['name']=='resnet18.onnx')
    assert asset['browser_download_url']=='https://github.com/yakhyo/face-parsing/releases/download/weights/resnet18.onnx'
    (output/'release_metadata.json').write_text(json.dumps(release,indent=2),encoding='utf-8')
    sources={}
    for name in ['onnx_inference.py','utils/common.py','LICENSE','README.md']:
        with fetch('https://raw.githubusercontent.com/yakhyo/face-parsing/'+revision+'/'+name) as response:data=response.read()
        target=output/('upstream_'+name.replace('/','_'));target.write_bytes(data)
        sources[name]=hashlib.sha256(data).hexdigest()
    partial=model.with_suffix('.download')
    with fetch(asset['browser_download_url']) as response:
        with partial.open('xb') as stream:
            size=0
            while chunk:=response.read(1024*1024):
                size+=len(chunk)
                if size>128*1024*1024:raise ValueError('Unexpected model size')
                stream.write(chunk)
    assert size==asset['size']
    sha=hashlib.sha256(partial.read_bytes()).hexdigest()
    if asset.get('digest'):assert asset['digest']=='sha256:'+sha
    partial.rename(model)
    record=dict(source_url=asset['browser_download_url'],release_tag=release['tag_name'],source_revision=revision,
        asset_id=asset['id'],bytes=size,sha256=sha,upstream_digest=asset.get('digest'),author_source_sha256=sources,
        downloaded_at_utc=datetime.now(timezone.utc).isoformat(),status='Development diagnostic only, not runtime adoption',
        protocol_sha256=hashlib.sha256((ROOT/'docs/face-parsing-protocol.md').read_bytes()).hexdigest())
    metadata.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in record.items() if k!='author_source_sha256'},indent=2))


if __name__=='__main__':main()
