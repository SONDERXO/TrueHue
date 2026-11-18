"""One exact existing-data adapter; no training or pixels on import."""
import math
import platform
from pathlib import Path
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
from direct_control_ridge_workflow import ROOT,read,write,sha,fit_and_seal
from direct_control_ridge_verify import close
from src.model_training.luminance_chroma_operator import render_rgb8
from src.evaluation.luminance_chroma_scalar import replay
from src.evaluation.directional_recoverability import metrics,regions

ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']


def main():
    parent=ROOT/'outputs/wb_feature_direct_prediction_v1'
    out=ROOT/'outputs/direct_control_ridge_prediction_v1'
    design=ROOT/'outputs/direct_control_ridge_design_v1'
    if out.exists() or design.exists():raise FileExistsError('Preserve existing attempt')
    qa_path=ROOT/'outputs/direct_control_ridge_generated_v1/verification.json';qa=read(qa_path)
    assert qa['passed'] and qa['main_models']==11 and qa['independent_scalar_renders']==66
    assert qa['versions']==dict(python=platform.python_version(),numpy=np.__version__)
    for path,h in qa['code_sha256'].items():assert sha(ROOT/path)==h,path
    old=read(parent/'verification.json');assert old['passed'] and old['real_tree_fits']==22
    manifest={p.replace('\\','/'):h for p,h in old['artifacts'].items()}
    required=['plan.json','rows.json','records.json','summary.json','held_controls_sealed.json']
    bindings={str(qa_path.relative_to(ROOT)):sha(qa_path),str((parent/'verification.json').relative_to(ROOT)):sha(parent/'verification.json')}
    for path in required:
        assert sha(parent/path)==manifest[path],path
        bindings[str((parent/path).relative_to(ROOT))]=manifest[path]
    original_plan=read(parent/'plan.json');raw=read(parent/'rows.json')
    rows=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x314','y']} for r in raw]
    assert len(rows)==66 and all(r['generated_fixture'] is False for r in rows)
    original={r['case_id']:r for r in original_plan['rows']}
    for r in rows:
        a=original[r['case_id']]
        assert all(r[k]==a[k] for k in ['case_id','source_id','role','y'])
        assert r['case_id']=='camera_halfstop_ffhq_'+r['source_id']+'__'+r['role']
        path='evaluation/'+r['case_id']+'.npz'
        assert sha(parent/path)==manifest[path]
        bindings[str((parent/path).relative_to(ROOT))]=manifest[path]
    for p in ['scripts/run_direct_control_ridge_real.py','docs/direct-control-ridge-protocol-2026-11-16.md']:
        bindings[p]=sha(ROOT/p)
    plan=dict(folds=original_plan['folds'],generated_fixture=False,dimensions=314,alpha=1.0,
              target_names=original_plan['target_names'],model_ready=False,
              role='exposed_development_research_not_paper_adoption')
    design.mkdir();write(design/'bindings.json',bindings);write(design/'plan.json',plan)
    write(design/'pre_execution.json',dict(exact_rows=66,source_held_folds=11,maximum_new_fits=11,
          parent_verified=True,generated_qa_pass=True,portrait_arrays_decoded=0,
          paper_alignment='pages63/65 goal retained; different final learner is an authorized research amendment'))
    # All eleven model proofs and all66prediction seal precede any array decode.
    access=[]
    try:
        sealed=fit_and_seal(plan,rows,out)
        write(out/'bindings.json',bindings)
        seal=read(out/'prediction_seal.json');assert sha(out/'held_controls_sealed.json')==seal['sha256']
        (out/'evaluation').mkdir();scores=[]
        old_scores={r['case_id']:r for r in read(parent/'records.json')}
        by_id={r['case_id']:r for r in rows}
        for idx,p in enumerate(sealed):
            source=parent/'evaluation'/(p['case_id']+'.npz')
            with np.load(source,allow_pickle=False) as pack:
                a={k:pack[k].copy() for k in ['input','reference','alpha','protected','314','constant']}
            access.append(dict(case_id=p['case_id'],keys=list(a),stage='after_all_fits_verified_and_66_controls_sealed'))
            image,ref,alpha,protected=[a[k] for k in ['input','reference','alpha','protected']]
            output=render_rgb8(image,alpha,protected,p['controls'])
            scalar,_=replay(image,ref,alpha,protected,p['controls'])
            assert np.array_equal(output,scalar)
            assert np.array_equal(output[alpha==0],image[alpha==0]) and np.array_equal(output[protected],image[protected])
            all_outputs=dict(input=image,constant=a['constant'],saved314=a['314'],ridge=output)
            scored={name:{label:metrics(value,ref,mask) for label,value in all_outputs.items()} for name,mask in regions(alpha).items()}
            # Independent scalar aggregation, using the standard CIE implementation.
            ref_lab=rgb2lab(ref/255.)
            for label,value in all_outputs.items():
                rgb=np.abs(value.astype(float)-ref);de=deltaE_ciede2000(rgb2lab(value/255.),ref_lab)
                for name,mask in regions(alpha).items():
                    if mask.any():
                        close(scored[name][label]['RGB'],math.fsum(float(v) for v in rgb[mask].flat)/(3*int(mask.sum())),1e-10)
                        close(scored[name][label]['DE'],math.fsum(float(v) for v in de[mask])/int(mask.sum()),1e-10)
                    else:assert scored[name][label] is None
                    if label!='ridge' and mask.any():
                        old_label='314' if label=='saved314' else label
                        for metric in ['RGB','DE']:close(scored[name][label][metric],old_scores[p['case_id']]['regions'][name][old_label][metric],1e-10)
            record={k:p[k] for k in ['case_id','source_id','role']}|dict(regions=scored,
                     controls=p['controls'],parameter_MAE=[abs(x-y) for x,y in zip(p['controls'],by_id[p['case_id']]['y'])],
                     changed_pixels=int(np.any(output!=image,axis=2).sum()))
            scores.append(record)
            np.savez(out/'evaluation'/(p['case_id']+'.npz'),input=image,reference=ref,alpha=alpha,protected=protected,ridge=output)
            if (idx+1)%11==0:print('Candidate scalar render/metrics verified '+str(idx+1)+'/66',flush=True)
        write(out/'records.json',scores);write(out/'access.json',access)
        means={role:{label:{m:math.fsum(r['regions']['primary'][label][m] for r in scores if r['role']==role)/11
                            for m in ['RGB','DE']} for label in ['input','constant','saved314','ridge']} for role in ROLES}
        gates={role:all(means[role]['ridge'][m]<means[role][b][m]-1e-10 for m in ['RGB','DE'] for b in ['input','constant']) for role in ROLES[1:]}
        exposure_gain=all(means['exposure_under']['ridge'][m]<means['exposure_under']['saved314'][m]-1e-10 for m in ['RGB','DE'])
        colour_preserved=all(means['colour_only']['ridge'][m]<=means['colour_only']['saved314'][m]+1e-10 for m in ['RGB','DE'])
        eligible=all(gates.values()) and exposure_gain and colour_preserved
        report=dict(by_role=means,role_gates=gates,under_improvement=exposure_gain,colour_nonworse=colour_preserved,
                    numerical_eligible=eligible,model_ready=False,human_review='NOT_REQUESTED',
                    identity_changed=sum(r['changed_pixels']>0 for r in scores if r['role']=='identity'),
                    case_regressions=[r['case_id'] for r in scores if r['role']!='identity' and any(r['regions']['primary']['ridge'][m]>r['regions']['primary']['input'][m]+1e-10 for m in ['RGB','DE'])],
                    parameter_MAE_by_role={role:[math.fsum(r['parameter_MAE'][j] for r in scores if r['role']==role)/11 for j in range(5)] for role in ROLES})
        write(out/'summary.json',report)
        for path,h in bindings.items():assert sha(ROOT/path)==h,path
        assert sha(out/'held_controls_sealed.json')==seal['sha256']
        proof=dict(passed=True,real_fits=11,scalar_fitting_predictions=660,held_predictions=66,
                   scalar_render_metric_checks=66,parameter_target_joins=66,existing_rows_preserved=True,
                   baseline_refits=0,new_features=0,target_fits=0,numerical_eligible=eligible)
        write(out/'verification.json',proof)
        print(report);print(proof)
    except Exception as exc:
        if out.exists():write(out/'execution_failure.json',dict(error=str(exc),array_access=access))
        raise


if __name__=='__main__':main()
