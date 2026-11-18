"""One fixed joint-cue tree workflow; no execution on import."""
import math
from pathlib import Path
import sys
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from skimage.color import rgb2lab,deltaE_ciede2000
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from wb_feature_direct_workflow import SETTINGS,read,write,sha
from wb_feature_direct_verify import route,verify_fit,close
from src.model_training.luminance_chroma_operator import parameters,render_rgb8
from src.evaluation.luminance_chroma_scalar import replay
from src.evaluation.directional_recoverability import metrics,regions
ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']


def select(rows,fold):
    wanted=set(fold['fitting_cases']);found={}
    for r in rows:
        if r['case_id'] not in wanted:continue
        if r['case_id'] in found or r['source_id']==fold['held_source_id']:raise ValueError('Held/duplicate fit payload')
        x=r['x'];y=r['y']
        if len(x)!=4410 or not np.isfinite(x).all() or np.asarray(x,np.float32).astype(float).tolist()!=x:raise ValueError('Finite float32 width4410 required')
        parameters(y);found[r['case_id']]=r
    if set(found)!=wanted or len(found)!=60:raise ValueError('Incomplete fit roster')
    result=[found[k] for k in fold['fitting_cases']]
    if len({r['source_id'] for r in result})!=10 or any(sum(r['role']==v for r in result)!=10 for v in ROLES):raise ValueError('Incomplete source/role coverage')
    return result


def fit_and_seal(plan,rows,out,factory=DecisionTreeRegressor):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    assert len(rows)==66 and len(plan['folds'])==11 and plan['settings']==SETTINGS
    assert len({r['case_id'] for r in rows})==66 and len({(r['source_id'],r['role']) for r in rows})==66
    assert all(r['generated_fixture'] is plan['generated_fixture'] for r in rows)
    payloads=[]
    for f in plan['folds']:
        assert [r['case_id'] for r in rows if r['source_id']==f['held_source_id']]==f['evaluation_cases']
        payloads.append((f,select(rows,f)))
    out.mkdir();(out/'models').mkdir();write(out/'plan.json',plan);write(out/'rows.json',rows)
    entries=[];models={};constants={};started=0
    try:
        for fold,fitting in payloads:
            started+=1;assert started<=11
            write(out/'fit_accounting.json',dict(started=started,maximum=11))
            x=np.asarray([r['x'] for r in fitting],np.float32);y=np.asarray([r['y'] for r in fitting])
            native=factory(**SETTINGS);native.fit(x,y);t=native.tree_;nodes=[]
            for i in range(t.node_count):
                if t.children_left[i]==-1:nodes.append(dict(kind='leaf',values=t.value[i,:,0].tolist()))
                else:nodes.append(dict(kind='split',feature=int(t.feature[i]),threshold=float(t.threshold[i]),left=int(t.children_left[i]),right=int(t.children_right[i])))
            model=dict(schema='truehue_camera_control_cart_research_v1',dimensions=4410,
                       target_names=['gamma','exposure_gain','red_balance','blue_balance','chroma_scale'],
                       settings=native.get_params(deep=False),comparison='<=',nodes=nodes)
            assert model['settings']==SETTINGS
            scalar=[route(model,r['x']) for r in fitting]
            assert [p for leaf,p in scalar]==native.predict(x).tolist()
            assert [leaf for leaf,p in scalar]==native.apply(x).tolist()
            constant=verify_fit(model,fitting,fold,SETTINGS)
            sid=fold['held_source_id'];path='models/'+sid+'.json';write(out/path,model)
            entries.append(dict(source=sid,path=path,sha256=sha(out/path)))
            models[sid]=model;constants[sid]=constant
            print('Joint tree verified '+str(started)+'/11',flush=True)
        write(out/'all_fits_verified.json',dict(verified_fits=11,fitting_routes=660,models=entries))
        inference=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x']} for r in rows]
        write(out/'inference.json',inference)
        for e in entries:assert sha(out/e['path'])==e['sha256']
        sealed=[]
        for r in inference:
            leaf,p=route(models[r['source_id']],r['x']);parameters(p)
            sealed.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture']}|dict(controls=p,leaf=leaf,constant=constants[r['source_id']]))
        write(out/'held_controls_sealed.json',sealed)
        write(out/'prediction_seal.json',dict(predictions=66,sha256=sha(out/'held_controls_sealed.json')))
        return sealed
    except Exception as exc:
        write(out/'failure.json',dict(error=str(exc),started_fits=started));raise


