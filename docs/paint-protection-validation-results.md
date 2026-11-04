# Broader protected-material development results

26 October 2026. **No candidate passes the protection gate. Training-pair
regeneration, mask adoption and correction-tree fitting remain held.** The
broader test confirms useful face coverage but persistent selection of paint,
cosmetic and visible-mark regions. See the [gallery](../outputs/paint_protection_validation_v1/review.html),
[readiness decision](../outputs/paint_protection_validation_v1/readiness.json)
and [independent replay](../outputs/paint_protection_validation_v1/verification.json).

## Scope and reference provenance

Following the user's authorization to continue recommended steps autonomously,
visually inventoried all114 previously exposed TRAIN sources on10 original-image
contact sheets. Cross-checked the source partition audit and four prior source
screening records. No reserved or previously unseen source was opened. Prior
13529/84888/58397 source holds and all other decisions remain unchanged.

The [predeclared protocol](paint-protection-validation-protocol.md) freezes17
frames: original user references16798/40048/60162; cosmetic challenges3183/58397/
67436/84888; visible forehead marks81250; ambiguous colored appearance13529/72347;
lighting challenges81965/76160; previous hair/fabric/scarf/foliage controls31154/
63870/51446/55007/56444. Native224/256 frames and source hashes are retained.

The [frozen manifest](../data/manifests/paint_protection_validation_v1/frozen_manifest.json)
SHA256 is `294e51833f58cbad187bc16064f7878aa91c5ca2576e6c2e5e30425e08bb2225`.
It preserves114 inventory entries,17 source records and prior review provenance.
There are13 additional conservative protected-region polygons across five frames.
These are **provisional Codex development annotations**, not user/expert labels,
complete makeup masks or training targets. Five original-image overlays were
inspected before inference. Four67436 polygons were narrowed to remove ambiguous
ordinary-skin/teeth/mouth edges; original draft coordinates and changes are saved
separately in `region_qa.json`. Frozen67436 overlay was also inspected before
inference. No annotation enters mask construction or material seeds.

Original user polygons, original draft export, separate completion confirmation,
label rasters and historical reviews are unchanged. All three rasters were
independently reconstructed. 16798 remains the only user-annotated broad paint
example. Helmet/colored rendering and strong lighting are not asserted to be
paint. Mark origin is not inferred. Unmarked pixels stay unlabeled.

## Fixed experiment and availability

Reused unchanged A/F/C/C2 recipes, models, preprocessing, thresholds, anatomy
exclusions and2native-pixel guard. A is dense skin/nose intersected with coarse
face-skin, anatomical exclusions and bounded processing extent. F uses relative
3D Lab distance<=3; C omits L*; C2 removes C pixels within2pixels of A's chroma
outliers. No model download, tuning or per-image recipe selection occurred.

Each source has clean, dark(gamma0.7/R0.85/B0.95) and color-shift(gamma1/R0.85/
B1.15) probes. These are global diagnostic transforms, not mask-generated
training pairs. Exact recipes, hashes and clipping counts are saved;11 color
probes clip some pixels. No inverse target or training table was created.

Of51probes,48 are available. 13529color-shift,76160clean and76160color-shift have
fewer than1000material seeds; no fallback, threshold relaxation or replacement
was used. These failures stay visible in all results/boards. Generation support
is evaluated only on clean sources; measurement and correction are recomputed
from each actual probe. The448saved candidate masks comprise64generation,
192measurement and192correction masks.

The original complete-mouth anchor is recomputed from each actual probe and
intersected with coarse face/body-skin. This is explicitly distinct from earlier
saved training-generation masks. One available76160dark probe has no available
clean prospective denominator, so retention is unavailable rather than passing.

## Protection, coverage and numerical results

Examples of C2 correction selection in protected regions:

| Frame/region | Clean selected | Dark selected | Color-shift selected |
| --- | ---: | ---: | ---: |
| 16798 user paint,6003pixels | 851 | 880 | 479 |
| 3183 provisional cosmetic/feature interiors,combined | 304 | 237 | 305 |
| 58397 provisional cosmetic/feature interiors,combined | 366 | 549 | 627 |
| 67436 provisional purple cosmetics,combined | 33 | 31 | 17 |
| 84888 provisional blue eye cosmetics,combined | 44 | 21 | 33 |
| 81250 provisional forehead marks,combined | 112 | 91 | 49 |

