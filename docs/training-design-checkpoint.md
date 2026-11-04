# Training-design checkpoint and next development plan

24 October 2026. Pause small-batch fitting. The implementation works technically, but current correction quality is not ready for final training or runtime adoption.

## What the evidence establishes

- 39 pairs come from only10 source photos; synthetic variants do not increase the number of independent sources. Subject identities are unverified.
- Only3 sources have all5 variants. Seven sources contribute fewer pairs because of quality holds or clipping. Current counts: dark7, bright/warm6, color shift6, unchanged10 and mild10. Unweighted fitting gives a5-pair source2.5 times the influence of a2-pair source.
- The ten brightness/color measurements improved one fixed comparison, but adding eight pairs then worsened error6.25 to7.59 on the same39 probes. All10 unchanged probes were still altered. This supports a fragile prototype, not a successful correction model.
- Original photographs let us test recovery from a known synthetic edit. They do not establish correct complexion, neutral lighting or calibrated skin color. Existing casts/shadows and hard synthetic boundaries remain limitations.
- Mask success, minimum pixel counts and coverage retention are separate from reliable correction. Keep those statuses separate.

## Fixed next review:60 training-source attempts

Use the remaining230 eligible training sources. A proposed60-ID list is saved using metadata only: three recorded L* rank groups, two b* groups within each,10 sources per cell by a fixed hash. This covers recorded appearance, not MST classes or intrinsic complexion. Sixty is a practical review budget, not a statistical power calculation or a promised accepted sample size.

The list excludes recorded development exposure, current source/duplicate groups, non-singleton duplicate groups and non-TRAIN allocations. Do not replace failed candidates with photos chosen for favorable model predictions. Newly inspected sources must be logged before opening. No new exposure was recorded by preparing this metadata list.

For every selected source, record the following separately:

1. Numerical processing: detection, landmarks and available measurements.
2. Reference suitability: detail, occlusion and strong pre-existing lighting/color effects. Do not judge against a preferred skin brightness.
3. Estimation coverage and correction-region quality, including facial hair, paint, clothing and pose concerns. Actual neck skin is not automatically contamination.
4. All five fixed variant attempts, including unchanged/mild controls; preserve failures, coverage holds and clipped stress cases.

Keep the existing mask policies, ten-feature schema and five transform recipes fixed. No new thresholds, fallback measurements or predicted-performance-based admission. Codex screening remains a documented development observation; it does not overwrite pending human labels or final dataset eligibility. Review the complete batch and freeze all dispositions before fitting.

## Comparison prepared in advance

The proposed list includes five source/duplicate-group folds, assigned by fixed hash order before image inspection. All variants inherit their source fold. These are development folds, not a new final test or verified subject separation. If fewer than five eligible groups remain, report an insufficient cohort instead of silently changing the protocol.

Use a single depth3/seed42/leaf1 tree with the frozen ten measurements and no-correction baseline. Give each fitting source total weight1 (`1 / number of its eligible pairs` per row), so partial sources do not automatically count less. This is a proposed development change and must be labeled separately from earlier unweighted results. It does not eliminate missing-variant selection bias. Report complete-five sources as a separate sensitivity analysis; preserve all failures and variant-specific denominators.

Report source-balanced and pair averages, every variant, unchanged/mild harm counts and excluded-attempt rates. Keep current10 sources as an already-exposed regression set: do not include them in a fitting fold when presenting their predictions as source-held-out. Do not use reserved74 or external development126 source allocations for this experiment. These historical allocations are provisional and do not establish compliance with the proposal's final split.

Do not tune features, depth or a correction-skip threshold on these results. Do not promote a runtime model solely because this development comparison improves. A larger cohort may still fail; report that rather than repeatedly changing the evaluation set.

## Thesis and implementation implications

This plan preserves the decision-tree correction direction. It does not resolve operational MST mapping, final FairFace/SCIN roles, calibrated color/reference limitations, expert evaluation, Android completion or visible-neck support. The ten-feature extension, proposed weighting, source selection and development folds are recorded distinctions for later thesis edits, not silently approved methodology amendments. The original proposal remains unchanged.

Next action is to execute the fixed60-source screen, then assess its yield before any variant generation or fitting. No images, models, masks, human labels, reserved data or exposure ledger changed during this checkpoint.

[Verified cohort audit](../outputs/training_design_checkpoint_v1/audit.json) | [Proposed60-source list](../data/manifests/training_design_checkpoint_v1/proposed_source_review60.json) | [Proposed protocol](../data/manifests/training_design_checkpoint_v1/proposed_protocol.json) | [Latest correction results](development39-comparison.md)

Executed follow-up: [fixed60-source screening results](training-source60-screen.md).15promising/45held;no variants or fitting yet.
