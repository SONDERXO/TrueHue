# Parser, anatomical and material protection results

26 October 2026. Completed the recommended combined-mask experiment and one
fixed boundary-guard follow-up without waiting for routine reviewer responses.
The user's exact direction is preserved in
`data/manifests/parser_combination_v1/user_direction.json`. This direction
authorizes development; it does not turn historical rejections into admissions.

[Combined comparison gallery](../outputs/parser_material_boundary_v1/review.html) |
[Readiness report](../outputs/parser_material_boundary_v1/readiness.json) |
[Core A/F/C results](../outputs/parser_material_core_v1/summary.json) |
[Historical A/F/C results](../outputs/parser_material_historical_v1/summary.json) |
[C2 results](../outputs/parser_material_boundary_v1/summary.json).

## Fixed experiments and stage handling

The [initial protocol](parser-combination-protocol.md) was fixed before execution.
It combines dense skin/nose support, coarse face-skin class3, the previously fixed
expanded eye/brow/complete-mouth exclusions and a10% padded detector processing
limit. Three arms were compared without threshold/model searches:

- A: anatomical/semantic support only.
- F: A plus the existing robust relative3D Lab distance<=3, scale floors12/6/6.
- C: A plus the same relative a*/b* distance<=3, floors6/6, omitting L*.

Material seeds come from the original measurement support intersected with A,
or original generation support on clean source cases. At least1000 pixels are
required. Manual labels, reference colors and correction targets never enter
inference. Generation/correction use fresh prospective arm support; measurement
is the original measurement subset intersected with that support.

After C still selected painted regions, a separate
[fixed follow-up](parser-material-boundary-protocol.md) declared C2: remove C
pixels within2 native pixels of material-rejected pixels inside A. This reuses
the earlier native two-pixel exclusion-distance convention; no radius search
followed. It is an adaptive development follow-up, not independent confirmation.
C2 is removal-only relative to C. Both earlier experiments remain preserved.

These are prospective masks on OLD saved inputs. No consistently regenerated
dataset, new training table or corrected-image improvement is claimed.

## Scope and checks

All53 core cases succeeded: nine clean sources,32 current inputs and12 native
regressions. The identical recipe also ran on all15 historical clean sources
and75 historical variants, including all rejects, uncertain, clipped and
source-contamination cases. All90 historical cases succeeded numerically.
These143 cases reuse already exposed TRAIN/development sources, not143
independent people or a new evaluation set. Ledger membership was checked.

The original83184 geometry rejection remains unchanged; no unsupported geometry
fallback or admission was introduced. No new source, reserved imagery, label
change or source substitution occurred. Internal parser512 inference retains
the exact native224/256 annotation coordinates.

## Cheek and skin-coverage tradeoffs

C and C2 select the annotated40048 cheek point202/124 in clean source generation
and all three saved correction variants. F misses it in dark correction,
showing that the lightness term can reject this otherwise supported patch.
This establishes a specific recovered reference pixel, not complete facial
coverage or global improvement.

| Correction case | Original labeled-skin coverage | C | C2 | C2 selected exclusions |
| --- | ---: | ---: | ---: | ---: |
| 40048 dark | 97.34% | 94.86% | 93.89% | 130 |
| 40048 unchanged | 97.19% | 95.16% | 94.74% | 172 |
| 40048 mild | 96.84% | 94.97% | 94.60% | 207 |
| 60162 dark | 95.97% | 95.66% | 95.37% | 180 |
| 60162 color | 98.75% | 96.03% | 96.03% | 318 |
| 16798 clean | 91.76% | 89.64% | 86.22% | 986 |
| 16798 shifted | 91.71% | 88.20% | 84.89% | 662 |

The broader feature protection and material veto lose labeled skin while
reducing exclusion overlap. C2's extra margin increases some losses. The
improved cheek does not compensate for those losses by definition; no validated
aggregate quality score is invented. Full/interior metrics remain available.

## Paint findings and concrete readiness failure

| 16798 correction | Painted pixels selected, clean / shifted | Newly selected painted pixels versus original, clean / shifted |
| --- | --- | --- |
| A | 5624 /5683 | 4298 /4688 |
| F | 1096 /781 | 206 /165 |
| C | 1411 /1067 | 302 /290 |
| C2 | 851 /479 | 113 /69 |

C2 reduces total painted-area overlap relative to C, but **still adds113/69
pixels in protected painted reference regions** compared with the original
correction masks. Prospective C2 clean generation selects851painted pixels,
including385 additions relative to original generation. This prevents a
paint-safe policy claim or consistent regeneration for training.

