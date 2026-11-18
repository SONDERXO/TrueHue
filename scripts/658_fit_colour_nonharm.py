"""Exactly11 fixed colour-nonharm fits, unchanged clean veto and facial exception."""
from pathlib import Path
import copy,json,hashlib,sys,runpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.colour_nonharm_action_tree import fit_action_tree
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/colour_nonharm_models_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve completed/partial fits')
    read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    source=ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json';m=read(source)
    assert read(source.parent/'verification_PRIVATE.json')['passed']
    bound=dict(m['input_sha256'])
    for p in (source,Path(__file__),ROOT/'src/model_training/colour_nonharm_action_tree.py',ROOT/'docs/colour-only-nonharm-protocol-2026-11-09.md'):bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir();result=copy.deepcopy(m)
    outside=runpy.run_path(str(ROOT/'scripts/636_apply_facial_veto_exception.py'))['outside']
    for f in result['folds']+[result['full']]:
        old=f['model'];flags=[c.split('__',1)[1] in ('colour_cool','colour_warm','stress_color_none') for c in f['training_cases']]
        model=fit_action_tree(f['training_features'],old['costs'],old['clean'],old['actions'],m['feature_names'],max_depth=4,nonharm=flags)
        model.update(costs=old['costs'],clean=old['clean'],nonharm=flags);f['pre_veto_model']=copy.deepcopy(model)
        tree=PortableTree(model['tree']);hits={}
        for r in f['reserved_clean_vectors']:
            leaf=tree.leaf_id(r['features'])
            if tree.predict_one(r['features'])!=[1.,1.,1.]:hits.setdefault(str(leaf),[]).append(r['case_id'])
        for leaf in hits:model['tree']['nodes'][int(leaf)]['values']=[1.,1.,1.]
        f.update(model=model,vetoed_leaves=hits)
        (OUT/(f['held_key']+'_PRIVATE.json')).write_text(json.dumps(f,indent=2));print('Fit',f['held_key'],'colour constraints',sum(flags),flush=True)
    fits={f['held_key']:f for f in result['folds']+[result['full']]}
    def controls(f,x):
        tree=PortableTree(f['model']['tree']);leaf=tree.leaf_id(x)
        if str(leaf) in f['vetoed_leaves'] and outside(x,m['feature_names'],m['facial_exception_policy']['fits'][f['held_key']]['clean_bounds']):return PortableTree(f['pre_veto_model']['tree']).predict_one(x)
        return tree.predict_one(x)
    for f in fits.values():
        for i,x in enumerate(f['training_features']):
            a=f['model']['actions'].index(controls(f,x));cost=f['model']['costs'][i]
            if f['model']['clean'][i]:assert cost[a]==0
            if f['model']['nonharm'][i]:assert cost[a]<=cost[0]
        for r in f['reserved_clean_vectors']:assert controls(f,r['features'])==[1.,1.,1.]
    for p in result['predictions']:
        f=fits[p['subject_id']] if p['cohort']=='development' else fits['full'];p['parameters']=controls(f,p['features']) if p['features'] is not None else None
    result.update(input_sha256=bound,new_action_tree_fits=11,new_matching_MST_fits=0,new_target_fits=0,
        policy_note='New colour-nonharm greedy fit; clean veto and frozen facial exception applied on new leaf routes',exception_trace=None)
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':main()
