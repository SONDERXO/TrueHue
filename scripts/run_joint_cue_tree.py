"""Single actual4410-feature tree assessment on already cached camera cases."""
import numpy as np
from joint_cue_tree_workflow import ROOT,read,write,sha,fit_and_seal,score,close
from check_joint_cue_tree_generated import versions


def main():
    design=ROOT/'outputs/joint_cue_tree_design_v1';out=ROOT/'outputs/joint_cue_tree_prediction_v1'
    if out.exists() or (design/'execution_bindings.json').exists():raise FileExistsError('Attempt already exists')
    check=read(design/'verification.json');assert check['passed'] and check['scalar_join_values']==291060
    assert sha(design/'rows.json')==check['rows_sha256'] and sha(design/'plan.json')==check['plan_sha256']
    qa_path=ROOT/'outputs/joint_cue_tree_generated_v1/verification.json';qa=read(qa_path)
    assert qa['passed'] and qa['fits']==11 and qa['scalar_pixel_checks']==66 and qa['versions']==versions()
    bindings=read(design/'bindings.json')|qa['code_sha256']
    for p in [design/'verification.json',design/'rows.json',design/'plan.json',qa_path]:bindings[str(p.relative_to(ROOT))]=sha(p)
    for p,h in bindings.items():assert sha(ROOT/p)==h,p
    write(design/'execution_bindings.json',dict(sha256=bindings,versions=versions(),arrays_decoded=0))
    plan=read(design/'plan.json');rows=read(design/'rows.json')
    parent=ROOT/'outputs/wb_feature_direct_prediction_v1'
    old_scores={r['case_id']:r for r in read(parent/'records.json')}
    old_controls={r['case_id']:r for r in read(parent/'held_controls_sealed.json')}
    access=[]
    try:
        fit_and_seal(plan,rows,out)
        write(out/'bindings.json',bindings)
        def loader(row,p):
            for a,b in zip(p['constant'],old_controls[row['case_id']]['constant']):close(a,b,1e-12)
            path=parent/'evaluation'/(row['case_id']+'.npz')
            with np.load(path,allow_pickle=False) as pack:
                a={k:pack[k].copy() for k in ['input','reference','alpha','protected','314','constant']}
            access.append(dict(case_id=row['case_id'],keys=list(a),stage='after11verifiedfits_and66sealed_controls'))
            a['saved314']=a.pop('314');a['parent_scores']=old_scores[row['case_id']]['regions']
            return a
        summary=score(rows,out,loader)
        for p,h in bindings.items():assert sha(ROOT/p)==h,p
        write(out/'access.json',access)
        report=dict(passed=True,real_fits=11,fitting_routes=660,held_routes=66,scalar_pixel_metric_checks=66,
                    feature_recomputations=0,encoder_runs=0,target_fits=0,baseline_refits=0,
                    numerical_eligible=summary['numerical_eligible'],model_ready=False)
        write(out/'verification.json',report)
        print(summary);print(report)
    except Exception as exc:
        if out.exists():write(out/'execution_failure.json',dict(error=str(exc),array_access=access))
        raise


if __name__=='__main__':main()
