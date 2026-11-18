"""Open or assess the explicitly criterion-revised post-hoc review."""
from pathlib import Path
from http.server import ThreadingHTTPServer
import hashlib,json,sys,threading,webbrowser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.acceptability_review import handler,assess
def main():
    out=ROOT/'outputs/joint_colour_acceptability_review_v2';receipt=json.loads((out/'preparation_PRIVATE.json').read_text(encoding='utf-8'))
    for rel,h in receipt['assets_sha256'].items():assert hashlib.sha256((out/rel).read_bytes()).hexdigest()==h
    assert hashlib.sha256((out/'review_public.json').read_bytes()).hexdigest()==receipt['public_sha256']
    if sys.argv[1:]:
        if len(sys.argv)!=3 or sys.argv[1]!='--assess':raise ValueError('Use --assess saved_revision.json')
        result=assess(out,sys.argv[2])
        with (out/('assessment_'+sys.argv[2])).open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
        print(result['development_status']);return
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(out));url=f'http://127.0.0.1:{server.server_port}/'
    print('Revised acceptability continuation:9answers retained. Slight acceptable differences allowed.\n'+url,flush=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();webbrowser.open(url)
    try:thread.join()
    except KeyboardInterrupt:server.shutdown()
    finally:server.server_close()
if __name__=='__main__':main()
