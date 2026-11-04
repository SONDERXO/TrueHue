"""Training-only control-preserving leaf outputs on saved trees; no new splits."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.evaluation.correction_prototype import apply_correction,image_errors
from src.data_preparation.controlled_training_table import TARGETS

PARENT=ROOT/'outputs/table2_chroma_distribution_comparison_v1'
OUT=ROOT/'outputs/table2_clean_leaf_policy_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(PARENT/'plan.json');data=read(PARENT/'summary.json');verify=read(PARENT/'verification.json')
    assert digest(PARENT/'summary.json')==verify['summary_sha256']
    assert digest(PARENT/'features.json')==verify['features_sha256']
    rows={r['pair_id']:dict(r) for r in plan['rows']}
    for r in read(PARENT/'features.json'):rows[r['pair_id']].update(r['features'])
    columns=plan['features'];baseline={r['pair_id']:r for r in data['records']}
    paths=[Path(__file__),ROOT/'docs/table2-clean-leaf-policy-protocol.md',PARENT/'plan.json',PARENT/'features.json',PARENT/'summary.json',PARENT/'verification.json']
    paths+=list(PARENT.glob('fold_*/*'))
    for r in rows.values():paths.extend(ROOT/r[k] for k in ['input_path','input_mask_path','reference_mask_path','reference_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.mkdir()
    write(OUT/'plan.json',dict(status='frozen_before_policy_evaluation',rule='Any fitting identity member makes leaf output identity; other leaf vectors unchanged',
        rows=list(rows.values()),folds=plan['folds'],features=columns,excluded=plan['excluded'],retained_holds=plan['retained_holds'],
        input_sha256=hashes,identity_tolerance=0.,new_tree_fits=0,runtime_replacement=False))
    records=[];fold_records=[]
    for fold in plan['folds']:
        fid=fold['fold_id'];payload=read(PARENT/f'fold_{fid}/decision_tree.json');original=PortableTree(payload)
        training=[rows[p] for p in fold['train_pair_ids']];held=[rows[p] for p in fold['inner_validation_pair_ids']]
        assert len(training)==18 and len(held)==2
        assert {r['duplicate_group_id'] for r in training}.isdisjoint(r['duplicate_group_id'] for r in held)
        leaves={}
        for r in training:leaves.setdefault(original.leaf_id([r[k] for k in columns]),[]).append(r)
        modified=deepcopy(payload);changed=[];leaf_records=[]
        for leaf,members in sorted(leaves.items()):
            controls=[r for r in members if r['variant']=='identity']
            for r in controls:assert all(r[k]==1. for k in TARGETS)
            before=payload['nodes'][leaf]['values']
            if controls:
                modified['nodes'][leaf]['values']=[1.,1.,1.]
                if before!=[1.,1.,1.]:changed.append(leaf)
            leaf_records.append(dict(leaf=leaf,fitting_members=[r['pair_id'] for r in members],
                identity_members=[r['pair_id'] for r in controls],original_parameters=before,
                policy_parameters=modified['nodes'][leaf]['values']))
        modified['provenance']=dict(experimental=True,policy='training_identity_leaf_v1',fold_id=fid,
            parent_sha256=digest(PARENT/f'fold_{fid}/decision_tree.json'),new_split_fitting=False)
        folder=OUT/f'fold_{fid}';folder.mkdir();write(folder/'decision_tree.json',modified)
        policy=PortableTree(modified)
        for r in training:
            if r['variant']=='identity':assert policy.predict_one([r[k] for k in columns])==[1.,1.,1.]
        fold_records.append(dict(fold_id=fid,changed_leaves=changed,leaves=leaf_records,fitting_controls_identity=True))
        for r in held:
            pair=r['pair_id'];x=[r[k] for k in columns];parameters=policy.predict_one(x)
            assert policy.leaf_id(x)==original.leaf_id(x)
            image=rgb(ROOT/r['input_path']);reference=rgb(ROOT/r['reference_path'])
            mask=cv2.imread(str(ROOT/r['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/r['reference_mask_path']),0)>0
            corrected=apply_correction(image,mask,parameters)
            output=OUT/(pair+'_corrected.png');assert cv2.imwrite(str(output),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
            records.append(dict(pair_id=pair,variant=r['variant'],fold_id=fid,leaf=policy.leaf_id(x),parameters=parameters,
                original_parameters=baseline[pair]['parameters'],policy_changed=parameters!=baseline[pair]['parameters'],
                no_correction=baseline[pair]['no_correction'],original=baseline[pair]['candidate'],
                policy=image_errors(reference,corrected,scoring),output_sha256=digest(output)))
    aggregate={group:{method:float(np.mean([r[method]['ciede2000_source_mask'] for r in subset])) for method in ['no_correction','original','policy']}
        for group,subset in [('all',records),('identity',[r for r in records if r['variant']=='identity']),('distorted',[r for r in records if r['variant']!='identity'])]}
    harmed=[r['pair_id'] for r in records if r['variant']=='identity' and r['policy']['ciede2000_source_mask']>0]
    gate=dict(overall_improves=aggregate['all']['policy']<aggregate['all']['no_correction'],identity_pass=not harmed,harmed_identity_ids=harmed)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',dict(status='complete_experimental_policy',records=records,folds=fold_records,aggregate=aggregate,gate=gate,
        new_tree_fits=0,runtime_replaced=False,final_validated=False,input_sha256=hashes))
    print(json.dumps(dict(aggregate=aggregate,gate=gate,changed_predictions=sum(r['policy_changed'] for r in records)),indent=2))


if __name__=='__main__':main()
