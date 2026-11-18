"""Loopback-only review with immutable JSON revisions and restricted assets."""
import hashlib
import json
from pathlib import Path
import re
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

IDENTITY={'no_noticeable_change','noticeable_change','cannot_judge'}
PREFERENCE={'A','B','no_noticeable_difference','both_unacceptable','cannot_judge'}
ARTIFACT={'A','B','both','none','cannot_judge'}

def validate(public,value):
    if value.get('protocol_id')!=public['protocol_id']:raise ValueError('Wrong protocol')
    display=value.get('display',{})
    if not all(isinstance(display.get(k),str) and display[k].strip() for k in ['browser','resolution','os_scale','colour_settings']):
        raise ValueError('Record browser, resolution, OS scale and colour settings (unknown allowed)')
    ratings=value.get('ratings',{})
    if set(ratings)-{c['id'] for c in public['cases']}:raise ValueError('Unknown case')
    for case in public['cases']:
        if case['id'] not in ratings:continue
        r=ratings[case['id']]
        if case['kind']=='identity':
            if r.get('identity') not in IDENTITY:raise ValueError('Missing identity judgment')
        elif r.get('preference') not in PREFERENCE or r.get('artifact') not in ARTIFACT:
            raise ValueError('Missing preference/artifact judgment')
        if not isinstance(r.get('reason',''),str):raise ValueError('Invalid reason')
    return len(ratings)==len(public['cases'])

def save_revision(folder,public,value):
    complete=validate(public,value)
    dest=folder/'ratings';dest.mkdir(exist_ok=True)
    revision=dict(value,complete=complete)
    data=(json.dumps(revision,indent=2,allow_nan=False)+'\n').encode()
    name=uuid.uuid4().hex+'.json'
    with (dest/name).open('xb') as stream:
        stream.write(data);stream.flush()
        import os
        os.fsync(stream.fileno())
    return dict(saved=True,revision=name,sha256=hashlib.sha256(data).hexdigest(),complete=complete)

def handler(folder):
    public=json.loads((folder/'review_public.json').read_text(encoding='utf-8'))
    assets={c[k] for c in public['cases'] for k in ['A','B','R'] if c.get(k)}
    page=Path(__file__).with_name('oblique_comparison_review.html').read_bytes()
    class ReviewHandler(BaseHTTPRequestHandler):
        def reply(self,status,data,kind='application/json'):
            if not isinstance(data,bytes):data=json.dumps(data).encode()
            self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store')
            self.end_headers();self.wfile.write(data)
        def do_GET(self):
            if self.path=='/':return self.reply(200,page,'text/html; charset=utf-8')
            if self.path=='/public':return self.reply(200,public)
            if self.path=='/latest':
                paths=sorted((folder/'ratings').glob('*.json'),key=lambda p:p.stat().st_mtime_ns) if (folder/'ratings').exists() else []
                return self.reply(200,json.loads(paths[-1].read_text()) if paths else None)
            if self.path in {'/'+p for p in assets}:
                return self.reply(200,(folder/self.path[1:]).read_bytes(),'image/png')
            return self.reply(404,dict(error='Unknown review asset'))
        def do_POST(self):
            if self.path!='/save':return self.reply(404,{})
            # Same-origin UI only; do not accept cross-origin browser writes.
            origin=self.headers.get('Origin')
            if origin and origin!='http://'+self.headers.get('Host',''):return self.reply(403,{})
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=200000:raise ValueError('Invalid save size')
                result=save_revision(folder,public,json.loads(self.rfile.read(length)))
                self.reply(200,result)
            except (ValueError,TypeError,KeyError) as error:self.reply(400,dict(error=str(error)))
        def log_message(self,*args):pass
    return ReviewHandler

def serve(folder,port=8768):
    ThreadingHTTPServer(('127.0.0.1',port),handler(Path(folder))).serve_forever()

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);parser.add_argument('--port',type=int,default=8768)
    args=parser.parse_args();serve(args.folder,args.port)
