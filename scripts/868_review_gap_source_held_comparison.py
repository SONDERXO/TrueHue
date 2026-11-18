"""Normal-browser review of verified primary outputs only; no fits/scores."""
from pathlib import Path
from http.server import ThreadingHTTPServer
import threading,webbrowser,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.oblique_comparison_review import handler

def main():
    out=ROOT/'outputs/histogram_gap_source_held_comparison_v1'
    receipt=json.loads((out/'verification_PRIVATE.json').read_text(encoding='utf-8'))
    assert receipt['passed'] and receipt['held_routes']==44 and receipt['render_metric_replays']==88
    for name,h in receipt['artifact_sha256'].items():
        p=(out/name).resolve();assert p.is_relative_to(out.resolve()) and hashlib.sha256(p.read_bytes()).hexdigest()==h
    public=json.loads((out/'review_public.json').read_text(encoding='utf-8'));assert len(public['cases'])==44
    assert all(not c[k] or c[k].startswith('review_assets/') for c in public['cases'] for k in ['A','B','R'])
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(out));url=f'http://127.0.0.1:{server.server_port}/'
    print('44 primary cases with approved ear coverage. Scores/diagnostic outputs concealed.\n'+url,flush=True)
    print('Save ratings regularly; keep this window open. Ctrl+C stops the server.',flush=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();webbrowser.open(url)
    try:thread.join()
    except KeyboardInterrupt:server.shutdown()
    finally:server.server_close()

if __name__=='__main__':main()
