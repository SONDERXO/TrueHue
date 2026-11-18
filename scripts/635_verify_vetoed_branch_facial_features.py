"""Independent scalar range, usefulness and saved reserved-route verification."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree,float32
def main():
    out=ROOT/'outputs/vetoed_branch_facial_audit_v1';d=json.loads((out/'audit_PRIVATE.json').read_text())
    m=json.loads((ROOT/'outputs/reserved_clean_veto_models_v1/models_PRIVATE.json').read_text());fits={f['held_key']:f for f in m['folds']+[m['full']]};checked=0
    for r in d['records']:
        f=fits[r['fit_key']];pre=f['pre_veto_model'];t=pre['trace'][r['leaf']]
        assert t['action']==r['action'] and f['vetoed_leaves'][str(r['leaf'])]==r['reserved_clean_hits']
        clean=[x for x,flag in zip(f['training_features'],pre['clean']) if flag]+[x['features'] for x in f['reserved_clean_vectors']]
        for name,(lo,hi) in r['pooled_clean_ranges'].items():
            j=m['feature_names'].index(name);assert lo==min(float32(x[j]) for x in clean) and hi==max(float32(x[j]) for x in clean)
        useful=[i for i in t['rows'] if pre['costs'][i][r['action']]<pre['costs'][i][0]]
        assert [f['training_cases'][i] for i in useful]==[x['case_id'] for x in r['targets']]
        for i,row in zip(useful,r['targets']):
            values={name:float32(f['training_features'][i][m['feature_names'].index(name)]) for name in r['pooled_clean_ranges']}
            outside=[name for name,value in values.items() if value<r['pooled_clean_ranges'][name][0] or value>r['pooled_clean_ranges'][name][1]]
            assert row['facial_values']==values and row['outside_pooled_clean_axes']==outside;checked+=1
        for cid in r['reserved_clean_hits']:
            x=next(x['features'] for x in f['reserved_clean_vectors'] if x['case_id']==cid)
            assert PortableTree(pre['tree']).leaf_id(x)==r['leaf']
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,fit_leaves=len(d['records']),useful_training_row_occurrences=checked,new_fits=0,new_evaluation_predictions=0,holdout_image_reads=0)
    (out/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
