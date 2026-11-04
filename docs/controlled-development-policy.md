# Controlled-development policy (2026-10-20)

This fixes a small software-development configuration, not the final thesis
cohort or an adviser-approved methodology revision. Original human decisions
and baseline artifacts remain unchanged. No new pairs or model were produced.

## Source suitability

Script 23 regenerated current-version evidence for all 35 provisional sources
and checked stored measurements. Codex visually inspected all six contact
sheets (original / face crop / current mask). This is not an expert or second
human review, measured segmentation accuracy, or calibrated color assessment.

Eight sources are selected for controlled development: train/12288, 19,
22211, 22454, 51739, 62331, 6236 and 75027 (all `.jpg`). They retain seven
training and one development-validation allocation. There are no eligible
final-test sources in this small subset, and it cannot support generalization
or skin-tone-stratified conclusions. Detail, shading and small source artifacts
remain documented limitations rather than presumed absent.

The other 27 sources are held with per-image reasons, including hair/background
or glasses inclusion, facial hair, paint, occlusion, strong rendering casts,
blur, fragmentation or uncertain reference quality. These conservative
judgments concern this particular reconstruction task, not universal image
usability. Pilot source 7303 is now held; earlier operator-test results are
preserved and do not establish training suitability.

Script 24 writes `data/manifests/controlled_development_v1/` with:

- `source_audit.csv`: all 650 prior rows and separate controlled-use decisions.
- `selected_sources.csv`: eight selected source records, with original partitions.
- `source_suitability_review.csv`: all 35 Codex decisions and reasons.
- `distortion_policy.json`: the fixed development contract.
- `summary.json`: counts and input hashes.

Original human labels remain unchanged. Existing `training_ready=False` is
preserved: `controlled_development_eligible` is a different, narrower status.
Selection conditions on source/mask appearance and may bias the cohort. Do not
claim demographic fairness, representativeness or true-skin-color recovery.

## Fixed scope and severity

Configuration `controlled_skin_mask_v1` specifies:

- Shared float encoded-RGB gamma-then-gain operator, quantized once on export.
- Binary source-skin-mask-only generation with `v2_complete_mouth_v1`.
- No blending, face-oval restriction, brightness offset, noise or extra transforms.
  Visible mask seams are a known controlled-simulation artifact, not validated
  realism or deployment blending.
- Three identical parameter sets per source, ordered gamma / red gain / blue
  gain: dark `(0.70, 0.85, 0.95)`, bright_warm `(1.25, 1.08, 0.95)`, and
  color_shift `(1.00, 0.85, 1.15)`.
- Group-independent technical development only. This is not the proposal's
  tone-conditioned severity procedure; no MST labels or ITA thresholds invented.
- Analytic inverse targets, clipping tracked separately. Successful clipped
  inputs are stress-only; failed input processing excludes a pair with reason.
- Features recomputed from saved distorted inputs, never reference features.
  Fixed source masks serve generation/oracle checks, not inference shortcuts.
- Every variant inherits its source partition. One validation source supports
  only an implementation check, not final model evaluation.

## Next milestone and outstanding thesis decisions

A small controlled training-table builder can now use this fixed configuration
without further review batches or guessed tone labels. It must retain all
attempted pairs and their failures and keep clipped stress cases separate.

Implemented: script 25 produced all 24 attempts, with 16 train, 3 validation,
4 clipped stress and 1 failed-input row. See `docs/controlled-training-table.md`
for the input-only feature schema, output paths and limitations. No model fit.

Before final thesis training, resolve with the adviser whether tone-dependent
severity will use a defensible grouping method or require a proposal revision.
Final cohort expansion, end-to-end masking/blending and final evaluation
boundaries remain separate. Ordinary source photos are relative reconstruction
targets, not calibrated true skin color.
