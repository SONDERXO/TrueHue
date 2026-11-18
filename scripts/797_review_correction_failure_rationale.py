"""Saved paths and training loss budgets only; no alternate fits or predictions."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,statistics

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/correction_failure_rationale_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve prior or partial rationale')
    bound={}
    def read(p):
        p=Path(p);raw=p.read_bytes();bound[str(p)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    resultroot=ROOT/'outputs/source_matched_restoration_comparison_v1'
    receipt=read(resultroot/'review_PRIVATE.json');assert receipt['passed_verification'] and not receipt['development_checks_passed']
    rows={r['case_id']:r for r in read(ROOT/'outputs/source_matched_restoration_preparation_v1/combined_rows_PRIVATE.json')}
    predictions=read(resultroot/'predictions_PRIVATE.json');models=read(resultroot/'models_PRIVATE.json')
    contexts=[];training_losses=[];pair_paths=[]
    def kind(row):return row.get('experimental_role','original_source' if row['role']=='source' else 'identity')
    for fit in models:
        held=fit['definition']['held_publisher_group'];train=[rows[c] for c in fit['definition']['fitting_cases']]
        trace={t['node']:t for t in fit['model']['trace']};nodes=fit['model']['tree']['nodes']
        for node in fit['model']['trace']:
            if nodes[node['node']]['kind']!='leaf':continue
            for i in node['rows']:
                row=train[i];action=node['action'];role=kind(row)
                if row['clean_identity_constraint']:assert row['action_costs'][action]==0
                training_losses.append(dict(held_group=held,case_id=row['case_id'],role=role,chosen_action=action,
                    identity_cost=row['identity_cost'],oracle_cost=row['oracle_cost'],selected_cost=row['action_costs'][action],
                    available_absolute_reduction=row['identity_cost']-row['oracle_cost']))
        own=[p for p in predictions if p['held_publisher_group']==held]
        for p in own:
            leaf=trace[p['leaf_id']];support=[train[i] for i in leaf['rows']]
            contexts.append(dict(case_id=p['case_id'],role=p['experimental_role'],held_group=held,
                selected_action=p['action_index'],leaf_id=p['leaf_id'],support_cases=[r['case_id'] for r in support],
                support_roles=dict(Counter(kind(r) for r in support)),RGB_improvement=p['RGB_improvement'],
                DE_improvement=p['DE_improvement'],changed_pixels=p['changed_pixels']))
        identity=next(p for p in own if p['role']=='target')
        colour=next(p for p in own if p['experimental_role']=='colour_cool')
        pair_paths.append(dict(held_group=held,identity_leaf=identity['leaf_id'],colour_leaf=colour['leaf_id'],
            same_leaf=identity['leaf_id']==colour['leaf_id'],identity_action=identity['action_index'],colour_action=colour['action_index']))
    budgets={}
    for role in ('identity','exposure_under','exposure_over','colour_cool'):
        group=[r for r in training_losses if r['role']==role]
        budgets[role]=dict(appearances=len(group),unique_images=len({r['case_id'] for r in group}),
            mean_identity_cost=statistics.mean(r['identity_cost'] for r in group),
            mean_oracle_cost=statistics.mean(r['oracle_cost'] for r in group),
            mean_saved_training_selected_cost=statistics.mean(r['selected_cost'] for r in group),
            total_available_absolute_reduction=sum(r['available_absolute_reduction'] for r in group))
    gains={k:v['total_available_absolute_reduction'] for k,v in budgets.items() if k!='identity'}
    for role in gains:budgets[role]['fraction_of_total_available_absolute_reduction']=gains[role]/sum(gains.values())
    harmed=[r for r in contexts if r['role']=='colour_cool' and r['DE_improvement']<-1e-12]
    edited=[r for r in contexts if r['role']=='identity' and r['changed_pixels']>0]
    summary=dict(training_loss_budgets=budgets,held_colour_harms=len(harmed),held_edited_identity=len(edited),
        harmed_colour_in_exposure_only_leaves=sum(set(r['support_roles'])<= {'exposure_under','exposure_over'} for r in harmed),
        edited_identity_without_fitting_identity=sum(r['support_roles'].get('identity',0)==0 for r in edited),
        same_leaf_identity_colour_pairs=sum(p['same_leaf'] for p in pair_paths),pairs=7,
        available_under_to_colour_gain_ratio=gains['exposure_under']/gains['colour_cool'],
        available_over_to_colour_gain_ratio=gains['exposure_over']/gains['colour_cool'],
        interpretation='Absolute RGB-loss gain gives unequal learning incentive to equally frequent corruption types; saved routes also show cross-content confusion. Association is not a causal proof or evidence a loss change will pass preservation.',
        historical_comparison='Earlier key/layer balancing normalized continuous parameter-regression targets; it is not per-example identity-baseline normalization of this finite-action rendered RGB loss. Both are weighting-related and prior failure remains relevant.',
        candidate_for_design_only='For nonidentity fitting rows divide each action cost by that same row identity cost; retain hard identity feasibility, original raw costs/metrics and all other settings. No held data/reference at inference.',
        proposal_limits='No new information is added. This may change priorities but cannot guarantee identity or correction-direction generalization; no normalization strength search or fit is authorized.',
        new_fits=0,new_predictions=0,image_reads=0,holdout_reads=0,intervention_executed=False,runtime_adopted=False)
    for relative in ('src/model_training/image_loss_action_tree.py','src/model_training/layer_balanced_tree.py',
        'docs/clean-harm-diagnosis-and-repair-results-2026-11-06.md','docs/correction-model-and-paper-realignment-2026-11-11.md'):
        p=ROOT/relative;bound[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    OUT.mkdir()
    for name,value in [('summary_PRIVATE.json',summary),('held_leaf_contexts_PRIVATE.json',contexts),
        ('saved_training_losses_PRIVATE.json',training_losses),('paired_paths_PRIVATE.json',pair_paths),('input_sha256_PRIVATE.json',bound)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
