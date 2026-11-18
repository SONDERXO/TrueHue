"""Independent portable routing and saved leaf-membership checks."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree
def main():
    out=ROOT/'outputs/correction_branch_clean_evidence_v1';d=json.loads((out/'audit_PRIVATE.json').read_text())
    m=json.loads((ROOT/'outputs/depth_four_correction_models_v1/models_PRIVATE.json').read_text());fits={f['held_key']:f for f in m['folds']+[m['full']]}
    for r in d['leaves']:
        f=fits[r['fit_key']];t=f['model']['trace'][r['node']]
        assert r['training_rows']==len(t['rows']) and r['clean_rows']==sum(f['model']['clean'][i] for i in t['rows'])
        for i in t['rows']:assert PortableTree(f['model']['tree']).leaf_id(f['training_features'][i])==r['node']
    pred={p['case_id']:p for p in m['predictions']}
    for r in d['usable_clean_routes']:
        p=pred[r['case_id']];tree=PortableTree(fits[r['fit_key']]['model']['tree'])
        assert tree.leaf_id(p['features'])==r['leaf'] and tree.predict_one(p['features'])==r['parameters']
        for a,b in zip(r['path'],r['path'][1:]):assert a['chosen_child_clean_rows']==b['parent_clean_rows']
    assert all(r['clean_rows']==0 for r in d['leaves'] if r['action']!=0)
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,leaves=len(d['leaves']),usable_clean_routes=len(d['usable_clean_routes']),new_fits=0,holdout_image_reads=0)
    (out/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
