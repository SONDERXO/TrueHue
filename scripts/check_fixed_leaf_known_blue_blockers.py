"""Structural unchanged-output certificate from saved records. No leaf solve."""
from pathlib import Path
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    out=ROOT/'outputs/fixed_linear_leaf_known_blockers_v1'
    if out.exists():raise FileExistsError('Preserve certificate')
    source=ROOT/'outputs/blue_axis_source_held_comparison_v1';review=read(ROOT/'outputs/blue_axis_review_assessment_v1/assessment_PRIVATE.json')
    models={m['definition']['held_publisher_group']:m for m in read(source/'models_PRIVATE.json')};predictions=read(source/'predictions_PRIVATE.json');outcomes={r['review_id']:r for r in review['outcomes']}
    selected=[p for p in predictions if p['role']=='blue_increase' and outcomes[p['review_id']]['outcome']=='input_preferred'];assert {p['review_id'] for p in selected}=={'case-12','case-24','case-48'}
    inputfiles=['outputs/blue_axis_source_held_comparison_v1/models_PRIVATE.json','outputs/blue_axis_source_held_comparison_v1/predictions_PRIVATE.json','outputs/blue_axis_review_assessment_v1/assessment_PRIVATE.json','docs/linear-leaf-bounded-trial-decision-2026-11-14.md','src/model_training/linear_leaf_generated.py','src/model_training/portable_linear_leaf_tree.py','src/correction/seamless_blend.py','scripts/check_fixed_leaf_known_blue_blockers.py'];certificates=[]
    checked=read(source/'verification_PRIVATE.json')
    for p in selected:
        m=models[p['source']];folder=source/m['directory'];tree=read(folder/'candidate_PRIVATE.json');rows=read(folder/'fitting_inputs_PRIVATE.json');replay=read(folder/'training_replay_PRIVATE.json')
        for n in ['candidate_PRIVATE.json','fitting_inputs_PRIVATE.json','training_replay_PRIVATE.json']:
            rel=(folder/n).relative_to(source).as_posix();assert sha(folder/n)==checked['artifact_sha256'][rel];inputfiles.append((folder/n).relative_to(ROOT).as_posix())
        assert p['case_id'] in m['definition']['evaluation_cases'] and p['case_id'] not in m['definition']['fitting_cases']
        members=[r for r,leaf in zip(rows,replay['candidate_leaves']) if leaf==p['leaf']]
        assert len(members)==8 and all(r['role']=='blue_increase' and r['source']!=p['source'] for r in members)
        targets=np.asarray([r['y'] for r in members],float);mu=targets.mean(axis=0)
        assert np.all(targets==targets[0]) and np.all(targets-mu==0)
        assert mu.tolist()==p['controls']==tree['nodes'][p['leaf']]['values']
        scalar=[math.fsum(r['y'][j] for r in members)/8 for j in range(3)];assert scalar==mu.tolist()
        # No design matrix, ridge solve or new correction is evaluated. A zero
        # centered target gives zero RHS; positive ridge makes slope uniquely0.
        implied=[[mu[j].item(),0.,0.] for j in range(3)]
        assert [math.fsum(c) for c in implied]==p['controls']
        certificates.append(dict(review_id=p['review_id'],case_id=p['case_id'],source=p['source'],leaf=p['leaf'],fit_members=[r['case_id'] for r in members],constant_targets=mu.tolist(),centered_targets_exact_zero=True,
            mathematically_implied_affine_coefficients=implied,same_saved_controls_exact=True,byte_identical_output_if_same_input_support_renderer=True,prior_judgment=outcomes[p['review_id']]['raw_rating'],new_rating_needed=False))
    hashes={n:sha(ROOT/n) for n in inputfiles};out.mkdir()
    result=dict(status='FIXED_BRANCH_AFFINE_ROUTE_BLOCKED_BY_UNCHANGED_KNOWN_CONCERNS',certificates=certificates,conditions=['exact_saved_fold_branches_and_fitting_roster','fixed_ridge_affine_solver','same_input_support_renderer_reference_viewing_question_contract'],remaining_fold_fits_recommended=False,new_review_recommended=False,
        real_leaf_solves=0,branch_fits=0,new_candidate_predictions=0,new_renders=0,image_arrays_decoded=0,model_adopted=False,input_sha256=hashes)
    write(out/'certificate_PRIVATE.json',result);assert all(sha(ROOT/n)==h for n,h in hashes.items())
    write(out/'verification_PRIVATE.json',dict(passed=True,certificates=3,zero_target_means_numpy_and_scalar_agree=True,certificate_sha256=sha(out/'certificate_PRIVATE.json'),new_leaf_solves=0,new_renders=0,photo_arrays=0))
    print('PASS3unchanged-blue certificates; no additional leaf solves/predictions/renders. Remaining fixed-branch run not recommended.')
if __name__=='__main__':main()
