"""One fixed 11-tree comparison: crop-local context, unchanged nested MST/costs."""
from pathlib import Path
import json,hashlib,sys,copy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.whole_scene_features import scene_features
from src.model_training.image_loss_action_tree import fit_action_tree
from src.model_training.portable_tree import PortableTree
P=ROOT/'outputs/aligned_correction_preparation_v1'
OUT=ROOT/'outputs/face_local_action_models_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    if OUT.exists():raise FileExistsError('Preserve fits; no automatic repeat')
    parent_path=ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json';parent=read(parent_path)
    prep=read(P/'results_PRIVATE.json');rows={r['case_id']:r for r in prep['records']}
    bound=dict(parent['input_sha256'])
    for p in (parent_path,P/'results_PRIVATE.json',Path(__file__),ROOT/'docs/face-local-action-design-2026-11-08.md',
              ROOT/'src/model_training/whole_scene_features.py',ROOT/'src/model_training/image_loss_action_tree.py'):
        bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    local={}
    for r in rows.values():
        if r['status']!='available':continue
        path=Path(r['scene_path']);bound[str(path)]=sha(path)
        im=cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB)
        x0,y0,x1,y1=r['input_bridge']['native_bounds']
        local[r['case_id']]=list(scene_features(im[y0:y1,x0:x1]).values())
    names=parent['feature_names'][:5]+[n.replace('scene_','face_crop_',1) for n in parent['feature_names'][5:]]
    OUT.mkdir();fits=[];constraints=0
    for old in parent['folds']+[parent['full']]:
        fit={k:copy.deepcopy(v) for k,v in old.items() if k not in ('model','training_features')}
        features=[x[:5]+local[cid] for cid,x in zip(old['training_cases'],old['training_features'],strict=True)]
        m=old['model'];new=fit_action_tree(features,m['costs'],m['clean'],m['actions'],names,max_depth=3)
        new.update(costs=copy.deepcopy(m['costs']),clean=copy.deepcopy(m['clean']))
        fit.update(training_features=features,model=new);fits.append(fit)
        constraints+=sum(m['clean']);print('Fit',fit['held_key'],len(features),'rows',flush=True)
    predictions=[];bykey={f['held_key']:f for f in fits};full=fits[-1]
    for p in parent['predictions']:
        q=copy.deepcopy(p)
        q['features']=p['features'][:5]+local[p['case_id']] if p['features'] is not None else None
        fit=bykey[p['subject_id']] if p['cohort']=='development' else full
        q['parameters']=PortableTree(fit['model']['tree']).predict_one(q['features']) if q['features'] is not None else None
        predictions.append(q)
    result=dict(folds=fits[:-1],full=full,calibrations=parent['calibrations'],predictions=predictions,feature_names=names,
        input_sha256=bound,new_action_tree_fits=11,new_matching_MST_fits=0,new_target_fits=0,
        fitting_clean_constraint_occurrences=constraints,production_adopted=False,training_admitted=False,calibration_admitted=False,
        measurement_contract_sha256=parent['measurement_contract_sha256'],context_scope='saved_actual_input_native_face_crop',
        parent_model_sha256=sha(parent_path))
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('Completed exactly11trees;',constraints,'repeated fitting clean constraints; no MST fits.')

if __name__=='__main__':main()
