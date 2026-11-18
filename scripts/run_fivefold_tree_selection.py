"""Execute exactly the approved231-fit study on bound existing features."""
import numpy as np
from fivefold_tree_workflow import ROOT,read,write,sha,run_nested
from fivefold_tree_verify import verify_outer,close
from joint_cue_tree_workflow import score
from check_fivefold_tree_selection_generated import versions


def main():
    design=ROOT/'outputs/joint_cue_tree_design_v1'
    proposal=ROOT/'outputs/fivefold_tree_selection_proposal_v1'
    out=ROOT/'outputs/fivefold_tree_selection_prediction_v1'
    execution=proposal/'execution_bindings.json'
    if out.exists() or execution.exists():raise FileExistsError('Preserve prior attempt')
    allocation=read(proposal/'allocation.json');assert allocation['maximum_total_fits']==231 and allocation['executed_fits']==0
    authorization=read(proposal/'user_authorization.json');assert authorization['exact_answer']=='Approve the fivefold selection study'
    join=read(design/'verification.json');assert join['passed'] and join['scalar_join_values']==291060
    assert sha(design/'rows.json')==join['rows_sha256']==allocation['rows_sha256']
    assert sha(design/'plan.json')==join['plan_sha256']
    qa_path=ROOT/'outputs/fivefold_tree_selection_generated_v1/verification.json';qa=read(qa_path)
    assert qa['passed'] and qa['fits']==231 and qa['scalar_pixel_checks']==66 and qa['versions']==versions()
    bindings=read(design/'bindings.json')|qa['code_sha256']
    for p in [proposal/'allocation.json',proposal/'user_authorization.json',design/'verification.json',design/'rows.json',design/'plan.json',qa_path]:bindings[str(p.relative_to(ROOT))]=sha(p)
    for p,h in bindings.items():assert sha(ROOT/p)==h,p
    rows=read(design/'rows.json');assert all(r['generated_fixture'] is False for r in rows)
    # Exact outer allocations must still equal the original source-held design.
    for old,new in zip(read(design/'plan.json')['folds'],allocation['outer_folds']):
        assert old['held_source_id']==new['held_source_id']
        assert old['fitting_cases']==new['outer_fitting_cases'] and old['evaluation_cases']==new['outer_evaluation_cases']
    write(execution,dict(sha256=bindings,versions=versions(),portrait_arrays_decoded=0,maximum_fits=231))
    parent=ROOT/'outputs/wb_feature_direct_prediction_v1'
    old_scores={r['case_id']:r for r in read(parent/'records.json')}
    old_controls={r['case_id']:r for r in read(parent/'held_controls_sealed.json')};access=[]
    try:
        selections=run_nested(allocation,rows,out)
        outer_proof=verify_outer(out,rows,allocation);write(out/'outer_verification.json',outer_proof)
        write(out/'bindings.json',bindings)
        def loader(row,p):
            assert (out/'selection_verified.json').exists() and (out/'outer_verification.json').exists()
            assert (out/'prediction_seal.json').exists()
            for a,b in zip(p['constant'],old_controls[row['case_id']]['constant']):close(a,b)
            path=parent/'evaluation'/(row['case_id']+'.npz')
            with np.load(path,allow_pickle=False) as pack:
                a={k:pack[k].copy() for k in ['input','reference','alpha','protected','314','constant']}
            access.append(dict(case_id=row['case_id'],keys=list(a),stage='after231fits_selection_proofs_and66sealed_controls'))
            a['saved314']=a.pop('314');a['parent_scores']=old_scores[row['case_id']]['regions']
            return a
        summary=score(rows,out,loader)
        for p,h in bindings.items():assert sha(ROOT/p)==h,p
        write(out/'access.json',access)
        proof=dict(passed=True,real_fits=231,inner_fits=220,selected_outer_fits=11,
             inner_fit_routes=10560,inner_validation_routes=2640,outer_fit_routes=660,outer_held_routes=66,
             scalar_pixel_metric_checks=66,selected_depths={s['held_source_id']:s['depth'] for s in selections},
             encoder_runs=0,feature_recomputations=0,target_fits=0,baseline_refits=0,
             numerical_eligible=summary['numerical_eligible'],model_ready=False)
        write(out/'verification.json',proof);print(summary);print(proof)
    except Exception as exc:
        if out.exists():write(out/'execution_failure.json',dict(error=str(exc),array_access=access))
        raise


if __name__=='__main__':main()
