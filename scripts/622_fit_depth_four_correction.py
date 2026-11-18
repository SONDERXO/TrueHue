"""Exactly eleven depth-four fits from verified immutable expanded matrices."""
from pathlib import Path
import json,hashlib,copy,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.image_loss_action_tree import fit_action_tree
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/depth_four_correction_models_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve existing fits')
    p=ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json'
    m=json.loads(p.read_text());v=json.loads((p.parent/'verification_PRIVATE.json').read_text())
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    assert v['passed'] and v['model_sha256']==sha(p)
    assert all(sha(p)==h for p,h in m['input_sha256'].items())
    bound=dict(m['input_sha256'])
    for path in (p,p.parent/'verification_PRIVATE.json',Path(__file__),ROOT/'docs/depth-four-correction-protocol-2026-11-08.md'):
        bound[str(path)]=sha(path)
    OUT.mkdir();result=copy.deepcopy(m)
    for f in result['folds']+[result['full']]:
        parent=f['model'];model=fit_action_tree(f['training_features'],parent['costs'],parent['clean'],parent['actions'],m['feature_names'],max_depth=4)
        model.update(costs=parent['costs'],clean=parent['clean']);f['model']=model
        (OUT/(f['held_key']+'_PRIVATE.json')).write_text(json.dumps(f,indent=2))
        print('Fitted depth four:',f['held_key'],flush=True)
    fits={f['held_key']:f for f in result['folds']}
    for q in result['predictions']:
        f=fits[q['subject_id']] if q['cohort']=='development' else result['full']
        q['parameters']=PortableTree(f['model']['tree']).predict_one(q['features']) if q['features'] is not None else None
    result.update(input_sha256=bound,maximum_depth=4,new_action_tree_fits=11,new_matching_MST_fits=0,new_target_fits=0,expanded_depth_three_sha256=sha(p))
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':main()
