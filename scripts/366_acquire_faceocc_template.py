"""Acquire the pinned alignment template only; no additional models/data."""
import hashlib
import json
from pathlib import Path
import urllib.request
ROOT = Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'models/faceocc_candidate_v1'
    path=folder/'similarity_Lm3D_all.mat'
    if path.exists(): raise FileExistsError(path)
    tree=json.loads((ROOT/'outputs/faceocc_readiness_v2/source_tree.json').read_text(encoding='utf-8'))
    entry=next(r for r in tree['tree'] if r['path']=='face_align/similarity_Lm3D_all.mat')
    revision=tree['sha']
    url='https://raw.githubusercontent.com/mertakinstd/FaceOcc/'+revision+'/'+entry['path']
    with urllib.request.urlopen(url,timeout=25) as response: raw=response.read()
    assert len(raw)==entry['size']
    git_hash=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    assert git_hash==entry['sha']
    path.write_bytes(raw)
    (folder/'template_provenance.json').write_text(json.dumps(dict(url=url,source_revision=revision,
        bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),git_blob_sha1=git_hash),indent=2))
    print('Pinned alignment template acquired and Git blob verified: '+str(len(raw))+' bytes')


if __name__=='__main__': main()
