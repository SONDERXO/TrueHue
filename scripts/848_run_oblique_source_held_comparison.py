"""One fixed development comparison. Explicit CLI execution only."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.oblique_comparison_workflow import *

def main():
    if sys.argv[1:]!=['--execute-fixed-development']:raise SystemExit('Explicit --execute-fixed-development required')
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    engineering=ROOT/'outputs/oblique_comparison_workflow_readiness_v2/verification_PRIVATE.json'
    qa=read(engineering);assert qa['passed']
    for name,digest in qa['input_sha256'].items():assert sha(ROOT/name)==digest
    plan=read(ROOT/'outputs/oblique_source_held_comparison_design_v1/plan_PRIVATE.json')
    for name,digest in plan['input_sha256'].items():assert sha(ROOT/name)==digest
    out=ROOT/'outputs/oblique_source_held_comparison_v1'
    if out.exists():raise FileExistsError('Preserve attempt; no restart')
    out.mkdir();write(out/'execution_plan_PRIVATE.json',dict(plan=plan,engineering_sha256=sha(engineering)))
    try:
        prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
        records={r['case_id']:r for r in read(prep/'rows_PRIVATE.json')}
        assert set(records)=={c for f in plan['folds'] for c in f['evaluation_cases']}
        # Read metadata provenance, never blindly hash every receipt path (some are images).
        provenance=read(prep/'verification_PRIVATE.json')
        assert provenance['passed']
        for name,digest in provenance['input_sha256'].items():
            path=Path(name)
            # Only the explicitly recorded metadata/code provenance; never images.
            assert path.suffix in ('.json','.py') and path.resolve().is_relative_to(ROOT.resolve())
            assert sha(path)==digest
        write(out/'preparation_provenance_PRIVATE.json',provenance)
        axes=read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json')
        feasibility=ROOT/'outputs/oblique_training_feasibility_v1'
        source=feasibility/'candidate_PRIVATE.json';assert sha(source)==plan['reuse_candidate']['sha256']
        models=fit_all(out,plan['folds'],axes,records,read(source),read(feasibility/'optimization_PRIVATE.json'),load_verifier(ROOT).verify_arrays)
        # Exact source bytes retained independently of JSON reserialization.
        (out/'reused_candidate_EXACT_PRIVATE.json').write_bytes(source.read_bytes())
        assert sha(out/'reused_candidate_EXACT_PRIVATE.json')==sha(source)
        assert len(models)==11 and read(out/'all_fits_verified_PRIVATE.json')['passed']
        import cv2
        predictions=[];review=[]
        assets=out/'review_assets';assets.mkdir()
        for model in models:
            tree=PortableObliqueTree(model['tree'])
            for case in model['definition']['evaluation_cases']:
                r=records[case];path=Path(r['pixels_file'])
                allowed=(prep/case/'paired_pixels.npz').resolve()
                assert path.resolve()==allowed and path.suffix=='.npz'
                assert sha(path)==r['pixels_sha256']
                with np.load(path,allow_pickle=False) as pack:
                    image=pack['input_rgb8'];ref=pack['reference_rgb8'];alpha=pack['alpha'];mask=pack['scoring_mask'];protected=pack['protected']
                    controls=tree.predict_one(r['input_vector_float32']);output=render(image,alpha,controls)
                    assert np.array_equal(output,replay_render(image,alpha,controls))
                    assert np.array_equal(output[protected],image[protected]) and np.array_equal(output[alpha==0],image[alpha==0])
                    folder=out/case;folder.mkdir()
                    order=hashlib.sha256((plan['protocol_id']+case).encode()).digest()[-1]&1
                    anonymous=f'case-{len(review)+1:02}'
                    for name,array in [('A',output if order else image),('B',image if order else output),('R',ref)]:
                        assert cv2.imwrite(str(assets/(anonymous+'_'+name+'.png')),array[:,:,::-1])
                    predictions.append(dict(case_id=case,source=r['publisher_group'],role=r['experimental_role'],controls=controls,
                        input=measure(image,ref,mask),output=measure(output,ref,mask),
                        changed_pixels=int(np.any(output!=image,axis=2).sum()),protected_unchanged=True,zero_alpha_unchanged=True,
                        output_panel='A' if order else 'B',review_id=anonymous,pixel_sha256=r['pixels_sha256']))
                    review.append(dict(id=anonymous,kind='identity' if r['experimental_role']=='identity' else 'distorted',
                        A='review_assets/'+anonymous+'_A.png',B='review_assets/'+anonymous+'_B.png',
                        R=None if r['experimental_role']=='identity' else 'review_assets/'+anonymous+'_R.png'))
                write(out/'predictions_PRIVATE.json',predictions)
        write(out/'review_public.json',dict(protocol_id=plan['protocol_id'],cases=review))
        write(out/'summary_PRIVATE.json',dict(attempted=48,available=44,excluded=4,by_role=aggregate(predictions),visual_status='PENDING',model_ready=False))
        write(out/'status_PRIVATE.json',dict(status='NUMERICAL_RUN_COMPLETE_VISUAL_PENDING',new_fits=10,reused_fits=1))
    except BaseException as error:
        write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise

if __name__=='__main__':main()
