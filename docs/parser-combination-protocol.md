# Fixed parser, anatomy and material combination

26 October 2026. Fixed before execution. User prefers the dense-parser result
and explicitly authorizes continuing recommended work without routine pauses.
This is direction for development, not approval of every new mask or training
admission. Original annotations, acceptances/rejections and holds are immutable.

## Three fixed arms

Use cached dense parser skin1/nose10, existing coarse semantic face-skin3,
existing crop-based expanded eye/brow/complete-mouth exclusions from script91,
and selected detector bounds padded10% of its larger dimension. All pixels
must pass these anatomical/semantic/spatial constraints. This base is arm A.
The padded rectangle is only a processing limit; it is not labeled as skin.

Material seeds are original measurement support (original generation support
for clean source cases) intersected with A. Require at least1000 seeds; no
imputation, fallback, reference/target colors or manual annotation use.

- A: anatomical base alone, to expose material failure separately.
- F: A AND existing robust3D Lab distance<=3, with median/MAD scale floors
  [12,6,6], exactly the earlier relative-material recipe applied to ALL support.
- C: A AND robust2D a*/b* distance<=3, using the same seeds and a*/b* median/MAD
  floors[6,6]. L* is omitted in this fixed ablation because illumination and
  complexion both affect it. No threshold sweep or tone-conditioned rule.

F/C are material consistency vetoes, not learned/validated paint recognition.
Skin-colored paint and unusual shadows remain potential failures; measure them.
Nose/nostril and eyelid discrepancies are not silently relabeled.

Generation and correction are prospective fresh arm supports. Measurement is
the original measurement support intersected with each arm. Thus correction
can recover a cheek while estimation retains a representative original subset.
No old correction pixel is exempted from the new anatomical/material vetoes.
This is a replacement-support experiment, not removal-only V or a production
rule. Inputs were still generated with OLD masks; no end-to-end dataset claim.

## Fixed samples and verification

Phase1: same53 known cases (9clean sources,32 cohort inputs,12native regressions)
plus two83184 sentinels retained as rejected/not geometry-approved. Use the
same three completed references, nine coordinate-matching frames,48 point
observations and unchanged descriptive paint/feature polygon groups.

Phase2: apply the identical frozen recipe to all75 historical variant attempts
and15 clean sources from `training_source60_variants_v1`, including every
rejected/clipped/uncertain/source-contamination case. These are previously
exposed TRAIN sources; verify exposure-ledger membership. No new source,
replacement sample or reserved image. Recompute parser/landmarks only where
not already cached; retain existing semantic maps and explicit failures.
Do not select a different rule for individual faces based on review outcomes.

Save all masks, seed/geometry/material diagnostics, CIELAB/ITA and frozen input
brightness features, original-generation retention, changed/addition counts,
reference/interior skin and exclusion scores, and sparse point results. Report
paint overlap on the full painted polygons separately from feature overlap and
paint-point success. Assess cheek202/124 and all added labeled exclusions;
unlabeled pixels remain unscored. Inspect every source/variant board, all native
regressions and sentinel outputs. Historical decisions never become admissions.

Independently replay all arm masks from saved ingredients and compare full/
interior scores and measurement statistics/features. Verify hashes of original
images/masks/models/labels/reviews/ledger. Run the Python suite. No training,
replacement original artifacts, runtime adoption or Android app creation.

## Decision gates

Compare anatomy versus material effects; prefer no arm by decree. Record
coverage gains and skin losses, retained/new non-skin, finite feature failures,
point regressions and historical witness contamination. A candidate that leaves
paint-area contamination or loses valid skin cannot be described as validated
merely because numerical/point screens pass. Any new technical hold is separate
from original human acceptance. If material protection remains inadequate,
stop short of regeneration/fitting and document that concrete limitation.
If a candidate is promising, prepare a reviewable version and a consistent
regeneration plan; preserve training-design/split constraints. No final model
claim without the outstanding method and evaluation requirements.

## Thesis distinctions

Dense learned anatomy plus coarse semantic support, feature margins, relative
material vetoes and omission of L* in C exceed the proposed rule-based mask.
The added ONNX model, internal512 inference/device costs and exposed manual
development references must be disclosed. No automatic-paint, skin-color truth,
final independent evaluation or application-user annotation requirement is
claimed. Neck localization, MST mapping, final datasets/splits, expert MOS and
Android validation remain pending; this is not an approved proposal amendment.
