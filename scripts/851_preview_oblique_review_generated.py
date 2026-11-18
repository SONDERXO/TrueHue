"""Prepare/serve only two synthetic UI examples, never scientific data."""
from pathlib import Path
import hashlib
import json
import sys
import threading
import webbrowser
from http.server import ThreadingHTTPServer

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.oblique_comparison_review import handler
OUT=ROOT/'outputs/oblique_review_generated_preview_v1'
PROTOCOL='truehue_GENERATED_UI_PREVIEW_ONLY_v1'

def prepare():
    if OUT.exists():
        public=json.loads((OUT/'review_public.json').read_text(encoding='utf-8'))
        if public['protocol_id']!=PROTOCOL:raise ValueError('Unexpected preview folder; preserve it')
        return OUT  # Retain previous answers and assets; never reset reviews.
    import cv2
    import numpy as np
    OUT.mkdir();assets=OUT/'assets';assets.mkdir()
    yy,xx=np.mgrid[:256,:256]
    image=np.stack([70+xx//3,60+yy//3,50+(xx+yy)//5],axis=2).astype(np.uint8)
    image[40:90,40:90]=[190,145,105]
    altered=np.clip(image.astype(float)*.65,0,255).astype(np.uint8)
    for name,array in [('identity_A',image),('identity_B',image),('distorted_A',altered),('distorted_B',image),('reference',image)]:
        if not cv2.imwrite(str(assets/(name+'.png')),array[:,:,::-1]):raise OSError('Could not save generated image')
    public=dict(protocol_id=PROTOCOL,
        preview_note='GENERATED UI TEST ONLY — two artificial colour patterns, no photographs. Enter any test answers. Test Save, Reload saved ratings and Download saved JSON; these answers are never model evidence.',
        cases=[dict(id='generated-01',kind='identity',A='assets/identity_A.png',B='assets/identity_B.png',R=None),
               dict(id='generated-02',kind='distorted',A='assets/distorted_A.png',B='assets/distorted_B.png',R='assets/reference.png')])
    (OUT/'review_public.json').write_text(json.dumps(public,indent=2)+'\n',encoding='utf-8')
    (OUT/'fixture_receipt_PRIVATE.json').write_text(json.dumps(dict(generated_only=True,scientific_rows=0,
        photo_reads=0,asset_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in assets.iterdir()}),indent=2)+'\n',encoding='utf-8')
    return OUT

def main():
    folder=prepare()
    if sys.argv[1:]==['--prepare-only']:
        print('Prepared two generated-only review examples; existing ratings preserved.');return
    if sys.argv[1:]:raise SystemExit('Only --prepare-only is supported')
    # Free loopback port avoids conflicts with earlier local review tools.
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(folder))
    url=f'http://127.0.0.1:{server.server_port}/'
    print('GENERATED UI TEST ONLY - no real photographs or model training.\n'+url,flush=True)
    print('Leave this window open while testing. Press Ctrl+C here when finished.',flush=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    webbrowser.open(url)
    try:thread.join()
    except KeyboardInterrupt:server.shutdown()
    finally:server.server_close()

if __name__=='__main__':main()
