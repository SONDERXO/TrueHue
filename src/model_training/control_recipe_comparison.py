"""Explicit fitting-ID gates for the isolated core control-recipe experiment."""
from src.data_preparation.source_group_folds import source_group_folds

CONTROLS=frozenset({'identity_control','mild_bright_exposure'})

def plan_control_folds(probes,eligible_ids,held_ids):
    """Every source group is held out; held IDs can only be evaluation probes."""
    eligible=set(eligible_ids);held=set(held_ids)
    if len(eligible)!=len(eligible_ids) or len(held)!=len(held_ids):raise ValueError('Unique explicit eligibility IDs required')
    ids=[r['pair_id'] for r in probes]
    if eligible&held or eligible|held!=set(ids):raise ValueError('Eligible/held IDs must partition the exact probe universe')
    for row in probes:
        if int(row['clipped_pixel_count'])!=0 or row['input_processing_status']!='success':raise ValueError('Clipped/failed inputs cannot enter this fitting experiment')
    folds=source_group_folds(probes);by_id={r['pair_id']:r for r in probes};plans=[]
    for fold in folds:
        fitting=sorted(set(fold['train_pair_ids'])&eligible);evaluation=fold['inner_validation_pair_ids']
        older=[p for p in fitting if by_id[p]['variant'] not in CONTROLS]
        if not fitting or not older:raise ValueError('Empty fitting recipe; no fallback')
        if {by_id[p]['source_image_id'] for p in fitting}&{by_id[p]['source_image_id'] for p in evaluation}:raise ValueError('Fitting/evaluation source leakage')
        plans.append(dict(fold_id=fold['fold_id'],held_out_duplicate_group=fold['held_out_duplicate_group'],
            held_out_source_ids=fold['inner_validation_source_ids'],evaluation_pair_ids=evaluation,
            primary_pair_ids=sorted(set(evaluation)&eligible),held_diagnostic_pair_ids=sorted(set(evaluation)&held),
            fit_pair_ids=dict(older_recipe=older,with_controls=fitting)))
    return plans
