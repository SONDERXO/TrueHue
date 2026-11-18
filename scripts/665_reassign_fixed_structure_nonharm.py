"""Fixed structures, eleven constrained leaf-action reassignments; zero split fits."""
from pathlib import Path
import copy,json,hashlib,sys,runpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/fixed_structure_nonharm_models_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve completed/partial fits')
    read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    source=ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json';m=read(source)
    assert read(source.parent/'verification_PRIVATE.json')['passed']
    bound=dict(m['input_sha256'])
    for p in (source,Path(__file__),ROOT/'docs/fixed-structure-nonharm-protocol-2026-11-09.md'):bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir();result=copy.deepcopy(m)
    outside=runpy.run_path(str(ROOT/'scripts/636_apply_facial_veto_exception.py'))['outside']
    for f in result['folds']+[result['full']]:
        old=f['model'];flags=[c.split('__',1)[1] in ('colour_cool','colour_warm','stress_color_none') for c in f['training_cases']]
        model=copy.deepcopy(f['pre_veto_model'])
        loss=np.asarray(old['costs']);clean=np.asarray(old['clean']);safe=np.asarray(flags)
        for trace in model['trace']:
            node=model['tree']['nodes'][trace['node']]
            if node['kind']!='leaf':continue
            ix=trace['rows'];sums=loss[ix].sum(0)
            forbidden=np.any((clean[ix,None]&(loss[ix]>0))|(safe[ix,None]&(loss[ix]>loss[ix,0,None])),axis=0)
            sums[forbidden]=np.inf;action=int(np.argmin(sums));trace.update(action=action,cost=float(sums[action]));node['values']=model['actions'][action]
        model['tree']['provenance']['fixed_structure_reassignment']=True
        model.update(costs=old['costs'],clean=old['clean'],nonharm=flags);f['pre_veto_model']=copy.deepcopy(model)
        tree=PortableTree(model['tree']);hits={}
        for r in f['reserved_clean_vectors']:
            leaf=tree.leaf_id(r['features'])
            if tree.predict_one(r['features'])!=[1.,1.,1.]:hits.setdefault(str(leaf),[]).append(r['case_id'])
        for leaf in hits:model['tree']['nodes'][int(leaf)]['values']=[1.,1.,1.]
        f.update(model=model,vetoed_leaves=hits)
        (OUT/(f['held_key']+'_PRIVATE.json')).write_text(json.dumps(f,indent=2));print('Fit',f['held_key'],'colour constraints',sum(flags),flush=True)
    fits={f['held_key']:f for f in result['folds']+[result['full']]}
    trees={k:(PortableTree(f['model']['tree']),PortableTree(f['pre_veto_model']['tree'])) for k,f in fits.items()}
    def controls(f,x):
        tree,pre=trees[f['held_key']];leaf=tree.leaf_id(x)
        if str(leaf) in f['vetoed_leaves'] and outside(x,m['feature_names'],m['facial_exception_policy']['fits'][f['held_key']]['clean_bounds']):return pre.predict_one(x)
        return tree.predict_one(x)
    for f in fits.values():
        for i,x in enumerate(f['training_features']):
            a=f['model']['actions'].index(controls(f,x));cost=f['model']['costs'][i]
            if f['model']['clean'][i]:assert cost[a]==0
            if f['model']['nonharm'][i]:assert cost[a]<=cost[0]
        for r in f['reserved_clean_vectors']:assert controls(f,r['features'])==[1.,1.,1.]
    for p in result['predictions']:
        f=fits[p['subject_id']] if p['cohort']=='development' else fits['full'];p['parameters']=controls(f,p['features']) if p['features'] is not None else None
    result.update(input_sha256=bound,new_action_tree_fits=0,fixed_structure_configurations=11,new_matching_MST_fits=0,new_target_fits=0,
        policy_note='Fixed old split structure; constrained leaf actions only. Internal traces historical; leaf actions updated.',exception_trace=None)
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':main()
