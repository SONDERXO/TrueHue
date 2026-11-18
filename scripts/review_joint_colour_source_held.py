"""Verified identity-first normal-browser review, with partial early rejection."""
from pathlib import Path
from http.server import ThreadingHTTPServer
import hashlib,json,sys,threading,webbrowser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.joint_colour_review import handler,assess_saved
def main():
    out=ROOT/'outputs/joint_colour_source_held_comparison_v1'
    check=json.loads((out/'verification_PRIVATE.json').read_text());assert check['passed'] and check['numeric_families_pass']
    for n,h in check['artifact_sha256'].items():
        p=(out/n).resolve();assert p.is_relative_to(out.resolve()) and hashlib.sha256(p.read_bytes()).hexdigest()==h
    if sys.argv[1:]:
        if len(sys.argv)!=3 or sys.argv[1]!='--assess':raise ValueError('Use --assess saved_revision.json')
        result=assess_saved(out,sys.argv[2])
        with (out/('assessment_'+sys.argv[2])).open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
        print(result['development_status']);return
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(out));url=f'http://127.0.0.1:{server.server_port}/'
    print('Unchanged photos first. Save regularly; a noticeable-change failure stops further review.\n'+url,flush=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();webbrowser.open(url)
    try:thread.join()
    except KeyboardInterrupt:server.shutdown()
    finally:server.server_close()
if __name__=='__main__':main()
