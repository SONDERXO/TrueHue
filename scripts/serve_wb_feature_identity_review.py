"""Read-only localhost review server; no private records served."""
import argparse
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse,unquote
ROOT=Path(__file__).resolve().parents[1]/'outputs/wb_feature_identity_review_v1'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        p=unquote(urlparse(self.path).path).lstrip('/') or 'index.html'
        target=(ROOT/p).resolve()
        allowed=p in ('index.html','qa/index.html','qa/fixture.png') or (p.startswith('images/') and p.endswith('.png'))
        if not allowed or not target.is_relative_to(ROOT.resolve()) or not target.is_file():self.send_error(404);return
        super().do_GET()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8881);args=parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
