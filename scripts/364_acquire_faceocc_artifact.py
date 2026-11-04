"""Pinned FaceOcc weights and inference evidence; no model execution."""
import hashlib
import json
import math
from pathlib import Path
import struct
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / 'outputs/faceocc_readiness_v2'
OUT = ROOT / 'models/faceocc_candidate_v1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    model = json.loads((PARENT / 'model_api.json').read_text(encoding='utf-8'))
    commit = json.loads((PARENT / 'source_commit.json').read_text(encoding='utf-8'))
    assert model['gated'] is False and model['private'] is False
    OUT.mkdir()
    evidence=[]
    def fetch(name,url):
        path=OUT/name
        request=urllib.request.Request(url,headers={'User-Agent':'TrueHue-model-readiness'})
        with urllib.request.urlopen(request,timeout=45) as response, path.open('xb') as f:
            count=0
            while chunk:=response.read(1024*1024):
                count+=len(chunk)
                if count>100*1024*1024: raise ValueError('Artifact exceeds declared acquisition bound')
                f.write(chunk)
        raw=path.read_bytes()
        evidence.append(dict(file=name,url=url,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
        return raw
    revision=model['sha']; source=commit['sha']
    metadata=fetch('hub_file_metadata.json','https://huggingface.co/api/models/mertakin/FaceOcc/tree/'+revision+'?recursive=true&expand=false')
    tree=json.loads(metadata); item=next(r for r in tree if r['path']=='model.safetensors')
    payload=fetch('model.safetensors','https://huggingface.co/mertakin/FaceOcc/resolve/'+revision+'/model.safetensors')
    assert len(payload)==item['size']
    expected=item.get('lfs',{}).get('oid')
    if expected: assert hashlib.sha256(payload).hexdigest()==expected
    header_size=struct.unpack('<Q',payload[:8])[0]
    assert 0<header_size<1024*1024
    header=json.loads(payload[8:8+header_size]); tensors={k:v for k,v in header.items() if k!='__metadata__'}
    data_size=len(payload)-8-header_size; intervals=[]
    for name,t in tensors.items():
        assert t['dtype'] in {'F32','I64'}
        start,end=t['data_offsets'];width=4 if t['dtype']=='F32' else 8
        assert 0<=start<=end<=data_size and end-start==math.prod(t['shape'])*width
        intervals.append((start,end))
    intervals.sort();assert intervals[0][0]==0 and intervals[-1][1]==data_size
    assert all(a[1]==b[0] for a,b in zip(intervals,intervals[1:]))
    for name in ['config.json','LICENSE','NOTICE.md','README.md']:
        fetch(name,'https://huggingface.co/mertakin/FaceOcc/resolve/'+revision+'/'+name)
    for name in ['evaluation_cofw.py','faceocc_runtime.py','Dataset/dataset.py','Dataset/utils.py','requirements.txt']:
        fetch('source_'+name.replace('/','__'),'https://raw.githubusercontent.com/mertakinstd/FaceOcc/'+source+'/'+name)
    report=dict(status='artifact_integrity_checked_not_runtime_ready',model_revision=revision,source_revision=source,
        evidence=evidence,publisher_lfs_sha256=expected,tensor_count=len(tensors),
        tensors={k:dict(dtype=v['dtype'],shape=v['shape']) for k,v in tensors.items()},
        source_code_executed=False,model_loaded=False,photos_processed=0,python_environment_changed=False)
    (OUT/'acquisition.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ['evidence','tensors']},indent=2))


if __name__=='__main__': main()
