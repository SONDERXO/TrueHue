"""One-shot future66 development workflow. No work on import."""
from pathlib import Path
import hashlib,platform,sys
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.blue_axis_workflow import read,write,sha,fit_all,seal_support,after_fit_barrier,score_context,numerical_gate,load_case
from src.model_training.portable_tree import PortableTree

def versions():return dict(python=platform.python_version(),numpy=version('numpy'),sklearn=version('scikit-learn'),opencv=cv2.__version__,skimage=version('scikit-image'))

def main():
    if sys.argv[1:]!=['--execute-fixed-development']:raise SystemExit('Explicit execution flag required')
    design=ROOT/'outputs/blue_axis_source_held_design_v1';plan=read(design/'plan_PRIVATE.json');checked=read(design/'verification_PRIVATE.json')
    qa_path=ROOT/'outputs/blue_axis_workflow_engineering_v1/verification_PRIVATE.json';qa=read(qa_path)
    assert qa['passed'] and qa['runtime_versions']==versions() and checked['plan_sha256']==sha(design/'plan_PRIVATE.json')
    for table in [plan['input_sha256'],plan['inherited_input_sha256'],qa['input_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h,n
    out=ROOT/'outputs/blue_axis_source_held_comparison_v1';out.mkdir()
    write(out/'execution_plan_PRIVATE.json',dict(plan=plan,engineering_sha256=sha(qa_path),code_sha256=qa['input_sha256']))
    try:
        prep=ROOT/'outputs/blue_axis_preparation_v1';records=read(prep/'rows_PRIVATE.json');by={r['case_id']:r for r in records}
        assert sha(prep/'rows_PRIVATE.json')==read(prep/'verification_PRIVATE.json')['rows_sha256']
        models=fit_all(out,plan,records,ROOT/Path(plan['reuse']['path']).parent)
        def load():return {s['source']:seal_support(ROOT,out,s) for s in plan['support_sources']}
        def score(supports):
            predictions=[];public={};assets=out/'review_assets';assets.mkdir()
            declared={r['case_id']:r for r in plan['declared_pixel_containers']};anon={c:f'case-{i+1:02}' for i,c in enumerate(plan['anonymous_case_order'])};references={}
            # Identity pack/reference checks are bound explicitly; no new-pack parser assumption.
            for entry in models:
                for c in entry['definition']['evaluation_cases']:
                    if by[c]['role']!='identity':continue
                    image,ref=load_case(by[c]['pixels_file'],declared[c],supports[by[c]['source']])
                    assert np.array_equal(image,ref);references[by[c]['source']]=ref
            for entry in models:
                tree=PortableTree(read(out/entry['directory']/'candidate_PRIVATE.json'))
                for c in entry['definition']['evaluation_cases']:
                    r=by[c];s=supports[r['source']];image,ref=load_case(r['pixels_file'],declared[c],s)
                    assert np.array_equal(ref,references[r['source']])
                    controls=tree.predict_one(r['x']);output,metrics=score_context(image,ref,s['alpha'],s['mask'],s['protected'],controls)
                    ident=anon[c];bit=hashlib.sha256((plan['protocol_id']+c).encode()).digest()[-1]&1
                    for panel,data in [('A',output if bit else image),('B',image if bit else output),('R',ref)]:assert cv2.imwrite(str(assets/f'{ident}_{panel}.png'),data[:,:,::-1])
                    public[c]=dict(id=ident,kind='identity' if r['role']=='identity' else 'distorted',A=f'review_assets/{ident}_A.png',B=f'review_assets/{ident}_B.png',R=None if r['role']=='identity' else f'review_assets/{ident}_R.png')
                    predictions.append(dict(case_id=c,review_id=ident,source=r['source'],role=r['role'],leaf=tree.leaf_id(r['x']),controls=controls,output_panel='A' if bit else 'B',primary=metrics,parameter_absolute_error=[abs(a-b) for a,b in zip(controls,r['y'])]))
                    write(out/'predictions_PRIVATE.json',predictions)
            stats,numeric=numerical_gate(predictions)
            write(out/'summary_PRIVATE.json',dict(attempted=72,available=66,excluded=6,primary=dict(by_role=stats),numeric_families_pass=numeric,visual_status='PENDING_READINESS_AND_REUSE_AUDIT' if numeric else 'NOT_REQUIRED_NUMERICAL_FAILURE',model_ready=False))
            # Private draft only. No public manifest/HTTP review before independent numerical verification.
            write(out/'review_draft_PRIVATE.json',dict(protocol_id=plan['protocol_id'],cases=[public[c] for c in plan['review_order']]))
            write(out/'role_ledger_PRIVATE.json',read(prep/'role_ledger_PRIVATE.json'))
        after_fit_barrier(out,plan,models,load,score)
        for table in [plan['input_sha256'],plan['inherited_input_sha256']]:
            for n,h in table.items():assert sha(ROOT/n)==h
        write(out/'status_PRIVATE.json',dict(status='COMPLETE_PENDING_INDEPENDENT_VERIFICATION',new_fits=10,reused_fits=1,held_controls=66,renders=66))
    except BaseException as error:write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise

if __name__=='__main__':main()
