"""Independent saved-record coverage checks; no models or images."""
from pathlib import Path
from collections import Counter
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/reviewed_correction_training_coverage_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    bindings=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bindings.items())
    summary=read(OUT/'summary_PRIVATE.json');folds=read(OUT/'fold_coverage_PRIVATE.json');decisions=read(OUT/'held_decision_support_PRIVATE.json')
    leaves=read(OUT/'fitting_leaf_coverage_PRIVATE.json');ledger=read(OUT/'role_action_ledger_PRIVATE.json')
    models=read(ROOT/'outputs/reviewed_correction_comparison_v1/models_PRIVATE.json')
    rows={r['case_id']:r for r in read(ROOT/'outputs/reviewed_correction_comparison_design_v1/rows_PRIVATE.json')}
    predictions={p['case_id']:p for p in read(ROOT/'outputs/reviewed_correction_comparison_v1/predictions_PRIVATE.json')}
    assert len(folds)==7 and len(ledger)==len(decisions)==len(rows)==14
    assert Counter(r['role'] for r in ledger)=={'source':7,'target':7}
    for row in ledger:
        original=rows[row['case_id']]
        assert row['saved_oracle_controls']==original['oracle_direct_controls'] and row['saved_oracle_action']==original['oracle_action_index']
        assert row['physical_exposure_or_colour_only_label'] is None
    bygroup={f['held_group']:f for f in folds}
    for fit in models:
        definition=fit['definition'];train=[rows[c] for c in definition['fitting_cases']];group=definition['held_publisher_group']
        assert Counter(r['role'] for r in train)==bygroup[group]['fitting_role_counts']=={'source':6,'target':6}
        for d in [d for d in decisions if d['held_group']==group]:
            p=predictions[d['case_id']];trace=next(t for t in fit['model']['trace'] if t['node']==p['leaf_id'])
            own=[train[i] for i in trace['rows']]
            assert d['fitting_leaf_cases']==[r['case_id'] for r in own]
            assert d['leaf_identity_rows']==sum(r['role']=='target' for r in own)
            assert d['leaf_source_rows']==sum(r['role']=='source' for r in own)
            assert d['changed_pixels']==p['changed_pixels']
    assert len(leaves)==summary['leaves']==38
    assert summary['singleton_row_leaves']==sum(l['rows']==1 for l in leaves)==25
    assert summary['single_publisher_leaves']==sum(l['publisher_groups']==1 for l in leaves)==25
    edited=[d for d in decisions if d['role']=='target' and d['changed_pixels']]
    assert len(edited)==summary['changed_held_identity_outputs']==3
    assert all(d['leaf_identity_rows']==0 and d['leaf_source_rows']==1 and d['leaf_publisher_groups']==1 for d in edited)
    assert summary['new_fits']==summary['new_predictions']==summary['image_reads']==0 and summary['new_intervention_selected'] is False
    result=dict(passed=True,original_role_action_joins=14,fold_balance_checks=7,held_leaf_support_checks=14,
        original_leaves_checked=38,singleton_leaves=25,reference_harms_in_singleton_correction_leaves=3,
        new_fits=0,new_predictions=0,image_reads=0,holdout_reads=0,summary_sha256=sha(OUT/'summary_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(result,indent=2)+'\n');print('PASS:14 role/action joins,7 balanced folds,14 leaf contexts,38 leaves;zero fits/predictions/images.')


if __name__=='__main__':main()
