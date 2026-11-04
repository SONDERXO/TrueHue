"""Export the unchanged prototype and verify numeric parity, with no new fit."""
import csv
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from src.utilities.config import get_config
from src.model_training.train_model import load_model
from src.model_training.portable_tree import export_tree,PortableTree
from src.data_preparation.controlled_training_table import FEATURES,TARGETS
from src.evaluation.correction_prototype import apply_correction

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as stream:return list(csv.DictReader(stream))

def boundary_cases(model,baseline):
    """Witness each reachable split from its ancestor-constrained float32 domain."""
    maximum=np.finfo(np.float32).max;tree=model.tree_;cases=[]
    pending=[(0,np.full(len(baseline),-maximum,np.float32),np.full(len(baseline),maximum,np.float32))]
    while pending:
        node,low,high=pending.pop();left,right=map(int,[tree.children_left[node],tree.children_right[node]])
        if left==right:continue
        feature=int(tree.feature[node]);threshold=float(tree.threshold[node]);floor=np.float32(threshold)
        if float(floor)>threshold:floor=np.nextafter(floor,np.float32(-np.inf))
        ceiling=np.nextafter(floor,np.float32(np.inf))
        for name,value in [('below',np.nextafter(floor,np.float32(-np.inf))),('left_edge',floor),('right_edge',ceiling),('above',np.nextafter(ceiling,np.float32(np.inf)))]:
            if not np.isfinite(value) or not low[feature]<=value<=high[feature]:continue
            vector=np.clip(np.asarray(baseline,np.float32),low,high);vector[feature]=value
            path=model.decision_path(vector[None,:]).toarray()[0];expected_child=left if float(value)<=threshold else right
            assert path[node] and path[expected_child]
            cases.append(dict(node=node,position=name,expected_child=expected_child,features=vector.astype(float).tolist()))
        left_high=high.copy();left_high[feature]=min(left_high[feature],floor)
        right_low=low.copy();right_low[feature]=max(right_low[feature],ceiling)
        if (low<=left_high).all():pending.append((left,low.copy(),left_high))
        if (right_low<=high).all():pending.append((right,right_low,high.copy()))
    return cases

def main():
    args=argparse.ArgumentParser();args.add_argument('--output-dir',type=Path,default=ROOT/get_config().OUTPUTS_ROOT/'core_tree_portability_v1');args=args.parse_args()
    out=args.output_dir
    if out.exists():raise FileExistsError(out)
    path=ROOT/get_config().CORRECTION_PROTOTYPE_MODEL_PATH;meta_path=path.with_name('metadata.json');meta=json.loads(meta_path.read_text())
    assert tuple(meta['feature_columns'])==FEATURES and tuple(meta['target_columns'])==TARGETS and digest(path)==meta['model_sha256']
    tables=ROOT/'data/manifests/controlled_training_v1';rows=[];table_paths=[]
    for name,count in [('train',16),('development_validation',3),('clipped_stress',4)]:
        table=tables/(name+'.csv');part=read(table);assert len(part)==count
        rows.extend(dict(record=row,split=name) for row in part);table_paths.append(table)
    failures=read(tables/'excluded_pairs.csv');assert len(failures)==1
    tracked=[path,meta_path,*table_paths,tables/'excluded_pairs.csv',Path(__file__),ROOT/'src/model_training/portable_tree.py',
        ROOT/'docs/core-tree-portability.md',ROOT/'data/manifests/development_exposure_additions.jsonl',
        ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json',ROOT/'data/manifests/face_boundary_reference_v1/original_export.json']
    hashes={str(p.relative_to(ROOT)):digest(p) for p in tracked};model=load_model(str(path))
    payload=export_tree(model,FEATURES,TARGETS,dict(source_model_sha256=digest(path),source_metadata=meta,
        status='Frozen development prototype; software parity only; no MST lookup or final model adoption'))
    out.mkdir();model_path=out/'decision_tree.json';model_path.write_text(json.dumps(payload,indent=2,allow_nan=False))
    portable=PortableTree(json.loads(model_path.read_text()));vectors=np.asarray([[float(r['record'][f]) for f in FEATURES] for r in rows]);assert np.isfinite(vectors).all()
    records=[]
    for source,vector in zip(rows,vectors):
        predicted=model.predict(vector[None,:])[0];actual=portable.predict_one(vector)
        np.testing.assert_array_equal(actual,predicted)
        leaf=portable.leaf_id(vector);assert leaf==int(model.apply(vector[None,:])[0])
        records.append(dict(pair_id=source['record']['pair_id'],split=source['split'],features=vector.tolist(),parameters=actual,leaf_id=leaf))
    boundaries=boundary_cases(model,vectors[0]);covered_edges=set();leaves=set(r['leaf_id'] for r in records)
    for case in boundaries:
        vector=np.asarray(case['features']);np.testing.assert_array_equal(portable.predict_one(vector),model.predict(vector[None,:])[0])
        leaf=portable.leaf_id(vector);assert leaf==int(model.apply(vector[None,:])[0]);case['leaf_id']=leaf
        leaves.add(leaf);covered_edges.add((case['node'],case['expected_child']))
    splits=sum(n['kind']=='split' for n in payload['nodes']);assert len(covered_edges)==2*splits
    assert len(leaves)==sum(n['kind']=='leaf' for n in payload['nodes'])
    # Pure numeric RGB grid: confirms exported predictions preserve existing transform outputs.
    rgb=np.arange(16*16*3,dtype=np.uint16).reshape(16,16,3).astype(np.uint8);mask=np.ones((16,16),bool);mask[:2,:]=False
    for vector in vectors:
        expected=apply_correction(rgb,mask,model.predict(vector[None,:])[0]);actual=apply_correction(rgb,mask,portable.predict_one(vector))
        np.testing.assert_array_equal(actual,expected);np.testing.assert_array_equal(actual[~mask],rgb[~mask])
    # A double just above a split can still round to its float32 left boundary.
    for n in payload['nodes']:
        if n['kind']=='split':assert np.isfinite(n['threshold'])
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    result=dict(status='pass_software_parity_only_no_runtime_adoption',source_model_sha256=digest(path),export_sha256=digest(model_path),
        export_bytes=model_path.stat().st_size,node_count=len(payload['nodes']),split_nodes=splits,leaves_covered=len(leaves),
        saved_feature_rows_verified=len(records),excluded_rows_retained=failures,boundary_vectors_verified=len(boundaries),
        split_edges_covered=len(covered_edges),synthetic_rgb_corrections_verified=len(vectors),records=records,boundary_cases=boundaries,
        prediction_max_absolute_error=0.,input_sha256=hashes,new_model_fits=0,training_pairs_regenerated=0,
        mst_status='Unavailable/unvalidated; no guessed category inserted',
        limitations='Frozen weak development model. Numeric parity does not establish correction quality, Android implementation/latency or final study readiness.')
    (out/'verification.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps({k:result[k] for k in ['status','export_bytes','node_count','split_nodes','leaves_covered','saved_feature_rows_verified','boundary_vectors_verified','split_edges_covered','prediction_max_absolute_error']}))
if __name__=='__main__':main()
