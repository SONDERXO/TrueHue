# Crop versus full-image landmark comparison

26 October 2026. Script93 executed the [fixed protocol](landmark-framing-protocol.md)
on the same53 source/input cases and two83184 sentinels. The only intended change
is landmarker input framing: original first-success crop versus one full-native-
image inference. E/EC rules, detector boxes, categories, margins, relative-color
checks, geometry threshold, references and original masks remain fixed.

[Comparison gallery](../outputs/landmark_framing_v1/review.html) |
[Metrics](../outputs/landmark_framing_v1/summary.json) |
[Verification](../outputs/landmark_framing_v1/verification.json).

## Outcome

Full-image landmarks succeed on all53 cases but do not solve the annotated
cheek or consistently improve anatomical alignment. No framing switch is adopted.

| Correction mask | Crop E: skin coverage / excluded pixels selected | Full E | Crop EC | Full EC |
| --- | --- | --- | --- | --- |
| 40048 dark | 95.01% /198 | 94.88% /175 | 95.01% /198 | 95.19% /178 |
| 40048 unchanged | 94.78% /174 | 94.83% /253 | 94.82% /174 | 95.20% /272 |
| 40048 mild | 94.41% /215 | 94.65% /246 | 94.49% /215 | 94.98% /253 |
| 60162 dark | 93.41% /289 | 92.84% /325 | unavailable | unavailable |
| 60162 color | 96.21% /386 | 95.69% /301 | unavailable | 95.82% /301 |
| 16798 clean native regression | 88.46% /1565 | 88.30% /1516 | unavailable | unavailable |
| 16798 shifted native regression | 88.57% /1238 | 88.55% /1214 | unavailable | unavailable |

Reference coverage/exclusion counts are diagnostic on the three exposed manual
frames, not final segmentation accuracy. Full/interior sensitivity counts are
saved for every available reference mask. Full E reduces some exclusion overlap
while increasing others; full EC can also add labeled-exclusion pixels (for
example40048 unchanged253 to272 relative to full E). Small coverage gains do
not establish a preferable segmentation policy.

Cheek202/124 remains absent from all40048 generation/measurement/correction
arms. Native source geometry comparison shows both framings still trace the
oval inside that cheek boundary; broad eye/brow mismatch remains. Full-image
framing alone is therefore insufficient in this ablation.

## Availability and regressions

EC generation becomes available9/9 cohort sources (previous8/9), EC correction
30/32 cohort inputs (previous29/32), and9/12 native regression corrections
(previous8/12). Newly available cases are60162 source generation,
60162color correction and19shifted correction. These are availability changes,
not acceptances.67583dark/60162dark remain unavailable. Native19clean and
16798clean/shift remain unavailable for correction expansion. Both83184
sentinels retain rejected geometry, with the same0.0666/0.0644 retention.

All E native point outcomes are unchanged from crop E across all three stages:
correction skin12/12 retained per variant, paint0/3 selected, pre-existing clean
hair1/4 selected and shifted hair0/4. Full EC correction retains9/9 assessable
skin points clean and11/11 shifted, with3/1 skin points respectively unavailable.
All3 paint points per variant remain unavailable for EC correction. This does
not establish paint-safe expansion. Native generation EC remains4/6 available;
generation uses only clean source imagery.

All32 cohort measurement CIELAB/ITA/brightness sets remain valid. Original-
generation retention screens pass32/32 E and30/30 available EC, with two EC
corrections unavailable. These numerical checks do not validate masks or change
training eligibility. All saved inputs retain OLD generation-mask provenance;
no consistent synthetic regeneration is claimed.

## Verification and limitations

All35 boards were inspected via15 source contacts, plus three annotated-source
geometry boards. The same hairline, fabric, side-pose and lower-jaw caveats
remain. Existing shifted19/62331 measurement gaps persist. No global visual
approval is recorded.

All199 saved full-image candidate masks were independently replayed using disk
dilation instead of the inference helper's distance transforms. Saved-mask
pixels match exactly. Independent recalculation verifies all44 measurement
CIELAB/ITA and brightness sets (32 cohort plus12 native regressions). Original
input/mask/model/reference/ledger/review-decision hashes remain unchanged.
All471 tests pass (10.84s, workspace-local temporary directory).

The experiment applies E/EC to the same legacy masks. Original feature holes
remain, so this is not a complete skin-mask rebuild under each framing. No
per-image framing selection, threshold sweep or annotation-guided inference was
introduced. Full-image model success does not independently verify selected-
person alignment; the sentinel geometry rejection remains essential evidence.

## Decision and next checkpoint

Keep both framing policies experimental and preserve the original runtime,
all human decisions/holds and fold status. No further margin or crop tuning is
justified by this result alone. Before another mask rule, audit the existing
semantic class predictions against the fixed skin/exclusion regions to identify
which limitations come from the segmentation classes versus landmark geometry.
Use cached native category maps, report feature/paint disagreement separately,
and keep unmarked pixels unscored. Do not infer automatic paint recognition or
final skin truth from a face-skin category.

Thesis distinctions remain: added landmark margins/learned contour support are
experimental departures from the proposal, human polygons are development
diagnostics rather than an application-user requirement, and exposed mixed224/
256 sources are not final evaluation. Validated MST mapping, neck localization,
final dataset/split/evaluation, expert MOS and Android remain pending. No
proposal amendment or model adoption occurred.
