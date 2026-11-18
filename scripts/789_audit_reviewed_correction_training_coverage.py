"""Audit saved role/action/leaf evidence only; no fitting or image reads."""
from pathlib import Path
from collections import Counter
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/reviewed_correction_training_coverage_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve existing or partial audit')
    bound={}
    def read(p):
        p=Path(p);raw=p.read_bytes();bound[str(p)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    prior=ROOT/'outputs/reviewed_correction_comparison_v1'
    receipt=read(prior/'review_PRIVATE.json');assert receipt['passed_verification'] and not receipt['development_checks_passed']
    for p,h in receipt['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    rows=read(ROOT/'outputs/reviewed_correction_comparison_design_v1/rows_PRIVATE.json')
    models=read(prior/'models_PRIVATE.json');predictions=read(prior/'predictions_PRIVATE.json')
    indexed={r['case_id']:r for r in rows}
    def direction(r):
        if r['role']=='target':return 'defined_identity_reference'
        gamma=r['oracle_direct_controls'][0]
        return 'oracle_gamma_lt1' if gamma<1 else 'oracle_gamma_gt1' if gamma>1 else 'oracle_gamma_equal1'
    def counts(group):return dict(Counter(direction(r) for r in group))
    labels=[dict(case_id=r['case_id'],role=r['role'],group=r['publisher_group'],defined_identity_constraint=r['clean_identity_constraint'],
        saved_oracle_action=r['oracle_action_index'],saved_oracle_controls=r['oracle_direct_controls'],
        descriptor=direction(r),identity_cost=r['identity_cost'],best_catalogue_cost=r['oracle_cost'],
        target_aware_catalogue_gain=r['identity_cost']-r['oracle_cost'],
        physical_exposure_or_colour_only_label=None) for r in rows]
    folds=[];decisions=[];leaf_records=[]
    for fit in models:
        definition=fit['definition'];held=definition['held_publisher_group']
        train=[indexed[c] for c in definition['fitting_cases']]
        assert len(train)==12 and sum(r['role']=='target' for r in train)==sum(r['role']=='source' for r in train)==6
        folds.append(dict(held_group=held,fitting_role_counts=dict(Counter(r['role'] for r in train)),
            fitting_oracle_descriptors=counts(train),held_oracle_descriptors=counts([indexed[c] for c in definition['evaluation_cases']]),
            fitting_unique_nonidentity_oracle_actions=sorted({r['oracle_action_index'] for r in train if r['role']=='source'})))
        traces={t['node']:t for t in fit['model']['trace']}
        for node_index,node in enumerate(fit['model']['tree']['nodes']):
            if node['kind']!='leaf':continue
            trace=traces[node_index];support=[train[i] for i in trace['rows']]
            action=trace['action'];identity=[r for r in support if r['role']=='target']
            assert all(r['action_costs'][action]==0 for r in identity)
            leaf_records.append(dict(held_group=held,node=node_index,action=action,rows=len(support),
                publisher_groups=len({r['publisher_group'] for r in support}),source_rows=sum(r['role']=='source' for r in support),
                identity_rows=len(identity),fitting_identity_constraints_satisfied=True))
        for p in [p for p in predictions if p['held_publisher_group']==held]:
            trace=traces[p['leaf_id']];support=[train[i] for i in trace['rows']]
            decisions.append(dict(case_id=p['case_id'],role=p['role'],held_group=held,selected_action=p['action_index'],
                saved_oracle_action=indexed[p['case_id']]['oracle_action_index'],oracle_descriptor=direction(indexed[p['case_id']]),
                fitting_leaf_cases=[r['case_id'] for r in support],leaf_source_rows=sum(r['role']=='source' for r in support),
                leaf_identity_rows=sum(r['role']=='target' for r in support),leaf_publisher_groups=len({r['publisher_group'] for r in support}),
                RGB_improvement=p['RGB_improvement'],DE_improvement=p['DE_improvement'],changed_pixels=p['changed_pixels']))
    sources=[d for d in decisions if d['role']=='source'];targets=[d for d in decisions if d['role']=='target']
    changed_targets=[d for d in targets if d['changed_pixels']>0]
    summary=dict(roles=14,source_reference_pairs=7,defined_identity_rows=7,source_rows=7,
        overall_oracle_descriptors=counts(rows),source_oracle_action_counts=dict(Counter(r['oracle_action_index'] for r in rows if r['role']=='source')),
        all_folds_have_six_source_six_identity=True,all_fitting_identity_constraints_satisfied=True,
        changed_held_identity_outputs=len(changed_targets),changed_held_identity_in_source_only_single_group_leaves=sum(
            d['leaf_identity_rows']==0 and d['leaf_publisher_groups']==1 for d in changed_targets),
        leaves=len(leaf_records),single_publisher_leaves=sum(l['publisher_groups']==1 for l in leaf_records),
        singleton_row_leaves=sum(l['rows']==1 for l in leaf_records),
        source_identity_predictions=sum(d['selected_action']==0 for d in sources),
        oracle_gamma_gt1_sources_left_identity=[d['case_id'] for d in sources if d['oracle_descriptor']=='oracle_gamma_gt1' and d['selected_action']==0],
        colour_only_cases_explicitly_labelled=0,near_unchanged_source330_not_identity_label=True,
        source455_oracle_gamma=indexed['455_0__source']['oracle_direct_controls'][0],
        interpretation='Unchanged examples are present and balanced by role; limited action/context coverage and source-only single-case leaves do not generalize. Counts are not proof of cause or a selected repair.',
        no_missing_identity_flag_bug=True,new_fits=0,new_predictions=0,image_reads=0,holdout_reads=0,
        additional_mask_reviews_required=False,new_intervention_selected=False)
    OUT.mkdir()
    for name,value in [('summary_PRIVATE.json',summary),('role_action_ledger_PRIVATE.json',labels),('fold_coverage_PRIVATE.json',folds),
                       ('held_decision_support_PRIVATE.json',decisions),('fitting_leaf_coverage_PRIVATE.json',leaf_records),('input_sha256_PRIVATE.json',bound)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
