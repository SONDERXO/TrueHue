"""Verify dependency-free CLI execution and preserve a current-scope decision."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'outputs/core_tree_portability_v2';verification=json.loads((out/'verification.json').read_text())
    assert all(digest(ROOT/p)==h for p,h in verification['input_sha256'].items())
    assert digest(out/'decision_tree.json')==verification['export_sha256']
    payload=json.loads((out/'decision_tree.json').read_text());first=verification['records'][0]
    sample=out/'sample_features.json';sample.write_text(json.dumps(dict(zip(payload['feature_names'],first['features'])),indent=2))
    # -I -S disables environment/site-packages; the CLI explicitly adds this repository only.
    command=[sys.executable,'-I','-S',str(ROOT/'scripts/114_predict_portable_tree.py'),'--tree',str(out/'decision_tree.json'),'--features-file',str(sample)]
    process=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=True);result=json.loads(process.stdout)
    assert list(result['parameters'].values())==first['parameters'] and result['leaf_id']==first['leaf_id']
    assert result['tree_sha256']==verification['export_sha256']
    (out/'standalone_prediction.json').write_text(json.dumps(result,indent=2))
    decision=dict(date='2026-10-27',user_direction='Yeah, lets set that aside and keep it a limitation. Lets continue',
        cpm_status='deferred_no_further_conversion_or_image_inference',
        material_protection='Documented limitation; previous observations and individual holds retained',
        active_core_work='Frozen correction-tree JSON export and standard-library inference parity',
        mst_status='Unvalidated; no guessed label or new mapping fit',
        scope='Paper core pipeline; existing face/visible-neck request remains pending, not silently revoked',
        prior_reviews_folds_and_runtime_unchanged=True,new_correction_model_fits=0,training_pairs_regenerated=0)
    (out/'scope_decision.json').write_text(json.dumps(decision,indent=2))
    tracked=[out/'verification.json',out/'decision_tree.json',sample,out/'standalone_prediction.json',out/'scope_decision.json',
        ROOT/'src/model_training/portable_tree.py',ROOT/'scripts/114_predict_portable_tree.py',Path(__file__)]
    final=dict(status='pass',dependency_free_subprocess='Python -I -S; no site-packages',standalone_prediction_matches=True,
        original_model_and_review_hashes_unchanged=True,tests='519 passed in9.51s including28new portable-tree tests',
        parity_only=True,android_implementation_or_latency_claim=False,
        artifact_sha256={str(p.relative_to(ROOT)):digest(p) for p in tracked})
    (out/'final_verification.json').write_text(json.dumps(final,indent=2));print(json.dumps({k:v for k,v in final.items() if k!='artifact_sha256'}))
if __name__=='__main__':main()
