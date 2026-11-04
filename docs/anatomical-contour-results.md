# Anatomical-exclusion and contour ablation results

26 October 2026. Completed the [fixed protocol](anatomical-contour-protocol.md)
with scripts91/92. Both candidates remain experimental. No runtime policy,
synthetic input, original mask, training table, human decision or model changed.

[Local comparison gallery](../outputs/anatomical_contour_v1/review.html) |
[Full results](../outputs/anatomical_contour_v1/summary.json) |
[Independent verification](../outputs/anatomical_contour_v1/verification.json).

## Diagnosis and fixed candidates

On40048/60162 clean references, saved generation masks contain **zero** pixels
inside recomputed existing feature exclusions. All805/1059 selected manual
exclusion pixels fall outside those existing polygons. Visual geometry inspection
shows eye polygons narrower than the manual regions and brow polygons displaced
relative to the drawn brows. Coordinate remapping is consistent; this is feature
localization/extent disagreement, not demonstrated coordinate corruption.

E adds one fixed eye/brow margin, ceil3% of inter-eye-center distance, to the
existing feature/complete-mouth exclusions. It removes pixels at generation,
measurement and correction, with no additions. EC uses E measurement and adds
bounded local contour support at generation/correction: distance<=ceil2% of
detector size from old support and oval, bounded padded box, predicted face-skin
class3, and robust input-relative Lab distance<=3. Geometry still requires the
prior75% oval-retention gate. Added support deliberately bypasses HSV/YCrCb;
this is a documented new ablation, not the frozen proposed rule.

Parameters were fixed before candidate execution, with no sweep or retuning.
Manual labels are used only for scoring. Each actual input gets its own predicted
landmarks/categories; no clean-reference landmarks are substituted.

## Fixed scope and availability

All32 saved inputs across9 development sources and all9 clean generation sources
were processed. Twelve native regression inputs (six sources x clean/global
shift) supplied48 prior point observations. Two83184 geometry sentinels were
checked. All53 source/input cases yielded landmarks and E masks.

| Scope | E available | EC generation/correction available |
| --- | ---: | ---: |
| Nine clean source generation masks | 9/9 | 8/9 |
| Thirty-two saved correction masks | 32/32 | 29/32 |
| Six clean native regression generation masks | 6/6 | 4/6 |
| Twelve native regression correction masks | 12/12 | 8/12 |

EC is unavailable at60162 source generation,67583dark correction,
60162dark/color correction, and19/16798 regression generation/correction.
All fail the prior geometry gate. E results remain separate; unavailable EC
panels display the input with an explicit label, not a successful fallback.
The83184 sentinel fails extension geometry in both variants (oval retention
0.0666/0.0644); it was not silently accepted.

## Reference tradeoffs

Each cell reports labeled-skin coverage / selected labeled-exclusion pixels.
These are selected development-reference statistics, not final mask accuracy.

| Mask | Original | E | EC |
| --- | --- | --- | --- |
| 40048 generation | 97.01% /805 | 94.59% /174 | 94.74% /174 |
| 40048 dark correction | 97.34% /806 | 95.01% /198 | 95.01% /198 |
| 40048 unchanged correction | 97.19% /805 | 94.78% /174 | 94.82% /174 |
| 40048 mild correction | 96.84% /847 | 94.41% /215 | 94.49% /215 |
| 60162 generation | 98.78% /1059 | 96.26% /423 | unavailable |
| 60162 dark correction | 95.97% /873 | 93.41% /289 | unavailable |
| 60162 color correction | 98.75% /1025 | 96.21% /386 | unavailable |
| 16798 clean regression correction | 91.76% /2110 | 88.46% /1565 | unavailable |
| 16798 shifted regression correction | 91.71% /1743 | 88.57% /1238 | unavailable |

E substantially reduces eye/brow exclusion overlap but also removes valid labeled
skin. One-pixel-interior exclusion overlaps remain34-55 on40048 correction,
88/109 on60162dark/color correction, and937/663 on16798clean/shift correction.
Margin expansion is not a complete anatomical-localization fix. Some removal
extends above the brows and around eyelids; boundaries remain approximate.

