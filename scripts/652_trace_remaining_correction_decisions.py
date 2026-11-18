"""Frozen sixteen-case decision trace; no new action evaluation or training."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/remaining_correction_decision_trace_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve trace')
    bound={}
    def read(name):
        p=ROOT/name;b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
    audit=read('outputs/remaining_correction_failure_audit_v1/audit_PRIVATE.json')
    assert read('outputs/remaining_correction_failure_audit_v1/verification_PRIVATE.json')['passed']
    m=read('outputs/facial_veto_exception_models_v1/models_PRIVATE.json');parent=read('outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    preds={p['case_id']:p for p in m['predictions']};pp={p['case_id']:p for p in parent['predictions']}
    fits={f['held_key']:f for f in m['folds']+[m['full']]}
    selected=[r for r in audit['records'] if (r['layer']=='core' and r['metrics']['rgb8_mae_codes']['category']=='no_gain_but_saved_alternative_helped' and not r['explicitly_vetoed_leaf']) or r['metrics']['rgb8_mae_codes']['category']=='harmful_edit']
    assert len(selected)==16;records=[]
    for r in selected:
        cid=r['case_id'];p=preds[cid];f=fits[r['fit_key']];model=f['model'];tree=model['tree'];x=np.asarray(p['features'],np.float32);node=0;steps=[]
        while tree['nodes'][node]['kind']=='split':
            n=tree['nodes'][node];left=bool(x[n['feature']]<=n['threshold']);steps.append(dict(node=node,feature=m['feature_names'][n['feature']],value=float(x[n['feature']]),threshold=n['threshold'],left=left));node=n['left'] if left else n['right']
        assert PortableTree(tree).leaf_id(p['features'])==node and tree['nodes'][node]['values']==p['parameters']
        t=model['trace'][node];ids=t['rows'];cost=np.asarray(model['costs']);clean=np.asarray(model['clean']);total=cost[ids].sum(0);flags=clean[ids];feasible=[j for j in range(len(model['actions'])) if not np.any(cost[ids,j][flags]>0)]
        chosen=model['actions'].index(p['parameters']);assert chosen==min(feasible,key=lambda j:total[j])
        parentcontrols=pp[cid]['parameters'];pa=model['actions'].index(parentcontrols) if parentcontrols in model['actions'] else None
        matrix=np.asarray(f['training_features'],np.float32)[ids];outside=[name for j,name in enumerate(m['feature_names']) if x[j]<matrix[:,j].min() or x[j]>matrix[:,j].max()]
        heldclean=[]
        for q in m['predictions']:
            key=q['subject_id'] if q['cohort']=='development' else 'full'
            if key==r['fit_key'] and q['case_id'].endswith('__clean') and q['features'] is not None and PortableTree(tree).leaf_id(q['features'])==node:heldclean.append(q['case_id'])
        records.append(dict(case_id=cid,cohort=r['cohort'],kind=r['metrics']['rgb8_mae_codes']['category'],fit_key=r['fit_key'],leaf=node,route=steps,selected_action=chosen,parameters=p['parameters'],
            leaf_depth=t['depth'],leaf_training_rows=len(ids),leaf_training_clean=int(flags.sum()),training_recipes=dict(Counter(f['training_cases'][i].split('__',1)[1] for i in ids)),
            feasible_actions=feasible,unconstrained_best=int(total.argmin()),selected_total_cost=float(total[chosen]),identity_total_cost=float(total[0]),
            aligned_parent_parameters=parentcontrols,aligned_parent_action=pa,aligned_parent_feasible=pa in feasible if pa is not None else None,
            aligned_parent_total_cost=float(total[pa]) if pa is not None else None,outside_fitting_leaf_axes=outside,same_leaf_evaluation_clean=heldclean,
            errors=r['metrics']))
    summary=dict(cases=len(records),missed_core=sum(r['kind']!='harmful_edit' for r in records),harmful=sum(r['kind']=='harmful_edit' for r in records),
        missed_leaf_depths=dict(Counter(str(r['leaf_depth']) for r in records if r['kind']!='harmful_edit')),
        missed_identity_unconstrained_best=sum(r['unconstrained_best']==0 for r in records if r['kind']!='harmful_edit'),
        missed_parent_action_forbidden=sum(r['aligned_parent_feasible'] is False for r in records if r['kind']!='harmful_edit'))
    for p,h in bound.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    bound[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    OUT.mkdir();(OUT/'trace_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records,input_sha256=bound,new_fits=0,new_inference=0,holdout_image_reads=0),indent=2));print(json.dumps(summary,indent=2))
    print(json.dumps([r for r in records if r['kind']=='harmful_edit'],indent=2))
if __name__=='__main__':main()