def score(rows,out,loader):
    out=Path(out);seal=read(out/'prediction_seal.json')
    assert seal['predictions']==66 and sha(out/'held_controls_sealed.json')==seal['sha256']
    predictions=read(out/'held_controls_sealed.json');by_id={r['case_id']:r for r in rows}
    (out/'evaluation').mkdir();records=[]
    for i,p in enumerate(predictions):
        a=loader(by_id[p['case_id']],p)
        image,ref,alpha,protected=[a[k] for k in ['input','reference','alpha','protected']]
        candidate=render_rgb8(image,alpha,protected,p['controls'])
        scalar,_=replay(image,ref,alpha,protected,p['controls'])
        assert np.array_equal(candidate,scalar)
        assert np.array_equal(candidate[protected],image[protected]) and np.array_equal(candidate[alpha==0],image[alpha==0])
        outputs=dict(input=image,constant=a['constant'],saved314=a['saved314'],joint=candidate)
        region=regions(alpha)
        scored={name:{label:metrics(value,ref,mask) for label,value in outputs.items()} for name,mask in region.items()}
        # Independent per-pixel arithmetic/aggregation, same standard DE implementation.
        reference_lab=rgb2lab(ref/255.)
        for label,value in outputs.items():
            rgb=np.abs(value.astype(float)-ref);de=deltaE_ciede2000(rgb2lab(value/255.),reference_lab)
            for name,mask in region.items():
                n=int(mask.sum())
                if not n:assert scored[name][label] is None;continue
                close(scored[name][label]['RGB'],math.fsum(float(v) for v in rgb[mask].flat)/(3*n))
                close(scored[name][label]['DE'],math.fsum(float(v) for v in de[mask])/n)
                if 'parent_scores' in a and label!='joint':
                    original='314' if label=='saved314' else label
                    for m in ['RGB','DE']:close(scored[name][label][m],a['parent_scores'][name][original][m])
        r={k:p[k] for k in ['case_id','source_id','role']}|dict(regions=scored,controls=p['controls'],leaf=p['leaf'],
             parameter_MAE=[abs(u-v) for u,v in zip(p['controls'],by_id[p['case_id']]['y'])],
             changed_pixels=int(np.any(candidate!=image,axis=2).sum()))
        records.append(r)
        np.savez(out/'evaluation'/(p['case_id']+'.npz'),input=image,reference=ref,alpha=alpha,protected=protected,joint=candidate)
        if (i+1)%11==0:print('Joint scalar render/metrics verified '+str(i+1)+'/66',flush=True)
    write(out/'records.json',records)
    means={role:{label:{m:math.fsum(r['regions']['primary'][label][m] for r in records if r['role']==role)/11
                  for m in ['RGB','DE']} for label in ['input','constant','saved314','joint']} for role in ROLES}
    gates={role:all(means[role]['joint'][m]<means[role][b][m]-1e-10 for m in ['RGB','DE'] for b in ['input','constant']) for role in ROLES[1:]}
    under=all(means['exposure_under']['joint'][m]<means['exposure_under']['saved314'][m]-1e-10 for m in ['RGB','DE'])
    colour=all(means['colour_only']['joint'][m]<=means['colour_only']['saved314'][m]+1e-10 for m in ['RGB','DE'])
    summary=dict(by_role=means,role_gates=gates,under_improvement=under,colour_nonworse=colour,
        numerical_eligible=all(gates.values()) and under and colour,model_ready=False,
        identity_changed=sum(r['changed_pixels']>0 for r in records if r['role']=='identity'),
        nonidentity_harms=[r['case_id'] for r in records if r['role']!='identity' and any(r['regions']['primary']['joint'][m]>r['regions']['primary']['input'][m]+1e-10 for m in ['RGB','DE'])],
        parameter_MAE_by_role={role:[math.fsum(r['parameter_MAE'][j] for r in records if r['role']==role)/11 for j in range(5)] for role in ROLES})
    assert sha(out/'held_controls_sealed.json')==seal['sha256']
    write(out/'summary.json',summary)
    return summary
