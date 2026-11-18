"""Independent saved routing/membership checks and fixed diagnostic boards."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/aligned_clean_error_trace_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'results_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json')
    assert all(sha(p)==h for p,h in bound.items())
    models=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    predictions={r['case_id']:r for r in models['predictions']}
    evals={r['case_id']:r for r in read(ROOT/'outputs/aligned_action_tree_comparison_v1/results_PRIVATE.json')['records']}
    fits={f['held_key']:f for f in models['folds']};fits['full']=models['full']
    routes=0;boards=[];imagehashes={}
    for r in d['records']:
        fit=fits[r['fit_key']];model=fit['model'];tree=PortableTree(model['tree']);p=predictions[r['case_id']]
        assert tree.leaf_id(p['features'])==r['leaf'] and tree.predict_one(p['features'])==r['parameters']
        members=[i for i,x in enumerate(fit['training_features']) if tree.leaf_id(x)==r['leaf']]
        assert len(members)==r['leaf_training_rows']
        assert not any(model['clean'][i] for i in members)
        assert abs(sum(model['costs'][i][r['action_index']] for i in members)-r['training_leaf_action_cost'])<1e-9
        x=np.asarray(p['features'],np.float32);mat=np.asarray(fit['training_features'],np.float32)[members]
        outside=[name for j,name in enumerate(models['feature_names']) if x[j]<mat[:,j].min() or x[j]>mat[:,j].max()]
        assert outside==r['outside_training_leaf_axes']
        # Validate every sibling and outcome-selected comparator against exported tree.
        for q in r['same_source_conditions']+r['selected_successful_same_leaf']:
            pred=predictions[q['case_id']]
            if pred['features'] is not None:assert tree.predict_one(pred['features'])==pred['parameters'];routes+=1
        chosen=[r['case_id']]+[q['case_id'] for q in r['selected_successful_same_leaf']]
        for cid in chosen:
            e=evals[cid];panels=[]
            for path in (e['reference_path'],e['image_path'],e['output_paths']['aligned_tree']):
                imagehashes[path]=sha(path);im=cv2.imread(path);assert im is not None;panels.append(im)
            label=np.full((30,672,3),255,np.uint8)
            cv2.putText(label,r['case_id']+' / '+cid+' ref | input | output',(3,21),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
            boards.append(np.vstack([label,np.hstack(panels)]))
    assert cv2.imwrite(str(OUT/'fixed_and_selected_boards_PRIVATE.png'),np.vstack(boards))
    receipt=dict(status='PASS',focal_queries=4,sibling_and_comparator_routes=routes,input_hashes=len(bound),
        image_sha256=imagehashes,trace_sha256=sha(OUT/'results_PRIVATE.json'),verifier_sha256=sha(Path(__file__)),
        board_sha256=sha(OUT/'fixed_and_selected_boards_PRIVATE.png'),new_fits=0,new_inference=0,
        selection='All four clean errors, then up to two outcome-selected positive-benefit same-leaf comparators each. Repeated comparator photos are not independent.')
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print('PASS four focal routes/leaf memberships/costs/ranges;',routes,'sibling and comparator routes; saved image hashes; no inference/fits.')

if __name__=='__main__':main()
