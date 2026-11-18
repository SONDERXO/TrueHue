"""Fixedp6 scene-descriptor readiness;44 cached images, zero model fits."""
from pathlib import Path
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'outputs/bright_scene_cue_design_v1'
P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
OUT=ROOT/'outputs/bright_scene_cue_readiness_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')

def main():
    if OUT.exists():raise FileExistsError('Preserve readiness screen')
    plan=read(D/'plan_PRIVATE.json');bound=dict(plan['input_sha256']);bound[str(D/'plan_PRIVATE.json')]=sha(D/'plan_PRIVATE.json');bound[str(Path(__file__))]=sha(__file__)
    assert all(sha(p)==h for p,h in bound.items());rows=read(P/'rows_PRIVATE.json');assert len(rows)==44
    OUT.mkdir();records=[]
    for r in rows:
        assert sha(r['pixels_file'])==r['pixels_sha256'];bound[r['pixels_file']]=r['pixels_sha256']
        with np.load(r['pixels_file'],allow_pickle=False) as pack:
            image=pack['input_rgb8'];assert image.shape==(256,256,3)
            mean=image.reshape(-1,3).mean(axis=0);p6=np.mean((image.astype(float)/255.)**6,axis=(0,1))**(1/6)*255
            additions=dict(zip(plan['feature_names'],[float(np.log((p6[0]+1)/(p6[1]+1))),float(np.log((p6[2]+1)/(p6[1]+1)))]))
            p1=[float(np.log((mean[0]+1)/(mean[1]+1))),float(np.log((mean[2]+1)/(mean[1]+1)))]
            np.testing.assert_allclose(p1,[r['features']['scene_log_r_over_g'],r['features']['scene_log_b_over_g']],rtol=1e-12,atol=1e-12)
            records.append(dict(case_id=r['case_id'],group=r['publisher_group'],role=r['experimental_role'],p6_channel_means_codes=p6.tolist(),new_features=additions,first_moment_ratios=p1,input_vector_float32_18=r['input_vector_float32']+np.asarray(list(additions.values()),np.float32).tolist(),any_zero_fraction=float(np.any(image==0,axis=2).mean()),any_full_fraction=float(np.any(image==255,axis=2).mean()),training_admitted=False,calibration_admitted=False))
    indexed={(r['group'],r['role']):r for r in records};pairs=[];oldnames=['scene_log_r_over_g','scene_log_b_over_g']
    for group in sorted({r['group'] for r in records}):
        normal=indexed[group,'identity']
        for role in ['exposure_under','exposure_over','colour_cool']:
            changed=indexed[group,role]
            pairs.append(dict(group=group,role=role,new_delta=[changed['new_features'][k]-normal['new_features'][k] for k in plan['feature_names']],old_delta=[a-b for a,b in zip(changed['first_moment_ratios'],normal['first_moment_ratios'])]))
    originals=[r for r in records if r['role']=='identity'];dispersion={}
    for axis,newname,oldname in zip(range(2),plan['feature_names'],oldnames):
        old=[r['first_moment_ratios'][axis] for r in originals];new=[r['new_features'][newname] for r in originals]
        dispersion[newname]=dict(original_sd=float(np.std(new)),original_min=min(new),original_max=max(new),old_original_sd=float(np.std(old)),old_original_min=min(old),old_original_max=max(old),mean_cool_shift=float(np.mean([r['new_delta'][axis] for r in pairs if r['role']=='colour_cool'])),mean_old_cool_shift=float(np.mean([r['old_delta'][axis] for r in pairs if r['role']=='colour_cool'])))
    ranges={}
    for role in ['identity','exposure_under','exposure_over','colour_cool']:
        own=[r for r in records if r['role']==role];ranges[role]={k:[min(r['new_features'][k] for r in own),max(r['new_features'][k] for r in own)] for k in plan['feature_names']}
    summary=dict(rows=44,added_feature_values=88,preserved_parent_feature_values=704,pairs=33,all_finite=all(np.isfinite(list(r['new_features'].values())).all() for r in records),cool_red_decreases=sum(r['new_delta'][0]<0 for r in pairs if r['role']=='colour_cool'),cool_blue_unchanged=sum(r['new_delta'][1]==0 for r in pairs if r['role']=='colour_cool'),original_dispersion=dispersion,role_marginal_ranges=ranges,new_fits=0,new_predictions=0,original_photo_reads=0,image_model_calls=0,holdout_reads=0)
    write(OUT/'records_PRIVATE.json',records);write(OUT/'pairs_PRIVATE.json',pairs);write(OUT/'summary_PRIVATE.json',summary);write(OUT/'input_sha256_PRIVATE.json',bound)
    assert all(sha(p)==h for p,h in bound.items());print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
