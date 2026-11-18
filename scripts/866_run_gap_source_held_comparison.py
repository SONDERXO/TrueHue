"""Explicit single-run comparison; no effects when imported."""
from pathlib import Path
import sys,hashlib,json,platform
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.gap_source_held_workflow import *
from src.model_training.gap_training_feasibility import SETTINGS,f32

def main():
    if sys.argv[1:]!=['--execute-fixed-development']:raise SystemExit('Explicit --execute-fixed-development required')
    qa_path=ROOT/'outputs/gap_source_held_engineering_v1/verification_PRIVATE.json';qa=read(qa_path);assert qa['passed']
    assert qa['runtime_versions']==dict(python=platform.python_version(),numpy=version('numpy'),sklearn=version('scikit-learn'),opencv=cv2.__version__,skimage=version('scikit-image'))
    for name,h in qa['input_sha256'].items():assert sha(ROOT/name)==h
    design=ROOT/'outputs/histogram_gap_source_held_design_v1';plan=read(design/'plan_PRIVATE.json');check=read(design/'verification_PRIVATE.json')
    assert check['passed'] and sha(design/'plan_PRIVATE.json')==check['plan_sha256'] and plan['settings']==SETTINGS
    for name,h in plan['input_sha256'].items():assert sha(ROOT/name)==h
    out=ROOT/'outputs/histogram_gap_source_held_comparison_v1';out.mkdir()
    write(out/'execution_plan_PRIVATE.json',dict(plan=plan,engineering_sha256=sha(qa_path),code_sha256=qa['input_sha256']))
    try:
        prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
        records={r['case_id']:r for r in read(prep/'rows_PRIVATE.json')}
        assert set(records)=={c for f in plan['folds'] for c in f['evaluation_cases']}
        audited=read(ROOT/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')
        parents=read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json')
        models=fit_models(out,plan,parents,records,audited,ROOT/'outputs/histogram_gap_training_feasibility_v1',load_verifier(ROOT))
        assert len(models)==11 and read(out/'all_fits_verified_PRIVATE.json')['passed']
        supports={s['source']:prepare_support(ROOT,out,s) for s in plan['support_sources']}
        write(out/'all_supports_sealed_PRIVATE.json',dict(passed=True,supports=[s['record'] for s in supports.values()]))
        gaps={r['case_id']:r for r in audited};predictions=[];public=[]
        assets=out/'review_assets';assets.mkdir();diagnostic=out/'fixed_diagnostic';diagnostic.mkdir()
        ledger=read(prep/'role_ledger_PRIVATE.json');assert len(ledger)==48
        write(out/'role_ledger_PRIVATE.json',ledger)
        saved_parent={r['case_id']:r for r in read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/predictions_PRIVATE.json')}
        for model in models:
            tree=PortableTree(model['tree'])
            for case in model['definition']['evaluation_cases']:
                r=records[case];gap=gaps[case];assert gap['source']==r['publisher_group'] and gap['role']==r['experimental_role']
                values=r['input_vector_float32']+[f32(gap['features'][n]) for n in plan['feature_names'][16:]]
                controls=tree.predict_one(values)
                path=Path(r['pixels_file']);assert path.resolve()==(prep/case/'paired_pixels.npz').resolve() and sha(path)==r['pixels_sha256']
                with np.load(path,allow_pickle=False) as pack:
                    image=pack['input_rgb8'];ref=pack['reference_rgb8'];alpha=pack['alpha'];mask=pack['scoring_mask'];protected=pack['protected']
                    support=supports[r['publisher_group']];assert np.array_equal(support['protected'],protected)
                    assert np.array_equal(mask,alpha>0)
                    primary,pmetrics=score_context(image,ref,support['alpha'],support['mask'],protected,controls)
                    secondary,dmetrics=score_context(image,ref,alpha,mask,protected,controls)
                    # Saved parent compatibility is checked on the original region ONLY.
                    old=saved_parent[case]
                    assert abs(old['input_RGB']-dmetrics['input']['RGB'])<=1e-10 and abs(old['input_DE']-dmetrics['input']['DE'])<=1e-10
                    anon=f'case-{len(public)+1:02}'
                    bit=hashlib.sha256((plan['protocol_id']+case).encode()).digest()[-1]&1
                    for name,data in [('A',primary if bit else image),('B',image if bit else primary),('R',ref)]:
                        assert cv2.imwrite(str(assets/(anon+'_'+name+'.png')),data[:,:,::-1])
                    assert cv2.imwrite(str(diagnostic/(anon+'.png')),secondary[:,:,::-1])
                    predictions.append(dict(case_id=case,review_id=anon,source=r['publisher_group'],role=r['experimental_role'],controls=controls,
                        leaf=tree.leaf_id(values),primary=pmetrics,fixed_diagnostic=dmetrics,output_panel='A' if bit else 'B',
                        parameter_absolute_error=[abs(a-b) for a,b in zip(controls,r['nominal_controls'])],
                        saved_parent_original_region=dict(output_RGB=old['output_RGB'],output_DE=old['output_DE'])))
                    public.append(dict(id=anon,kind='identity' if r['experimental_role']=='identity' else 'distorted',
                        A=f'review_assets/{anon}_A.png',B=f'review_assets/{anon}_B.png',R=None if r['experimental_role']=='identity' else f'review_assets/{anon}_R.png'))
                write(out/'predictions_PRIVATE.json',predictions)
        assert len(predictions)==44
        write(out/'review_public.json',dict(protocol_id=plan['protocol_id'],cases=public))
        write(out/'summary_PRIVATE.json',dict(attempted=48,available=44,excluded=4,primary=dict(by_role=aggregate(predictions,'primary')),
            fixed_diagnostic=dict(by_role=aggregate(predictions,'fixed_diagnostic')),visual_status='PENDING',model_ready=False))
        for name,h in plan['input_sha256'].items():assert sha(ROOT/name)==h
        write(out/'status_PRIVATE.json',dict(status='COMPLETED_PENDING_INDEPENDENT_VERIFICATION',new_fits=10,reused_fits=1,held_controls=44,renders=88))
    except BaseException as error:
        write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise

if __name__=='__main__':main()
