"""Freeze one existing-data correction diagnostic; no model fit or image reads."""
from pathlib import Path
import hashlib,json,math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/reviewed_correction_comparison_design_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve previous or partial design')
    bound={}
    def read(p):
        p=Path(p);raw=p.read_bytes();bound[str(p)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    realignment=read(ROOT/'outputs/correction_paper_realignment_v1/review_PRIVATE.json')
    assert realignment['source_search_next_step_superseded'] and not realignment['frozen_gates_relaxed']
    rows=read(ROOT/'outputs/shared_core_mst_features_v1/complete_development_rows_PRIVATE.json')
    mapping=read(ROOT/'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json')
    contract=read(ROOT/'outputs/reviewed_feature_control_contract_v1/execution_plan_PRIVATE.json')
    allocation=read(ROOT/'outputs/reviewed_feature_control_contract_v1/publisher_folds_PRIVATE.json')
    verification=read(ROOT/'outputs/shared_core_mst_features_v1/verification_PRIVATE.json')
    assert verification['passed']
    names=contract['contract']['feature_names'];actions=contract['contract']['frozen_actions']
    assert len(names)==16 and len(actions)==14 and actions[0]==[1.,1.,1.]
    assert len(rows)==14 and len({r['publisher_group'] for r in rows})==7
    indexed={r['case_id']:r for r in rows}
    for r in rows:
        assert set(r['features'])==set(names) and all(math.isfinite(v) for v in r['features'].values())
        assert len(r['action_costs'])==14 and len(r['input_vector_float32'])==16
        assert r['mapping_artifact_sha256']==bound[str(ROOT/'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json')]
        assert not r['training_admitted'] and not r['calibration_admitted']
        assert r['clean_identity_constraint']==(r['role']=='target')
        if r['role']=='target':assert r['action_costs'][0]==0 and r['oracle_action_index']==0
    folds=[]
    assert len(allocation['folds'])==8 and len(allocation['ledger'])==16
    for old in allocation['folds']:
        held=old['held_publisher_group'];train=old['available_fitting_roles'];test=old['available_evaluation_roles']
        assert all(indexed[c]['publisher_group']!=held for c in train)
        assert all(indexed[c]['publisher_group']==held for c in test)
        assert len(train)==(12 if test else 14) and len(test) in (0,2)
        folds.append(dict(held_publisher_group=held,fitting_cases=train if test else [],
            evaluation_cases=test,attempted_evaluation_roles=old['attempted_evaluation_roles'],
            unavailable_evaluation_roles=old['unavailable_evaluation_roles'],fit_required=bool(test),
            fit_skip_reason=None if test else 'Both904rolesunavailable;skipfitratherthancreateunevaluatedall-datafit.',
            fitting_role_weights={c:1. for c in train} if test else {}))
    assert sum(f['fit_required'] for f in folds)==7
    assert len({c for f in folds for c in f['evaluation_cases']})==14
    for relative in ('src/model_training/image_loss_action_tree.py','src/model_training/portable_tree.py',
                     'src/model_training/aligned_correction_support.py','src/correction/seamless_blend.py',
                     'src/distortion_generation/paper_gamma.py'):
        path=ROOT/relative;bound[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    source=[r for r in rows if r['role']=='source']
    plan=dict(status='prepared_not_executed',purpose='Does reviewed photographic supervision produce useful held-group correction with the retained tree?',
        intervention='New reviewed photographic correction supervision versus prior synthetic-supervision development; no feature or calibration redesign.',
        candidate=dict(implementation='src/model_training/image_loss_action_tree.py:fit_action_tree',maximum_depth=4,
            feature_names=names,actions=actions,input_dtype='float32',objective='Equal-role sum of existing native all-positive-alpha RGB8MAE costs.',
            identity_constraints='Fitting editor-target roles only; source roles are not assumed clean.',
            nonharm_flags='No source colour-only flags invented; use existing clean-feasibility tree, no added global guard/veto.',
            tie_rules='Existing implementation: first minimum action, strict cost-reducing split, feature/threshold enumeration unchanged.'),
        execution_bounds=dict(tree_fits=7,held_role_predictions=14,attempted_roles=16,held_source_outputs=7,held_identity_outputs=7,
            all_data_fit=False,new_MST_fits=0,new_MST_predictions=0,new_image_model_calls=0,original_photo_reads=0),
        comparators=dict(primary='Uncorrected input/identity action on the exact same native positive-alpha region.',
            target_aware_catalogue_minimum='Saved14-action oracle cost is supervision/representability context, NOT predictive comparator accuracy.',
            old_trees='Do not paste incompatible old controls/features or compare numerical errors across different target cohorts.'),
        metrics=dict(primary='Equal-publisher mean source RGB8MAE and CIEDE2000 against same accepted editor reference.',
            footprint='All native pixels with alpha>0, all RGB channels; no target-mask intersection or region shrink.',
            identity='Exact input/output pixel equality on all7held editor-target roles; report selected controls separately.',
            report=['All16outcomes including2blocked904','Per-source input/output RGB and DE','Benefits/harms/ties and worst harms',
                    'Selected gamma/red/blue and missed oracle-benefit cases','Source cases grouped by saved oracle gamma direction, descriptively only',
                    'Protected/zero-alpha pixel equality','Actual split features including ITA/MST usage']),
        development_checks=dict(coverage='Exactly14held predictions,16attempted ledger;904two unavailable remain failures, not identity.',
            source_RGB='Held7source equal-publisher mean strictly below uncorrected mean.',
            source_DE='Held7source equal-publisher mean strictly below uncorrected mean.',
            identity_and_protection='All7held editor-target outputs unchanged; all protected/zero-alpha pixels unchanged.',
            numerical_tolerance=1e-12,
            interpretation='Passing supports further development only; individual harms remain visible and prohibit a blanket safety claim. No old gate is relaxed.'),
        review='View all14held-role original/output/reference panels plus two blocked904 ledger panels; score labels hidden.',
        limitations=['Seven publisher groups, exposed development, not verified independent people or final evaluation.',
            'ConstantMST4.494736842105263: cannot demonstrate learned MST conditioning on thisbatch; retain feature and disclose.',
            'No photographic MST reference labels or per-tone fairness claim.',
            'Editor target registration assumed; no intrinsic-tone recovery claim.',
            'User-reviewed masks;1188low-native-detail retained.',
            'Photographic-editor supervision is a method extension, not the paper synthetic-original benchmark.'],
        stop_rule='One candidate/sevenfolds then close regardless of result. No depth/action/weight/feature/veto/calibration/recipe repair or alternate cohort.',
        not_selected=['STW/CHROMA-FIT acquisition','Further annotations','New mapper','Parser project','Android integration','Final holdout reads'],
        execution_authorized_by_this_preparation=False,new_fits=0,new_predictions=0,runtime_adopted=False,calibration_admitted=False)
    OUT.mkdir()
    for name,value in [('plan_PRIVATE.json',plan),('rows_PRIVATE.json',rows),('folds_PRIVATE.json',folds),
        ('attempted_role_ledger_PRIVATE.json',allocation['ledger']),('input_sha256_PRIVATE.json',bound)]:
        (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    print('Prepared1candidate/7held-groupfits/14predictions/16attemptedroles;no new fits,predictions or image reads.')


if __name__=='__main__':main()
