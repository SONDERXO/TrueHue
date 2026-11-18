"""Saved branch evidence audit; no fitted guard, new predictions or image reads."""
from pathlib import Path
from collections import Counter
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/correction_branch_clean_evidence_v1'
f32=lambda v:struct.unpack('f',struct.pack('f',v))[0]
def main():
    if OUT.exists():raise FileExistsError('Preserve audit')
    bound={}
    def read(p):
        p=ROOT/p;b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
    m=read('outputs/depth_four_correction_models_v1/models_PRIVATE.json')
    assert read('outputs/depth_four_correction_models_v1/verification_PRIVATE.json')['passed']
    e=read('outputs/depth_four_correction_comparison_v1/results_PRIVATE.json')
    assert read('outputs/depth_four_correction_comparison_v1/verification_PRIVATE.json')['passed']
    fits={f['held_key']:f for f in m['folds']+[m['full']]};leaves=[];cleanroutes=[]
    for key,f in fits.items():
        for t in f['model']['trace']:
            if f['model']['tree']['nodes'][t['node']]['kind']!='leaf':continue
            leaves.append(dict(fit_key=key,node=t['node'],action=t['action'],training_rows=len(t['rows']),clean_rows=sum(f['model']['clean'][i] for i in t['rows'])))
    for p in m['predictions']:
        if not p['case_id'].endswith('__clean') or p['features'] is None:continue
        key=p['subject_id'] if p['cohort']=='development' else 'full';f=fits[key];model=f['model'];tree=model['tree'];x=list(map(f32,p['features']));node=tree['root'];path=[]
        allclean=[i for i,v in enumerate(model['clean']) if v]
        globaloutside=[]
        for j,name in enumerate(m['feature_names']):
            vals=[f32(f['training_features'][i][j]) for i in allclean]
            if x[j]<min(vals) or x[j]>max(vals):globaloutside.append(name)
        while tree['nodes'][node]['kind']=='split':
            n=tree['nodes'][node];t=model['trace'][node];clean=[i for i in t['rows'] if model['clean'][i]];left=x[n['feature']]<=n['threshold'];child=n['left'] if left else n['right']
            childtrace=model['trace'][child];childclean=sum(model['clean'][i] for i in childtrace['rows'])
            vals=[f32(f['training_features'][i][n['feature']]) for i in clean]
            path.append(dict(node=node,feature=m['feature_names'][n['feature']],value=x[n['feature']],threshold=n['threshold'],left=left,
                parent_clean_rows=len(clean),chosen_child_clean_rows=childclean,parent_clean_min=min(vals) if vals else None,parent_clean_max=max(vals) if vals else None))
            node=child
        assert tree['nodes'][node]['values']==p['parameters']
        cleanroutes.append(dict(case_id=p['case_id'],cohort=p['cohort'],fit_key=key,parameters=p['parameters'],leaf=node,global_clean_range_outside_axes=globaloutside,path=path))
    summary={}
    for scope in ('full','folds'):
        rr=[r for r in leaves if (r['fit_key']=='full')==(scope=='full')];correct=[r for r in rr if r['action']!=0]
        summary[scope]=dict(correction_leaves=len(correct),correction_leaves_without_clean=sum(r['clean_rows']==0 for r in correct),correction_training_row_occurrences=sum(r['training_rows'] for r in correct))
    changed=[r for r in cleanroutes if r['parameters']!=[1.,1.,1.]]
    # Describe the fixed hypothetical leaf-evidence requirement, not an evaluated model.
    evalcorrect=[r for r in e['records'] if r['candidate']['changed_channels']>0]
    lookup={(r['fit_key'],r['node']):r for r in leaves}
    blocked=0
    preds={p['case_id']:p for p in m['predictions']}
    for r in evalcorrect:
        p=preds[r['case_id']];key=p['subject_id'] if p['cohort']=='development' else 'full';f=fits[key];x=list(map(f32,p['features']));i=0
        while f['model']['tree']['nodes'][i]['kind']=='split':
            n=f['model']['tree']['nodes'][i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
        blocked+=lookup[(key,i)]['clean_rows']==0
    summary['fixed_leaf_clean_requirement']=dict(existing_changed_conditions=len(evalcorrect),would_block=blocked,not_rendered_or_adopted=True)
    for p,h in bound.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    bound[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    OUT.mkdir();result=dict(summary=summary,leaves=leaves,usable_clean_routes=cleanroutes,changed_clean=changed,input_sha256=bound,new_fits=0,new_inference=0,holdout_image_reads=0)
    (OUT/'audit_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(summary=summary,changed_clean=changed),indent=2))
if __name__=='__main__':main()
