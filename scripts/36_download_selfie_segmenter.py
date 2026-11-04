"""Fetch the official version-1 segmentation weights into ignored local models."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config


def main():
    config=get_config();destination=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    metadata=destination.with_suffix('.provenance.json')
    if destination.exists() or metadata.exists(): raise FileExistsError('Model/provenance exists; refusing overwrite')
    destination.parent.mkdir(parents=True,exist_ok=True)
    partial=destination.with_suffix('.download')
    with urllib.request.urlopen(config.SELFIE_SEGMENTER_MODEL_URL,timeout=90) as response:
        headers=dict(response.headers);final_url=response.url
        with partial.open('xb') as stream:
            count=0
            while chunk:=response.read(1024*1024):
                count+=len(chunk)
                if count>64*1024*1024: raise ValueError('Unexpected model size')
                stream.write(chunk)
    data=partial.read_bytes()
    if len(data)<1000 or data[4:8]!=b'TFL3': raise ValueError('Expected TFLite flatbuffer')
    partial.rename(destination)
    record=dict(source_url=config.SELFIE_SEGMENTER_MODEL_URL,final_url=final_url,version='1',
        bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),downloaded_at_utc=datetime.now(timezone.utc).isoformat(),
        etag=headers.get('ETag'),last_modified=headers.get('Last-Modified'),
        guide='https://developers.google.com/edge/mediapipe/solutions/vision/image_segmenter',
        status='Local development experiment only; not adopted into production pipeline')
    metadata.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record,indent=2))


if __name__=='__main__': main()
