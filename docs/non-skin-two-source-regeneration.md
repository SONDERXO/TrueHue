# Consistent regeneration:60162 and63870

24 October 2026. Reviewed the full three-stage comparisons and regenerated all five fixed variants for each of60162/63870 in a separate experiment. The four previously accepted variations pass current numerical/coverage checks, but their changed masks remain pending user review.31154 stays technically held.

Generation uses the fixed non-skin veto on the clean source mask. Inputs are freshly synthesized from that mask. Detection, baseline/YCrCb masks, material-checked support and guarded boundary are recomputed from each actual new input, then the same semantic veto intersects measurement and correction support. The ten feature names/formulas are unchanged, but their measurement-mask policy is experimental and differs from the runtime. No previous table or image was overwritten.

| Regenerated candidate | Clipped pixels | Estimation retention | Correction retention |
|---|---:|---:|---:|
|60162 dark|0|95.2%|95.2%|
|60162 color shift|0|89.4%|98.0%|
|63870 unchanged|0|100%|100%|
|63870 mild|0|98.2%|99.0%|

Retention uses each new clean-source generation mask, not annotated true skin. These numbers cannot be interpreted as improvement solely by comparing to old denominators. Codex inspected all ten new previews: the accepted four retain broad facial coverage while remaining pose, eye-edge and partial-mask caveats persist. No calibrated-color or model-performance claim follows.

The earlier non-skin witnesses are excluded from generation, measurement and correction in all four candidates.60162's background witness no longer receives synthetic alteration;63870's fabric witness no longer contributes to measurements. This is witness-level evidence, not proof of globally clean masks.

60162 bright remains clipped63pixels;63870 bright remains clipped73pixels.63870 dark/color still fail coverage (estimation40.5%/40.7%, correction58.3%/65.7%).60162 unchanged/mild remain user-rejected despite new numerical passes. No original rejection, uncertain decision or immutable exclusion is promoted.

## Review and next step

Open [the focused four-candidate comparison](../outputs/non_skin_regenerated_two_v1/review.html). Each row shows original/regenerated measurement, then original/regenerated correction. Each mask is displayed on its own input; generation changed, so those inputs are not necessarily identical. These are mask previews, not corrected outputs. Original human acceptances remain preserved separately from review of the regenerated versions.

After changed-mask review, stage only technically suitable regenerated candidates in a separate policy version. Do not mix their new measurement policy into the remaining old-policy28 pairs and call the result consistent: a future training-cohort policy must be fixed and applied to all included sources before fitting.31154's unresolved hair contamination still empties original fold4; even provisionally clearing these four would not restore that fold. No silent regrouping, replacement source selection or fivefold fitting.

Independently verified10 generation recipes, inverse targets and clipping counts;20 paired statistics/retention results;10 brightness sets; and source masks exactly matching the frozen veto. All tested witnesses are zero in the four candidates. Original review/model/input/schema/ledger hashes remain unchanged. **464 tests passed**. No fitting or runtime adoption.

The semantic-veto measurement/generation policy and partial regeneration remain recorded development-method distinctions. Operational MST, face-and-neck support, final data/reference eligibility and final evaluation remain unfinished. No original thesis amendment was made.

[All ten previews](../outputs/non_skin_regenerated_two_v1/review-index.md) | [Preserved decisions and new dispositions](../data/manifests/non_skin_regenerated_two_v1/recheck_dispositions.json) | [Verification](../outputs/non_skin_regenerated_two_v1/verification.json)

25 October2026: user approved the four regenerated candidates. [Approval record](../data/manifests/non_skin_regenerated_two_v1/user_changed_mask_approval.json). Cohort consistency and original emptyfold remain unresolved;no training admission.

25 October2026: [remaining28 consistently regenerated](non-skin-remaining28-regeneration.md),allnumericalchecks pass;changedmaskreview pending. Originalfivefold remainsinfeasible;explicitnine-source replacement proposed separately.
