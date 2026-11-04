"""Fixed-support JPEG stress of frozen source-held trees; no retraining."""
import argparse
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.ita_estimation.square_measurement import contract
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.model_training.portable_tree import PortableTree
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors
h=importlib.import_module('256_compare_clean_control_tree_depth')
PARENT=ROOT/'outputs/endpoint_feature_tree_v1';OUT=ROOT/'outputs/endpoint_jpeg_sensitivity_v1'
ENCODINGS={'lossless':None,'jpeg95':95,'jpeg85':85}


def summarize(records):
    aggregates=[];gates={}
    for encoding in ENCODINGS:
        for scope in ('all','clean','distorted'):
            part=[r for r in records if r['encoding']==encoding and (scope=='all' or (r['variant']=='identity')==(scope=='clean'))]
            aggregates.append(dict(encoding=encoding,scope=scope,pairs=len(part),
                mean_ciede2000=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in part])),
                no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in part])),
                corrected_pairs=sum(r['changed_input_pixels']>0 for r in part),
                parameter_changes_vs_lossless=sum(r['parameters_changed'] for r in part)))
        harms=[r['pair_id'] for r in records if r['encoding']==encoding and r['variant']=='identity' and r['changed_input_pixels']]
        full=next(a for a in aggregates if a['encoding']==encoding and a['scope']=='all')
        improves=full['mean_ciede2000']<full['no_correction']
        gates[encoding]=dict(overall_improves=improves,clean_unchanged=not harms,harmed_clean_ids=harms,passed=improves and not harms)
    return dict(aggregates=aggregates,gates=gates,models_fitted=0,predictions=141,
        active_demo_changed=False,scope='fixed masks; feature and curve sensitivity, not end-to-end JPEG validation')


