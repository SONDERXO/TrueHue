"""Fixed all-severity integrated replay of three saved ten-source methods."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.evaluation.correction_prototype import image_errors

OUT=ROOT/'outputs/development_mst_stress_v1'
METHODS=['baseline5','chroma9','clean-leaf']


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    runner=importlib.import_module('180_run_development_mst_pipeline')
    parent=ROOT/'outputs/table2_clean_leaf_policy_v1';plan=read(parent/'plan.json')
    stress=ROOT/'outputs/table2_counterfactual_coverage_v1';data=read(stress/'summary.json')
    assert digest(stress/'summary.json')==read(stress/'verification.json')['summary_sha256']
    cases=[]
    for row in plan['rows']:
        if row['variant']=='identity':cases.append(dict(case_id=row['pair_id'],source_id=row['pair_id'].split('__')[0],
            scope='identity',input_path=row['input_path'],input_mask_path=row['input_mask_path'],
            reference_path=row['reference_path'],reference_mask_path=row['reference_mask_path'],expected_status='success'))
    for r in data['records']:
        cases.append(dict(case_id=r['pair_id'],source_id=r['source_id'],scope=r['severity_probe'],
            input_path=str((stress/'images'/(r['pair_id']+'_input.png')).relative_to(ROOT)),
            input_mask_path=str((stress/'images'/(r['pair_id']+'_mask.png')).relative_to(ROOT)) if r['status']=='success' else None,
            reference_path=r['reference_path'],reference_mask_path=r['reference_mask_path'],expected_status=r['status']))
    assert len(cases)==34 and len({r['case_id'] for r in cases})==34
    source_folds={rowsource.split('__')[0]:f['fold_id'] for f in plan['folds'] for rowsource in f['inner_validation_pair_ids']}
    paths=[Path(__file__),ROOT/'scripts/180_run_development_mst_pipeline.py',ROOT/'src/correction/development_mst_pipeline.py',
        parent/'plan.json',parent/'summary.json',parent/'verification.json',stress/'summary.json',stress/'verification.json']
    for method in METHODS:
        folder=ROOT/'outputs'/runner.EXPERIMENTS[method];paths+=list(folder.glob('fold_*/*'))
        paths.extend([folder/'summary.json',folder/'verification.json'])
    for case in cases:paths.extend(ROOT/case[k] for k in ['input_path','reference_path','reference_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.mkdir()
    write(OUT/'plan.json',dict(status='frozen_before_inference',cases=cases,methods=METHODS,source_folds=source_folds,input_sha256=hashes,
        design='Ten identity sources plus fixed24counterfactual severities on8sources; report scopes separately, no pooled unequal-source mean',
        fitting='No new fits, source selection, mask/feature/threshold changes; same ten-source held fold per source for all methods',
        caution='Exposed-development robustness check,not independent final evaluation or actual dark-complexion coverage'))
    records=[];cache={}
    for case in cases:
        image=cv2.imread(str(ROOT/case['input_path']));reference=cv2.cvtColor(cv2.imread(str(ROOT/case['reference_path'])),cv2.COLOR_BGR2RGB)
        score=cv2.imread(str(ROOT/case['reference_mask_path']),0)>0
        for method in METHODS:
            key=(method,source_folds[case['source_id']])
            if key not in cache:cache[key]=runner.build_pipeline(*key)
            pipeline,provenance=cache[key];result=pipeline.run(image)
            success=result.corrected is not None
            assert success==(case['expected_status']=='success')
            if success:
                np.testing.assert_array_equal(result.mask,cv2.imread(str(ROOT/case['input_mask_path']),0))
            else:assert result.report['failed_stage']=='face_detection' and result.report['parameters'] is None and result.report['mst'] is None
            folder=OUT/case['case_id']/method;runner.save_result(folder,result,provenance)
            metric=image_errors(reference,cv2.cvtColor(result.corrected,cv2.COLOR_BGR2RGB),score) if success else None
            records.append(dict(case_id=case['case_id'],source_id=case['source_id'],scope=case['scope'],method=method,
                fold_id=key[1],success=success,failed_stage=result.report['failed_stage'],metrics=metric,
                no_correction=image_errors(reference,cv2.cvtColor(image,cv2.COLOR_BGR2RGB),score),
                report_path=str((folder/'report.json').relative_to(OUT))))
        print(case['case_id'],'all methods checked',flush=True)
    aggregate={}
    for scope in ['identity','light','medium','dark']:
        aggregate[scope]={}
        for method in METHODS:
            attempted=[r for r in records if r['scope']==scope and r['method']==method];successful=[r for r in attempted if r['success']]
            aggregate[scope][method]=dict(attempted=len(attempted),successful=len(successful),
                no_correction_ciede2000=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in successful])),
                corrected_ciede2000=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in successful])),
                harmed_cases=[r['case_id'] for r in successful if r['metrics']['ciede2000_source_mask']>r['no_correction']['ciede2000_source_mask']],
                unchanged_distorted_inputs=[r['case_id'] for r in successful if scope!='identity' and
                    np.array_equal(cv2.imread(str(OUT/r['case_id']/method/'corrected.png')),cv2.imread(str(ROOT/next(c['input_path'] for c in cases if c['case_id']==r['case_id']))))])
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',dict(status='complete_development_stress',records=records,aggregate=aggregate,input_sha256=hashes,
        new_fits=0,runtime_replaced=False,final_validated=False))
    print(json.dumps({s:{m:dict(successes=r['successful'],ciede2000=r['corrected_ciede2000']) for m,r in methods.items()} for s,methods in aggregate.items()},indent=2))


if __name__=='__main__':main()
