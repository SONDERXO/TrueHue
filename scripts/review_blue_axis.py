"""Open the bound review, or assess one exact saved revision after completion."""
from pathlib import Path
from http.server import ThreadingHTTPServer
import sys,threading,webbrowser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.blue_axis_preparation import read,write,sha
from src.demo.blue_axis_review import handler,assess

def main():
    out=ROOT/'outputs/blue_axis_review_v1';receipt=read(out/'preparation_PRIVATE.json');ready=read(out/'readiness_PRIVATE.json')
    assert ready['passed'] and sha(out/'review_public.json')==receipt['public_sha256']
    for rel,h in receipt['assets_sha256'].items():assert sha(out/rel)==h
    for rel,h in ready['code_sha256'].items():assert sha(ROOT/rel)==h
    if sys.argv[1:]:
        if len(sys.argv)!=3 or sys.argv[1]!='--assess':raise ValueError('Use --assess saved_revision.json')
        result=assess(out,sys.argv[2]);dest=out/('assessment_'+sys.argv[2])
        if dest.exists():raise FileExistsError('Preserve assessment')
        write(dest,result);print(result['status']);return
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(out));url=f'http://127.0.0.1:{server.server_port}/'
    print('22 judgments retained;44 cases to review. Save regularly, then Download.\n'+url,flush=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();webbrowser.open(url)
    try:thread.join()
    except KeyboardInterrupt:server.shutdown()
    finally:server.server_close()
if __name__=='__main__':main()
