"""Explicit one-shot real comparison; import has no fit/read effects."""
from pathlib import Path
import hashlib,json,platform,sys
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.joint_colour_workflow import read,write,sha,fit_all,seal_support,after_fit_barrier,score_context,aggregate
from src.model_training.portable_tree import PortableTree
from src.model_training.gap_training_feasibility import f32

def versions():return dict(python=platform.python_version(),numpy=version('numpy'),sklearn=version('scikit-learn'),opencv=cv2.__version__,skimage=version('scikit-image'))

def main():
    if sys.argv[1:]!=['--execute-fixed-development']:raise SystemExit('Explicit --execute-fixed-development required')
    design=ROOT/'outputs/joint_colour_source_held_design_v1';plan=read(design/'plan_PRIVATE.json');check=read(design/'verification_PRIVATE.json')
    qa_path=ROOT/'outputs/joint_colour_workflow_engineering_v1/verification_PRIVATE.json';qa=read(qa_path)
    assert qa['passed'] and qa['runtime_versions']==versions() and check['plan_sha256']==sha(design/'plan_PRIVATE.json')
    for table in [plan['input_sha256'],qa['input_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h,n
    out=ROOT/plan['output_directory'];assert out.resolve()==(ROOT/'outputs/joint_colour_source_held_comparison_v1').resolve();out.mkdir()
    write(out/'execution_plan_PRIVATE.json',dict(plan=plan,engineering_sha256=sha(qa_path),code_sha256=qa['input_sha256']))
    try:
        prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
        records={r['case_id']:r for r in read(prep/'rows_PRIVATE.json')}
        gaps={r['case_id']:r for r in read(ROOT/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')}
        audited=read(ROOT/'outputs/joint_log_colour_exposed_audit_v1/features_PRIVATE.json')
        parents=read(ROOT/'outputs/histogram_gap_source_held_comparison_v1/models_PRIVATE.json')
        models=fit_all(out,plan,parents,records,gaps,audited,ROOT/'outputs/joint_log_colour_training_feasibility_v1')
        def load():return {s['source']:seal_support(ROOT,out,s) for s in plan['support_sources']}
        def score(supports):
            predictions=[];public={};assets=out/'review_assets';assets.mkdir();joint={r['case_id']:r for r in audited}
            declared={r['case_id']:r for r in plan['declared_pixel_containers']}
            anonymous={c:f'case-{i+1:02}' for i,c in enumerate(plan['anonymous_id_case_order'])}
            for entry in models:
                tree=PortableTree(read(out/entry['directory']/'candidate_PRIVATE.json'))
                for case in entry['definition']['evaluation_cases']:
                    r=records[case];a=joint[case];g=gaps[case]
                    assert a['source']==g['source']==r['publisher_group'] and a['role']==g['role']==r['experimental_role']
                    x=r['input_vector_float32']+[f32(g['features'][n]) for n in plan['feature_names'][16:22]]+[f32(v) for v in a['features']]
                    controls=tree.predict_one(x);path=Path(r['pixels_file'])
                    assert path.resolve()==(prep/case/'paired_pixels.npz').resolve()==Path(declared[case]['path']).resolve()
                    assert sha(path)==r['pixels_sha256']==declared[case]['sha256']
                    with np.load(path,allow_pickle=False) as pack:
                        image=pack['input_rgb8'];ref=pack['reference_rgb8'];s=supports[r['publisher_group']]
                        assert np.array_equal(pack['protected'],s['old_protected'])
                        assert image.shape==ref.shape==(256,256,3)
                        output,metrics=score_context(image,ref,s['alpha'],s['mask'],s['protected'],controls)
                        ident=anonymous[case];bit=hashlib.sha256((plan['protocol_id']+case).encode()).digest()[-1]&1
                        for panel,data in [('A',output if bit else image),('B',image if bit else output),('R',ref)]:
                            assert cv2.imwrite(str(assets/f'{ident}_{panel}.png'),data[:,:,::-1])
                        public[case]=dict(id=ident,kind='identity' if r['experimental_role']=='identity' else 'distorted',A=f'review_assets/{ident}_A.png',B=f'review_assets/{ident}_B.png',R=None if r['experimental_role']=='identity' else f'review_assets/{ident}_R.png')
                        predictions.append(dict(case_id=case,review_id=ident,source=r['publisher_group'],role=r['experimental_role'],leaf=tree.leaf_id(x),controls=controls,
                            output_panel='A' if bit else 'B',primary=metrics,parameter_absolute_error=[abs(a-b) for a,b in zip(controls,r['nominal_controls'])]))
                    write(out/'predictions_PRIVATE.json',predictions)
            assert len(predictions)==44
            write(out/'review_public.json',dict(protocol_id=plan['protocol_id'],preview_note='Unchanged-photo cases first. Save regularly. A noticeable change closes this candidate early; no further ratings are then needed.',cases=[public[c] for c in plan['review_order']]))
            stats=aggregate(predictions,'primary');numeric=all(stats[r]['source_equal_DE_improvement']>0 for r in plan['families'])
            write(out/'summary_PRIVATE.json',dict(attempted=48,available=44,excluded=4,primary=dict(by_role=stats),numeric_families_pass=numeric,visual_status='PENDING' if numeric else 'NOT_REQUIRED_NUMERICAL_FAILURE',model_ready=False))
            write(out/'role_ledger_PRIVATE.json',read(prep/'role_ledger_PRIVATE.json'))
        after_fit_barrier(out,plan,models,load,score)
        for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h
        write(out/'status_PRIVATE.json',dict(status='COMPLETE_PENDING_INDEPENDENT_VERIFICATION',new_fits=10,reused_fits=1,held_controls=44,renders=44))
    except BaseException as error:write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise

if __name__=='__main__':main()
