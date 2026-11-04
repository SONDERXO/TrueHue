"""Freeze exact five-source review; compare fixed5/9feature and clean-leaf recipes."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.data_preparation.table2_stress_contract import validate_stress_rows
from src.data_preparation.source_group_folds import source_group_folds
from src.data_preparation.controlled_training_table import TARGETS
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.model_training.chroma_distribution import ADDITIONS,chroma_distribution_features
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import PortableTree,export_tree
from src.evaluation.correction_prototype import apply_correction,image_errors

OUT=ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1'
STATEMENT="1398: accept concern: little bit of body captured in face mask, 68453: accept concern: minor holes in face mask, 12222: reject reason: reference support captured clothing in face mask, 59944: accept concern: some hair is captured in face mask, 66156: accept concern: little bit of background caught, 63087: accept concern: little bit of body captured, 60381: reject reason: captured a body part in face mask\n\nLet's improve this and make progress on the model."
DECISIONS={'1398':('accept','little bit of body captured in face mask'),'68453':('accept','minor holes in face mask'),
    '12222':('reject','reference support captured clothing in face mask'),'59944':('accept','some hair is captured in face mask'),
    '66156':('accept','little bit of background caught'),'63087':('accept','little bit of body captured'),
    '60381':('reject','captured a body part in face mask')}


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    old=ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1';prior=read(old/'fit_plan.json')
    assert digest(old/'fit_plan.json')==read(old/'verification.json')['fit_plan_sha256']
    folder=ROOT/'outputs/table2_source_expansion60_v1';data=read(folder/'summary.json');verify=read(folder/'verification.json');screen=read(folder/'screen_verification.json')
    assert digest(folder/'summary.json')==verify['summary_sha256']
    assert digest(folder/'shortlist_review.html')==screen['shortlist_review_sha256']
    assert digest(folder/'codex_source_screen.json')==screen['source_screen_sha256']
    for p,h in verify['evidence_sha256'].items():assert digest(folder/p)==h
    _,identity=contract(ROOT);assert identity==data['measurement_contract_sha256']
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json';assert digest(artifact)==data['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(read(artifact),identity)
    OUT.mkdir();review=OUT/'user_review.json'
    write(review,dict(user_statement_verbatim=STATEMENT,decisions={k:dict(decision=v[0],concern=v[1] if v[0]=='accept' else '',reason=v[1] if v[0]=='reject' else '') for k,v in DECISIONS.items()},
        review_html_sha256=digest(folder/'shortlist_review.html'),summary_sha256=digest(folder/'summary.json'),
        scope='Exact displayed reference/identity and assigned distortion. Explicit accepted contamination retained,not hair-free/face-only or MST truth approval.'))
    rows=[dict(r) for r in prior['rows']];excluded=list(prior['excluded']);sources={r['source_id']:r for r in data['records']}
    for name,(decision,concern) in DECISIONS.items():
        s=sources[name]
        if decision=='reject':
            excluded.extend(dict(pair_id=name+'__'+v,reason=concern) for v in ['identity','table2_'+s['assigned_severity']]);continue
        assert s['status']=='pending_review'
        for control in [True,False]:
            r=dict(next(r for r in prior['rows'] if (r['variant']=='identity')==control))
            for k in ['target_fit','target_fit_report_sha256','target_fit_report_path','distortion_gamma','distortion_red_gain','distortion_blue_gain']:r.pop(k,None)
            variant='identity' if control else 'table2_'+s['assigned_severity']
            image=folder/'images'/(name+('_reference.png' if control else '_input.png'));mask=folder/'images'/(name+('_reference_mask.png' if control else '_input_mask.png'))
            rm=folder/'images'/(name+'_reference_mask.png');reference=folder/'images'/(name+'_reference.png')
            measurement=s['reference_measurement'] if control else s['input_measurement'];features=measurement['features'];pixels=s['reference_measurement']['skin_pixels']
            count=0 if control else s['clipping']['clipped_pixels']
            r.update(pair_id=name+'__'+variant,source_image_id=s['image_id'],duplicate_group_id=s['duplicate_group_id'],variant=variant,
                input_processing_status=measurement['status'],measurement_contract_sha256=identity,input_mst_index=lookup.label(features['input_ita_degrees'])-1,
                reference_mst_estimate=s['reference_mst_estimate'],severity_probe=s['assigned_severity'],mask_review_report_sha256=digest(review),review_concern=concern,
                clipped_pixel_count=count,clipped_channel_samples=0 if control else s['clipping']['clipped_channel_samples'],generation_skin_pixels=pixels,clipped_pixel_fraction=count/pixels,
                input_path=str(image.relative_to(ROOT)),input_sha256=digest(image),input_mask_path=str(mask.relative_to(ROOT)),input_mask_sha256=digest(mask),
                reference_mask_path=str(rm.relative_to(ROOT)),reference_mask_sha256=digest(rm),reference_path=str(reference.relative_to(ROOT)))
            r.update(features)
            if control:
                parameters=[1.,1.,1.];r.update(transform_version='encoded_rgb_gamma_then_gain_v1',target_method='exact_gamma_gain_inverse',distortion_gamma=1.,distortion_red_gain=1.,distortion_blue_gain=1.)
            else:
                fit=s['target_fit'];fitpath=OUT/(name+'_target_fit.json');write(fitpath,fit);parameters=fit['parameters']
                r.update(transform_version='table2_encoded_rgb_composite_v1',target_method='bounded_rgb_recovery_target_v1',target_fit=fit,
                    target_fit_report_path=str(fitpath.relative_to(ROOT)),target_fit_report_sha256=digest(fitpath))
            r.update(zip(TARGETS,parameters));rows.append(r)
    rows=validate_stress_rows(rows,measurement_contract_sha256=identity,lookup_sha256=digest(artifact),eligible_pair_ids=[r['pair_id'] for r in rows])
    folds=source_group_folds(rows);assert len(rows)==30 and len(folds)==15
    rejected={'51739','40048','42532','63870','713','12222','60381'};assert not {r['pair_id'].split('__')[0] for r in rows}&rejected
    held=prior['retained_holds']+[dict(source_id=r['source_id'],status=r['status'],reason='Unchanged numerical/qualitative hold') for r in data['records'] if r['source_id'] not in DECISIONS]
    assert len(held)==74
    paths=[Path(__file__),review,old/'fit_plan.json',old/'summary.json',old/'verification.json',folder/'summary.json',folder/'verification.json',folder/'shortlist_review.html',folder/'screen_verification.json',artifact,
        ROOT/'src/model_training/chroma_distribution.py',ROOT/'src/model_training/development_build.py',ROOT/'src/data_preparation/table2_stress_contract.py']
    for r in rows:
        for p,k in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256'),('reference_mask_path','reference_mask_sha256')]:assert digest(ROOT/r[p])==r[k];paths.append(ROOT/r[p])
        paths.append(ROOT/r['reference_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    columns=tuple(MST_FEATURES)+ADDITIONS
    write(OUT/'fit_plan.json',dict(status='frozen_before_feature_extraction_and_fit',rows=rows,folds=folds,excluded=excluded,retained_holds=held,
        methods=['baseline5','chroma9','clean_leaf'],features=list(columns),baseline_features=list(MST_FEATURES),settings=SETTINGS,
        sample_weight=None,identity_tolerance=0.,planned_regression_fits=30,input_sha256=hashes,
        severity_counts={g:sum(r['variant']=='table2_'+g for r in rows) for g in ['light','medium','dark']},
        limitation='Exposed development; accepted hair/body/background concerns retained. No person separation or final validity claim.'))
    feature_records=[]
    for r in rows:
        extra=chroma_distribution_features(cv2.imread(str(ROOT/r['input_path'])),cv2.imread(str(ROOT/r['input_mask_path']),0)>0)
        feature_records.append(dict(pair_id=r['pair_id'],**extra))
        if not extra['valid']:write(OUT/'unavailable.json',feature_records);raise ValueError('No missing-feature cohort fallback')
        r.update(extra['features'])
    write(OUT/'features.json',feature_records)
    records=[]
    for fold in folds:
        training=[r for r in rows if r['pair_id'] in fold['train_pair_ids']];validation=[r for r in rows if r['pair_id'] in fold['inner_validation_pair_ids']]
        assert len(training)==28 and len(validation)==2
        assert {r['duplicate_group_id'] for r in training}.isdisjoint(r['duplicate_group_id'] for r in validation)
        folder_out=OUT/f"fold_{fold['fold_id']}";folder_out.mkdir();trees={}
        for method,names in [('baseline5',tuple(MST_FEATURES)),('chroma9',columns)]:
            model=DecisionTreeRegressor(**SETTINGS).fit([[r[k] for k in names] for r in training],[[r[k] for k in TARGETS] for r in training])
            joblib.dump(model,folder_out/(method+'.joblib'));payload=export_tree(model,names,TARGETS,dict(experimental=True,fold_id=fold['fold_id']))
            write(folder_out/(method+'.json'),payload);trees[method]=PortableTree(payload)
            if method=='chroma9':
                conservative=deepcopy(payload)
                for r in training:
                    if r['variant']=='identity':conservative['nodes'][trees[method].leaf_id([r[k] for k in columns])]['values']=[1.,1.,1.]
                conservative['provenance']['leaf_policy']='identity_if_any_fitting_control'
                write(folder_out/'clean_leaf.json',conservative);trees['clean_leaf']=PortableTree(conservative)
        for row in validation:
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path']);mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            record=dict(pair_id=row['pair_id'],variant=row['variant'],fold_id=fold['fold_id'],no_correction=image_errors(reference,image,score),methods={})
            for method,tree in trees.items():
                parameters=tree.predict_one([row[k] for k in tree.feature_names]);corrected=apply_correction(image,mask,parameters)
                path=OUT/(row['pair_id']+'_'+method+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
                record['methods'][method]=dict(parameters=parameters,metrics=image_errors(reference,corrected,score),output_sha256=digest(path))
            records.append(record)
    aggregate={};gates={}
    for method in ['baseline5','chroma9','clean_leaf']:
        aggregate[method]={scope:dict(no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in subset])),
            corrected=float(np.mean([r['methods'][method]['metrics']['ciede2000_source_mask'] for r in subset])))
            for scope,subset in [('all',records),('identity',[r for r in records if r['variant']=='identity']),('distorted',[r for r in records if r['variant']!='identity'])]}
        harms=[r['pair_id'] for r in records if r['variant']=='identity' and r['methods'][method]['metrics']['ciede2000_source_mask']>0]
        gate=dict(overall_improves=aggregate[method]['all']['corrected']<aggregate[method]['all']['no_correction'],identity_pass=not harms,harmed_identity_ids=harms)
        gate['passed']=gate['overall_improves'] and gate['identity_pass'];gates[method]=gate
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',dict(status='complete_exposed_development',records=records,aggregate=aggregate,gates=gates,input_sha256=hashes,
        sources=15,pairs=30,new_fits=30,runtime_replaced=False,final_validated=False))
    print(json.dumps(dict(aggregate=aggregate,gates=gates),indent=2))


if __name__=='__main__':main()
