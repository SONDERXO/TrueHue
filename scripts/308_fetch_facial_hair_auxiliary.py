"""Fetch one pinned skin parser whose upstream annotations exclude beard."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
REVISION='19e22b9d1bfd87e67b82e4b2749405686aeecba2'
SHA256='f649f30a4f000ea3d8c5f4593b01c140b3c50659388c6d2997a6f546a451c434'


def main():
    out=ROOT/'models/facial_hair_auxiliary_v1'
    if out.exists():raise FileExistsError(out)
    out.mkdir()
    base=f'https://huggingface.co/sadzip/EasyPortrait-ONNX/resolve/{REVISION}/'
    for name in ['manifest.json','README.md','fcn_mobilenetv2_fp.onnx']:
        print('Downloading',name,flush=True)
        with urllib.request.urlopen(base+name,timeout=60) as response, (out/name).open('xb') as stream:
            while chunk:=response.read(1024*1024):stream.write(chunk)
    model=out/'fcn_mobilenetv2_fp.onnx';assert hashlib.sha256(model.read_bytes()).hexdigest()==SHA256
    manifest=json.loads((out/'manifest.json').read_text())
    entry=next(r for r in manifest['models'] if r['key']=='fcn_mobilenetv2_fp')
    assert entry['classes']==8 and entry['argmax_match']
    provenance=dict(repo='sadzip/EasyPortrait-ONNX',revision=REVISION,sha256=SHA256,bytes=model.stat().st_size,
        upstream='https://github.com/hukenovs/easyportrait',
        upstream_checkpoint='fcn-fp.pth',exported_by='sadzip/preposition17 conversion; not an upstream-native ONNX release',
        model_card_license='apache-2.0; preserve upstream terms separately',
        purpose='Auxiliary lower-face non-skin suggestion only; no dedicated beard class, no dark-pixel rule',
        input_size=384,channels='BGR',mean=[143.55267075,132.96705975,126.94924335],
        std=[60.2625333,60.32740275,59.30988645],
        class_names=['background','skin','left_brow','right_brow','left_eye','right_eye','lips','teeth'],
        converter_validation=entry)
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    print(json.dumps(provenance,indent=2))


if __name__=='__main__':main()
