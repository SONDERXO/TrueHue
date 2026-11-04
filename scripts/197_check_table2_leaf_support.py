"""Fixed fitting-only leaf-range abstention on five-feature development models."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.model_training.portable_tree import PortableTree,float32
from src.evaluation.correction_prototype import apply_correction,image_errors


def main():
    parent=ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1';previous=ROOT/'outputs/table2_five_feature_clean_leaf_v1'
    out=ROOT/'outputs/table2_leaf_support_guard_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(parent/'fit_plan.json');prior=read(previous/'summary.json')
    assert digest(previous/'summary.json')==read(previous/'verification.json')['summary_sha256']
    assert digest(parent/'fit_plan.json')==read(parent/'verification.json')['fit_plan_sha256']
    rows={r['pair_id']:r for r in plan['rows']};columns=plan['baseline_features'];expected={r['pair_id']:r for r in prior['records']}
    paths=[Path(__file__),ROOT/'docs/table2-leaf-support-protocol.md',parent/'fit_plan.json',previous/'summary.json',previous/'verification.json']
    paths+=list(previous.glob('fold_*/*'))+list(parent.glob('fold_*/*'))
    for r in rows.values():paths.extend(ROOT/r[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    out.mkdir();write(out/'plan.json',dict(status='frozen_before_scoring',rows=plan['rows'],folds=plan['folds'],features=columns,
        excluded=plan['excluded'],retained_holds=plan['retained_holds'],input_sha256=hashes,
        rule='Identity if any float32 feature is outside reached fitting-leaf closed min/max;otherwise unchanged conservative prediction',new_fits=0))
    records=[];range_records=[]
    for fold in plan['folds']:
        fid=fold['fold_id'];tree=PortableTree(read(previous/f'fold_{fid}/decision_tree.json'))
        training=[rows[p] for p in fold['train_pair_ids']];members={}
        for r in training:members.setdefault(tree.leaf_id([r[k] for k in columns]),[]).append(r)
        ranges={leaf:dict(minimum=[min(float32(r[k]) for r in selected) for k in columns],maximum=[max(float32(r[k]) for r in selected) for k in columns],
            fitting_pair_ids=[r['pair_id'] for r in selected]) for leaf,selected in members.items()}
        folder=out/f'fold_{fid}';folder.mkdir();write(folder/'leaf_ranges.json',ranges)
        range_records.append(dict(fold_id=fid,ranges=ranges))
        for pair in fold['inner_validation_pair_ids']:
            row=rows[pair];assert all(r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
            x=[row[k] for k in columns];leaf=tree.leaf_id(x);support=ranges[leaf];original=tree.predict_one(x)
            violations=[columns[i] for i,v in enumerate(x) if not support['minimum'][i]<=float32(v)<=support['maximum'][i]]
            parameters=[1.,1.,1.] if violations else original
            assert original==expected[pair]['parameters']
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path']);mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            corrected=apply_correction(image,mask,parameters);path=out/(pair+'_corrected.png');assert cv2.imwrite(str(path),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
            records.append(dict(pair_id=pair,variant=row['variant'],fold_id=fid,leaf=leaf,outside_axes=violations,abstained=bool(violations),
                parameters=parameters,original_parameters=original,no_correction=expected[pair]['no_correction'],original=expected[pair]['candidate'],
                guarded=image_errors(reference,corrected,score),output_sha256=digest(path)))
    aggregate={scope:{m:float(np.mean([r[m]['ciede2000_source_mask'] for r in subset])) for m in ['no_correction','original','guarded']}
        for scope,subset in [('all',records),('identity',[r for r in records if r['variant']=='identity']),('distorted',[r for r in records if r['variant']!='identity'])]}
    harms=[r['pair_id'] for r in records if r['variant']=='identity' and r['guarded']['ciede2000_source_mask']>0]
    gate=dict(overall_improves=aggregate['all']['guarded']<aggregate['all']['no_correction'],identity_pass=not harms,harmed_identity_ids=harms)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(out/'summary.json',dict(status='complete_experimental_support_guard',records=records,ranges=range_records,aggregate=aggregate,gate=gate,input_sha256=hashes,
        abstentions=sum(r['abstained'] for r in records),new_fits=0,runtime_replaced=False,final_validated=False))
    print(json.dumps(dict(aggregate=aggregate,gate=gate,abstentions=sum(r['abstained'] for r in records)),indent=2))


if __name__=='__main__':main()
