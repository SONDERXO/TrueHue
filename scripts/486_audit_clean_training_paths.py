"""No-refit audit of clean targets, independent routes and terminal leaf capacity."""
from collections import Counter,defaultdict
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.blended_recovery_targets import render_rgb8
BASE=ROOT/'outputs/nested_correction_diagnostic_v1'
OUT=ROOT/'outputs/clean_training_path_audit_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def route(payload,vector):
    values=np.asarray(vector,dtype=np.float32);node=0;depth=0
    while payload['nodes'][node]['kind']=='split':
        r=payload['nodes'][node];node=r['left'] if values[r['feature']]<=r['threshold'] else r['right'];depth+=1
    return node,depth


def main():
    if OUT.exists():raise FileExistsError(OUT)
    old=read(BASE/'results_PRIVATE.json');rows={r['case_id']:r for r in read(BASE/'prepared_rows_PRIVATE.json')}
    packages=dict(original=BASE,balanced=ROOT/'outputs/balanced_correction_comparison_v1',chroma=ROOT/'outputs/chroma_feature_correction_v1')
    bindings={};results={}
    for name,package in packages.items():
        bindings.update({str(package/n):h for n,h in read(package/'sha256.json').items()})
        data=read(package/'results_PRIVATE.json');counts=Counter();records=[];foldsummaries=[]
        for fold,sourcefold in zip(data['folds'],old['folds']):
            held=sourcefold['held_key'];assert fold.get('held_key')==held
            payload=fold['tree'];tree=PortableTree(payload);traces=sourcefold['training_feature_trace'];groups=defaultdict(list)
            targets=np.array([rows[t['case_id']]['target'] for t in traces])
            weights=np.array(fold['normalization']['weights']) if name=='balanced' else np.ones(len(traces))
            vectors=[t['features']+(data['distribution_features'][t['case_id']] if name=='chroma' else []) for t in traces]
            for i,vec in enumerate(vectors):
                leaf,depth=route(payload,vec);assert leaf==tree.leaf_id(vec);groups[leaf].append(i);counts['independent_training_routes']+=1
            leafdepths={}
            for leaf,ix in groups.items():
                mean=np.average(targets[ix],axis=0,weights=weights[ix])
                np.testing.assert_allclose(mean,payload['nodes'][leaf]['values'],atol=1e-12,rtol=0)
                counts['independent_leaf_means']+=1;leafdepths[leaf]=route(payload,vectors[ix[0]])[1]
            for i,t in enumerate(traces):
                row=rows[t['case_id']]
                if row['case']['layer']!='clean':continue
                assert row['target']==[1.,1.,1.] and row['target_report']['status']=='exact_neutral_target'
                assert row['subject_id']!=held
                leaf,depth=route(payload,vectors[i]);parameters=tree.predict_one(vectors[i]);ix=groups[leaf]
                layers=Counter(rows[traces[j]['case_id']]['case']['layer'] for j in ix)
                folder=BASE/row['source_case'];reference=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB)
                clean=cv2.cvtColor(cv2.imread(str(folder/'clean/input.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
                assert np.array_equal(clean,reference)
                assert np.array_equal(render_rgb8(clean,mask.astype(float),[1.,1.,1.]),clean)
                output=render_rgb8(clean,mask.astype(float),parameters)
                changed=int(np.count_nonzero(output!=clean));counts['clean_training_routes']+=1
                counts['clean_neutral_target_and_renderer_checks']+=1;counts['clean_non_neutral_controls']+=any(abs(p-1)>1e-12 for p in parameters)
                counts['clean_changed_training_outputs']+=changed>0;counts['clean_at_depth_limit']+=depth==3
                records.append(dict(case_id=t['case_id'],outer_key=held,leaf=leaf,depth=depth,leaf_layer_counts=dict(layers),
                    target=row['target'],predicted_parameters=parameters,changed_channels=changed,
                    training_rgb_mae=float(np.abs(output[mask].astype(float)-clean[mask]).mean())))
            foldsummaries.append(dict(held_key=held,used_leaves=len(groups),max_leaf_depth=max(leafdepths.values()),leaf_depths=leafdepths))
        results[name]=dict(counts=dict(counts),folds=foldsummaries,clean_training_records=records,
            mean_clean_training_mae=float(np.mean([r['training_rgb_mae'] for r in records])))
    assert all(sha(Path(p))==h for p,h in bindings.items())
    OUT.mkdir(parents=True)
    for name,value in [('results_PRIVATE.json',results),('input_sha256_PRIVATE.json',bindings)]:
        (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()},indent=2),encoding='utf-8')
    print(json.dumps({k:dict(counts=v['counts'],mean_clean_training_mae=v['mean_clean_training_mae']) for k,v in results.items()},indent=2))


if __name__=='__main__':main()