The16798 baseline here is the old saved support **intersected with the learned
semantic veto**, unlike the earlier pre-veto table. Its2110/1743 selected exclusion
pixels therefore must not be confused with the earlier2152/1811. E is an
assessable newer-veto removal experiment on the native frame; paint/feature area
overlap still remains. There is no assessable EC paint-expansion result.

40048's labeled cheek probe202/124 remains absent from generation and all
correction arms. Independent gate replay shows it is predicted face-skin,
within processing bounds and near old support, and outside the expanded oval.
Relative Lab distance is2.162 on source/unchanged,2.189 on mild, but3.408 on
dark (limit3). Thus enlarging the rectangle or removing the absolute color
threshold alone does not solve the contour discrepancy. No radius or material
threshold was adjusted after observing this.

Across9 sources E removes13,123 generation pixels; across32 inputs it removes
45,151 measurement and45,811 correction pixels. EC adds5,183 prospective
generation pixels across8 available sources and18,800 correction pixels across29
available inputs. Additions are not established as skin. On40048, EC adds98/66/71
correction pixels dark/unchanged/mild, with no added labeled-exclusion pixels,
but little or no labeled-skin benefit. Unlabeled additions remain unvalidated.

## Hair, paint and numerical checks

E preserves prior point outcomes at all three stages. Clean/shift correction
retains12/12 labeled skin points, excludes all3/3 labeled paint points, and
retains the pre-existing one clean hair point (shift0/4 hair). Clean generation
retains11/12 skin points, and measurement11/12 clean and8/12 shifted; E does not
introduce new point losses. These are sparse points, not area safety proof.

EC correction is assessable on9/12 skin points per variant and retains all9;
the other3 skin points are unavailable. **All3 paint points per variant are
unavailable for EC correction**, so zero observed paint inclusions must not be
reported as a paint-safety pass. The existing clean hair inclusion remains.

All32 E-filtered measurement cases have valid CIELAB/ITA and six brightness
features, using the unchanged frozen ten-feature definitions. EC measurement
equals E by design. Original-generation-denominator retention screens pass32/32
for E and29/29 available EC cases; three EC corrections are unavailable. These
numerical screens do not override visual defects or human review holds.

## Visual review and verification

All35 comparison boards were inspected via15 source contact sheets, covering
all9 generation sources,32 input masks and12 regression inputs. Wider eye/brow
protection is visible throughout. Existing hairline, side-pose, fabric and
lower-jaw ambiguity remain; contour additions are not blanket approved.
Large existing measurement gaps in shifted19/62331 and fragmented10480
generation remain visible. These diagnostic regressions were not admitted into
the candidate cohort.

Script92 independently reconstructs all196 saved masks with disk dilation,
instead of the candidate's Euclidean distance-transform implementation. It
checks exact pixel equality, removal/addition counts, reference/interior counts,
and independently recalculates CIELAB/ITA/brightness for all44 measurement sets
(32 cohort plus12 regression). All pass. All recorded original input/mask/model,
ledger, review-decision, polygon and reference hashes remain unchanged.

Tests: **471 passed** using a fresh workspace-local pytest temporary directory.
Four added tests cover mandatory exclusions, bounded growth, added non-skin
category rejection, material rejection and explicit geometry/seed failure.

## Decision and thesis record

Do not adopt E or EC or regenerate training data yet. E supplies evidence that
feature extent matters but trades real skin loss for improved exclusion. EC
does not resolve the annotated cheek and remains unavailable on paint cases.
The geometry gate's rejection is retained as a limitation, not worked around.

Next recommended development step is a fixed **landmark-framing comparison**:
compare the current first-success crop with a full-frame landmark inference on
the same cases, without further margin/threshold sweeps. Examine contour and
eye/brow alignment, record failures, and score the unchanged references before
deciding whether landmark localization is adequate or another segmentation
approach is warranted. Do not assume a new framing will improve masks.

This experiment adds anatomical margins and learned-class/relative-color contour
support beyond the proposal's rule-based mask. It uses exposed mixed224/256
development frames and human diagnostics, not new independent evaluation or an
application-user annotation requirement. Neck localization, validated MST
mapping, final datasets/splits/evaluation, expert MOS and Android remain pending.
No adviser approval or proposal amendment is implied. Prior human decisions,
31154 hold, original empty fold4 and unexecuted revised fold plan all stand.
