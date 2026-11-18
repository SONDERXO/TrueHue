"""Apply one frozen facial-range exception to existing saved predictions; zero fits."""
from pathlib import Path
import copy,json,hashlib,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree,float32
OUT=ROOT/'outputs/facial_veto_exception_models_v1'

def outside(features,names,bounds):
    try:
        pairs=[(float32(features[names.index(k)]),float(v[0]),float(v[1])) for k,v in bounds.items()]
        if len(pairs)!=4 or any(not math.isfinite(v) or not math.isfinite(lo) or not math.isfinite(hi) or lo>hi for v,lo,hi in pairs):return False
        return any(v<lo or v>hi for v,lo,hi in pairs)
    except (ValueError,TypeError,IndexError,KeyError,OverflowError):return False

def main():
    if OUT.exists():raise FileExistsError('Preserve completed candidate')
    read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    source=ROOT/'outputs/reserved_clean_veto_models_v1/models_PRIVATE.json';m=read(source)
    pp=ROOT/'outputs/vetoed_branch_facial_audit_v1/proposed_policy_PRIVATE.json';policy=read(pp)
    protocol=ROOT/'docs/facial-exception-to-veto-protocol-2026-11-08.md'
    assert sha(protocol)==policy['protocol_sha256'] and read(pp.parent/'verification_PRIVATE.json')['passed']
    assert sha(pp.parent/'audit_PRIVATE.json')==policy['audit_sha256']
    assert read(source.parent/'verification_PRIVATE.json')['passed']
    bound=dict(m['input_sha256'])
    for p in (source,pp,protocol,Path(__file__)):bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    result=copy.deepcopy(m);fits={f['held_key']:f for f in m['folds']+[m['full']]};traces=[]
    for q in result['predictions']:
        f=fits[q['subject_id']] if q['cohort']=='development' else fits['full'];p=policy['fits'][f['held_key']]
        restore=False;leaf=None
        if q['features'] is not None and q['status']=='available':
            leaf=PortableTree(f['model']['tree']).leaf_id(q['features'])
            if str(leaf) in f['vetoed_leaves']:
                restore=outside(q['features'],m['feature_names'],p['clean_bounds'])
                if restore:q['parameters']=PortableTree(f['pre_veto_model']['tree']).predict_one(q['features'])
        traces.append(dict(case_id=q['case_id'],fit_key=f['held_key'],leaf=leaf,restored=restore))
    result.update(input_sha256=bound,new_action_tree_fits=0,new_matching_MST_fits=0,new_target_fits=0,
        facial_exception_policy=policy,exception_trace=traces,policy_note='Saved post-veto trees unchanged; conditional facial exception applied to predictions separately')
    OUT.mkdir();(OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    print('Restored',sum(t['restored'] for t in traces),'of756 controls; zero fits.')
if __name__=='__main__':main()
