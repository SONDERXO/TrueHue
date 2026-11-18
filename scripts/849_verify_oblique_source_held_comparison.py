"""Post-run independent fitting, pixel and metric replay; zero refits."""
from pathlib import Path
import json,sys,math,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import cv2
from skimage.color import rgb2lab,deltaE_ciede2000
from src.model_training.oblique_comparison_workflow import load_verifier,sha,write,aggregate

def main():
    out=ROOT/'outputs/oblique_source_held_comparison_v1';dest=out/'independent_verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve existing verification')
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    execution=read(out/'execution_plan_PRIVATE.json');plan=execution['plan']
    for name,digest in plan['input_sha256'].items():assert sha(ROOT/name)==digest
    qa=read(ROOT/'outputs/oblique_comparison_workflow_readiness_v2/verification_PRIVATE.json')
    for name,digest in qa['input_sha256'].items():assert sha(ROOT/name)==digest
    prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
    rows={r['case_id']:r for r in read(prep/'rows_PRIVATE.json')}
    models=read(out/'models_PRIVATE.json');axes=read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json')
    verify=load_verifier(ROOT);routes=0
    for i,(model,axis) in enumerate(zip(models,axes)):
        assert model['definition']==axis['definition']==plan['folds'][i]
        records=[rows[c] for c in model['definition']['fitting_cases']]
        group=model['definition']['held_publisher_group']
        initial=read(out/group/'initial_PRIVATE.json')
        verify.verify_arrays(axis['tree'],initial,model['tree'],model['report'],
            [r['input_vector_float32'] for r in records],[r['nominal_controls'] for r in records],[r['experimental_role'] for r in records])
        routes+=len(records)
    assert len(models)==11 and sha(out/'reused_candidate_EXACT_PRIVATE.json')==plan['reuse_candidate']['sha256']
    predictions=read(out/'predictions_PRIVATE.json');assert len(predictions)==44
    assert {p['case_id'] for p in predictions}==set(rows)
    bygroup={m['definition']['held_publisher_group']:m for m in models}
    for p in predictions:
        r=rows[p['case_id']];path=Path(r['pixels_file'])
        assert path.resolve()==(prep/p['case_id']/'paired_pixels.npz').resolve() and sha(path)==r['pixels_sha256']
        model=bygroup[r['publisher_group']]
        assert p['case_id'] in model['definition']['evaluation_cases']
        _,controls=verify.predict(model['tree'],r['input_vector_float32']);assert controls==p['controls']
        with np.load(path,allow_pickle=False) as pack:
            image=pack['input_rgb8'];ref=pack['reference_rgb8'];alpha=pack['alpha'];mask=pack['scoring_mask']
            u=image.astype(np.float64)/255.;expected=np.empty_like(image)
            for j,gain in enumerate([controls[1],1.,controls[2]]):
                value=np.clip(np.power(u[:,:,j],controls[0])*gain,0.,1.)
                expected[:,:,j]=np.rint(255.*((1.-alpha)*u[:,:,j]+alpha*value)).astype(np.uint8)
            order=hashlib.sha256((plan['protocol_id']+p['case_id']).encode()).digest()[-1]&1
            assert p['output_panel']==('A' if order else 'B')
            asset=out/'review_assets'/p['review_id']
            actual=cv2.imread(str(asset)+'_'+p['output_panel']+'.png')[:,:,::-1]
            input_panel='B' if order else 'A'
            assert np.array_equal(cv2.imread(str(asset)+'_'+input_panel+'.png')[:,:,::-1],image)
            assert np.array_equal(cv2.imread(str(asset)+'_R.png')[:,:,::-1],ref)
            assert np.array_equal(actual,expected)
            assert np.array_equal(actual[pack['protected']],image[pack['protected']]) and np.array_equal(actual[alpha==0],image[alpha==0])
            for prefix,data in [('input',image),('output',actual)]:
                rgb=float(np.abs(data[mask].astype(float)-ref[mask]).mean())
                de=float(deltaE_ciede2000(rgb2lab(data[mask]/255.),rgb2lab(ref[mask]/255.)).mean())
                for key,value in [('RGB',rgb),('DE',de)]:assert math.isclose(value,p[prefix][key],abs_tol=1e-10,rel_tol=1e-10)
    assert aggregate(predictions)==read(out/'summary_PRIVATE.json')['by_role']
    write(dest,dict(passed=True,fitting_routes=routes,held_routes=44,pixel_metric_replays=44,
        refits=0,visual_assessment='PENDING',model_ready=False,
        artifact_sha256={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}))
    print('Independent fitting/held-render/metric replay PASS; visual review still required')

if __name__=='__main__':main()
