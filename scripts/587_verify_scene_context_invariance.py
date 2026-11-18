"""Independent counterfactual feature and exported-tree replay, no fitting."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.whole_scene_features import scene_features
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/scene_context_invariance_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'results_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json')
    assert all(sha(p)==h for p,h in bound.items())
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    m=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json');preds={r['case_id']:r for r in m['predictions']}
    fits={f['held_key']:f for f in m['folds']};replays=0
    for r in d['records']:
        source=prep[r['case_id']];p=preds[r['case_id']];fit=fits[p['subject_id']] if p['cohort']=='development' else m['full']
        tree=PortableTree(fit['model']['tree']);image=cv2.cvtColor(cv2.imread(source['scene_path']),cv2.COLOR_BGR2RGB)
        x0,y0,x1,y1=source['input_bridge']['native_bounds'];crop=image[y0:y1,x0:x1].copy()
        assert np.array_equal(crop,cv2.cvtColor(cv2.imread(str(Path(source['scene_path']).parent/'native_input.png')),cv2.COLOR_BGR2RGB))
        fixed=scene_features(crop)
        for v in r['variants']:
            a=np.full(image.shape,v['neutral_context'],np.uint8);a[y0:y1,x0:x1]=crop
            assert np.array_equal(a[y0:y1,x0:x1],crop) and scene_features(a[y0:y1,x0:x1])==fixed
            sf=scene_features(a);assert sf==v['scene_features']
            values=dict(zip(m['feature_names'],p['features']));values.update(sf);x=[values[n] for n in m['feature_names']]
            assert tree.predict_one(x)==v['parameters'] and tree.leaf_id(x)==v['leaf'];replays+=1
        assert r['any_context_changes_action']==any(v['parameters']!=p['parameters'] for v in r['variants'])
        assert not r['replacement_contexts_agree']
    assert len(d['records'])==451 and replays==1353
    receipt=dict(status='PASS',conditions=451,replays=1353,input_hashes=len(bound),
        local_crop_features_invariant=True,new_fits=0,new_image_model_forwards=0,
        result_sha256=sha(OUT/'results_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print('PASS 451 exact native crops,1353 scene vectors/action routes and local-crop feature invariance;',len(bound),'source hashes.')

if __name__=='__main__':main()
