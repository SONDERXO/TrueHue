"""One declared higher-capacity auxiliary check after the small model failed."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'models/facial_hair_fpn_auxiliary_v1'
    if (out/'provenance.json').exists():raise FileExistsError(out/'provenance.json')
    out.mkdir(exist_ok=True);revision='19e22b9d1bfd87e67b82e4b2749405686aeecba2'
    name='fpn_resnet50_fp_512.onnx';url=f'https://huggingface.co/sadzip/EasyPortrait-ONNX/resolve/{revision}/{name}'
    if not (out/name).exists():
        with urllib.request.urlopen(url,timeout=60) as response,(out/name).open('xb') as stream:
            while chunk:=response.read(1024*1024):stream.write(chunk)
    sha=hashlib.sha256((out/name).read_bytes()).hexdigest()
    assert sha=='cc5e9ce11c8e51b00b2975ba24c560b82d298d428b8c4ee4d15e9d005d567d15'
    (out/'provenance.json').write_text(json.dumps(dict(repo='sadzip/EasyPortrait-ONNX',revision=revision,
        file=name,sha256=sha,bytes=(out/name).stat().st_size,upstream_checkpoint='fpn-fp-512.pth',
        input_size=512,classes=8,upstream='https://github.com/hukenovs/easyportrait',
        purpose='Final declared higher-capacity diagnostic; no parameter sweep or automatic adoption'),indent=2),encoding='utf-8')
    print('Downloaded pinned FPN512 auxiliary:',sha)


if __name__=='__main__':main()
