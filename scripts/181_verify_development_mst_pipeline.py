"""Fresh detection-to-correction replay on saved held-source inputs, plus failure."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np


def main():
    out=ROOT/'outputs/development_mst_pipeline_replay_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    runner=importlib.import_module('180_run_development_mst_pipeline')
    parent=ROOT/'outputs/table2_clean_leaf_policy_v1';plan=read(parent/'plan.json');summary=read(parent/'summary.json')
    assert digest(parent/'summary.json')==read(parent/'verification.json')['summary_sha256']
    rows={r['pair_id']:r for r in plan['rows']}
    tracked=[Path(__file__),ROOT/'scripts/180_run_development_mst_pipeline.py',ROOT/'src/correction/development_mst_pipeline.py',parent/'summary.json',parent/'plan.json']
    tracked+=list(parent.glob('fold_*/*'))
    for r in rows.values():tracked.extend(ROOT/r[k] for k in ['input_path','input_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in tracked}
    out.mkdir();records=[];pipelines={}
    for expected in summary['records']:
        row=rows[expected['pair_id']];fid=expected['fold_id']
        if fid not in pipelines:pipelines[fid]=runner.build_pipeline('clean-leaf',fid)
        pipeline,provenance=pipelines[fid]
        result=pipeline.run(cv2.imread(str(ROOT/row['input_path'])))
        assert result.report['status']=='development_experimental_mst'
        for k in plan['features']:assert result.report['features'][k]==row[k]
        assert result.report['mst']['config_index']==row['input_mst_index']
        assert result.report['parameters']==expected['parameters']
        np.testing.assert_array_equal(result.mask,cv2.imread(str(ROOT/row['input_mask_path']),0))
        np.testing.assert_array_equal(result.corrected,cv2.imread(str(parent/(row['pair_id']+'_corrected.png'))))
        runner.save_result(out/row['pair_id'],result,{**provenance,'verification_role':'Correct saved held-source fold chosen from frozen plan'})
        records.append(dict(pair_id=row['pair_id'],fold_id=fid,elapsed_ms=result.report['elapsed_ms'],timings_ms=result.report['timings_ms']))
        print(row['pair_id'],'parity',flush=True)
    failed=ROOT/'outputs/table2_counterfactual_coverage_v1/images/75027__dark_input.png'
    failed_hash=digest(failed);result=pipelines[6][0].run(cv2.imread(str(failed)))
    assert result.report['failed_stage']=='face_detection' and result.corrected is None and result.report['mst'] is None and result.report['parameters'] is None
    runner.save_result(out/'75027_dark_failure',result,pipelines[6][1]);assert digest(failed)==failed_hash
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    report=dict(status='pass',successful_exact_replays=20,preserved_detection_failures=1,records=records,input_sha256=hashes,
        observed_pipeline_ms=dict(min=float(min(r['elapsed_ms'] for r in records)),median=float(np.median([r['elapsed_ms'] for r in records])),max=float(max(r['elapsed_ms'] for r in records))),
        timing_scope='21sequential local Python calls;20success timing observations,initialization reported separately; no warmup/repetitions,not Android benchmark',
        active_model_changed=False,quality_validated=False)
    (out/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['status','successful_exact_replays','preserved_detection_failures','observed_pipeline_ms']},indent=2))


if __name__=='__main__':main()
