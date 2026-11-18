"""Same tested durable review UI; no controls/scores served or old ratings reused."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
from http.server import ThreadingHTTPServer
import threading
import webbrowser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.oblique_comparison_review import handler

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    out=ROOT/'outputs/source_bagged_source_held_v1'
    check=read(out/'verification_PRIVATE.json');assert check['passed'] and check['numeric_families_pass']
    assert check['held_means']==44 and check['render_metric_replays']==44
    for name,h in check['artifact_sha256'].items():
        path=(out/name).resolve();assert path.is_relative_to(out.resolve()) and hashlib.sha256(path.read_bytes()).hexdigest()==h
    if sys.argv[1:]:
        if len(sys.argv)!=3 or sys.argv[1]!='--assess' or Path(sys.argv[2]).name!=sys.argv[2] or not sys.argv[2].endswith('.json'):
            raise ValueError('Use --assess exact_saved_revision.json')
        spec=importlib.util.spec_from_file_location('accepted_visual_assessment',ROOT/'scripts/850_assess_saved_oblique_review.py')
        assessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(assessor)
        result=assessor.assess(read(out/'review_public.json'),read(out/'ratings'/sys.argv[2]),read(out/'predictions_PRIVATE.json'),read(out/'summary_PRIVATE.json')['primary'])
        with (out/('assessment_'+sys.argv[2])).open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2)
        print(result['development_status']);return
    public=read(out/'review_public.json');assert len(public['cases'])==44
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(out));url=f'http://127.0.0.1:{server.server_port}/'
    print('44 new ensemble cases. Save44/44 then Download. Keep this window open.\n'+url,flush=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();webbrowser.open(url)
    try:thread.join()
    except KeyboardInterrupt:server.shutdown()
    finally:server.server_close()

if __name__=='__main__':main()
