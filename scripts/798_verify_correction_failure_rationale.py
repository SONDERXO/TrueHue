"""Independent saved-loss budget and path-support checks; no refit/prediction."""
from pathlib import Path
from collections import Counter
import hashlib,json,math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/correction_failure_rationale_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    bound=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    summary=read(OUT/'summary_PRIVATE.json');losses=read(OUT/'saved_training_losses_PRIVATE.json');contexts=read(OUT/'held_leaf_contexts_PRIVATE.json')
    rows={r['case_id']:r for r in read(ROOT/'outputs/source_matched_restoration_preparation_v1/combined_rows_PRIVATE.json')}
    models=read(ROOT/'outputs/source_matched_restoration_comparison_v1/models_PRIVATE.json')
    assert len(losses)==168 and len(contexts)==35
    close=lambda a,b:math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-11)
    for r in losses:
        original=rows[r['case_id']];assert close(r['identity_cost'],original['action_costs'][0])
        assert close(r['selected_cost'],original['action_costs'][r['chosen_action']])
        assert close(r['oracle_cost'],min(original['action_costs']))
        if r['role']=='identity':assert r['selected_cost']==0
    total=0;gains={}
    for role,m in summary['training_loss_budgets'].items():
        own=[r for r in losses if r['role']==role];assert len(own)==m['appearances']==42
        assert len({r['case_id'] for r in own})==m['unique_images']==7
        gain=sum(r['identity_cost']-r['oracle_cost'] for r in own);assert close(gain,m['total_available_absolute_reduction'])
        assert close(m['mean_saved_training_selected_cost'],sum(r['selected_cost'] for r in own)/42)
        if role!='identity':gains[role]=gain;total+=gain
    for role,gain in gains.items():assert close(summary['training_loss_budgets'][role]['fraction_of_total_available_absolute_reduction'],gain/total)
    fits={f['definition']['held_publisher_group']:f for f in models}
    for r in contexts:
        fit=fits[r['held_group']];node=next(t for t in fit['model']['trace'] if t['node']==r['leaf_id'])
        cases=[fit['definition']['fitting_cases'][i] for i in node['rows']];assert cases==r['support_cases']
        kinds=[rows[c].get('experimental_role','identity' if rows[c]['role']=='target' else 'original_source') for c in cases]
        assert dict(Counter(kinds))==r['support_roles']
    harmed=[r for r in contexts if r['role']=='colour_cool' and r['DE_improvement']< -1e-12]
    assert len(harmed)==6 and all(set(r['support_roles'])<= {'exposure_under','exposure_over'} for r in harmed)
    pairs=read(OUT/'paired_paths_PRIVATE.json');assert len(pairs)==7 and sum(p['same_leaf'] for p in pairs)==5
    assert summary['new_fits']==summary['new_predictions']==summary['image_reads']==0
    report=dict(passed=True,saved_training_row_appearances=168,unique_fitting_images=28,held_contexts_checked=35,
        paired_paths=7,loss_budgets_checked=4,new_fits=0,new_predictions=0,image_reads=0,holdout_reads=0,
        summary_sha256=sha(OUT/'summary_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(report,indent=2)+'\n');print('PASS:168saved training appearances/35held contexts/7pairedpaths/4lossbudgets;zero fits.')


if __name__=='__main__':main()
