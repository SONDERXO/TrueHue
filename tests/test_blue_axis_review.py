"""Generated HTTP and carried-rating integrity tests, without scientific data."""
from pathlib import Path
import json,threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen,Request
from urllib.error import HTTPError
import pytest
from src.demo.blue_axis_review import handler,save,assess,page

def fixture(folder):
    public=dict(protocol_id='GENERATED_BLUE_REVIEW',carried_ids=['carried'],cases=[dict(id='i',kind='identity',A='review_assets/a.png',B='review_assets/b.png',R=None),dict(id='carried',kind='distorted',A='review_assets/a.png',B='review_assets/b.png',R='review_assets/r.png'),dict(id='d',kind='distorted',A='review_assets/a.png',B='review_assets/b.png',R='review_assets/r.png')])
    seed=dict(protocol_id=public['protocol_id'],display={k:'GENERATED' for k in ['browser','resolution','os_scale','colour_settings']},ratings={'carried':dict(preference='A',artifact='none',reason='GENERATED_PRIOR')})
    for name,value in [('review_public.json',public),('carry_forward_seed_PRIVATE.json',seed)]: (folder/name).write_text(json.dumps(value),encoding='utf-8')
    (folder/'review_assets').mkdir()
    for n in ['a.png','b.png','r.png']:(folder/'review_assets'/n).write_bytes(b'GENERATED_ASSET')
    return public,seed

def test_carried_judgment_and_display_cannot_silently_change(tmp_path):
    p,s=fixture(tmp_path);s['ratings']['carried']['preference']='B'
    with pytest.raises(ValueError,match='intact'):save(tmp_path,p,s)
    s['ratings']['carried']['preference']='A';s['display']['os_scale']='changed'
    with pytest.raises(ValueError,match='Viewing setup'):save(tmp_path,p,s)

def test_partial_and_unwanted_assessment_never_access_private_results(tmp_path):
    p,s=fixture(tmp_path);revision=save(tmp_path,p,s)['revision']
    with pytest.raises(ValueError,match='Complete initial'):assess(tmp_path,revision)
    s['ratings']['i']=dict(identity='unwanted_change',reason='GENERATED');revision=save(tmp_path,p,s)['revision']
    assert assess(tmp_path,revision)==dict(status='FAIL_CLOSED_NOT_ADOPTED',scores_unblinded=False)

def test_page_keeps_panel_geometry_and_skips_carried():
    text=page({}).decode();assert 'carried_ids' in text and 'slight_acceptable_change' in text
    assert 'max-width:min(512px,100%)' in text and "im.naturalWidth+'px'" in text

def test_http_save_reload_download_payload_and_private_denial(tmp_path):
    public,seed=fixture(tmp_path);save(tmp_path,public,seed)
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(tmp_path));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
    def post(value):return json.loads(urlopen(Request(base+'/save',data=json.dumps(value).encode(),headers={'Content-Type':'application/json'})).read())
    try:
        assert b'carried_ids' in urlopen(base+'/').read()
        assert json.loads(urlopen(base+'/latest').read())['ratings']==seed['ratings']
        seed['ratings']['i']=dict(identity='slight_acceptable_change');assert not post(seed)['complete']
        assert not json.loads(urlopen(base+'/review-status').read())['closed']
        for rel in ['summary_PRIVATE.json','predictions_PRIVATE.json','provenance_PRIVATE.json','carry_forward_seed_PRIVATE.json','ratings/x.json','../AGENTS.md']:
            with pytest.raises(HTTPError) as error:urlopen(base+'/'+rel)
            assert error.value.code==404
        seed['ratings']['i']=dict(identity='unwanted_change');assert post(seed)['saved']
        assert json.loads(urlopen(base+'/review-status').read())['closed']
        assert json.loads(urlopen(base+'/latest').read())['ratings']==seed['ratings']
        with pytest.raises(HTTPError) as error:post(seed)
        assert error.value.code==409
    finally:server.shutdown();server.server_close();thread.join()