All three labeled paint points per variant are excluded by F/C/C2 correction;
A selects all three. All12/12 labeled skin points are retained by every arm,
and hair/other correction points remain0/4 and0/5 selected. These point passes
do not override the painted-area failure. Paint-reference groupings remain
the prior descriptive mapping of the reviewer's unchanged exclusion polygons.

Paint detail boards show remaining/new selection around painted transitions
and small areas inside marked paint regions. Coarse manual edges can include
ordinary skin, so these counts are not calibrated pixel truth; the original
exclusions are nevertheless preserved as the fixed development constraints.
No polygon was changed to improve scores. No automatic paint-recognition
claim is justified by relative color or a local safety margin.

## Broader regressions and prior holds

| Arm | Current32 retention, old / prospective generation denominator | Historical75 retention, old / prospective denominator |
| --- | --- | --- |
| A | 32/32 /32/32 | 54/75 /70/75 |
| F | 32/32 /32/32 | 52/75 /69/75 |
| C | 32/32 /32/32 | 53/75 /70/75 |
| C2 | 32/32 /32/32 | 53/75 /70/75 |

Both denominators are reported. The old generation mask contains historical
non-skin support; prospective denominator changes can improve a retention
fraction without establishing mask accuracy. Numerical passes do not replace
the manual region checks or clear historical human decisions.

C2's five historical prospective-denominator failures are31154color,
63870dark/color,67583color and84364color. All original75 variant dispositions,
clipping/stress information, source holds and reviewer notes remain unchanged.
No rejected/uncertain case is admitted because a new mask looks cleaner.

On the existing diagnostic rectangles,60162 background and63870 fabric
overlap reach zero across the assessed stages.31154 source overlap falls
614 to3 pixels; the three remaining coordinates are(48,205),(49,205),(49,206).
Zoom inspection places them on a blurred face/background edge, so they are
recorded as ambiguous witness overlap, not certified hair or clean skin.
31154color correction also adds3 pixels in that rectangle. The previous
technical hold is not cleared. Rectangles are illustrative witnesses, not full
annotations or proof that the remaining masks are clean.

All source/input comparisons were inspected via30 phase/source contact sheets
covering80 A/F/C boards and80 C/C2 boards. Paint detail boards and the31154
witness zoom were also inspected. Persistent caveats include closed eyes,
side pose, hairline/jaw edges, scarf/fabric boundaries, large old measurement
gaps and legitimate skin lost near newly protected regions.

## Verification

- Script99 independently replays804 A/F/C masks and357 measurement feature sets
  across the two cohorts, plus102 full/interior reference-count checks.
- Script100 independently replays268 C2 masks using disk dilation rather than
  its distance-transform guard, and recalculates119 measurement feature sets.
- An additional34 independent full/interior reference checks verify C2 scores.
- All recorded original source/input/mask/model/label/review/ledger hashes stay
  unchanged.481 Python tests pass in9.70s with a workspace-local temporary dir.

The frozen ten-feature definitions remain unchanged. These are changed
experimental measurements, not a new fitted correction model. Parser/Android
backend parity, phone latency/memory and final device integration are still
unverified as recorded in the preceding parser experiment.

## Decision and next gate

Save C/C2 as promising contour-recovery development candidates, with explicit
technical holds. Do not adopt an arm, regenerate training pairs or fit a model.
This hold comes from measured added paint, skin loss and unresolved historical
failures, not from waiting for routine user permission.

No further material threshold/margin search is implied. Before another expansive
mask, the paint/material design must demonstrate protection over the full fixed
painted regions and preserve useful facial coverage. Evidence should cover more
than one painted face before final claims; no inspected data may be described
as untouched evaluation. A paint-specific model, new labeled material data or
workflow exception would need a separately documented method/design decision,
not a silent change to the proposal. Do not add a required manual paint mask to
the application without reconciling its photo-selection-only workflow.

The user's preference for the dense parser remains recorded. Prior approvals,
31154 hold, empty original fold4 and the unexecuted revised fold plan remain
intact. Runtime masks, models and original data have not changed.

## Thesis differences

Dense learned parsing, coarse semantic intersection, anatomical margins, global
relative-material vetoes, omission of L* in C and the C2 native safety margin
all extend the proposed rule-based method. Report their roles and failure cases,
the53.2MB parser, internal512 inference and unresolved device costs. Exposed
manual mixed-resolution references are development diagnostics, not final
evaluation, calibrated skin-color truth or an application-user annotation step.
Neck localization, validated MST mapping, final data/split/evaluation, expert
MOS and Android requirements remain unfinished. No adviser approval or proposal
amendment is claimed.
