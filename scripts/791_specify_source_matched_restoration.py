"""Metadata-only source-matched supervision specification; no generation/fits."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/source_matched_restoration_design_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve previous or partial specification')
    bound={}
    def read(p):
        p=Path(p);raw=p.read_bytes();bound[str(p)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    coverage=read(ROOT/'outputs/reviewed_correction_training_coverage_v1/review_PRIVATE.json');assert coverage['passed']
    previous=read(ROOT/'outputs/reviewed_correction_comparison_v1/summary_PRIVATE.json');assert previous['development_checks_passed'] is False
    rows=read(ROOT/'outputs/reviewed_correction_comparison_design_v1/rows_PRIVATE.json')
    oldplan=read(ROOT/'outputs/reviewed_correction_comparison_design_v1/plan_PRIVATE.json')
    pixels=read(ROOT/'outputs/reviewed_photographic_pixels_v1/records_PRIVATE.json')
    bycase={r['case_id']:r for r in rows};geometry={r['case_id']:r for r in pixels['records']}
    recipes=[dict(id='exposure_under',implementation='development_roles.core_exposure',preset='medium',direction='under',
                  gamma=1/.7,red_gain=1.,blue_gain=1.),
             dict(id='exposure_over',implementation='development_roles.core_exposure',preset='medium',direction='over',
                  gamma=.7,red_gain=1.,blue_gain=1.),
             dict(id='colour_cool',implementation='core_colour_recipe.render_rgb',preset='medium',direction='none',cast='cool',
                  gamma=1.,red_gain=245/255,blue_gain=1.)]
    ledger=[];bases=[]
    for group in sorted({r['publisher_group'] for r in rows}):
        source=bycase[group+'_0__source'];base=bycase[group+'_0__target'];assert base['clean_identity_constraint']
        bases.append(dict(publisher_group=group,base_case_id=base['case_id'],original_source_case_id=source['case_id'],
            pixels_file=base['pixels_file'],pixels_sha256=base['pixels_sha256'],annotation_folder=base['annotation_folder'],
            annotation_manifest_sha256=base['annotation_manifest_sha256'],input_bridge=geometry[base['case_id']]['input_bridge'],
            role='accepted_photographic_reference_not_intrinsic_tone_truth',provided_MST_label=None))
        for kind,case in [('original_source',source['case_id']),('identity',base['case_id'])]+[(r['id'],group+'_0__matched_'+r['id']) for r in recipes]:
            ledger.append(dict(case_id=case,publisher_group=group,role=kind,status='existing_available' if kind in ('original_source','identity') else 'planned_not_generated',
                fitting_allowed=kind!='original_source',clean_constraint=kind=='identity',training_admitted=False,calibration_admitted=False))
    for kind,case in [('original_source','904_0__source'),('identity','904_0__target')]+[(r['id'],'904_0__matched_'+r['id']) for r in recipes]:
        ledger.append(dict(case_id=case,publisher_group='904',role=kind,status='unavailable_no_accepted_matching_base',
            fitting_allowed=False,clean_constraint=kind=='identity',training_admitted=False,calibration_admitted=False))
    folds=[]
    for group in sorted({r['publisher_group'] for r in ledger}):
        available=[r for r in ledger if r['publisher_group']!='904']
        evaluation=[r['case_id'] for r in available if r['publisher_group']==group]
        fitting=[r['case_id'] for r in available if r['publisher_group']!=group and r['fitting_allowed']] if group!='904' else []
        assert len(fitting)==(0 if group=='904' else 24) and len(evaluation)==(0 if group=='904' else 5)
        folds.append(dict(held_publisher_group=group,fitting_cases=fitting,evaluation_cases=evaluation,
            attempted_evaluation_cases=[r['case_id'] for r in ledger if r['publisher_group']==group],
            fit_required=group!='904',fitting_role_weights={c:1. for c in fitting}))
    for relative in ('src/distortion_generation/development_roles.py','src/distortion_generation/core_colour_recipe.py',
        'src/distortion_generation/table2_composite.py','src/distortion_generation/paper_gamma.py',
        'src/model_training/image_loss_action_tree.py','docs/correction-redesign-feasibility-results-2026-11-09.md',
        'docs/green-feature-correction-results-2026-11-09.md'):
        p=ROOT/relative;bound[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    plan=dict(status='specified_not_generated_not_fitted',intervention='Replace photographic source/editor fitting supervision with controlled source-matched restoration supervision on the same seven accepted reference bases.',
        not_novel='Generators and four-role synthetic structure already exist; only reviewed base/support context and fitting-role composition change.',
        generation=dict(bases=7,new_images=21,recipes=recipes,application='Whole delivered RGB8 frame, generator alpha=ones.',
            formula='u=inputRGB8/255; raw=u**gamma*[red,1,blue]; output=rint(255*raw). Existing clip-free core functions, no offsets/contrast.',
            common_preset='medium is an engineering severity, not a person/MST label; no tone-dependent claims.',
            proposed_paper_relationship='Three explicit diagnostic recipes, not the literal complete Table2 procedure; primary tone-dependent recipe scope remains separately documented.'),
        input_handling=dict(mode='manual_template_assisted_fixed_geometry_controlled_augmentation',
            mask='Propagate only the same base user-reviewed geometric measurement/correction support to its own RGB-only derivatives; mark mask_origin=propagated_same_geometry, not a new human save or automatic prediction.',
            measurement='Compute Lab/ITA/green from each actual transformed native crop resized to256 at the same recorded bounds, with the original1000guard; scene features from actual full transformed frame.',
            mapping='Apply existing fixed external isotonic artifact to21newITAs, retain raw/support/clipping flags; no mapper fit or true-MST label invention.',
            original_held_source='Use its existing independent reviewed mask/features, never the editor-reference mask or clean features.',
            no_automatic_detection_claim=True,new_detector_parser_FaceOcc_calls=0),
        training=dict(original_sources='Evaluation-only in every fold; not used to fit/select recipes or controls.',
            per_fitting_base=['identity','exposure_under','exposure_over','colour_cool'],rows_per_fold=24,
            identity_rows_per_fold=6,corrupt_rows_per_fold=18,weights='Equal row1, equal total4 per fitting publisher; no tuned/repeated identity weights.',
            balance_change='Identity fraction changes from1/2 to1/4; this is disclosed as part of the supervision package, not claimed an isolated causal augmentation effect.',
            tree=oldplan['candidate'],target_costs='Recompute14fixed native blended-action RGB costs per new derivative against its base. No continuous oracle fitting, new actions or analytic-inverse-as-perfect-target claim.'),
        accounting=dict(attempted_groups=8,attempted_roles=40,available_roles_if_preparation_passes=35,unavailable904_roles=5,
            controlled_roles=28,new_derivatives=21,existing_identity_roles=7,existing_original_source_roles=7,
            new_cost_values=294,new_MST_applications=21,proposed_tree_fits=7,proposed_held_predictions=35,all_data_fit=False),
        comparison=dict(frozen_old_source_and_identity_results='outputs/reviewed_correction_comparison_v1/predictions_PRIVATE.json',
            primary='Report controlled21 RGB/DE improvement versus uncorrected, separately for allthree recipes.',
            real_source_transfer='Same7originalsource outcomes; meanRGB andmeanDE must not exceed frozenprevious32.002887577242504/12.031091229086034.',
            preservation='All7heldidentityoutputs unchanged; allprotected/zeroalpha pixels unchanged relative to their actual input, not pristine reference.',
            coverage='All35availablepredictions and40attemptedrows retained;904unavailable remains explicit.',
            claims='No tuning/evaluation using held group to choose recipes. All harm counts/worst cases shown; no fairness or full MST-conditioning claim.'),
        preparation_checks=['Verify existing base pixel/annotation manifests before cached-frame read.',
            'Exactly21derivatives/all7bases/all3recipes, independent arithmetic replay and clipping/quantisation reports; no failure replacement.',
            'Replay unchanged geometry and actual-input measurement/scene/green/statistics; no clean feature copy.',
            'Preserve old14vectors/outputs; new records explicitly propagated geometry/manual assistance.',
            'Stop after data preparation and all-case review; no fit implicitly authorized.'],
        stop='One data-supervision design only; no recipe strength/direction sweep, new base pool, masks, mapper, feature or leaf search.',
        next_step='Prepare and verify21controlled derivatives/features/costs only if selected, then decide whether the specified comparison is ready.',
        generation_authorized_by_this_specification=False,fit_authorized_by_this_specification=False,
        images_generated=0,new_fits=0,new_predictions=0,image_reads=0,runtime_adopted=False)
    OUT.mkdir()
    for name,value in [('plan_PRIVATE.json',plan),('bases_PRIVATE.json',bases),('role_ledger_PRIVATE.json',ledger),
        ('folds_PRIVATE.json',folds),('input_sha256_PRIVATE.json',bound)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    print('Specified7existingbases/21plannedderivatives/35available40attemptedroles;7folds24fit5eval;zero generation/fits.')


if __name__=='__main__':main()
