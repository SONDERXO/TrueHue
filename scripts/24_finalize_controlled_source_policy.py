"""Record Codex's 35-source review and a controlled-development transform policy.

No original human reviews are overwritten. This does not approve a revised
thesis methodology, identity-independent evaluation, or full training cohort.
"""
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]

# Visual judgments from all six source_suitability_v1 sheets, 2026-10-20.
ACCEPT={
 'train/12288':'Useful facial detail and current-mask coverage; eye artifact lies in excluded region. Ordinary image only, not calibrated color.',
 'train/19':'Usable face detail and largely facial selected region; complete-mouth exclusion applied.',
 'train/22211':'Usable facial reference despite hat shading; representative cheeks selected. Shading remains a reference limitation.',
 'train/22454':'Usable facial detail and selected skin; small facial decoration remains a limitation. Distorted-input failures must remain excluded.',
 'train/51739':'Useful facial detail with plausible feature exclusions and substantial facial-skin coverage.',
 'train/62331':'Useful facial detail; complete-mouth exclusion removes visible open-mouth region.',
 'train/6236':'Useful facial detail and cheek coverage; mouth now fully excluded.',
 'train/75027':'Useful facial detail and plausible selected skin; wrinkles are not an exclusion criterion.',
}
HOLD={
 'train/124':'Fabric/occlusion near mouth and current-mask non-skin inclusion; requires closer source/mask review.',
 'train/12492':'Current selection includes neck/edge regions and visible non-facial contamination.',
 'train/12947':'Glasses and surrounding non-skin pixels remain within the selected region.',
 'train/16611':'Strong yellow rendering and soft detail; reference suitability uncertain, not evidence of true skin color.',
 'train/16798':'Substantial face paint; unsuitable as an ordinary unaltered facial-skin reference for this controlled subset.',
 'train/17773':'Hair/background remain selected near the upper boundary.',
 'train/21241':'Limited detail, glasses and facial-hair contamination make reference/mask suitability uncertain.',
 'train/22057':'Object crosses mouth and selected lower region; mask scope is occluded.',
 'train/26799':'Fabric occludes lower face; some fabric remains in candidate measurement region.',
 'train/29479':'Substantial beard remains selected; facial-skin statistics are contaminated.',
 'train/29746':'Soft detail and uneven skin selection; reference/mask boundary judgment uncertain.',
 'train/30603':'Facial-hair inclusion around the mouth remains a measurement concern.',
 'train/40001':'Facial hair and irregular selection leave uncertain facial-skin representativeness.',
 'train/4214':'Blur and profile reduce confidence in reference detail and mask placement.',
 'train/47374':'Very bright rendering, limited detail and fragmented selection; reference suitability uncertain.',
 'train/48136':'Selected facial hair remains substantial despite improved mouth exclusion.',
 'train/53224':'Soft detail and peripheral selection; hold for closer assessment.',
 'train/60658':'Strong blur limits confidence in source detail and feature boundaries.',
 'train/63150':'Hair/edge regions remain selected and source detail is limited.',
 'train/66938':'Strong warm rendering; source suitability uncertain for a clean-reference development example.',
 'train/67854':'Strong shadow/highlight contrast and limited detail; uneven selection remains.',
 'train/71750':'Strong warm rendering and selected peripheral/non-skin areas; hold for reference/mask review.',
 'train/7303':'Highly fragmented selected face region and peripheral selection; do not assume pilot use establishes suitability.',
 'train/7712':'Hand/edge inclusion and bright rendering complicate source-mask suitability.',
 'val/10480':'Fragmented current mask and peripheral selection; full reference suitability not established.',
 'val/1728':'Finger occludes/touches facial region and is partly included in selection.',
 'val/7058':'Limited detail, uneven selection and peripheral contamination; hold for closer review.',
}


