"""Fixed crop-preserving scene counterfactuals, using exported saved trees only."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.whole_scene_features import scene_features,SCENE_FEATURES
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/scene_context_invariance_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve completed diagnostic')
    bound={}
    def read(p):p=Path(p);bound[str(p)]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    prep=read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']
    models=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    predictions={p['case_id']:p for p in models['predictions']};fits={f['held_key']:f for f in models['folds']}
    for rel in ('scripts/586_check_scene_context_invariance.py','docs/scene-context-invariance-protocol-2026-11-08.md',
                'src/model_training/whole_scene_features.py','src/model_training/portable_tree.py'):
        p=ROOT/rel;bound[str(p)]=sha(p)
    records=[];counts={}
    for r in prep:
        if r['status']!='available':continue
        p=predictions[r['case_id']];fit=fits[r['subject_id']] if r['cohort']=='development' else models['full']
        tree=PortableTree(fit['model']['tree']);assert tree.predict_one(p['features'])==p['parameters']
        path=Path(r['scene_path']);bound[str(path)]=sha(path)
        scene=cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB)
        x0,y0,x1,y1=r['input_bridge']['native_bounds'];face=scene[y0:y1,x0:x1].copy();variants=[]
        oldscene=scene_features(scene)
        for name in SCENE_FEATURES:assert oldscene[name]==p['features'][models['feature_names'].index(name)]
        for gray in (32,128,224):
            other=np.full_like(scene,gray);other[y0:y1,x0:x1]=face
            assert np.array_equal(other[y0:y1,x0:x1],face)
            values=dict(zip(models['feature_names'],p['features']));values.update(scene_features(other))
            vector=[values[n] for n in models['feature_names']]
            assert vector[:5]==p['features'][:5]
            action=tree.predict_one(vector)
            variants.append(dict(neutral_context=gray,parameters=action,leaf=tree.leaf_id(vector),
                differs_from_original=action!=p['parameters'],scene_features={n:values[n] for n in SCENE_FEATURES}))
        records.append(dict(case_id=r['case_id'],cohort=r['cohort'],recipe=r['recipe'],layer=r['layer'],
            original_parameters=p['parameters'],variants=variants,
            any_context_changes_action=any(v['differs_from_original'] for v in variants),
            replacement_contexts_agree=all(v['parameters']==variants[0]['parameters'] for v in variants)))
    for cohort in ('development','later'):
        for layer in ('clean','core','composite_stress_design'):
            rr=[r for r in records if r['cohort']==cohort and r['layer']==layer]
            counts[cohort+'_'+layer]=dict(available=len(rr),any_action_change=sum(r['any_context_changes_action'] for r in rr),
                replacement_contexts_disagree=sum(not r['replacement_contexts_agree'] for r in rr))
    assert len(records)==451
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();result=dict(summary=counts,attempts=756,available=451,unavailable=305,
        exported_tree_counterfactual_predictions=1353,new_fits=0,new_detector_parser_FaceOcc_forwards=0,
        records=records,limitation='Artificial outside-crop sensitivity diagnostic, frozen masks/features; no end-to-end or benefit claim.')
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print(json.dumps(counts,indent=2))
    for r in records:
        if r['case_id'] in ('case_02__clean','case_28__clean','eval_13__clean','eval_15__clean'):print(r['case_id'],r['original_parameters'],[(v['neutral_context'],v['parameters']) for v in r['variants']])

if __name__=='__main__':main()
