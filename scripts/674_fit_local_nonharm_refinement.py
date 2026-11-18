"""Single approved local refinement comparison; no recursive/depth sweep."""
from pathlib import Path
import copy,json,hashlib,sys,runpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree
from src.model_training.local_nonharm_refinement import refine_leaf
OUT=ROOT/'outputs/local_nonharm_refinement_models_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve completed/partial refinement')
    source=ROOT/'outputs/fixed_structure_nonharm_models_v1/models_PRIVATE.json'
    audit=ROOT/'outputs/conflicting_leaf_separability_v1/audit_PRIVATE.json'
    m=read(source);v=read(source.parent/'verification_PRIVATE.json')
    assert v['passed'] and v['model_sha256']==sha(source)
    av=read(audit.parent/'verification_PRIVATE.json');assert av['passed'] and av['audit_sha256']==sha(audit)
    bound=dict(m['input_sha256'])
    for p in (source,source.parent/'verification_PRIVATE.json',audit,audit.parent/'verification_PRIVATE.json',Path(__file__),ROOT/'src/model_training/local_nonharm_refinement.py',ROOT/'docs/local-nonharm-refinement-protocol-2026-11-09.md'):
        bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir();result=copy.deepcopy(m)
    outside=runpy.run_path(str(ROOT/'scripts/636_apply_facial_veto_exception.py'))['outside']
    eligible={r['configuration']:r['leaf'] for r in read(audit)['records']}
    for f in result['folds']+[result['full']]:
        model,receipt=refine_leaf(f['pre_veto_model'],f['training_features'],eligible[f['held_key']])
        model['tree']['provenance']['bounded_local_nonharm_refinement']=True
        f['pre_veto_model']=copy.deepcopy(model);f['local_refinement']=receipt
        tree=PortableTree(model['tree']);hits={}
        for r in f['reserved_clean_vectors']:
            leaf=tree.leaf_id(r['features'])
            if tree.predict_one(r['features'])!=[1.,1.,1.]:hits.setdefault(str(leaf),[]).append(r['case_id'])
        for leaf in hits:model['tree']['nodes'][int(leaf)]['values']=[1.,1.,1.]
        f.update(model=model,vetoed_leaves=hits)
        (OUT/(f['held_key']+'_PRIVATE.json')).write_text(json.dumps(f,indent=2));print(f['held_key'],json.dumps(receipt),flush=True)
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
    result.update(input_sha256=bound,new_action_tree_fits=0,local_refinement_configurations=11,
        added_split_fits=sum(f['local_refinement']['split_added'] for f in fits.values()),
        new_matching_MST_fits=0,new_target_fits=0,
        policy_note='At most one constrained split per audited conflicting leaf; all ancestors and other leaves fixed.',exception_trace=None)
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':main()
