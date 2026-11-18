"""Exactly the authorized ten current-mask contextual calibration fits."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.ita_estimation.reviewed_contextual_validation import evaluate
OUT=ROOT/'outputs/reviewed_contextual_validation_v1'
DESIGN=ROOT/'outputs/calibration_design_review_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')


def main():
    if OUT.exists():raise FileExistsError('Preserve earlier/partial validation')
    receipt=read(DESIGN/'review_with_transfer_limits_PRIVATE.json');assert receipt['passed']
    bound={}
    for p,h in receipt['input_sha256'].items():assert sha(p)==h;bound[p]=h
    plan=read(DESIGN/'proposed_validation_plan_PRIVATE.json')
    assert plan['planned_fits']==10 and plan['planned_predictions']==30 and plan['alpha']==1.
    for p,h in plan['input_sha256'].items():assert sha(p)==h;bound[p]=h
    rowpath=ROOT/'outputs/reviewed_feature_control_contract_v1/calibration_rows_PRIVATE.json'
    for p in [rowpath,DESIGN/'proposed_validation_plan_PRIVATE.json',DESIGN/'application_coverage_PRIVATE.json',
        DESIGN/'validation_folds_PRIVATE.json',ROOT/'src/ita_estimation/reviewed_contextual_validation.py',
        ROOT/'src/ita_estimation/contextual_mst_experiment.py',Path(__file__)]:bound[str(p)]=sha(p)
    rows=read(rowpath);folds=read(DESIGN/'validation_folds_PRIVATE.json');assert len(rows)==30 and len(folds)==10
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(authorized_fits=10,authorized_predictions=30,
        all_data_fit=False,PPR_prediction=False,tree_fit=False,frozen_gates=plan['development_advancement'],input_sha256=bound))
    result=evaluate(rows,folds,plan['saved_comparator_predictions'],plan['development_advancement'])
    assert result['mapping_fits']==10 and len(result['predictions'])==30
    assert all(sha(p)==h for p,h in bound.items())
    write(OUT/'results_PRIVATE.json',result)
    print(json.dumps(dict(metrics=result['metrics'],by_condition=result['by_condition'],
                         checks=result['advancement_checks'],development_advancement_passed=result['development_advancement_passed']),indent=2))


if __name__=='__main__':main()