16798 paint selection remains525/583/264pixels after one-pixel interior erosion
for clean/dark/color. For84888, clean selection still includes16interior pixels;
81250clean includes53interior pixels. Thus failure is not confined to a polygon's
outermost boundary. Cosmetic/feature overlap is labeled explicitly; its selection
does not isolate paint recognition from anatomical exclusion errors. Provisional
labels alone cannot certify accuracy, but the unchanged user paint reference
already establishes a protection failure. Generation/measurement counts are
reported separately in the summary and region CSV.

All24 assessable source/probe combinations with any supplied exclusion region
(three user references plus five provisionally marked sources) have some C2
correction overlap;23 also overlap an eroded interior. This combines different
reference types and is a diagnostic failure count, not a paint-accuracy score.
No accuracy denominator is assigned to the other qualitative/witness cases.

All192available measurement sets have valid Lab/ITA and six brightness features.
Numerical validity is insufficient: A/C/C2 prospective-generation retention
passes36/47assessable cases; F passes35/47. C2 fails11cases, including makeup,
helmet, patterned-light and prior hair/fabric controls. These thresholds measure
support consistency, not annotated skin truth. 40048C2 labeled-skin correction
coverage is94.74%clean,94.15%dark,93.25%color; the earlier coverage-loss gate is
unresolved. These global probes must not be described as the earlier masked
training inputs, even when clean results match.

60162background and63870fabric witness selections stay0. 31154's witness retains
3/4/3pixels clean/dark/color; the prior ambiguous blurred-edge interpretation and
technical hold remain. A zero witness count is not exhaustive contamination
clearance. All17 full stage/contact boards were inspected, covering every saved
candidate mask and explicit unavailable panels. Face contours generally improve,
but upper-eye cosmetic/forehead-mark selection, material-dependent holes and
reduced measurement support under stress remain visible. No region or parameter
was changed after seeing these predictions.

## Verification and implementation record

Scripts102/103prepare and freeze reference provenance;104executes inference;
105independently replays the saved results;106packages all stages and readiness;
107checks final artifacts and gallery links. Replay passed51transforms,
448mask compositions (including an independent integer-disk C2 reconstruction),
192measurement feature sets,168user-reference count checks and476protected-region
checks. All original source/model/label/review/ledger hashes match. Replay uses
saved model predictions/geometry; it is not an independent model-accuracy test
or Android parity check.

**481tests passed in11.58s**, using `python -m pytest tests/ -q
--basetemp=outputs/paint_protection_validation_v1/pytest_tmp --tb=short` from the
project root. The initial default temporary-directory run had85setup permission
errors (396tests passed); using an explicit writable workspace directory resolved
them without code changes. An initial diagnostic-script import typo was fixed
before inference/output creation. MediaPipe stderr makes PowerShell's redirected
run report a native-command error despite the script's complete51record summary;
completion was checked against run status, artifacts and independent replay.

## Decision and thesis differences

Save this candidate and its failure evidence. **Zero regenerated training pairs,
zero newly admitted cases, zero correction models fitted and no runtime policy
change.** Old approvals remain approvals under their original policy; this
candidate's failed readiness gate does not rewrite them. Previous historical
retention failures,31154hold, folds and revised unexecuted training plan remain.
Do not remove failed cases or fit the tree around the masks to claim completion.

The next design requirement is material-specific protection that also preserves
ordinary facial skin under varied lighting. The observed anatomy/global relative
color combination does not establish that capability. A further design needs a
separately declared, representative material-reference/evaluation plan before
another candidate; this result does not justify another margin/threshold sweep
or a manual annotation step for application users.

Learned dense/coarse parsing, relative material guards and exposed provisional
human/Codex reference diagnostics extend the proposal's rule-based masking stage.
The17frames are deliberately selected development sources, with mixed native
resolutions and global/clipped stress probes. They are not independent final
evaluation, calibrated skin-color truth, expert verification, population/fairness
evidence or an approved proposal amendment. The53.2MB parser and internal512
inference retain unverified phone costs. Neck localization, operational MST,
final data/reference/splits/evaluation, expert MOS and Android remain unfinished.

## 27 October 2026: reference-quality follow-up

The [cached attribution audit](material-protection-design-checkpoint.md) preserves
every count above but flags mixed-material ambiguity at specific16798scalar-order
witness points. Paint grouping is a descriptive grouping of original exclusion
polygons, not additional user-supplied material labels. Exact overlaps remain
development comparisons against saved labels, not verified physical paint/skin
accuracy. No automatic relabeling or reversal of earlier decisions occurred.
Adjudicated material references are required before using these regions as
material ground truth; the technical hold remains, with a reference-quality
prerequisite added. No new mask candidate or training was run.
