"""Fixed conservative outputs on saved five-feature fifteen-source trees."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
import joblib
from src.model_training.portable_tree import PortableTree
from src.evaluation.correction_prototype import apply_correction,image_errors


def main():
    parent=ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1';out=ROOT/'outputs/table2_five_feature_clean_leaf_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(parent/'fit_plan.json');data=read(parent/'summary.json');verification=read(parent/'verification.json')
    assert digest(parent/'summary.json')==verification['summary_sha256'] and digest(parent/'fit_plan.json')==verification['fit_plan_sha256']
    rows={r['pair_id']:r for r in plan['rows']};prior={r['pair_id']:r for r in data['records']};columns=plan['baseline_features']
    paths=[Path(__file__),ROOT/'docs/table2-five-feature-leaf-protocol.md',parent/'fit_plan.json',parent/'summary.json',parent/'verification.json']
    paths+=list(parent.glob('fold_*/*'))
    for r in rows.values():paths.extend(ROOT/r[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    out.mkdir();write(out/'plan.json',dict(status='frozen_before_scoring',parent_plan_sha256=digest(parent/'fit_plan.json'),
        rule='Identity if any fitting control in leaf; all other original outputs unchanged',input_sha256=hashes,new_fits=0))
    records=[];audits=[];checked_controls=0
    for fold in plan['folds']:
        fid=fold['fold_id'];original=read(parent/f'fold_{fid}/baseline5.json');tree=PortableTree(original);modified=deepcopy(original)
        training=[rows[p] for p in fold['train_pair_ids']];members={}
        for r in training:members.setdefault(tree.leaf_id([r[k] for k in columns]),[]).append(r)
        for leaf,selected in members.items():
            if any(r['variant']=='identity' for r in selected):modified['nodes'][leaf]['values']=[1.,1.,1.]
        folder=out/f'fold_{fid}';folder.mkdir();modified['provenance']['leaf_policy']='identity_if_any_fitting_control';write(folder/'decision_tree.json',modified)
        candidate=PortableTree(modified)
        # Independently check membership with the saved sklearn tree before evaluating held cases.
        model=joblib.load(parent/f'fold_{fid}/baseline5.joblib');leaves=model.apply([[r[k] for k in columns] for r in training])
        for index,(before,after) in enumerate(zip(original['nodes'],modified['nodes'])):
            if before['kind']=='split':assert before==after;continue
            controls=[r for r,l in zip(training,leaves) if l==index and r['variant']=='identity']
            assert after['values']==([1.,1.,1.] if controls else before['values'])
        for r in training:
            if r['variant']=='identity':assert candidate.predict_one([r[k] for k in columns])==[1.,1.,1.];checked_controls+=1
        audits.append(dict(fold_id=fid,leaves=[dict(leaf=l,members=[r['pair_id'] for r in m],identity_members=[r['pair_id'] for r in m if r['variant']=='identity']) for l,m in members.items()]))
        for pair in fold['inner_validation_pair_ids']:
            row=rows[pair];assert all(r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
            parameters=candidate.predict_one([row[k] for k in columns]);image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path'])
            mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            corrected=apply_correction(image,mask,parameters)
            g,r,b=parameters;raw=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
            independent=image.copy();independent[mask]=raw[mask];np.testing.assert_array_equal(corrected,independent)
            path=out/(pair+'_corrected.png');assert cv2.imwrite(str(path),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR));np.testing.assert_array_equal(rgb(path),independent)
            records.append(dict(pair_id=pair,variant=row['variant'],fold_id=fid,leaf=candidate.leaf_id([row[k] for k in columns]),parameters=parameters,
                changed=parameters!=prior[pair]['methods']['baseline5']['parameters'],no_correction=prior[pair]['no_correction'],
                baseline=prior[pair]['methods']['baseline5']['metrics'],candidate=image_errors(reference,independent,score),output_sha256=digest(path)))
    aggregate={scope:{m:float(np.mean([r[m]['ciede2000_source_mask'] for r in subset])) for m in ['no_correction','baseline','candidate']}
        for scope,subset in [('all',records),('identity',[r for r in records if r['variant']=='identity']),('distorted',[r for r in records if r['variant']!='identity'])]}
    harmed=[r['pair_id'] for r in records if r['variant']=='identity' and r['candidate']['ciede2000_source_mask']>0]
    gate=dict(overall_improves=aggregate['all']['candidate']<aggregate['all']['no_correction'],identity_pass=not harmed,harmed_identity_ids=harmed)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    assert hashes=={p:digest(ROOT/p) for p in hashes} and checked_controls==210 and len(records)==30
    write(out/'summary.json',dict(status='complete_experimental_policy',records=records,folds=audits,aggregate=aggregate,gate=gate,input_sha256=hashes,new_fits=0,runtime_replaced=False))
    write(out/'verification.json',dict(status='pass',verified_held_outputs=30,verified_exports=15,fitting_control_occurrences=210,
        independent_sklearn_membership_and_rgb_replay=True,original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')))
    print(json.dumps(dict(aggregate=aggregate,gate=gate,changed_predictions=sum(r['changed'] for r in records)),indent=2))


if __name__=='__main__':main()
