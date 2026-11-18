"""Read-only clean-harm attribution from frozen nested features, targets and leaves."""
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
PARENT=ROOT/'outputs/nested_correction_diagnostic_v1'
OUT=ROOT/'outputs/clean_correction_diagnosis_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    hashes={str(PARENT/n):h for n,h in read(PARENT/'sha256.json').items()}
    assert all(sha(Path(p))==h for p,h in hashes.items())
    result=read(PARENT/'results_PRIVATE.json');rows={r['case_id']:r for r in read(PARENT/'prepared_rows_PRIVATE.json')}
    predictions={r['case_id']:r for r in result['records']}
    folds=[];records=[];boards=[]
    for fold in result['folds']:
        trace=fold['training_feature_trace'];tree=PortableTree(fold['tree'])
        x=np.array([r['features'] for r in trace]);y=np.array([rows[r['case_id']]['target'] for r in trace]);layers=[rows[r['case_id']]['case']['layer'] for r in trace]
        counts=Counter(layers);leaves=defaultdict(list)
        for i,r in enumerate(trace):leaves[tree.leaf_id(r['features'])].append(i)
        scale=np.array(fold['normalization']['applied_scale']);neutral_sse={}
        for layer in counts:
            ix=[i for i,l in enumerate(layers) if l==layer];neutral_sse[layer]=float(np.sum(((y[ix]-1)/scale)**2))
        featuremean=x.mean(axis=0);featurestd=x.std(axis=0);featurestd=np.where(featurestd==0,1,featurestd)
        duplicate_groups=defaultdict(list)
        for i,vector in enumerate(x.astype(np.float32)):duplicate_groups[tuple(vector)].append(i)
        conflicting=sum(len(ix)>1 and bool(np.any(np.ptp(y[ix],axis=0)>1e-10)) for ix in duplicate_groups.values())
        folds.append(dict(held_key=fold['held_key'],fitting_rows=len(trace),layer_counts=dict(counts),
            clean_row_fraction=counts['clean']/len(trace),neutral_normalized_target_sse=neutral_sse,
            exactly_duplicate_float32_vectors_with_conflicting_targets=conflicting))
        for key in fold['held_cases']:
            pred=predictions[key]
            if pred['layer']!='clean' or pred['status']!='predicted':continue
            leaf=tree.leaf_id(pred['features']);ix=leaves[leaf];mean=y[ix].mean(axis=0)
            np.testing.assert_allclose(mean,pred['parameters'],atol=1e-12,rtol=0)
            contributions={}
            for layer in counts:
                group=[i for i in ix if layers[i]==layer]
                contributions[layer]=(np.sum(y[group]-1,axis=0)/len(ix)).tolist() if group else [0.,0.,0.]
            np.testing.assert_allclose(1+np.sum(list(contributions.values()),axis=0),pred['parameters'],atol=1e-12,rtol=0)
            distance=np.linalg.norm((x-np.array(pred['features']))/featurestd,axis=1);order=np.argsort(distance,kind='stable')[:5]
            nearest=[dict(case_id=trace[int(i)]['case_id'],layer=layers[int(i)],standardized_distance=float(distance[i]),target=y[i].tolist()) for i in order]
            records.append(dict(case_id=key,held_key=fold['held_key'],leaf=leaf,leaf_rows=len(ix),leaf_layer_counts=dict(Counter(layers[i] for i in ix)),
                neutral_control_drift=(mean-1).tolist(),layer_contribution_to_drift=contributions,nearest_fitting_rows=nearest,
                output_mae=pred['predicted_metrics']['rgb8_mae_codes']))
            r=rows[key];folder=PARENT/r['source_case'];ref=cv2.imread(str(folder/'reference.png'));out=cv2.imread(str(folder/'clean/prediction.png'))
            panel=np.concatenate([cv2.resize(im,(200,200),interpolation=cv2.INTER_NEAREST) for im in [ref,out]],axis=1)
            title=np.full((30,400,3),255,np.uint8);cv2.putText(title,r['source_case']+' original / clean tree',(4,21),cv2.FONT_HERSHEY_SIMPLEX,.48,(0,0,0),1)
            boards.append(np.concatenate([title,panel]))
    summary=dict(clean_held_images=len(records),leaf_mean_replays=len(records),drift_decompositions=len(records),
        clean_only_leaves=sum(set(r['leaf_layer_counts'])=={'clean'} for r in records),
        nearest_fitting_row_is_nonclean=sum(r['nearest_fitting_rows'][0]['layer']!='clean' for r in records),
        folds_with_exact_vector_target_conflict=sum(f['exactly_duplicate_float32_vectors_with_conflicting_targets']>0 for f in folds),
        clean_training_fraction_min=min(f['clean_row_fraction'] for f in folds),clean_training_fraction_max=max(f['clean_row_fraction'] for f in folds),
        fits=0,thresholds_tuned=0,source_masks_changed=0)
    assert all(sha(Path(p))==h for p,h in hashes.items())
    OUT.mkdir(parents=True)
    for n,v in [('diagnosis_PRIVATE.json',dict(summary=summary,folds=folds,clean_records=records)),('input_sha256_PRIVATE.json',hashes)]:
        (OUT/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
    for i in range(0,len(boards),10):cv2.imwrite(str(OUT/f'clean_contact_{i//10+1:02d}_PRIVATE.png'),np.concatenate(boards[i:i+10]))
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
