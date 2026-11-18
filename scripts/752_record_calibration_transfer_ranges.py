"""Frozen-input marginal coverage audit; no fitted predictor or image access."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/calibration_design_review_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    dest=OUT/'application_coverage_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve coverage evidence')
    a=ROOT/'outputs/reviewed_feature_control_contract_v1/calibration_rows_PRIVATE.json'
    b=ROOT/'outputs/shared_core_mst_features_v1/complete_development_rows_PRIVATE.json'
    calibration=read(a);application=read(b)
    names=['input_ita_degrees','input_mean_l_star','input_mean_a_star','input_mean_b_star']
    summary={};cases={r['case_id']:[] for r in application}
    for name in names:
        values=[r['features'][name] for r in calibration];lower,upper=min(values),max(values)
        outside=[]
        for r in application:
            if r['features'][name]<lower or r['features'][name]>upper:
                outside.append(r['case_id']);cases[r['case_id']].append(name)
        summary[name]=dict(calibration_min=lower,calibration_max=upper,
            application_min=min(r['features'][name] for r in application),application_max=max(r['features'][name] for r in application),
            outside_count=len(outside),outside_cases=outside)
    result=dict(rows_calibration=30,rows_application=14,feature_ranges=summary,
        outside_any_calibration_marginal=sum(bool(v) for v in cases.values()),outside_by_case=cases,
        inside_marginals_is_not_joint_support=True,marginal_overlap_is_not_validation=True,
        candidate_validation_is_not_cross_dataset_qualification=True,
        fixed_contextual_candidate_execution='proposed_not_executed_no_transfer_admission',
        new_fits=0,new_predictions=0,image_reads=0,holdout_bytes_read=0,
        input_sha256={str(p):sha(p) for p in [Path(__file__),a,b]})
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(outside_any=result['outside_any_calibration_marginal'],ranges={k:(v['calibration_min'],v['calibration_max'],v['application_min'],v['application_max'],v['outside_count']) for k,v in summary.items()}),indent=2))


if __name__=='__main__':main()