def run():
    if OUT.exists():raise FileExistsError(OUT)
    parent=h.read(PARENT/'plan.json');verified=h.read(PARENT/'verification.json');assert verified['status']=='pass'
    paths=[Path(__file__),Path(h.__file__),ROOT/'docs/endpoint-jpeg-sensitivity-protocol.md',PARENT/'verification.json']
    paths.extend(PARENT/path for path in verified['evidence_sha256'])
    hashes=dict(parent['input_sha256']);hashes.update({p.relative_to(ROOT).as_posix():h.digest(p) for p in paths})
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    _,identity=contract(ROOT);assert identity==parent['measurement_contract_sha256']
    lookup=DevelopmentMonotoneLookup(h.read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),identity)
    rows={r['pair_id']:r for r in parent['rows']}
    original=[r for r in h.read(PARENT/'predictions.json') if r['method']=='paired_endpoint11']
    OUT.mkdir();(OUT/'inputs').mkdir();(OUT/'results').mkdir()
    h.write(OUT/'plan.json',dict(input_sha256=hashes,parent_rows=parent['rows'],features=parent['features'],encodings=ENCODINGS,
        status='frozen_before_stress',measurement_contract_sha256=identity,mask_policy='original frozen input/scoring masks; no rerun'))
    records=[]
    for original_record in original:
        pair=original_record['pair_id'];row=rows[pair];source=cv2.imread(str(ROOT/row['input_path']))
        mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        tree=PortableTree(h.read(PARENT/f'fold_{original_record["fold_id"]}'/'candidate.json'))
        for encoding,quality in ENCODINGS.items():
            suffix='.png' if quality is None else '.jpg';input_path=OUT/'inputs'/(pair+'_'+encoding+suffix)
            if quality is None:assert cv2.imwrite(str(input_path),source)
            else:assert cv2.imwrite(str(input_path),source,[cv2.IMWRITE_JPEG_QUALITY,quality])
            image=cv2.imread(str(input_path));stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
            features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)}
            features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
            extra=facial_endpoint_features(image,mask);assert extra['valid'];features.update(extra['features'])
            vector=[features[k] for k in parent['features']];params=tree.predict_one(vector)
            if quality is None:assert params==original_record['parameters'] and vector==[{**row,**h.read(PARENT/'features.json')[pair]}[k] for k in parent['features']]
            rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);output=rgb.copy()
            output[mask]=np.rint(transform_rgb(rgb.astype(float)/255,*params)[mask]*255).astype(np.uint8)
            assert np.array_equal(output[~mask],rgb[~mask])
            result_path=OUT/'results'/(pair+'_'+encoding+'.png');assert cv2.imwrite(str(result_path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
            record=dict(pair_id=pair,encoding=encoding,fold_id=original_record['fold_id'],variant=row['variant'],cohort=row['cohort'],features=features,
                parameters=params,parameters_changed=params!=original_record['parameters'],leaf_id=tree.leaf_id(vector),
                changed_input_pixels=int(np.count_nonzero(np.any(output!=rgb,axis=2))),metrics=image_errors(reference,output,score),
                no_correction=image_errors(reference,rgb,score),encoded_input_path=input_path.relative_to(OUT).as_posix(),
                encoded_input_sha256=h.digest(input_path),output_sha256=h.digest(result_path))
            if quality is None:assert record['metrics']==original_record['metrics']
            records.append(record)
        print(pair,'complete',flush=True)
    h.write(OUT/'predictions.json',records);h.write(OUT/'summary.json',summarize(records))


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=h.read(OUT/'plan.json');parent=h.read(PARENT/'plan.json');rows={r['pair_id']:r for r in plan['parent_rows']}
    for path,sha in plan['input_sha256'].items():assert h.digest(ROOT/path)==sha
    lookup=DevelopmentMonotoneLookup(h.read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),plan['measurement_contract_sha256'])
    originals={r['pair_id']:r for r in h.read(PARENT/'predictions.json') if r['method']=='paired_endpoint11'}
    records=h.read(OUT/'predictions.json');assert len(records)==141 and len({(r['pair_id'],r['encoding']) for r in records})==141
    for r in records:
        row=rows[r['pair_id']];path=OUT/r['encoded_input_path'];assert h.digest(path)==r['encoded_input_sha256']
        image=cv2.imdecode(np.frombuffer(path.read_bytes(),np.uint8),cv2.IMREAD_COLOR)
        mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        stats=compute_masked_lab_statistics(image,mask,1000)
        features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)};features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        for channel,name in zip((2,1,0),('red','green','blue')):
            counts=np.bincount(image[:,:,channel][mask],minlength=256)
            features['input_'+name+'_zero_fraction']=float(counts[0]/mask.sum());features['input_'+name+'_full_fraction']=float(counts[255]/mask.sum())
        assert features==r['features']
        fold=next(f for f in parent['folds'] if f['fold_id']==r['fold_id']);assert row['pair_id'] in fold['held_pair_ids']
        membership=h.read(PARENT/f'fold_{r["fold_id"]}'/'membership.json')
        assert row['source_image_id'] not in {rows[p]['source_image_id'] for p in membership['train_pair_ids']}
        tree=PortableTree(h.read(PARENT/f'fold_{r["fold_id"]}'/'candidate.json'));vector=[features[k] for k in plan['features']]
        assert tree.predict_one(vector)==r['parameters'] and tree.leaf_id(vector)==r['leaf_id']
        assert r['parameters_changed']==(r['parameters']!=originals[r['pair_id']]['parameters'])
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        output=rgb.copy();output[mask]=np.rint(transform_rgb(rgb.astype(float)/255,*r['parameters'])[mask]*255).astype(np.uint8)
        result_path=OUT/'results'/(r['pair_id']+'_'+r['encoding']+'.png');assert h.digest(result_path)==r['output_sha256']
        np.testing.assert_array_equal(cv2.imread(str(result_path)),cv2.cvtColor(output,cv2.COLOR_RGB2BGR));np.testing.assert_array_equal(output[~mask],rgb[~mask])
        assert np.count_nonzero(np.any(output!=rgb,axis=2))==r['changed_input_pixels']
        assert image_errors(reference,output,score)==r['metrics'] and image_errors(reference,rgb,score)==r['no_correction']
        if r['encoding']=='lossless':assert r['parameters']==originals[r['pair_id']]['parameters'] and r['metrics']==originals[r['pair_id']]['metrics']
    assert summarize(records)==h.read(OUT/'summary.json')
    h.write(target,dict(status='pass',redecoded_feature_vectors=141,independent_endpoint_histograms=141,output_metric_replays=141,
        lossless_parent_predictions_matched=47,source_separation_verified=True,models_fitted=0,active_demo_changed=False,
        evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 141 decoded feature/output replays, 47 exact lossless matches, frozen source-held models.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else run()
