"""Same20pair thesis-development comparison with per-output target MAE."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/table2_same_cohort_report_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    names={'baseline5':'table2_reviewed_ten_source_evaluation_v1','chroma9':'table2_chroma_distribution_comparison_v1',
        'clean_leaf':'table2_clean_leaf_policy_v1','nested_selection':'table2_nested_safety_v1'}
    plan=read(ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1/fit_plan.json')
    rows={r['pair_id']:r for r in plan['rows']};targets=['target_gamma','target_red_gain','target_blue_gain']
    assert len(rows)==20
    hashes={};pair_records=[];aggregates=[]
    for method,name in names.items():
        folder=ROOT/'outputs'/name;data=read(folder/'summary.json');verify=read(folder/'verification.json')
        assert digest(folder/'summary.json')==verify['summary_sha256']
        for p in [folder/'summary.json',folder/'verification.json']:hashes[str(p.relative_to(ROOT))]=digest(p)
        records=data['outer_records'] if method=='nested_selection' else data['records']
        assert {r['pair_id'] for r in records}==set(rows)
        metric_key={'baseline5':'learned','chroma9':'candidate','clean_leaf':'policy','nested_selection':'nested'}[method]
        for record in records:
            row=rows[record['pair_id']];expected=[row[k] for k in targets]
            error=[abs(float(p)-float(t)) for p,t in zip(record['parameters'],expected)]
            pair_records.append(dict(method=method,pair_id=row['pair_id'],variant=row['variant'],
                ciede2000=record[metric_key]['ciede2000_source_mask'],no_correction_ciede2000=record['no_correction']['ciede2000_source_mask'],
                gamma_abs_error=error[0],red_gain_abs_error=error[1],blue_gain_abs_error=error[2]))
        for scope in ['all','identity','distorted']:
            subset=[r for r in pair_records if r['method']==method and (scope=='all' or (r['variant']=='identity')==(scope=='identity'))]
            aggregates.append(dict(method=method,scope=scope,pairs=len(subset),sources=len({r['pair_id'].split('__')[0] for r in subset}),
                mean_ciede2000=float(np.mean([r['ciede2000'] for r in subset])),
                mean_gamma_abs_error=float(np.mean([r['gamma_abs_error'] for r in subset])),
                mean_red_gain_abs_error=float(np.mean([r['red_gain_abs_error'] for r in subset])),
                mean_blue_gain_abs_error=float(np.mean([r['blue_gain_abs_error'] for r in subset])),
                harmed_clean_controls=sum(r['variant']=='identity' and r['ciede2000']>0 for r in subset)))
    assert len(pair_records)==80 and len(aggregates)==12
    hashes[str(Path(__file__).relative_to(ROOT))]=digest(Path(__file__))
    out.mkdir()
    for filename,records in [('pair_metrics.csv',pair_records),('aggregate_metrics.csv',aggregates)]:
        with (out/filename).open('x',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    note='All methods use same20exposed pairs/10source groups; parameter MAE is relative to approximate fitted recovery targets (identity exact), not calibrated skin-color truth. No pooled gamma/red/blue MAE: units/scales differ. No method passes both gates. Sequential development exposure prevents independent-final-performance claims.'
    (out/'summary.json').write_text(json.dumps(dict(status='complete_same_cohort_report',aggregate=aggregates,input_sha256=hashes,limitation=note),indent=2),encoding='utf-8')
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    for filename,expected in [('pair_metrics.csv',pair_records),('aggregate_metrics.csv',aggregates)]:
        with (out/filename).open(newline='',encoding='utf-8') as f:actual=list(csv.DictReader(f))
        assert len(actual)==len(expected)
        for a,b in zip(actual,expected):
            for key,value in b.items():assert a[key]==str(value)
    (out/'verification.json').write_text(json.dumps(dict(status='pass',verified_pairs=80,verified_aggregate_rows=12,
        identical_cohort=True,csv_roundtrips=True,input_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')),indent=2),encoding='utf-8')
    print('PASS:80 same-cohort pair records,12 aggregate rows; separate gamma/red/blue target MAE')


if __name__=='__main__':main()
