"""Fixed repeated local Python timing with exact saved-output parity on every call."""
import csv
import hashlib
import importlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import sys
import time
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np

OUT=ROOT/'outputs/development_mst_benchmark_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
    parent=ROOT/'outputs/table2_clean_leaf_policy_v1';plan=read(parent/'plan.json');prior=read(parent/'summary.json')
    assert digest(parent/'summary.json')==read(parent/'verification.json')['summary_sha256']
    rows={r['pair_id']:r for r in plan['rows']};expected={r['pair_id']:r for r in prior['records']}
    assert len(rows)==20
    orders={str(i):sorted(rows,key=lambda p:hashlib.sha256(f'mst_benchmark42/{i}/{p}'.encode()).hexdigest()) for i in range(1,6)}
    tracked=[Path(__file__),ROOT/'docs/development-mst-benchmark-protocol.md',ROOT/'scripts/180_run_development_mst_pipeline.py',
        ROOT/'src/correction/development_mst_pipeline.py',parent/'plan.json',parent/'summary.json',parent/'verification.json']
    tracked+=list(parent.glob('fold_*/*'))
    for r in rows.values():tracked.extend(ROOT/r[k] for k in ['input_path','input_mask_path'])
    tracked+=[parent/(pair+'_corrected.png') for pair in rows]
    hashes={str(p.relative_to(ROOT)):digest(p) for p in tracked}
    OUT.mkdir()
    environment=dict(python=sys.version,os=platform.system(),os_release=platform.release(),architecture=platform.machine(),
        processor=platform.processor(),logical_cpu_count=os.cpu_count(),opencv=cv2.__version__,opencv_threads=cv2.getNumThreads(),
        numpy=np.__version__,mediapipe=version('mediapipe'),scikit_learn=version('scikit-learn'),thread_settings_changed=False)
    write(OUT/'plan.json',dict(status='frozen_before_timing',pair_ids=sorted(rows),round_orders=orders,repeats=5,warmups_per_input=1,
        experiment='clean-leaf',environment=environment,input_sha256=hashes,
        primary_timing='External perf_counter around pipeline.run only; decoding/construction/parity/reporting excluded',
        scope='Repeated local Python calls,not Android or end-user latency; no quality promotion'))
    runner=importlib.import_module('180_run_development_mst_pipeline');pipelines={};construction=[]
    for fid in range(1,11):
        started=time.perf_counter();pipeline,provenance=runner.build_pipeline('clean-leaf',fid)
        construction.append(dict(fold_id=fid,external_construction_ms=(time.perf_counter()-started)*1000,
            provenance_initialization_ms=provenance['initialization_ms'],note='Hash/dependency construction; lazy detector/landmarker load may occur at warmup'))
        pipelines[fid]=pipeline
    images={p:cv2.imread(str(ROOT/r['input_path'])) for p,r in rows.items()}
    masks={p:cv2.imread(str(ROOT/r['input_mask_path']),0) for p,r in rows.items()}
    output_hashes={p:hashlib.sha256(cv2.imread(str(parent/(p+'_corrected.png'))).tobytes()).hexdigest() for p in rows}
    attempts=[]
    def run(pair,phase,round_id):
        started=time.perf_counter();result=pipelines[expected[pair]['fold_id']].run(images[pair]);elapsed=(time.perf_counter()-started)*1000
        record=dict(pair_id=pair,phase=phase,round_id=round_id,variant=rows[pair]['variant'],external_elapsed_ms=elapsed,
            internal_elapsed_ms=result.report['elapsed_ms'],stages=result.report['timings_ms'],status=result.report['status'],parity=False)
        attempts.append(record)
        if result.corrected is None:raise RuntimeError('Benchmark failure retained; no slow/failure replacement')
        assert result.report['parameters']==expected[pair]['parameters']
        for k in plan['features']:assert result.report['features'][k]==rows[pair][k]
        np.testing.assert_array_equal(result.mask,masks[pair])
        assert hashlib.sha256(result.corrected.tobytes()).hexdigest()==output_hashes[pair]
        record['parity']=True
        with (OUT/'attempts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
    try:
        for pair in sorted(rows):run(pair,'warmup',0)
        for round_id,order in orders.items():
            for pair in order:run(pair,'measured',int(round_id))
            print('completed measured round',round_id,flush=True)
        measured=[r for r in attempts if r['phase']=='measured']
        def stats(records):
            values=[r['external_elapsed_ms'] for r in records]
            return dict(calls=len(values),mean_ms=float(np.mean(values)),p50_ms=float(np.percentile(values,50,method='linear')),
                p95_ms=float(np.percentile(values,95,method='linear')),min_ms=min(values),max_ms=max(values))
        aggregates=dict(all=stats(measured),identity=stats([r for r in measured if r['variant']=='identity']),
            distorted=stats([r for r in measured if r['variant']!='identity']))
        per_case={p:stats([r for r in measured if r['pair_id']==p]) for p in rows}
        assert len(measured)==100 and len(attempts)==120
        assert hashes=={p:digest(ROOT/p) for p in hashes}
        with (OUT/'timings.csv').open('x',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,['pair_id','phase','round_id','variant','external_elapsed_ms','internal_elapsed_ms','parity'])
            writer.writeheader();writer.writerows({k:r[k] for k in writer.fieldnames} for r in attempts)
        write(OUT/'summary.json',dict(status='complete_local_python_benchmark',aggregate=aggregates,per_case=per_case,
            construction=construction,records=attempts,environment=environment,input_sha256=hashes,
            all_120_exact_parity=True,warmups_excluded=True,active_model_changed=False,quality_validated=False))
        print(json.dumps(aggregates,indent=2))
    except Exception as error:
        write(OUT/'failed_run.json',dict(status='failed',reason=str(error),attempts=attempts));raise


if __name__=='__main__':main()
