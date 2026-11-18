"""Independent channelwise nominal/bound replay; no optimizers or learners."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/correction_training_target_audit_v1';P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    dest=O/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    assert all(sha(p)==h for p,h in read(O/'input_sha256_PRIVATE.json').items())
    rows={r['case_id']:r for r in read(P/'rows_PRIVATE.json')};records=read(O/'rows_PRIVATE.json');summary=read(O/'summary_PRIVATE.json')
    def close(a,b):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(a,b)
    for r in records:
        row=rows[r['case_id']];q=row['recipe'];expected=[1/q['gamma'],math.pow(q['red_gain'],-1/q['gamma']),math.pow(q['blue_gain'],-1/q['gamma'])]
        for a,b in zip(expected,r['nominal_controls']):close(a,b)
        with np.load(row['pixels_file'],allow_pickle=False) as z:
            im=z['input_rgb8'];ref=z['reference_rgb8'];alpha=z['alpha'];mask=z['scoring_mask'];protected=z['protected'];out=np.empty_like(im);unmixed=np.empty_like(im);lower=np.empty(im.shape,float);upper=np.empty(im.shape,float)
            for c,gain in enumerate([expected[1],1.,expected[2]]):
                u=im[:,:,c]/255.;corrected=np.minimum(1.,np.maximum(0.,np.power(u,expected[0])*gain))
                unmixed[:,:,c]=np.rint(corrected*255).astype(np.uint8)
                out[:,:,c]=np.rint(255*(u*(1-alpha)+corrected*alpha)).astype(np.uint8)
                lower[:,:,c]=np.rint(255*u*(1-alpha));upper[:,:,c]=np.rint(255*(u*(1-alpha)+alpha))
            n=int(mask.sum())*3
            error=np.abs(out.astype(float)-ref.astype(float));unerror=np.abs(unmixed.astype(float)-ref.astype(float));floor=np.maximum(np.maximum(lower-ref.astype(float),ref.astype(float)-upper),0)
            close(math.fsum(error[mask].flat)/n,r['blended_nominal_RGB']);close(math.fsum(unerror[mask].flat)/n,r['unblended_nominal_RGB']);close(math.fsum(floor[mask].flat)/n,r['interval_relaxation_RGB_lower_bound'])
            close(float(deltaE_ciede2000(rgb2lab(out[mask]/255.),rgb2lab(ref[mask]/255.)).mean()),r['blended_nominal_DE'])
            assert np.all(error>=floor) and int(np.count_nonzero(floor[mask]))==r['unreachable_target_channels']
            assert np.array_equal(out[protected],im[protected]) and np.array_equal(out[alpha==0],im[alpha==0])
            if r['role']=='identity':np.testing.assert_array_equal(out,im)
    for role,m in summary['by_role'].items():
        own=[r for r in records if r['role']==role];assert len(own)==m['cases']==11
        for k in ['input_RGB','unblended_nominal_RGB','blended_nominal_RGB','blended_nominal_DE','interval_relaxation_RGB_lower_bound','saved_tree_RGB','saved_tree_DE']:close(sum(r[k] for r in own)/11,m[k])
    assert summary['coverage']['distinct_blue_targets']==[1.] and summary['coverage']['combined_cases']==0
    dest.write_text(json.dumps(dict(passed=True,nominal_controls_checked=44,channelwise_render_and_interval_bound_replays=44,metric_replays=44,role_aggregate_checks=4,new_fits=0,original_photo_reads=0,image_model_calls=0,holdout_reads=0,summary_sha256=sha(O/'summary_PRIVATE.json'),verifier_sha256=sha(__file__)),indent=2)+'\n')
    print(dest.read_text())

if __name__=='__main__':main()
