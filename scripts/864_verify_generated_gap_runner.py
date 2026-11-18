"""Preserve one generated numerical end-to-end run; no real data access."""
from pathlib import Path
import importlib.util,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.gap_training_feasibility import run_once
OUT=ROOT/'outputs/histogram_gap_runner_generated_v1'

def main():
    if OUT.exists():raise FileExistsError('Preserve generated check')
    names=[f'generated_old_{i}' for i in range(16)]+[f'generated_gap_{i}' for i in range(6)]
    rows=[dict(case_id=f'GENERATED_{i}',source=f'generated_source_{i//2}',role='under' if v<.5 else 'over',
        x=[0.]*16+[v]+[0.]*5,y=[.7,1.,1.] if v<.5 else [1.4,1.05,1.03]) for i,v in enumerate([0.,0.,.25,.25,.75,.75,1.,1.])]
    baseline=dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,
        feature_names=names[:16],target_names=['gamma','red_gain','blue_gain'],nodes=[dict(kind='leaf',values=[1.05,1.025,1.015])])
    run_once(OUT,rows,names,baseline,dict(generated_only=True,scientific_rows=0))
    path=ROOT/'scripts/863_verify_histogram_gap_training_feasibility.py'
    spec=importlib.util.spec_from_file_location('independent_gap_generated',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    read=lambda n:json.loads((OUT/n).read_text(encoding='utf-8'))
    result=module.verify(read('candidate_PRIVATE.json'),baseline,read('fitting_inputs_PRIVATE.json'),read('training_replay_PRIVATE.json'),names)
    assert result['passed'] and result['added_features_used'] and result['candidate']['SSE']<1e-25
    result.update(generated_only=True,scientific_rows=0,real_fits=0,real_predictions=0,photo_reads=0,
        artifact_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.json')})
    (OUT/'verification_GENERATED_ONLY.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS: 8 generated rows / 22 inputs / 3 outputs; independent routes and leaf means; added feature used')

if __name__=='__main__':main()
