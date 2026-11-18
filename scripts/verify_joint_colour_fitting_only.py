"""Independent saved metadata join, graph/routes/means/loss; no optimizer imports."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.joint_colour_verification import verify

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'outputs/joint_log_colour_training_feasibility_v1';dest=out/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    receipt=read(out/'execution_plan_PRIVATE.json')
    for table in ['input_sha256','code_sha256']:
        for n,h in receipt[table].items():assert sha(ROOT/n)==h
    folder=ROOT/'outputs/joint_log_colour_training_design_v1'
    assert sha(folder/'plan_PRIVATE.json')==receipt['plan_sha256']
    plan=read(folder/'plan_PRIVATE.json');rows=read(out/'fitting_inputs_PRIVATE.json')
    assert len(rows)==40 and [r['case_id'] for r in rows]==[r['case_id'] for r in plan['fitting_records']]
    wanted={r['case_id'] for r in rows}
    audit={r['case_id']:r for r in read(ROOT/plan['audited_features_path']) if r['case_id'] in wanted}
    gaps={r['case_id']:r for r in read(ROOT/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json') if r['case_id'] in wanted}
    parent=read(ROOT/'outputs/histogram_gap_training_feasibility_design_v1/plan_PRIVATE.json')
    for saved,binding in zip(rows,plan['fitting_records']):
        original=read(ROOT/binding['record']);a=audit[saved['case_id']];g=gaps[saved['case_id']]
        assert saved['source']==original['publisher_group']==a['source']==binding['source']!=plan['excluded_group']
        assert saved['role']==original['experimental_role']==a['role']==binding['role']
        assert a['generated_fixture'] is False and original['generated_fixture'] is False
        expected=original['input_vector_float32']+[struct.unpack('!f',struct.pack('!f',g['features'][n]))[0] for n in parent['new_feature_names']]
        expected += [struct.unpack('!f',struct.pack('!f',v))[0] for v in a['features']]
        assert saved['x']==expected and saved['y']==original['nominal_controls']
    baseline=read(ROOT/plan['baseline']['path']);assert baseline==read(out/'baseline_SAVED_PRIVATE.json')
    result=verify(read(out/'candidate_PRIVATE.json'),baseline,rows,read(out/'training_replay_PRIVATE.json'),plan['feature_names'])
    assert read(out/'status_PRIVATE.json')['fit_calls']==1
    result['artifact_sha256']={p.name:sha(p) for p in out.glob('*.json')}
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(result['classification'])

if __name__=='__main__':main()
