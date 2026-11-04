"""Fixed source-grouped ablation of unchanged/mild correction controls.

Uses the existing22 screen-pass development IDs only. No new source eligibility,
parameter search, external validation scoring or runtime-model replacement.
"""
import csv
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.utilities.config import get_config
from src.model_training.train_model import save_model
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS,TARGETS
from src.data_preparation.source_group_folds import source_group_folds
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.distortion_generation.generate_distortions import inverse_parameters
from src.evaluation.correction_prototype import model_arrays,apply_correction,image_errors

CONTROLS={'identity_control','mild_bright_exposure'}


def read(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    config=get_config();version='correction_controls_sourcecv_v1'
    output=ROOT/config.OUTPUTS_ROOT/version;tables=ROOT/'data/manifests'/version
    if output.exists() or tables.exists():raise FileExistsError('Comparison exists')
    screen=ROOT/'data/manifests/square_mask_quality_v1/screen_pass_train.csv'
    held=screen.with_name('held_train.csv')
    rows=read(screen)
    if len(rows)!=22 or len({r['source_image_id'] for r in rows})!=6:raise ValueError('Expected frozen22-ID selection')
    assert not {r['pair_id'] for r in rows}&{r['pair_id'] for r in read(held)}
    generation=ROOT/'outputs/hair_clean_generation_v1'
    ycb=ROOT/'outputs/ycrcb_estimation_ablation_v1'
    masks=ROOT/'outputs/additions_only_boundary_v1'
    clipping={r['pair_id']:r for r in json.loads((generation/'summary.json').read_text())['pairs']}
    tracked=[Path(__file__),screen,held,generation/'summary.json',masks/'summary.json',
             ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,
             ROOT/'src/data_preparation/source_group_folds.py',ROOT/'src/data_preparation/controlled_training_table.py',
             ROOT/'src/evaluation/correction_prototype.py',ROOT/'src/ita_estimation/compute_ita.py',
             ROOT/'src/distortion_generation/generate_distortions.py']
    inputs={};derived=[]
    for prior in rows:
        row=dict(prior);pair=row['pair_id'];stem=row['source_image_id'].replace('/','_')
        if row['partition']!='train' or row['table_use']!='train' or clipping[pair]['clipped_pixels']:
            raise ValueError('Ineligible/clipped fitting row')
        image_path=generation/(pair+'_input.png');score_path=generation/(stem+'_generation_mask.png')
        reference_path=ROOT/row['reference_path'];mask_path=masks/(pair+'_support.png')
        estimate_path=ycb/(pair+'_baseline_estimate.png')
        bgr=cv2.imread(str(image_path));estimate=cv2.imread(str(estimate_path),0)
        stats=compute_masked_lab_statistics(bgr,estimate,1000)
        if not stats['valid']:raise ValueError('Unavailable baseline features')
        row.update(zip(FEATURES,[stats[k] for k in FEATURE_KEYS]))
        params={k:float(row['distortion_'+k]) for k in ['gamma','red_gain','blue_gain']}
        targets=inverse_parameters(**params)
        np.testing.assert_allclose([float(row[k]) for k in TARGETS],[targets[k] for k in ['gamma','red_gain','blue_gain']],atol=1e-12,rtol=0)
        row.update(input_path=image_path.relative_to(ROOT).as_posix(),generation_mask_path=score_path.relative_to(ROOT).as_posix(),
                   generation_skin_pixels=int(np.count_nonzero(cv2.imread(str(score_path),0))),
                   policy_version='hair_clean_generation_v1',development_selection='frozen22screen_pass_IDs_not_final_cohort',
                   correction_mask_path=mask_path.relative_to(ROOT).as_posix(),parent_table=str(screen.relative_to(ROOT)))
        derived.append(row)
        rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB);reference=cv2.cvtColor(cv2.imread(str(reference_path)),cv2.COLOR_BGR2RGB)
        support=cv2.imread(str(mask_path),0)>0;scoring=cv2.imread(str(score_path),0)>0
        inputs[pair]=(rgb,reference,support,scoring)
        tracked += [image_path,score_path,reference_path,mask_path,estimate_path]
    rows=derived;hashes={str(p):digest(p) for p in tracked}
    folds=source_group_folds(rows);by_id={r['pair_id']:r for r in rows}
    output.mkdir(parents=True);tables.mkdir(parents=True);(output/'fold_models').mkdir()
    status=output/'run_status.json';status.write_text('{"state":"running"}',encoding='utf-8')
    policy=dict(version=version,status='Fixed exploratory training-only ablation; not thesis-final training',
        cohort='Existing22screen-pass IDs/6source groups, features recomputed on hair-clean256inputs; held8 stay out',
        methods=['no_correction','original_recipe_tree','controls_tree'],
        learner=dict(max_depth=3,random_state=42,min_samples_leaf=1,target_scaling='none'),
        ablation='Original recipe excludes identity/mild from each fitting fold; controls tree includes them. Same held-source probes for both.',
        folds='Leave one source/known duplicate group out; all variants remain together. Subject identity independence unverified.',
        evaluation='Fixed additions-only correction support/common generation region; report each variant and source. No external development/stress/reserved test used.',
        limitations='Six selected sources,10original-type probes and12controls; exploratory quality selection; no hyperparameter search or model promotion.')
    (output/'comparison_policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    with (tables/'development_train.csv').open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,list(rows[0]));writer.writeheader();writer.writerows(rows)
    (tables/'source_group_folds.json').write_text(json.dumps(dict(status='fixed_before_fitting',folds=folds),indent=2),encoding='utf-8')
    predictions=[];fit_audits=[];model_hashes={}
    try:
        for fold in folds:
            fit_rows=[by_id[p] for p in fold['train_pair_ids']]
            evaluation=[by_id[p] for p in fold['inner_validation_pair_ids']]
            if {r['source_image_id'] for r in fit_rows}&{r['source_image_id'] for r in evaluation}:raise ValueError('Fold source leakage')
            x_test,_=model_arrays(evaluation)
            parameter_sets={'no_correction':np.ones((len(evaluation),3))}
            for method,include_controls in [('original_recipe_tree',False),('controls_tree',True)]:
                fitting=[r for r in fit_rows if include_controls or r['variant'] not in CONTROLS]
                if not fitting:raise ValueError('Empty fitting fold')
                x,y=model_arrays(fitting)
                learner=DecisionTreeRegressor(max_depth=3,random_state=42)
                learner.fit(x,y);parameters=learner.predict(x_test)
                path=output/'fold_models'/f"fold{fold['fold_id']}_{method}.joblib"
                save_model(learner,str(path));model_hashes[path.name]=digest(path)
                parameter_sets[method]=parameters
                fit_audits.append(dict(fold_id=fold['fold_id'],method=method,fit_pair_ids=[r['pair_id'] for r in fitting],
                    fit_source_ids=sorted({r['source_image_id'] for r in fitting}),
                    fit_duplicate_groups=sorted({r['duplicate_group_id'] for r in fitting}),
                    evaluated_pair_ids=[r['pair_id'] for r in evaluation],held_out_group=fold['held_out_duplicate_group'],
                    feature_columns=list(FEATURES),target_columns=list(TARGETS)))
            for index,row in enumerate(evaluation):
                rgb,reference,support,scoring=inputs[row['pair_id']]
                for method,all_parameters in parameter_sets.items():
                    parameters=np.asarray(all_parameters[index],float)
                    corrected=apply_correction(rgb,support,parameters)
                    np.testing.assert_array_equal(corrected[~support],rgb[~support])
                    target=np.asarray([float(row[k]) for k in TARGETS])
                    error=image_errors(reference,corrected,scoring)
                    predictions.append(dict(pair_id=row['pair_id'],source_image_id=row['source_image_id'],variant=row['variant'],
                        fold_id=fold['fold_id'],method=method,features=[float(row[k]) for k in FEATURES],
                        predicted_parameters=parameters.tolist(),target_parameters=target.tolist(),
                        parameter_absolute_error=np.abs(parameters-target).tolist(),**error))
            print('Completed source fold '+str(fold['fold_id']),flush=True)
        assert len(predictions)==22*3
        assert hashes=={p:digest(p) for p in hashes},'Original inputs changed'
        aggregates={};by_variant={};by_source={}
        for method in policy['methods']:
            cohort=[r for r in predictions if r['method']==method]
            source_means=[np.mean([r['ciede2000_source_mask'] for r in cohort if r['source_image_id']==s]) for s in sorted({r['source_image_id'] for r in cohort})]
            aggregates[method]=dict(pairs=len(cohort),sources=6,
                mean_ciede2000=float(np.mean([r['ciede2000_source_mask'] for r in cohort])),
                equal_source_mean_ciede2000=float(np.mean(source_means)),
                parameter_mae=np.mean([r['parameter_absolute_error'] for r in cohort],axis=0).tolist())
        for variant in sorted({r['variant'] for r in rows}):
            by_variant[variant]={method:dict(pairs=len(cohort),mean_ciede2000=float(np.mean([r['ciede2000_source_mask'] for r in cohort])))
                for method in policy['methods'] if (cohort:=[r for r in predictions if r['method']==method and r['variant']==variant])}
        for source_id in sorted({r['source_image_id'] for r in rows}):
            by_source[source_id]={method:float(np.mean([r['ciede2000_source_mask'] for r in predictions if r['source_image_id']==source_id and r['method']==method])) for method in policy['methods']}
        summary=dict(status='complete',comparison_policy=policy,training_candidates=22,source_folds=6,
            variant_counts=dict(Counter(r['variant'] for r in rows)),aggregates=aggregates,by_variant=by_variant,by_source=by_source,
            fit_audits=fit_audits,predictions=predictions,input_sha256=hashes,fold_model_sha256=model_hashes,
            warning='No final all-source model trained, no production model replacement, no external validation tuning or generalization/fairness claim.')
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        status.write_text('{"state":"complete"}',encoding='utf-8')
        print(json.dumps(dict(aggregates=aggregates,variants=by_variant),indent=2))
    except Exception as error:
        status.write_text(json.dumps(dict(state='failed',error=str(error))),encoding='utf-8');raise


if __name__=='__main__':main()
