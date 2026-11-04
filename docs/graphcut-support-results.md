# Hair-removal experiment — 23 October 2026

Follow-up: [semantic skin/hair comparison](semantic-support-results.md) identifies
a more conservative hair-veto candidate while preserving the fixed regressions.

Reject this candidate: it removes the reviewed hair selections but loses too
much valid skin. No default mask, estimation features or trained model changed.

## Fixed candidate

GrabCut refines both existing and newly added correction support. A fixed central
ellipse intersected with original skin seeds foreground; anatomical exclusions
and the one-pixel crop border seed background. The previous color-checked support
initializes probable foreground. Five iterations and RNG seed 42 were fixed before
the run. Output is restricted to the previous color-checked support. Seeds are
assumptions from the input, not human skin labels or semantic material classes.

Your frozen 24-point labels enter scoring only. No threshold sweep, label changes,
reference-guided mask construction or tree fitting occurred. This tests one
initialization, not all possible GrabCut configurations.

## Human-label regression

| Input | Method | Skin retained / 12 | Non-skin selected / 12 |
| --- | --- | ---: | ---: |
| Clean | Previous color check | 12 | 3 |
| Clean | GrabCut | 6 | 0 |
| Color shifted | Previous color check | 10 | 1 |
| Color shifted | GrabCut | 5 | 0 |

All four reviewed hair and all three paint points are excluded by GrabCut in
both variants, but half or more of the reviewed skin is missed. Zero unwanted
point selections is therefore insufficient for adoption. All 48 new observations
were available; these are development regression points, not pixel-area accuracy.

## Image comparison and reliability

All seven earlier model pairs completed with their original features and tree
fixed. On three development variants of source19, mean CIEDE2000 rises from
6.622 with the color check to 8.794 with GrabCut (original mask 7.609). Coverage
of the original generation region falls from 93.4% to 56.2%. Broad regions of
forehead and chin disappear in the color-shift example; clean hair case29962
also loses much of the lower face.

Four nonindependent clipped stress pairs show color error 11.601 versus 13.967
with the color check, but coverage drops from 98.9% to 66.3%. Reducing the region
where a poor correction is applied can improve reconstruction error without
improving skin segmentation. Do not use that stress score alone to choose it.

Broader mask-only diagnostics completed 79 of 92 attempts: 46 clean and33
shifted. The failure ledger retains two landmark failures, seven insufficient
color-check seed cases, and four new insufficient-central-seed cases (12947,
82552,12288,41283). Do not compare successful-case averages with earlier larger
cohorts as though availability were unchanged. No broader model-performance
or final-test claim is made.

Visual review covered the source19 shifted image comparison and clean29962
mask comparison. Most broader sheets received automated checks only.

## Artifacts and verification

The first run stopped before final scores were saved. Partial artifacts remain
in `outputs/graphcut_support_v1/`. A separate completed run is preserved in
`outputs/graphcut_support_resume_v1/`, including metrics, point scores, masks,
comparisons, failure ledger and input hashes. Nothing was overwritten.

Runner: `scripts/35_test_graphcut_support.py --output-name graphcut_support_resume_v1`.
Existing output folders are protected. The module is isolated in
`src/skin_masking/graphcut_correction_support.py`.

427 tests passed during implementation, including synthetic removal of baseline
dark material, central skin preservation, exclusions, nonmutation, repeatability
and explicit failure. The actual-image failures show why these software tests
do not establish segmentation quality. Saved model and frozen label hashes,
unchanged pair features, reproduced prior color-checked images and run input
hashes were verified. The continuation added an output-name option only; it
did not change the segmentation rule.

## Recommended next step

Stop extending these color/foreground-background heuristics. Test a dedicated
skin-and-hair segmentation model as an isolated technical comparison against
the frozen regression points and broader ordinary faces. MediaPipe's official
[multi-class segmenter guide](https://developers.google.com/edge/mediapipe/solutions/vision/image_segmenter)
documents separate face-skin and hair categories and is a concrete candidate.
Its classes alone do not guarantee hair accuracy or paint rejection; those must
be checked explicitly, together with skin retained, failures and runtime.

No new segmentation weights were downloaded or installed here. Any adoption
would be a separately documented implementation/methodology decision, not an
automatic change to the approved thesis. Keep current candidates and failed
examples as evidence; defer wider training until the correction-mask decision
is resolved.
