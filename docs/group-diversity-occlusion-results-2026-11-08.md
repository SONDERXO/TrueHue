# Broader cohort: final-mask stage — 8 November 2026

Completed the unchanged occlusion-filtering and correction-support stage for the
new development cohort. **80of96photos pass the final technical checks**, compared
with83parent-stage passes. This does not establish80clean skin masks or finish
the correction model. No correction model was trained or applied.

## What ran

- Reused the saved83parent inputs, landmarks and categories; no new detector,
  landmark or parser forwards.
- Exactly83new raw aligned CPU FaceOcc forwards, all completed. Same pinned
  checkpoint, bridge, normalization, zero-logit rule and minimum measurement size.
- Replayed the existing identity-control correction-support renderer and inward
  blend, including native alpha/protection projection. No photo was corrected.
- Kept all13earlier failures. Three additional inputs fail the unchanged1000pixel
  processing-frame guard after occlusion filtering:832,904and564selected pixels.
- All96attempts remain in the ledger. No failures were replaced or relabelled.
- The8holdout groups/24photos remain unopened. No fits, distortions, new labels,
  scientific admissions, app changes or external sharing.

## Coverage

| Descriptive source-score interval | Final technical passes | Attempts |
| --- | ---: | ---: |
| [1,3) | 22 | 24 |
| [3,5) | 23 | 24 |
| [5,7) | 18 | 24 |
| [7,9) | 17 | 24 |
| Total | 80 | 96 |

Nineteen of32publisher groups retain all three conditions. The16total failures
include13from the parent stage and3from this stage. Continuous score intervals
are descriptive, not integer MST categories. Groups are publisher identifiers,
not verified identities. There are no fresh highest-[9,10]groups in this roster.

Passing measurement masks occupy50–981native grid locations. Processing-frame
enlargement does not create additional detail; passing the1000normalized-pixel
rule alone cannot certify native measurement reliability.

## Visual assessment and limitations

Viewed **all96fixed boards in24contact sheets**, showing original, parent mask,
final measurement and correction support. Some masks cover broad facial areas;
others remain restricted to forehead, chin or isolated patches. Beard boundaries,
glasses frames/reflections and neck/crop support remain uncertain. FaceOcc's
visibility veto is not a dedicated beard classifier.

The renderer uses explicit `uncertain` glasses mode. Its recorded automatic
`requires_glasses_choice` flag is zero among available rows; visible glasses in
the review mean this is not evidence that glasses are absent or frames are
correctly detected. The intended clear-lens/rim behavior remains a separate
explicit-choice branch, not an automatic result established here.

Diagnostic masks/alpha may exist for failed final measurements. They are clearly
labelled, have no usable feature output, and must not be applied as corrections
or treated as admitted training evidence. Assistant inspection is not a new
human annotation set, skin ground truth or independent validation.

## Verification

Scripts602–605 prepare, run, finalize and independently verify this stage.
The existing isolated FaceOcc batch worker is reused without network changes.

Verified all83cached measurement-service replays,83identity-support replays,
83native measurement projections and83independent native alpha/protection
reconstructions. Checked206,056projected protected pixel occurrences (not
independent samples),744bound source hashes, all96roles/statuses and the pinned
83logit outputs. Verification adds no model forwards or fits. The private visual
completion receipt records every fixed board hash.

The focused measurement/coordinate/preview/native-projection suite passed19tests
in8.19seconds. These are software checks, not skin-mask accuracy or model quality.

Private gallery: `outputs/group_diversity_final_masks_v1/review_PRIVATE.html`.
All prior parent artifacts and older model experiments remain preserved.

## Next boundary

This completes the requested clean-input preparation stage. The next action is
to freeze a **single expanded-development training comparison**, including which
existing distortion recipes to use, actual-distorted-input masks, nested matching
MST, failure handling and exact acceptance criteria. The new holdout must stay
closed during model development. Do not launch a large synthetic batch or fit
from a mere technical-pass count.

Any such comparison remains exploratory with unverified skin support. It must
retain the known clean-photo regression cases and require clean preservation
alongside distortion recovery. More groups may improve generalisation, but the
present preparation has not demonstrated that improvement. No model-completion
date or all-tone fairness claim follows.
