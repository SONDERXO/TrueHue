"""One fixed control-recipe comparison on the current core's cached inputs."""
import csv
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.train_model import load_model,save_model
from src.model_training.control_recipe_comparison import plan_control_folds
from src.data_preparation.controlled_training_table import FEATURES,TARGETS
from src.evaluation.correction_prototype import model_arrays,apply_correction,image_errors
from src.utilities.config import get_config

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def main():
    out=ROOT/get_config().OUTPUTS_ROOT/'core_control_comparison_v1'
    if out.exists():raise FileExistsError(out)
    tables=ROOT/'data/manifests/controlled_training_v2';train=tables/'train.csv';rows=read(train);assert len(rows)==30
    passed=ROOT/'data/manifests/square_mask_quality_v1/screen_pass_train.csv';held_path=passed.with_name('held_train.csv')
    eligibility=read(passed);holds=read(held_path)
    eligible=[r['parent_pair_id'] for r in eligibility];held=[r['parent_pair_id'] for r in holds]
    assert len(eligible)==22 and len(held)==8
    by_id={r['pair_id']:r for r in rows}
    for previous in eligibility+holds:
        row=by_id[previous['parent_pair_id']]
        assert row['source_image_id']==previous['source_image_id'] and row['variant']==previous['variant'] and row['duplicate_group_id']==previous['duplicate_group_id']
    folds=plan_control_folds(rows,eligible,held);assert len(folds)==7
    parent=ROOT/'outputs/core_pipeline_check_v1';core=json.loads((parent/'summary.json').read_text());core_rows={r['pair_id']:r for r in core['records']}
    assert all(digest(ROOT/p)==h for p,h in core['input_sha256'].items())
    tracked=[Path(__file__),train,passed,held_path,parent/'summary.json',parent/'verification.json',
        ROOT/'src/model_training/control_recipe_comparison.py',ROOT/'docs/core-control-comparison-protocol.md',
        ROOT/get_config().CORRECTION_PROTOTYPE_MODEL_PATH,ROOT/'data/manifests/development_exposure_additions.jsonl',
        ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json',ROOT/'data/manifests/face_boundary_reference_v1/original_export.json']
    inputs={}
    for row in rows:
        pair=row['pair_id'];case=core_rows[pair];assert case['status']=='development_partial_mst_unavailable' and case['features_match_saved']
        row.update(case['features'])
        for path in [ROOT/row['input_path'],Path(row['source_path']),ROOT/row['generation_mask_path'],parent/'cases'/pair/'correction_mask.png']:tracked.append(path)
        image=cv2.imread(str(ROOT/row['input_path']))[:,:,::-1].copy();reference=cv2.imread(row['source_path'])[:,:,::-1].copy()
        support=cv2.imread(str(parent/'cases'/pair/'correction_mask.png'),0)>0;scoring=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        inputs[pair]=(image,reference,support,scoring)
    hashes={str(p.relative_to(ROOT)):digest(p) for p in tracked}
    out.mkdir();(out/'fold_models').mkdir();(out/'boards').mkdir();(out/'run_status.json').write_text('{"status":"running"}')
    # These plans are written before the first fit.
    (out/'fold_plan.json').write_text(json.dumps(dict(status='frozen_before_fit',folds=folds,eligible_ids=eligible,held_ids=held,
        eligibility_map=[dict(prior_pair_id=r['pair_id'],core_pair_id=r['parent_pair_id']) for r in eligibility+holds],
        scope='22primary IDs/six eligible groups;8held diagnostics;native224core cached masks;not final-data admission'),indent=2))
    frozen=load_model(str(ROOT/get_config().CORRECTION_PROTOTYPE_MODEL_PATH));predictions=[];audits=[];model_hashes={}
    for fold in folds:
        evaluation=[by_id[p] for p in fold['evaluation_pair_ids']];x_test,y_test=model_arrays(evaluation)
        parameters={'no_correction':np.ones((len(evaluation),3)),'frozen_runtime_seen_source':frozen.predict(x_test)}
        for method,ids in fold['fit_pair_ids'].items():
            fitting=[by_id[p] for p in ids];x,y=model_arrays(fitting)
            learner=DecisionTreeRegressor(max_depth=3,random_state=42,min_samples_leaf=1)
            learner.fit(x,y);parameters[method]=learner.predict(x_test)
            path=out/'fold_models'/f"fold{fold['fold_id']}_{method}.joblib";save_model(learner,str(path));model_hashes[path.name]=digest(path)
            audits.append(dict(fold_id=fold['fold_id'],method=method,fit_pair_ids=ids,
                fit_source_ids=sorted({r['source_image_id'] for r in fitting}),fit_duplicate_groups=sorted({r['duplicate_group_id'] for r in fitting}),
                evaluation_pair_ids=fold['evaluation_pair_ids'],feature_columns=list(FEATURES),target_columns=list(TARGETS),settings=learner.get_params(),sample_weight=None))
        for i,row in enumerate(evaluation):
            pair=row['pair_id'];image,reference,support,scoring=inputs[pair]
            for method,vectors in parameters.items():
                vector=np.asarray(vectors[i],float);corrected=apply_correction(image,support,vector)
                np.testing.assert_array_equal(corrected[~support],image[~support])
                error=image_errors(reference,corrected,scoring)
                predictions.append(dict(pair_id=pair,source_image_id=row['source_image_id'],variant=row['variant'],fold_id=fold['fold_id'],
                    reference_status='primary_eligible_ID' if pair in eligible else 'held_ID_diagnostic_only',method=method,
                    evaluation_kind='seen_source_diagnostic' if method=='frozen_runtime_seen_source' else 'source_held_out',
                    features=x_test[i].tolist(),predicted_parameters=vector.tolist(),target_parameters=y_test[i].tolist(),
                    parameter_absolute_error=np.abs(vector-y_test[i]).tolist(),**error))
        print('Completed fold '+str(fold['fold_id']),flush=True)
    assert len(predictions)==120
    methods=['no_correction','older_recipe','with_controls','frozen_runtime_seen_source'];aggregate=[]
    for scope,ids in [('primary',set(eligible)),('held_diagnostic',set(held))]:
        for variant in ['all']+sorted({by_id[p]['variant'] for p in ids}):
            for method in methods:
                cohort=[p for p in predictions if p['pair_id'] in ids and p['method']==method and (variant=='all' or p['variant']==variant)]
                if not cohort:continue
                source_means=[float(np.mean([p['ciede2000_source_mask'] for p in cohort if p['source_image_id']==s])) for s in sorted({p['source_image_id'] for p in cohort})]
                baseline={p['pair_id']:p for p in predictions if p['method']=='no_correction'}
                aggregate.append(dict(scope=scope,variant=variant,method=method,evaluation_kind=cohort[0]['evaluation_kind'],pairs=len(cohort),sources=len(source_means),
                    mean_ciede2000=float(np.mean([p['ciede2000_source_mask'] for p in cohort])),equal_source_mean_ciede2000=float(np.mean(source_means)),
                    worsened_pairs=sum(p['ciede2000_source_mask']>baseline[p['pair_id']]['ciede2000_source_mask']+1e-12 for p in cohort),
                    parameter_mae=np.mean([p['parameter_absolute_error'] for p in cohort],axis=0).tolist()))
    lookup={(p['pair_id'],p['method']):p for p in predictions}
    for source in sorted({r['source_image_id'] for r in rows}):
        strips=[]
        for row in [r for r in rows if r['source_image_id']==source]:
            pair=row['pair_id'];image,reference,support,scoring=inputs[pair];panels=[]
            for title,value in [('Reference',reference),('Input/no correction',image),('Older recipe CV',apply_correction(image,support,lookup[(pair,'older_recipe')]['predicted_parameters'])),('With controls CV',apply_correction(image,support,lookup[(pair,'with_controls')]['predicted_parameters']))]:
                shown=cv2.cvtColor(value,cv2.COLOR_RGB2BGR);shown=cv2.copyMakeBorder(shown,42,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(shown,row['variant']+' '+title,(2,13),cv2.FONT_HERSHEY_SIMPLEX,.29,(255,255,255),1)
                cv2.putText(shown,'PRIMARY' if pair in eligible else 'HELD diagnostic only',(2,30),cv2.FONT_HERSHEY_SIMPLEX,.30,(0,220,255),1);panels.append(shown)
            strips.append(np.hstack(panels))
        assert cv2.imwrite(str(out/'boards'/(Path(source).stem+'.png')),np.vstack(strips))
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    summary=dict(status='complete_fixed_development_comparison',folds=folds,fit_audits=audits,predictions=predictions,aggregate=aggregate,
        eligible_ids=eligible,held_ids=held,input_sha256=hashes,fold_model_sha256=model_hashes,new_fold_models=14,
        runtime_model_replaced=False,training_pairs_regenerated=0,final_model_fitted=False,
        original_routing_counts=dict(train=30,development_validation=3,clipped_stress=4,excluded=1),
        limitations='Previously exposed selected sources; prior256screen IDs conservatively transferred as fit gate, not224quality validation. No MST or subject-independence claim. Frozen runtime is seen-source only.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'run_status.json').write_text('{"status":"complete"}')
    page=['<!doctype html><meta charset="utf-8"><title>Core control comparison</title><style>body{font:16px system-ui;max-width:1200px;margin:24px auto;background:#182028;color:#eee}img{max-width:100%}a{color:#9cd9ff}</style><h1>Core control-recipe comparison</h1><p>Both learned columns hold the entire source/group out.22primary IDs;8held diagnostic IDs never fitted. Current native224core inputs/masks, fixed four features/depth3. The frozen runtime appears only in JSON as seen-source history. No runtime replacement or MST estimate.</p><p><a href="summary.json">All metrics/provenance</a> · <a href="fold_plan.json">Frozen fold/eligibility plan</a></p>']
    for source in sorted({r['source_image_id'] for r in rows}):page.append('<h2>'+html.escape(source)+'</h2><img loading="lazy" src="boards/'+Path(source).stem+'.png">')
    (out/'review.html').write_text('\n'.join(page),encoding='utf-8')
    print(json.dumps([a for a in aggregate if a['scope']=='primary' and a['variant'] in ['all','identity_control','mild_bright_exposure']]))
if __name__=='__main__':main()
