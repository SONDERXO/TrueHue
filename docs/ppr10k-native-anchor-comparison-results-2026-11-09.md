# Native-input PPR10K anchor comparison — 9 November 2026

## Decision

**Native input improves intended-face availability from 4/8 to 7/8, but fails the
predeclared advancement criterion.** All eight produce one detected face, yet
904_0 selects the child rather than the historically selected image-right adult.
This is a real face detection with a wrong-person selection for this fixed task,
not a spurious face or a recovered adult detection. Do not report 8/8 success.

Retain the result as evidence that input sampling/aspect preservation matters
on these cases. Do not adopt it, manually select a different person, drop904_0,
change the threshold or run a resolution/crop/model rescue. The fixed comparison
ends here without a new experiment selected.

## Frozen comparison and checks

Explicit user approval followed the prepared protocol. Scripts706–707 use the
same exact eight source TIFFs, existing YuNet, confidence .85, NMS .3 and topK5000.
All eight source hashes, dimensions, uint16 precision and sRGB profile identities
pass before the first forward. The YuNet hash exactly matches its prior screen
binding. Source inference uses round(source/257) RGB8 converted to BGR, unchanged
from the first screen. No targets are read and no model/download/install is used.

The only intervention is full native-size input (360×540 or540×360), replacing
the stretched square256 anchor image. This changes resolution and aspect together;
the comparison does not isolate their individual effects. Native input sizes are
accepted by the existing OpenCV runtime. Eight calls total, one per source, no
retries. Raw returned score/keypoint rows are saved, then filtered/clamped/sorted
with the old helper's logic. Rejected square256 scores remain unavailable.

## All eight outcomes

Scores are detector outputs, not calibrated correctness probabilities.

| Pair | Previous square256 result | Native result | Score | Matches historical selected face? |
| --- | --- | --- | ---: | --- |
| 787_0 | One correct face | One face | .9121 | Yes: painter |
| 330_0 | No face | One face | .8871 | Yes: boat portrait |
| 767_0 | One correct face | One face | .9347 | Yes: seated bridal portrait |
| 1117_0 | One correct face | One face | .8965 | Yes: spotlit profile |
| 1188_0 | No face | One face | .8860 | Yes: image-right man in couple |
| 990_0 | One correct face | One face | .9131 | Yes: seated hat-wearing portrait |
| 904_0 | No face | One face | .9055 | **No: child instead of image-right adult** |
| 455_0 | No face | One face | .8945 | Yes: face with rollers |

All four previous successes retained; three of four previous misses recovered
as the intended face; one wrong-person selection. The protocol required retaining
four, recovering at least one, and no new wrong detection/selection. The last
requirement fails. A high score and exactly one returned detection do not ensure
the desired person was selected when a scene contains multiple visible people.

Viewed all eight source-only overlays. Yellow boxes/scores show native outputs,
cyan boxes show prior square256 detections mapped back for display, and green
polygons show historical selection locators. The polygons are not skin truth
or inference crops. No target edits or correction quality inform this selection
review. The result is exploratory on eight exposed photographs, not detector
accuracy across PPR10K or verified independent participants.

## Verification and interpretation

Script707 independently replays raw-score filtering, scalar integer box clamping,
area ordering and original square-to-native coordinate calculations without
repeating detection. All eight records, input hashes and original generated
artifacts pass. Its hash-bound review findings include every viewed overlay and
the wrong-person outcome. Software verification PASS and model-screen criterion
FAIL are separate results.

This is useful progress in diagnosing preprocessing: the prior four misses do
not imply all four source faces are undetectable by the existing model. However,
automatic selection remains unresolved, and native boxes must not be passed
straight into the old 256-coordinate crop bridge. No downstream mask/landmark/
FaceOcc run, coordinate integration or new training readiness is claimed.

There were zero parser, landmarker, FaceOcc, MST or correction-model calls; zero
target fits, mask changes, correction renders, runtime updates, acquisitions,
contacts, uploads, commits or pushes. All earlier artifacts are preserved. Final
eight-group/24-photo holdout remains byte-unread. Existing correction gates,
face/visible-neck scope and automatic workflow remain unchanged.

Private artifacts: `outputs/ppr10k_native_anchor_comparison_v1`, including frozen
plan, raw detections, eight overlays, original results/artifact hashes and
independent verification/visual findings. Original results retain their initial
`visual_review_pending` field; the separately bound verification supersedes that
pending status without rewriting the original record.

- [Executed protocol](ppr10k-native-anchor-comparison-protocol-2026-11-09.md)
- [Saved diagnosis](ppr10k-anchor-diagnosis-2026-11-09.md)
- [Original support screen](ppr10k-automatic-support-screen-results-2026-11-09.md)
