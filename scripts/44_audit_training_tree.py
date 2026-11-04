"""Read-only coverage, leaf composition and path audit of the frozen prototype."""
import csv
import json
import hashlib
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from src.utilities.config import get_config
from src.model_training.train_model import load_model
from src.data_preparation.controlled_training_table import FEATURES,TARGETS
from src.evaluation.tree_training_audit import gamma_direction,trace_tree


def read(path):
    with path.open(newline='',encoding='utf-8') as stream:return list(csv.DictReader(stream))


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config=get_config();out=ROOT/config.OUTPUTS_ROOT/'training_tree_audit_v1'
    if out.exists():raise FileExistsError('Audit exists; refusing overwrite')
    table=ROOT/'data/manifests/controlled_training_v1';integrated=ROOT/config.OUTPUTS_ROOT/'integrated_correction_v1'
    diagnosis=ROOT/config.OUTPUTS_ROOT/'mask_parameter_diagnosis_v1'
    model_path=ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH;metadata_path=model_path.with_name('metadata.json')
    metadata=json.loads(metadata_path.read_text())
    if digest(model_path)!=metadata['model_sha256'] or tuple(metadata['feature_columns'])!=FEATURES or tuple(metadata['target_columns'])!=TARGETS:raise ValueError('Model/schema mismatch')
    model=load_model(str(model_path));rows=[]
    table_names=('train.csv','development_validation.csv','clipped_stress.csv','excluded_pairs.csv')
    for name in table_names:rows+=read(table/name)
    training=[r for r in rows if r['table_use']=='train'];successful=[r for r in rows if r['table_use']!='excluded']
    if len(rows)!=24 or len(training)!=16 or len(successful)!=23:raise ValueError('Unexpected controlled cohort')
    if {r['source_image_id'] for r in training}&{r['source_image_id'] for r in rows if r['table_use']=='development_validation'}:raise ValueError('Source overlap')
    sources_path=ROOT/'data/manifests/controlled_development_v1/selected_sources.csv'
    reference_l={r['image_id']:float(r['mean_l_star']) for r in read(sources_path)}
    paths=[Path(__file__),ROOT/'src/evaluation/tree_training_audit.py',model_path,metadata_path,sources_path,
           diagnosis/'image_metrics.csv',diagnosis/'summary.json']+[table/name for name in table_names]
    for row in successful:paths.append(integrated/'pairs'/row['pair_id']/'material_hair_veto_v1/metadata.json')
    hashes={str(p):digest(p) for p in paths}
    x_train=np.asarray([[float(r[k]) for k in FEATURES] for r in training]);y_train=np.asarray([[float(r[k]) for k in TARGETS] for r in training])
    train_leaves=model.apply(x_train);lower=x_train.min(axis=0);upper=x_train.max(axis=0)
    scale=np.maximum(x_train.std(axis=0),1e-12)
    known_current={r['pair_id']:float(r['ciede2000_source_mask']) for r in read(diagnosis/'image_metrics.csv') if r['method']=='known_current_mask'}
    leaf_records=[];leaf_members=[]
    for leaf in sorted(set(map(int,train_leaves))):
        indices=np.flatnonzero(train_leaves==leaf);selected=[training[i] for i in indices]
        mean=y_train[indices].mean(axis=0);stored=model.tree_.value[leaf].ravel()
        np.testing.assert_allclose(mean,stored,atol=1e-12,rtol=0)
        if int(model.tree_.n_node_samples[leaf])!=len(selected):raise ValueError('Leaf sample support differs')
        record=dict(leaf_id=leaf,training_pairs=len(selected),training_sources=len({r['source_image_id'] for r in selected}),
                    variants=dict(Counter(r['variant'] for r in selected)),prediction=dict(zip(TARGETS,map(float,stored))),
                    target_min=dict(zip(TARGETS,map(float,y_train[indices].min(0)))),target_max=dict(zip(TARGETS,map(float,y_train[indices].max(0)))),
                    training_pair_ids=[r['pair_id'] for r in selected])
        leaf_records.append(record)
        for row in selected:leaf_members.append(dict(leaf_id=leaf,pair_id=row['pair_id'],source_image_id=row['source_image_id'],variant=row['variant']))
    trace_rows=[];traces=[];direction_rows=[];outside_rows=[]
    for row in successful:
        values=np.asarray([float(row[k]) for k in FEATURES]);targets=np.asarray([float(row[k]) for k in TARGETS])
        prediction=model.predict(values[None,:])[0];trace=trace_tree(model,values,FEATURES)
        saved=json.loads((integrated/'pairs'/row['pair_id']/'material_hair_veto_v1/metadata.json').read_text())
        np.testing.assert_allclose(prediction,[saved['parameters'][k] for k in ('gamma','red_gain','blue_gain')],atol=1e-12,rtol=0)
        np.testing.assert_allclose(values,[saved['features'][k] for k in FEATURES],atol=.00005,rtol=0)
        expected=gamma_direction(targets[0]);actual=gamma_direction(prediction[0])
        outside=[name for name,v,lo,hi in zip(FEATURES,values,lower,upper) if v<lo or v>hi]
        candidates=np.linalg.norm((x_train-values)/scale,axis=1)
        for i,train_row in enumerate(training):
            if train_row['pair_id']==row['pair_id']:candidates[i]=np.inf
        closest=int(np.argmin(candidates))
        leaf=next(r for r in leaf_records if r['leaf_id']==trace['leaf_id'])
        item=dict(pair_id=row['pair_id'],source_image_id=row['source_image_id'],table_use=row['table_use'],variant=row['variant'],
            leaf_id=trace['leaf_id'],leaf_training_pairs=leaf['training_pairs'],leaf_variants=json.dumps(leaf['variants'],sort_keys=True),
            expected_gamma_direction=expected,predicted_gamma_direction=actual,gamma_direction_mismatch=expected!=actual,
            opposite_gamma_direction=expected in ('brighten','darken') and actual in ('brighten','darken') and expected!=actual,
            target_gamma=float(targets[0]),predicted_gamma=float(prediction[0]),gamma_absolute_error=float(abs(prediction[0]-targets[0])),
            red_gain_absolute_error=float(abs(prediction[1]-targets[1])),blue_gain_absolute_error=float(abs(prediction[2]-targets[2])),
            known_current_mask_color_residual=known_current[row['pair_id']],outside_training_feature_ranges=';'.join(outside),
            nearest_other_training_pair=training[closest]['pair_id'],nearest_training_scaled_distance=float(candidates[closest]),
            **dict(zip(FEATURES,map(float,values))))
        trace_rows.append(item);traces.append(dict(**item,path=trace['rules']))
        for feature in outside:outside_rows.append(dict(pair_id=row['pair_id'],table_use=row['table_use'],feature=feature,value=float(values[FEATURES.index(feature)]),training_min=float(lower[FEATURES.index(feature)]),training_max=float(upper[FEATURES.index(feature)])))
    counts=[];coverage=[]
    for variant in ('dark','bright_warm','color_shift'):
        for split in ('train','development_validation','stress_only','excluded'):
            selected=[r for r in rows if r['variant']==variant and r['table_use']==split]
            counts.append(dict(variant=variant,table_use=split,pairs=len(selected),source_images=len({r['source_image_id'] for r in selected})))
    for row in rows:
        coverage.append(dict(pair_id=row['pair_id'],source_image_id=row['source_image_id'],variant=row['variant'],table_use=row['table_use'],
            original_partition=row['partition'],clipped_pixel_count=int(row['clipped_pixel_count']),
            source_reference_l_star_audit_only=reference_l[row['source_image_id']],
            input_l_star=float(row['input_mean_l_star']) if row['input_mean_l_star'] else None))
    for split in ('train','development_validation','stress_only'):
        selected=[r for r in trace_rows if r['table_use']==split]
        direction_rows.append(dict(table_use=split,pairs=len(selected),gamma_direction_mismatches=sum(r['gamma_direction_mismatch'] for r in selected),
            opposite_gamma_directions=sum(r['opposite_gamma_direction'] for r in selected),outside_marginal_training_ranges=sum(bool(r['outside_training_feature_ranges']) for r in selected)))
    out.mkdir()
    for name,records in [('pair_traces.csv',trace_rows),('leaf_training_members.csv',leaf_members),('variant_coverage.csv',counts),('source_routing.csv',coverage),('direction_summary.csv',direction_rows),('outside_feature_ranges.csv',outside_rows)]:
        with (out/name).open('x',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,list(records[0]));writer.writeheader();writer.writerows(records)
    (out/'exact_paths.json').write_text(json.dumps(traces,indent=2),encoding='utf-8')
    (out/'leaf_summary.json').write_text(json.dumps(leaf_records,indent=2),encoding='utf-8')
    if not all(digest(Path(p))==value for p,value in hashes.items()):raise RuntimeError('Audit inputs changed')
    bright_training=[r for r in coverage if r['variant']=='bright_warm' and r['table_use']=='train']
    bright_stress=[r for r in coverage if r['variant']=='bright_warm' and r['table_use']=='stress_only']
    target_variance=y_train.var(axis=0)
    np.testing.assert_allclose(float(model.tree_.impurity[0]),target_variance.mean(),atol=1e-12,rtol=0)
    summary=dict(training_pairs=16,training_sources=7,development_validation_pairs=3,development_validation_sources=1,stress_pairs=4,excluded_pairs=1,
        fitted_depth=int(model.get_depth()),leaves=int(model.get_n_leaves()),
        feature_importance=dict(zip(FEATURES,map(float,model.feature_importances_))),
        target_training_variance=dict(zip(TARGETS,map(float,target_variance))),
        feature_training_ranges={k:dict(min=float(lo),max=float(hi)) for k,lo,hi in zip(FEATURES,lower,upper)},
        gamma_direction_summary=direction_rows,variant_coverage=counts,
        full_identity_target_rows=int(np.all(np.isclose(y_train,[1,1,1],atol=1e-12,rtol=0),axis=1).sum()),
        bright_training_reference_l_star_range=[min(r['source_reference_l_star_audit_only'] for r in bright_training),max(r['source_reference_l_star_audit_only'] for r in bright_training)],
        clipped_bright_reference_l_star_range=[min(r['source_reference_l_star_audit_only'] for r in bright_stress),max(r['source_reference_l_star_audit_only'] for r in bright_stress)],
        input_sha256=hashes,
        warning='Read-only audit; no model refit or tuning. Reference L* is audit metadata only, not an input feature or MST/demographic label. Known development examples are not fresh validation. Nearest-row distances and marginal ranges are descriptive, not proofs of joint support or alternate-model performance.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('input_sha256','variant_coverage')},indent=2))


if __name__=='__main__':main()
