"""Launch only independently verified, frozen development-review panels."""
from pathlib import Path
from http.server import ThreadingHTTPServer
import hashlib
import json
import sys
import threading
import webbrowser

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.oblique_comparison_review import handler

def main():
    folder=ROOT/'outputs/oblique_source_held_comparison_v1'
    receipt=json.loads((folder/'independent_verification_PRIVATE.json').read_text(encoding='utf-8'))
    if not receipt['passed'] or receipt['held_routes']!=44:raise ValueError('Verified comparison required')
    for name,digest in receipt['artifact_sha256'].items():
        path=(folder/name).resolve()
        if not path.is_relative_to(folder.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Frozen review artifact changed: '+name)
    public=json.loads((folder/'review_public.json').read_text(encoding='utf-8'))
    if len(public['cases'])!=44:raise ValueError('Expected all 44 review cases')
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(folder))
    url=f'http://127.0.0.1:{server.server_port}/'
    print('44-case development review - scores and model labels concealed.\n'+url,flush=True)
    print('Use Save ratings regularly. Leave this window open; Ctrl+C stops the server.',flush=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    webbrowser.open(url)
    try:thread.join()
    except KeyboardInterrupt:server.shutdown()
    finally:server.server_close()

if __name__=='__main__':main()
