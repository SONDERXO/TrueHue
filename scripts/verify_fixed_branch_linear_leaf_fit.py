"""Independent actual60 join and scalar fit replay; no optimizer or NumPy."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.fixed_branch_linear_leaf_verification import verify
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'outputs/fixed_branch_linear_leaf_first_fit_v1';dest=out/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve independent verification')
    design=ROOT/'outputs/fixed_branch_linear_leaf_design_v1';plan=read(design/'plan_PRIVATE.json');execution=read(out/'execution_PRIVATE.json')
    assert sha(design/'plan_PRIVATE.json')==execution['plan_sha256']
    for table in [plan['input_sha256'],execution['code_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h
    first=ROOT/'outputs/blue_axis_first_fit_v1';canonical={r['case_id']:r for r in read(first/'fitting_inputs_PRIVATE.json')}
    wanted=set(plan['fitting_cases']);records={r['case_id']:r for r in read(ROOT/'outputs/blue_axis_preparation_v1/rows_PRIVATE.json') if r['case_id'] in wanted}
    bindings={r['case_id']:r for r in read(design/'fitting_join_metadata_PRIVATE.json')};rows=read(out/'fitting_inputs_PRIVATE.json')
    assert [r['case_id'] for r in rows]==plan['fitting_cases'] and set(records)==set(canonical)==set(bindings)==wanted
    for r in rows:
        c=r['case_id'];original=records[c];old=canonical[c];b=bindings[c]
        assert r=={k:original[k] for k in ['case_id','source','role','x','y','generated_fixture','status']}
        assert {k:r[k] for k in ['case_id','source','role','x','y']}==old
        assert (r['source'],r['role'],r['y'])==(b['source'],b['role'],b['nominal'])
    scaffold=read(first/'candidate_PRIVATE.json');baseline=read(first/'training_replay_PRIVATE.json')
    assert read(out/'baseline_SAVED_PRIVATE.json')==baseline
    report=verify(plan,rows,scaffold,baseline,read(out/'candidate_PRIVATE.json'),read(out/'replay_PRIVATE.json'))
    assert read(out/'status_PRIVATE.json')==dict(status='FITTED_PENDING_INDEPENDENT_VERIFICATION',solver_calls=6,branch_fits=0,held_predictions=0)
    report['artifact_sha256']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
    with dest.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print(report['classification']+'; fitting only, no correction quality or held result')
if __name__=='__main__':main()