def main():
    common=importlib.import_module('16_compare_face_outline')
    writer=importlib.import_module('21_synthetic_pair_pilot')
    check=importlib.import_module('15_prepare_fairface_mask_review')
    source=ROOT/'data/manifests/source_preparation_v1/source_audit_and_partitions.csv'
    evidence=ROOT/'outputs/source_suitability_v1/review.csv'
    output=ROOT/'data/manifests/controlled_development_v1'
    if output.exists():
        raise FileExistsError('Controlled development policy already exists')
    rows=common.read(source)
    provisional={r['image_id'] for r in rows if r['source_suitability']=='provisional_reviewed_candidate'}
    decisions={'fairface__'+k+'.jpg':('accept_controlled_development',v) for k,v in ACCEPT.items()}
    decisions.update({'fairface__'+k+'.jpg':('hold',v) for k,v in HOLD.items()})
    if set(decisions)!=provisional or len(decisions)!=35:
        raise ValueError('Every provisional source must have exactly one source judgment')
    evidence_rows=common.read(evidence)
    if {r['image_id'] for r in evidence_rows}!=provisional:
        raise ValueError('Evidence package does not match source cohort')
    fingerprints={str(source):check.digest(source),str(evidence):check.digest(evidence)}
    for r in rows:
        decision,note=decisions.get(r['image_id'],('not_assessed_in_this_pass','Retain prior hold/exclusion.'))
        r.update(controlled_source_decision=decision,controlled_source_notes=note,
            controlled_development_eligible=decision=='accept_controlled_development',
            source_assessor='Codex visual assessment' if r['image_id'] in decisions else '',
            source_assessment_date='2026-10-20' if r['image_id'] in decisions else '')
    audit=[]
    for r in evidence_rows:
        decision,note=decisions[r['image_id']]
        audit.append(dict(r,decision=decision,reason=note,assessment_date='2026-10-20'))
    policy=dict(policy_version='controlled_skin_mask_v1',status='fixed_for_technical_development_only',
        mask_version='v2_complete_mouth_v1',transform_version='encoded_rgb_gamma_then_gain_v1',
        transform_order=['gamma_power_1_over_gamma','red_blue_gain','clip','round_uint8_once'],
        generation_scope='binary_source_skin_mask_only',generation_boundary_blending='none',
        oracle_correction_scope='same_source_mask_for_operator_check_only',
        model_inference_mask='must_be_recomputed_from_distorted_input',
        deployment_blending='not_validated_or_specified_by_this_policy',
        severity_assignment='same_three_fixed_variants_per_source_no_skin_tone_conditioning',
        variants={k:dict(gamma=v[0],red_gain=v[1],blue_gain=v[2]) for k,v in writer.VARIANTS.items()},
        clipping_policy='exclude_from_primary_controlled_table_keep_as_stress_only',
        failed_input_policy='exclude_pair_keep_failure_record_do_not_substitute_reference_features',
        primary_metric_region='fixed_source_mask_oracle_only_distinguish_end_to_end_mask',
        subject_independence='not_verified',final_thesis_grouping_method='unresolved_requires_adviser_decision',
        final_evaluation_eligible=False,
        note='No more source expansion implied. Eight-image subset supports software development, not final thesis claims.')
    output.mkdir()
    writer.write_csv(output/'source_audit.csv',rows)
    writer.write_csv(output/'selected_sources.csv',[r for r in rows if r['controlled_development_eligible']])
    writer.write_csv(output/'source_suitability_review.csv',audit)
    (output/'distortion_policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    assert all(check.digest(Path(p))==h for p,h in fingerprints.items())
    from collections import Counter
    selected=[r for r in rows if r['controlled_development_eligible']]
    summary=dict(sources_reviewed=len(decisions),accepted_controlled=len(selected),held_in_review=len(HOLD),
        selected_by_partition=dict(Counter(r['partition'] for r in selected)),
        original_human_decisions_preserved=True,input_sha256=fingerprints,
        note='Separate Codex review; original labels unchanged. No pairs, model, or final thesis cohort generated.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
