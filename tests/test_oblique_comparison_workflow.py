"""Generated images/records only; HTTP saves use temporary directories."""
import json
from pathlib import Path
import threading
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
import numpy as np
import pytest
import importlib.util
from src.model_training.oblique_comparison_workflow import render,replay_render,measure,aggregate,fit_all,from_axis_tree,load_verifier
from src.demo.oblique_comparison_review import save_revision,handler,validate

def test_generated_render_and_metrics():
    image=np.arange(8*8*3,dtype=np.uint8).reshape(8,8,3);alpha=np.ones((8,8));alpha[:2]=0;alpha[2]=.5
    for controls in [[1.,1.,1.],[.7,1.03,.98],[1.4,.95,1.04]]:
        output=render(image,alpha,controls)
        assert np.array_equal(output,replay_render(image,alpha,controls))
        assert np.array_equal(output[:2],image[:2])
    assert np.array_equal(render(image,alpha,[1.,1.,1.]),image)
    assert measure(image,image,alpha>0)==dict(RGB=0.,DE=0.)
    with pytest.raises(ValueError):measure(image,image,np.zeros((8,8),bool))
    with pytest.raises(ValueError):render(image,alpha,[0,1,1])

def test_source_equal_not_row_equal():
    rows=[dict(role='under',source=s,input=dict(RGB=10,DE=d),output=dict(RGB=1,DE=1)) for s,d in [('a',5),('a',5),('b',1)]]
    assert aggregate(rows)['under']['source_equal_DE_improvement']==2.

def public():return dict(protocol_id='generated-only',cases=[dict(id='case-01',kind='identity',A='a.png',B='b.png',R=None)])
def value():return dict(protocol_id='generated-only',display=dict(browser='test',resolution='800x600',os_scale='100%',colour_settings='unknown'),ratings={'case-01':dict(identity='no_noticeable_change',reason='generated')})

def test_revision_validation_and_durability(tmp_path):
    first=save_revision(tmp_path,public(),value());second=save_revision(tmp_path,public(),value())
    assert first['revision']!=second['revision'] and len(list((tmp_path/'ratings').glob('*.json')))==2
    assert first['complete']
    bad=value();bad['display']['os_scale']=''
    with pytest.raises(ValueError):validate(public(),bad)
    bad=value();bad['ratings']['other']={}
    with pytest.raises(ValueError):validate(public(),bad)

def test_http_save_reload_private_denied(tmp_path):
    (tmp_path/'review_public.json').write_text(json.dumps(public()))
    (tmp_path/'secrets_PRIVATE.json').write_text('hidden')
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(tmp_path));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        assert json.load(urllib.request.urlopen(base+'/latest')) is None
        req=urllib.request.Request(base+'/save',data=json.dumps(value()).encode(),headers={'Content-Type':'application/json'})
        assert json.load(urllib.request.urlopen(req))['saved']
        assert json.load(urllib.request.urlopen(base+'/latest'))['ratings']==value()['ratings']
        with pytest.raises(urllib.error.HTTPError):urllib.request.urlopen(base+'/secrets_PRIVATE.json')
        req=urllib.request.Request(base+'/save',data=b'{}',headers={'Origin':'http://elsewhere'})
        with pytest.raises(urllib.error.HTTPError):urllib.request.urlopen(req)
    finally:server.shutdown();server.server_close()

def test_fit_barrier_reuse_without_training(tmp_path):
    root=Path(__file__).resolve().parents[1];verify=load_verifier(root)
    axis=dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,feature_names=['x'],target_names=['gamma','red_gain','blue_gain'],nodes=[dict(kind='leaf',values=[1.,1.,1.])])
    fold=dict(held_publisher_group='held',fitting_cases=['fit'],evaluation_cases=['held'])
    records={'fit':dict(publisher_group='fit',input_vector_float32=[0.],nominal_controls=[1.,1.,1.],experimental_role='identity')}
    report=dict(initial_SSE=0.,final_SSE=0.,status='no_strict_gain',SSE_history=[dict(event='initial',SSE=0.)])
    def forbidden(*args,**kwargs):raise AssertionError('Reused fit must not train')
    result=fit_all(tmp_path,[fold],[dict(definition=fold,tree=axis)],records,from_axis_tree(axis),report,verify.verify_arrays,trainer=forbidden)
    assert result[0]['reused'] and (tmp_path/'all_fits_verified_PRIVATE.json').exists()

def test_unblinding_requires_complete_saved_ratings_and_keeps_identity_policy():
    root=Path(__file__).resolve().parents[1]
    spec=importlib.util.spec_from_file_location('assess_oblique',root/'scripts/850_assess_saved_oblique_review.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    p=public();v=value();v['ratings']={}
    with pytest.raises(ValueError):module.assess(p,v,[],{})
    v=value();v['ratings']['case-01']['identity']='noticeable_change'
    summary=dict(by_role={r:dict(source_equal_DE_improvement=1.) for r in ['exposure_under','exposure_over','colour_cool']})
    predictions=[dict(review_id='case-01',case_id='generated',output_panel='A',role='identity')]
    result=module.assess(p,v,predictions,summary)
    assert result['development_status']=='NOTREADY' and result['concerns']==['case-01']
    assert v['ratings']['case-01']['identity']=='noticeable_change'
