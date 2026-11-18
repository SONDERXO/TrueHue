"""One budgeted40-row training search, without loading held case records."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.bounded_regression_search import search_tree
P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
OUT=ROOT/'outputs/training_search_feasibility_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')

def main():
    if OUT.exists():raise FileExistsError('Preserve completed or partial feasibility run; no restart')
    plan_path=ROOT/'outputs/correction_training_contract_v1/plan_PRIVATE.json';plan=read(plan_path);f=plan['feasibility']
    qa_path=ROOT/'outputs/bounded_regression_search_generated_check_v1/verification_PRIVATE.json';qa=read(qa_path);assert qa['passed']
    bound=dict(plan['input_sha256']);bound.update(qa['input_sha256']);bound[str(plan_path)]=sha(plan_path);bound[str(qa_path)]=sha(qa_path)
    # Hashing frozen metadata containers does not use their held values for training.
    assert all(sha(p)==h for p,h in bound.items())
    model_path=ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json'
    text=model_path.read_text().lstrip();assert text.startswith('[')
    first,_=json.JSONDecoder().raw_decode(text[1:].lstrip())
    assert first['definition']['held_publisher_group']==f['held_group']
    assert first['definition']['fitting_cases']==f['fitting_cases']
    # Only per-case training records are parsed; no held input vectors are loaded.
    rows=[]
    for case in f['fitting_cases']:
        path=P/case/'record_PRIVATE.json';row=read(path)
        assert row['case_id']==case and row['publisher_group']!=f['held_group'] and row['status']=='available'
        bound[str(path)]=sha(path);rows.append(row)
    assert len(rows)==40 and len(first['tree']['feature_names'])==16
    bound[str(Path(__file__))]=sha(__file__)
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(authorized_searches=1,first_fold_counts_toward_full11=True,training_cases=f['fitting_cases'],held_group=f['held_group'],held_case_records_loaded=0,metadata_containers_hashed_without_using_other_values=True,incumbent_source_sha256=sha(model_path),max_seconds=60,max_states=5000,input_sha256=bound))
    write(OUT/'fitting_inputs_PRIVATE.json',[dict(case_id=r['case_id'],input_vector_float32=r['input_vector_float32'],nominal_controls=r['nominal_controls'],role=r['experimental_role']) for r in rows]);write(OUT/'incumbent_PRIVATE.json',first['tree'])
    print('Starting one training-only search:40rows/16inputs/depth4/60seconds/5000states',flush=True)
    start=time.monotonic()
    result=search_tree([r['input_vector_float32'] for r in rows],[r['nominal_controls'] for r in rows],first['tree'],max_depth=4,max_states=5000,max_seconds=60.)
    write(OUT/'candidate_PRIVATE.json',result['tree']);write(OUT/'search_PRIVATE.json',result['search'])
    summary=dict(searches=1,fitting_rows=40,input_features=16,max_depth=4,wall_seconds=time.monotonic()-start,search=result['search'],held_predictions=0,photo_reads=0,held_case_records_loaded=0,image_model_calls=0,new_target_fits=0,new_MST_fits=0,incumbent_refits=0,training_admitted=False,runtime_adopted=False,full_comparison_selected=False,holdout_reads=0)
    assert all(sha(p)==h for p,h in bound.items());write(OUT/'summary_PRIVATE.json',summary);print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
