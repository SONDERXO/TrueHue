"""Package exact nested fitting/reserved vectors, without fitting/evaluation."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/fitting_green_features_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    target=OUT/'prepared_vectors_PRIVATE.json';assert not target.exists()
    source=ROOT/'outputs/colour_nonharm_models_v1/models_PRIVATE.json'
    parent=read(source);features=read(OUT/'features_PRIVATE.json')
    verification=read(OUT/'verification_with_metadata_PRIVATE.json')
    assert verification['passed'] and verification['features_sha256']==sha(OUT/'features_PRIVATE.json')
    assert verification['verifier_sha256']==sha(ROOT/'scripts/683_verify_fitting_green_features.py')
    rows={r['case_id']:r for r in features['records']};names=features['feature_names']
    fits=[]
    for f in parent['folds']+[parent['full']]:
        training=[]
        for cid,x in zip(f['training_cases'],f['training_features'],strict=True):
            assert rows[cid]['role']=='fitting'
            if f['held_key']!='full':assert rows[cid]['subject_id']!=f['held_key']
            training.append(list(x)+[rows[cid]['features'][k] for k in names])
        reserved=[]
        for r in f['reserved_clean_vectors']:
            assert rows[r['case_id']]['role']=='reserved_clean' and r['case_id'] not in f['training_cases']
            reserved.append(dict(case_id=r['case_id'],features=r['features']+[rows[r['case_id']]['features'][k] for k in names]))
        for x,y in zip(training,f['training_features'],strict=True):assert x[:12]==y and len(x)==16
        fits.append(dict(held_key=f['held_key'],training_cases=f['training_cases'],training_features=training,reserved_clean_vectors=reserved))
    d=dict(feature_names=parent['feature_names']+names,configurations=fits,
        parent_model_sha256=sha(source),features_sha256=sha(OUT/'features_PRIVATE.json'),
        authoritative_verification_sha256=sha(OUT/'verification_with_metadata_PRIVATE.json'),
        script_sha256=sha(Path(__file__)),new_fits=0,evaluation_vectors_included=False,
        scope='Only fitting/reserved vectors; old nested MST and original12 columns copied exactly; pair deltas excluded.')
    target.write_text(json.dumps(d,indent=2,allow_nan=False))
    result=dict(technical_preparation_passed=True,training_side_rationale_retained=True,
        independent_source_held_accuracy_demonstrated=False,model_comparison_run=False,
        ready_for_specifically_approved_fixed_comparison=True,configurations=len(fits),
        repeated_training_vectors=sum(len(f['training_features']) for f in fits),
        repeated_reserved_clean_vectors=sum(len(f['reserved_clean_vectors']) for f in fits),
        prepared_vectors_sha256=sha(target),new_MST_fits=0,new_correction_fits=0,
        evaluation_feature_rows=0,holdout_image_reads=0)
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
