"""Independent warm-up/count/order/percentile/CSV and benchmark evidence checks."""
import csv
import hashlib
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/development_mst_benchmark_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');data=read(out/'summary.json');records=data['records']
    assert len(records)==120 and len(plan['pair_ids'])==20
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    measured=[r for r in records if r['phase']=='measured'];warmup=[r for r in records if r['phase']=='warmup']
    assert len(measured)==100 and len(warmup)==20
    assert [r['pair_id'] for r in warmup]==sorted(plan['pair_ids'])
    for round_id in range(1,6):
        expected=sorted(plan['pair_ids'],key=lambda p:hashlib.sha256(f'mst_benchmark42/{round_id}/{p}'.encode()).hexdigest())
        assert expected==plan['round_orders'][str(round_id)]
        assert [r['pair_id'] for r in measured if r['round_id']==round_id]==expected
    for pair in plan['pair_ids']:
        assert sum(r['pair_id']==pair for r in warmup)==1
        assert sum(r['pair_id']==pair for r in measured)==5
    for r in records:
        assert r['parity'] is True and r['status']=='development_experimental_mst'
        assert 0<r['internal_elapsed_ms']<=r['external_elapsed_ms']
        assert all(isinstance(v,(float,int)) and math.isfinite(v) and v>=0 for v in r['stages'].values())
        assert set(r['stages'])=={'square_measurement','face_detection','skin_mask','mst_lookup','distribution_features','tree_prediction','application'}
        assert r['stages']['face_detection']+r['stages']['skin_mask']<=r['stages']['square_measurement']
    def quantile(sorted_values,q):
        index=(len(sorted_values)-1)*q;lo=math.floor(index);hi=math.ceil(index)
        return sorted_values[lo]+(sorted_values[hi]-sorted_values[lo])*(index-lo)
    def check_stats(summary,subset):
        values=sorted(r['external_elapsed_ms'] for r in subset)
        expected=dict(calls=len(values),mean_ms=math.fsum(values)/len(values),p50_ms=quantile(values,.5),p95_ms=quantile(values,.95),min_ms=values[0],max_ms=values[-1])
        for key,value in expected.items():assert abs(summary[key]-value)<1e-9
    check_stats(data['aggregate']['all'],measured)
    check_stats(data['aggregate']['identity'],[r for r in measured if r['variant']=='identity'])
    check_stats(data['aggregate']['distorted'],[r for r in measured if r['variant']!='identity'])
    for pair,summary in data['per_case'].items():check_stats(summary,[r for r in measured if r['pair_id']==pair])
    with (out/'timings.csv').open(encoding='utf-8',newline='') as f:csv_rows=list(csv.DictReader(f))
    assert len(csv_rows)==120
    for a,b in zip(csv_rows,records):
        for k,v in a.items():assert v==str(b[k])
    ledger=[json.loads(line) for line in (out/'attempts.jsonl').read_text(encoding='utf-8').splitlines() if line]
    assert ledger==records
    assert len(data['construction'])==10 and data['warmups_excluded'] and data['all_120_exact_parity']
    assert data['environment']==plan['environment']
    target.write_text(json.dumps(dict(status='pass',warmups_verified=20,measured_calls_verified=100,equal_case_repetition=True,
        deterministic_order_verified=True,independently_recomputed_summary_sets=23,csv_ledger_roundtrips=True,
        original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json'),timings_csv_sha256=digest(out/'timings.csv')),
        indent=2),encoding='utf-8')
    print('PASS:20warmups/100measured calls,case balance/order,23independent summaries,CSV/ledger/hashes')


if __name__=='__main__':main()
