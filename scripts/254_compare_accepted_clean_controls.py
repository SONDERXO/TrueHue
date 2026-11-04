"""Add only reviewed unchanged originals; compare diversity with count matching."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.controlled_training_table import FEATURE_KEYS,FEATURES,TARGETS
from src.data_preparation.redesign_access import training_candidate
from src.model_training.portable_tree import PortableTree,export_tree
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors

METHODS=('historical_only','count_matched_controls','new_clean_sources')


def main():
    out=ROOT/'outputs/accepted_clean_control_comparison_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    parent=ROOT/'outputs/direct_gamma_regression_comparison_v1';old_plan=read(parent/'plan.json')
    old_rows=[dict(r,cohort='historical',paper_target=old_plan['converted_targets'][r['pair_id']]) for r in old_plan['rows']]
    approved=ROOT/'outputs/training_review36_import_v1';reviews=read(approved/'combined_original_mask_reviews60.json')
    for name,sha in read(approved/'verification.json')['evidence_sha256'].items():assert digest(approved/name)==sha
    prepared=ROOT/'outputs/correction_training_preparation_v1';original_hashes=read(prepared/'verification.json')['evidence_sha256']
    sources={r['image_id']:r for r in (json.loads(x) for x in (prepared/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    quality={r['image_id']:r for r in read(ROOT/'outputs/training_reference_color_audit_v1/source_dispositions.json')}
    disposition={r['image_id']:r for r in read(ROOT/'outputs/correction_duplicate_audit_v1/candidate_dispositions.json')}
    allocation=ROOT/'outputs/correction_data_redesign_v1';manifest,policy=read(allocation/'selection.json'),read(allocation/'access_policy.json')
    _,identity=contract(ROOT);artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    lookup=DevelopmentMonotoneLookup(read(artifact),identity)
    # Source blur is an explicit user statement, not transferred candidate-mask rejection.
    blur_review=read(ROOT/'outputs/color_cast_ycrcb_review_import_v1/reconciled_reviews.json')
    blur=next(r for r in blur_review if r['source_id']=='66413')
    assert 'too blurry' in blur['notes']
    new_rows=[];held=[]
    for review in reviews:
        if review['decision']!='accept':continue
        image_id=review['image_id'];s=sources[image_id];name=s['source_id']
        if review['notes'].strip() or name=='66413':
            held.append(dict(image_id=image_id,decision='accept',exact_notes=review['notes'],
                hold='explicit_source_blur' if name=='66413' else 'accepted_reference_concerns_pending',
                additional_source_note=blur['notes'] if name=='66413' else ''));continue
        training_candidate(image_id,manifest,policy)
        assert disposition[image_id]['status']=='screen_clear_unreviewed'
        assert s['reference_measurement']['status']=='success' and quality[image_id]['status']=='requires_reference_review'
        assert image_id not in {r['source_image_id'] for r in old_rows}
        ref_relative=f'images/{name}_reference.png';mask_relative=f'images/{name}_reference_mask.png'
        assert digest(prepared/ref_relative)==original_hashes[ref_relative] and digest(prepared/mask_relative)==original_hashes[mask_relative]
        image=cv2.imread(str(prepared/ref_relative));mask=cv2.imread(str(prepared/mask_relative),0)
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
        features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)}
        features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        assert features==s['identity_features']
        new_rows.append(dict(pair_id=name+'__new_identity',source_image_id=image_id,duplicate_group_id=s['duplicate_group_id'],
            variant='identity',cohort='new_clean',paper_target=[1.,1.,1.],partition='train',reference_review='exact_original_reference_and_mask_accepted_no_notes',
            input_path=str((prepared/ref_relative).relative_to(ROOT)),reference_path=str((prepared/ref_relative).relative_to(ROOT)),
            input_mask_path=str((prepared/mask_relative).relative_to(ROOT)),reference_mask_path=str((prepared/mask_relative).relative_to(ROOT)),
            input_sha256=digest(prepared/ref_relative),input_mask_sha256=digest(prepared/mask_relative),measurement_contract_sha256=identity,
            **features))
    assert len(new_rows)==11 and len(old_rows)==30
    all_rows=old_rows+new_rows;groups=sorted({r['duplicate_group_id'] for r in all_rows});assert len(groups)==26
    columns=old_plan['features'];folds=[]
    for fid,group in enumerate(groups,1):
        held_rows=[r for r in all_rows if r['duplicate_group_id']==group]
        fitting_old=[r for r in old_rows if r['duplicate_group_id']!=group]
        fitting_new=[r for r in new_rows if r['duplicate_group_id']!=group]
        assert not {r['source_image_id'] for r in held_rows}&{r['source_image_id'] for r in fitting_old+fitting_new}
        controls=sorted([r for r in fitting_old if r['variant']=='identity'],key=lambda r:(hashlib.sha256(('clean_count_match_v1/'+r['pair_id']).encode()).hexdigest(),r['pair_id']))
        duplicated=[controls[i%len(controls)]['pair_id'] for i in range(len(fitting_new))]
        folds.append(dict(fold_id=fid,held_group=group,held_pair_ids=[r['pair_id'] for r in held_rows],
            historical_train_ids=[r['pair_id'] for r in fitting_old],new_control_train_ids=[r['pair_id'] for r in fitting_new],duplicate_control_ids=duplicated))
    paths=[Path(__file__),ROOT/'docs/accepted-clean-control-protocol.md',parent/'plan.json',parent/'verification.json',
        approved/'combined_original_mask_reviews60.json',ROOT/'outputs/color_cast_ycrcb_review_import_v1/reconciled_reviews.json',
        ROOT/'outputs/training_reference_color_audit_v1/source_dispositions.json',ROOT/'outputs/correction_duplicate_audit_v1/candidate_dispositions.json',
        ROOT/'src/model_training/training_identity_leaf_policy.py',artifact]
    for row in all_rows:paths.extend(ROOT/row[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_training',rows=all_rows,folds=folds,features=columns,target_names=old_plan['target_names'],
        settings=old_plan['settings'],methods=METHODS,new_clean_sources=11,held_accepted_references=held,
        new_distorted_pairs_admitted=0,input_sha256=hashes,measurement_contract_sha256=identity,
        active_demo_changed=False,evidence_role='exposed development with source-held comparisons, not final evaluation'))
    by_id={r['pair_id']:r for r in all_rows};records=[]
    for fold in folds:
        folder=out/f'fold_{fold["fold_id"]}';folder.mkdir()
        for method in METHODS:
            train_ids=fold['historical_train_ids']+(fold['new_control_train_ids'] if method=='new_clean_sources' else fold['duplicate_control_ids'] if method=='count_matched_controls' else [])
            training=[by_id[i] for i in train_ids]
            x=[[r[k] for k in columns] for r in training];y=[r['paper_target'] for r in training]
            model=DecisionTreeRegressor(**old_plan['settings']).fit(x,y)
            raw=export_tree(model,columns,old_plan['target_names'],dict(method=method,gamma_convention='direct_exponent',held_group=fold['held_group']))
            payload,audit=protect_identity_leaves(raw,x,[r['variant']=='identity' for r in training]);tree=PortableTree(payload)
            (folder/f'{method}.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
            (folder/f'{method}_membership.json').write_text(json.dumps(dict(train_pair_ids=train_ids,**audit),indent=2),encoding='utf-8')
            for pair in fold['held_pair_ids']:
                row=by_id[pair]
                assert row['duplicate_group_id'] not in {r['duplicate_group_id'] for r in training}
                params=tree.predict_one([row[k] for k in columns])
                image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
                reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
                mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
                output=image.copy();output[mask]=np.rint(transform_rgb(image.astype(float)/255,*params)[mask]*255).astype(np.uint8)
                assert np.array_equal(output[~mask],image[~mask])
                path=folder/(pair+'_'+method+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                records.append(dict(pair_id=pair,source_image_id=row['source_image_id'],cohort=row['cohort'],variant=row['variant'],fold_id=fold['fold_id'],
                    method=method,parameters=params,changed_input_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),
                    metrics=image_errors(reference,output,score),no_correction=image_errors(reference,image,score),output_sha256=digest(path)))
        print('Fold',fold['fold_id'],'complete',flush=True)
    scopes={'historical_all':lambda r:r['cohort']=='historical','historical_clean':lambda r:r['cohort']=='historical' and r['variant']=='identity',
        'historical_distorted':lambda r:r['cohort']=='historical' and r['variant']!='identity','new_clean':lambda r:r['cohort']=='new_clean','combined':lambda r:True}
    aggregates=[];gates={}
    for method in METHODS:
        for scope,include in scopes.items():
            values=[r for r in records if r['method']==method and include(r)]
            aggregates.append(dict(method=method,scope=scope,pairs=len(values),mean_ciede2000=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in values])),
                no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in values])),changed_pairs=sum(r['changed_input_pixels']>0 for r in values)))
        relevant=[r for r in records if r['method']==method]
        harm=[r['pair_id'] for r in relevant if r['variant']=='identity' and r['changed_input_pixels']]
        full=next(r for r in aggregates if r['method']==method and r['scope']=='combined')
        gates[method]=dict(overall_improves=full['mean_ciede2000']<full['no_correction'],clean_unchanged=not harm,harmed_clean_ids=harm)
        gates[method]['passed']=gates[method]['overall_improves'] and gates[method]['clean_unchanged']
    assert len(records)==123 and all(digest(ROOT/p)==sha for p,sha in hashes.items()) and contract(ROOT)[1]==identity
    write('predictions.json',records);write('summary.json',dict(status='complete_no_automatic_promotion',historical_sources=15,new_clean_only_sources=11,
        held_pairs=41,groups=26,regression_fits=78,aggregates=aggregates,gates=gates,active_demo_changed=False,
        new_distorted_pairs_admitted=0,final_validation_test_access=False))
    print(json.dumps(dict(aggregates=aggregates,gates=gates),indent=2))


if __name__=='__main__':main()
