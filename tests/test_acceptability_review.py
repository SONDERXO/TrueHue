"""Generated-only revised-policy review tests; no scientific answers changed."""
from pathlib import Path
import json,threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen,Request
from urllib.error import HTTPError
import pytest
from src.demo.acceptability_review import validate,save,assess,handler,page

def fixture(folder):
    public=dict(protocol_id='GENERATED_ACCEPTABILITY_V2',cases=[dict(id='id',kind='identity',A='assets/a.png',B='assets/b.png',R=None),dict(id='dist',kind='distorted',A='assets/a.png',B='assets/b.png',R='assets/r.png')])
    value=dict(protocol_id=public['protocol_id'],display=dict(browser='generated',resolution='8x8',os_scale='unknown',colour_settings='unknown'),ratings={})
    (folder/'review_public.json').write_text(json.dumps(public));(folder/'ratings').mkdir()
    return public,value

def test_slight_acceptable_allowed_but_not_partial_pass(tmp_path):
    public,value=fixture(tmp_path);value['ratings']['id']=dict(identity='slight_acceptable_change',reason='GENERATED')
    assert validate(public,value) is False
    result=save(tmp_path,public,value)
    assert not result['complete'] and not (tmp_path/'early_unwanted_change_PRIVATE.json').exists()
    with pytest.raises(ValueError,match='Complete initial'):assess(tmp_path,result['revision'])

def test_unwanted_change_early_stops_without_private_results(tmp_path):
    public,value=fixture(tmp_path);value['ratings']['id']=dict(identity='unwanted_change',reason='GENERATED')
    result=save(tmp_path,public,value)
    assessment=assess(tmp_path,result['revision'])
    assert assessment['development_status']=='POSTHOC_REVIEW_NOTREADY' and not assessment['scores_unblinded']

def test_old_visibility_only_rating_cannot_silently_pass(tmp_path):
    public,value=fixture(tmp_path);value['ratings']['id']=dict(identity='no_noticeable_change',reason='GENERATED')
    with pytest.raises(ValueError):validate(public,value)
    value['protocol_id']='wrong'
    with pytest.raises(ValueError):validate(public,value)

def test_page_explicit_new_rule_and_resume():
    p=page()
    assert b'slight_acceptable_change' in p and b'unwanted_change' in p and b'findIndex' in p
    assert b"['no_noticeable_change','noticeable_change','cannot_judge']" not in p

def test_http_save_reload_private_denial_and_no_stop_for_slight(tmp_path):
    public,value=fixture(tmp_path)
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(tmp_path));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
    try:
        assert json.loads(urlopen(base+'/latest').read()) is None
        assert b'slight_acceptable_change' in urlopen(base+'/').read()
        value['ratings']['id']=dict(identity='slight_acceptable_change',reason='GENERATED')
        def post(v):return json.loads(urlopen(Request(base+'/save',data=json.dumps(v).encode(),headers={'Content-Type':'application/json'})).read())
        response=post(value);assert response['saved'] and not response['complete']
        assert json.loads(urlopen(base+'/latest').read())['ratings']==value['ratings']
        assert not json.loads(urlopen(base+'/review-status').read())['closed']
        for name in ['provenance_PRIVATE.json','summary_PRIVATE.json','original_initial_ratings_PRIVATE.json']:
            with pytest.raises(HTTPError) as e:urlopen(base+'/'+name)
            assert e.value.code==404
        value['ratings']['id']['identity']='unwanted_change';post(value)
        assert json.loads(urlopen(base+'/review-status').read())['closed']
    finally:server.shutdown();server.server_close();thread.join()
