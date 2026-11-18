"""Magnitude audit of saved66 reviewed outputs; never render a correction."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,math
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    source=ROOT/'outputs/blue_axis_source_held_comparison_v1';out=ROOT/'outputs/reviewed_correction_magnitude_v1'
    if out.exists():raise FileExistsError('Preserve audit')
    verified=read(source/'verification_PRIVATE.json');predictions=read(source/'predictions_PRIVATE.json');assert len(predictions)==66
    prep={r['case_id']:r for r in read(ROOT/'outputs/blue_axis_preparation_v1/rows_PRIVATE.json')};design=read(ROOT/'outputs/blue_axis_source_held_design_v1/plan_PRIVATE.json');supports={s['source']:s for s in design['support_sources']}
    bindings={};alphas={}
    def bound(rel):
        path=source/rel;assert sha(path)==verified['artifact_sha256'][rel];bindings[rel]=sha(path);return path
    for name,s in supports.items():
        a=np.load(bound('supports/'+s['source_id']+'/alpha.npy'),allow_pickle=False);assert a.shape==(256,256) and np.isfinite(a).all() and a.min()>=0 and a.max()<=1;alphas[name]=a
    rows=[]
    for p in predictions:
        ident=p['review_id'];panels={k:cv2.imread(str(bound(f'review_assets/{ident}_{k}.png')))[:,:,::-1].copy() for k in ['A','B','R']}
        image=panels['B' if p['output_panel']=='A' else 'A'];output=panels[p['output_panel']];ref=panels['R'];alpha=alphas[p['source']]
        assert image.shape==output.shape==ref.shape==(256,256,3)
        masks=dict(primary=alpha>0,core=alpha==1,feather=(alpha>0)&(alpha<1),outside=alpha==0,whole=np.ones((256,256),bool))
        change=np.abs(output.astype(float)-image.astype(float));observed={}
        for label,m in masks.items():
            n=int(m.sum());observed[label]=dict(pixels=n,mean_absolute_RGB_change=float(change[m].mean()) if n else None,perchannel_mean_change=change[m].mean(axis=0).tolist() if n else None,changed_pixels=int(np.any(change[m]>0,axis=1).sum()) if n else 0)
        assert observed['outside']['changed_pixels']==0
        primary=masks['primary'];a=float(np.abs(image[primary].astype(float)-ref[primary]).mean());b=float(np.abs(output[primary].astype(float)-ref[primary]).mean())
        assert math.isclose(a,p['primary']['input']['RGB'],abs_tol=1e-10,rel_tol=1e-10) and math.isclose(b,p['primary']['output']['RGB'],abs_tol=1e-10,rel_tol=1e-10)
        assert math.isclose(observed['whole']['mean_absolute_RGB_change'],observed['primary']['mean_absolute_RGB_change']*observed['primary']['pixels']/65536,abs_tol=1e-10,rel_tol=1e-10)
        rows.append(dict(case_id=p['case_id'],review_id=ident,source=p['source'],role=p['role'],controls=p['controls'],nominal_controls=prep[p['case_id']]['y'],nominal_control_agreement=all(abs(v-w)<=1e-12 for v,w in zip(p['controls'],prep[p['case_id']]['y'])),
            regions=observed,primary_fraction=observed['primary']['pixels']/65536,core_fraction=observed['core']['pixels']/65536,feather_fraction=observed['feather']['pixels']/65536,mean_alpha_whole=float(alpha.mean()),mean_alpha_primary=float(alpha[primary].mean()),input_RGB_error=a,output_RGB_error=b))
    summary={}
    for role in sorted({r['role'] for r in rows}):
        rs=[r for r in rows if r['role']==role];assert len(rs)==len({r['source'] for r in rs})==11
        summary[role]=dict(cases=11,sources=11,nominal_controls=sum(r['nominal_control_agreement'] for r in rs),primary_mean_RGB_change=math.fsum(r['regions']['primary']['mean_absolute_RGB_change'] for r in rs)/11,
            core_mean_RGB_change=math.fsum(r['regions']['core']['mean_absolute_RGB_change'] for r in rs)/11,feather_mean_RGB_change=math.fsum(r['regions']['feather']['mean_absolute_RGB_change'] for r in rs)/11,
            whole_mean_RGB_change=math.fsum(r['regions']['whole']['mean_absolute_RGB_change'] for r in rs)/11,input_primary_RGB_error=math.fsum(r['input_RGB_error'] for r in rs)/11,output_primary_RGB_error=math.fsum(r['output_RGB_error'] for r in rs)/11)
    source_rows=[r for r in rows if r['role']=='identity'];geometry=dict(primary_fraction_range=[min(r['primary_fraction'] for r in source_rows),max(r['primary_fraction'] for r in source_rows)],mean_primary_fraction=math.fsum(r['primary_fraction'] for r in source_rows)/11,mean_core_fraction=math.fsum(r['core_fraction'] for r in source_rows)/11,mean_feather_fraction=math.fsum(r['feather_fraction'] for r in source_rows)/11,mean_primary_alpha=math.fsum(r['mean_alpha_primary'] for r in source_rows)/11)
    result=dict(passed=True,reviewed_cases=66,prior_exposure_cases_carried=22,scope='current66review includes broad feedback; earlierhistoricalassessmentsunchanged',families=summary,geometry=geometry,cases=rows,source_hashes=bindings,
        pure_colour_factors=[245/255,255/245],single_channel_nominal_percent_changes=[100*(245/255-1),100*(255/245-1)],primary_RGB_replays=66,alpha0_invariance_checks=66,new_correction_renders=0,new_fits=0,new_predictions=0,new_ratings=0,model_adopted=False)
    assert all(sha(source/n)==h for n,h in bindings.items());out.mkdir();write(out/'results_PRIVATE.json',result);write(out/'verification_PRIVATE.json',dict(passed=True,results_sha256=sha(out/'results_PRIVATE.json'),source_hashes_unchanged=True,RGB_replays=66,alpha_arrays=11,PNG_panels=198,no_new_model_or_renderer_run=True))
    print(json.dumps(dict(families=summary,geometry=geometry),indent=2))
if __name__=='__main__':main()
