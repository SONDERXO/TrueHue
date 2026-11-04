"""One fixed fitting-control rule on saved direct-gamma source-held models."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors


def main():
    parent=ROOT/'outputs/direct_gamma_regression_comparison_v1';out=ROOT/'outputs/direct_gamma_clean_leaf_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    for name,sha in read(parent/'verification.json')['evidence_sha256'].items():assert digest(parent/name)==sha
    plan=read(parent/'plan.json');prior=read(parent/'predictions.json')
    rows={r['pair_id']:r for r in plan['rows']};features=plan['features']
    paths=[Path(__file__),ROOT/'docs/direct-gamma-clean-leaf-protocol.md',ROOT/'src/model_training/training_identity_leaf_policy.py',parent/'plan.json',parent/'verification.json']
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_held_scoring',parent_plan_sha256=digest(parent/'plan.json'),
        rule='Identity if any fitting unchanged control reaches leaf; all other outputs and splits unchanged',input_sha256=hashes,new_regression_fits=0))
    records=[];fitting_controls=0
    for fold in plan['folds']:
        fid=fold['fold_id'];original=read(parent/f'fold_{fid}/paper_gamma_refit.json');tree=PortableTree(original)
        training=[rows[i] for i in fold['train_pair_ids']]
        modified,audit=protect_identity_leaves(original,[[r[k] for k in features] for r in training],[r['variant']=='identity' for r in training])
        folder=out/f'fold_{fid}';folder.mkdir()
        (folder/'tree.json').write_text(json.dumps(modified,indent=2),encoding='utf-8')
        audit['training_pair_ids']=[r['pair_id'] for r in training]
        (folder/'fitting_membership.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
        candidate=PortableTree(modified)
        for row in training:
            if row['variant']=='identity':assert candidate.predict_one([row[k] for k in features])==[1.,1.,1.];fitting_controls+=1
        for pair_id in fold['inner_validation_pair_ids']:
            row=rows[pair_id]
            assert row['source_image_id'] not in {r['source_image_id'] for r in training}
            assert row['duplicate_group_id'] not in {r['duplicate_group_id'] for r in training}
            x=[row[k] for k in features];leaf=tree.leaf_id(x);params=candidate.predict_one(x)
            members=audit['membership'][leaf]
            image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
            mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            output=image.copy();output[mask]=np.rint(transform_rgb(image.astype(float)/255,*params)[mask]*255).astype(np.uint8)
            assert np.array_equal(output[~mask],image[~mask])
            path=folder/(pair_id+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
            raw=next(r for r in prior if r['pair_id']==pair_id and r['method']=='paper_gamma_refit')
            no=next(r for r in prior if r['pair_id']==pair_id and r['method']=='no_correction')
            records.append(dict(pair_id=pair_id,source_image_id=row['source_image_id'],variant=row['variant'],fold_id=fid,leaf=leaf,
                fitting_control_members=[training[i]['pair_id'] for i in members['identity_indices']],
                parameters=params,unprotected_parameters=raw['paper_parameters'],changed_input_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),
                no_correction_error=no['ciede2000_source_mask'],unprotected_error=raw['ciede2000_source_mask'],
                metrics=image_errors(reference,output,score),output_sha256=digest(path)))
    aggregates={}
    for scope in ['all','identity','distorted']:
        selected=[r for r in records if scope=='all' or (r['variant']=='identity')==(scope=='identity')]
        aggregates[scope]=dict(pairs=len(selected),no_correction=float(np.mean([r['no_correction_error'] for r in selected])),
            unprotected=float(np.mean([r['unprotected_error'] for r in selected])),
            protected=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in selected])),
            changed_pairs=sum(r['changed_input_pixels']>0 for r in selected))
    harmed=[r['pair_id'] for r in records if r['variant']=='identity' and r['changed_input_pixels']>0]
    gate=dict(overall_improves=aggregates['all']['protected']<aggregates['all']['no_correction'],clean_unchanged=not harmed)
    gate['passed']=gate['overall_improves'] and gate['clean_unchanged']
    assert fitting_controls==210 and len(records)==30 and all(digest(ROOT/p)==sha for p,sha in hashes.items())
    write('predictions.json',records);write('summary.json',dict(status='complete_no_automatic_promotion',sources=15,pairs=30,
        aggregates=aggregates,gate=gate,harmed_identity_ids=harmed,fitting_control_checks=fitting_controls,
        new_regression_fits=0,active_demo_changed=False,final_validation_test_access=False))
    print(json.dumps(dict(aggregates=aggregates,gate=gate,harmed_identity_ids=harmed),indent=2))


if __name__=='__main__':main()
