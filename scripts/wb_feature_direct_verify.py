"""Independent scalar tree, pixel and metric verification; never fits a model."""
import json
import math
import struct
from pathlib import Path
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000
from src.evaluation.luminance_chroma_scalar import replay as pixel_replay

ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def close(a,b,tol=1e-10):assert math.isclose(a,b,abs_tol=tol,rel_tol=tol),(a,b)

def route(model,x):
    x=[struct.unpack('!f',struct.pack('!f',v))[0] for v in x]
    i=0;seen=set()
    while model['nodes'][i]['kind']=='split':
        assert i not in seen;seen.add(i);assert len(seen)<=4
        n=model['nodes'][i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
    return i,model['nodes'][i]['values']

def verify_fit(model,fit,fold,settings):
    assert model['schema']=='truehue_camera_control_cart_research_v1'
    assert model['target_names']==['gamma','exposure_gain','red_balance','blue_balance','chroma_scale']
    assert model['settings']==settings and model['comparison']=='<='
    assert len(fit)==60 and [r['case_id'] for r in fit]==fold['fitting_cases']
    assert len({r['source_id'] for r in fit})==10 and all(r['source_id']!=fold['held_source_id'] for r in fit)
    own={}
    for r in fit:
        assert len(r['x'])==model['dimensions']
        leaf,p=route(model,r['x']);own.setdefault(leaf,[]).append(r)
    assert set(own)=={i for i,n in enumerate(model['nodes']) if n['kind']=='leaf'}
    for leaf,rows in own.items():
        for j in range(5):close(model['nodes'][leaf]['values'][j],math.fsum(r['y'][j] for r in rows)/len(rows),1e-12)
    constant=[math.fsum(r['y'][j] for r in fit)/60 for j in range(5)]
    return constant

def verify_run(root):
    root=Path(root);plan=read(root/'plan.json');rows=read(root/'rows.json');by_id={r['case_id']:r for r in rows}
    cert=read(root/'all_fits_verified.json');assert cert['verified_fits']==22
    inference=read(root/'inference.json');assert len(inference)==66
    assert all(set(r)=={'case_id','source_id','role','generated_fixture','x281','x314'} for r in inference)
    for r in inference:
        assert r['x281']==by_id[r['case_id']]['x281'] and r['x314']==by_id[r['case_id']]['x314']
    models={};constants={};fitting_routes=0
    for entry in cert['models']:
        arm,sid=entry['arm'],entry['source_id'];fold=next(f for f in plan['folds'] if f['held_source_id']==sid)
        model=read(root/entry['path']);fit=[dict(by_id[c],x=by_id[c]['x'+arm]) for c in fold['fitting_cases']]
        constant=verify_fit(model,fit,fold,plan['settings'])
        if sid in constants:
            for a,b in zip(constants[sid],constant):close(a,b,1e-12)
        constants[sid]=constant;models[(arm,sid)]=model;fitting_routes+=60
    sealed=read(root/'held_controls_sealed.json');assert len(sealed)==66
    scores=read(root/'records.json');assert len(scores)==66
    checks=0
    for p,saved in zip(sealed,scores):
        assert p['case_id']==saved['case_id']
        r=by_id[p['case_id']]
        for arm in ['281','314']:
            _,expected=route(models[(arm,r['source_id'])],r['x'+arm])
            assert expected==p['controls'+arm]
        assert p['constant']==constants[r['source_id']]
        with np.load(root/'evaluation'/(r['case_id']+'.npz'),allow_pickle=False) as pack:
            image,ref,alpha,protected=[pack[k] for k in ['input','reference','alpha','protected']]
            outputs={k:pack[k] for k in ['281','314','constant']}
        for label,output in outputs.items():
            controls=p['constant'] if label=='constant' else p['controls'+label]
            independent,_=pixel_replay(image,ref,alpha,protected,controls)
            np.testing.assert_array_equal(output,independent)
            assert np.array_equal(output[alpha==0],image[alpha==0]) and np.array_equal(output[protected],image[protected])
            checks+=1
        masks={'primary':alpha>0,'core':alpha==1,'feather':(alpha>0)&(alpha<1),'whole':np.ones(alpha.shape,bool)}
        ref_lab=rgb2lab(ref/255.)
        for label,output in dict(input=image,**outputs).items():
            rgb=np.abs(output.astype(float)-ref);de=deltaE_ciede2000(rgb2lab(output/255.),ref_lab)
            for name,mask in masks.items():
                score=saved['regions'][name][label];n=int(mask.sum())
                if n:
                    close(score['RGB'],math.fsum(float(v) for v in rgb[mask].flat)/(3*n))
                    close(score['DE'],math.fsum(float(v) for v in de[mask])/n)
                else:assert score is None
        if r['role']=='identity':
            for arm in ['281','314']:
                assert saved['identity_changed_pixels'][arm]==int(np.any(outputs[arm]!=image,axis=2).sum())
        if checks%18==0:print(f'Independent tree/pixel replay {checks}/198',flush=True)
    summary=read(root/'summary.json');means={};gates={}
    for role in ROLES:
        own=[r for r in scores if r['role']==role];assert len(own)==11
        means[role]={label:{metric:math.fsum(r['regions']['primary'][label][metric] for r in own)/11 for metric in ['RGB','DE']} for label in ['input','constant','281','314']}
        for label in means[role]:
            for metric,value in means[role][label].items():close(value,summary['by_role'][role][label][metric])
    for arm in ['281','314']:
        gates[arm]={role:all(means[role][arm][metric]<means[role][comp][metric]-1e-10 for metric in ['RGB','DE'] for comp in ['input','constant']) for role in ROLES[1:]}
    assert gates==summary['role_gates']
    added=all(means['colour_only']['314'][metric]<means['colour_only']['281'][metric]-1e-10 for metric in ['RGB','DE'])
    assert added==summary['added_colour_benefit']
    passed=all(gates['314'].values()) and added
    assert summary['candidate_numeric_eligible']==passed
    return {'passed':True,'fits_replayed':22,'fitting_routes':fitting_routes,'held_routes':132,'scalar_render_metric_replays':checks,
            'candidate_numeric_eligible':passed,'verifier_fits':0}
