# Actual-input masks and blended correction are now evaluated together

7 November 2026. Completed the user-approved
[pipeline-alignment cycle](aligned-correction-pipeline-protocol-2026-11-07.md).
The preparation, matching MST calibration, joint-tree training and native-image
comparison are implemented and verified. **The model still changes clean photos
and has substantial measurement failures, so it is not adopted.**

## What changed

- Every one of the fixed 756 synthetic inputs receives its own detection and
  mask attempt. No original-photo mask or anchor is borrowed for input features
  or correction application. All 54 original photos and all failures remain.
- Measurement and correction regions are separate. The correction uses the
  current desktop's parser/FaceOcc composition, face/visible-neck support,
  object protection and inward blending, rather than a hard measurement patch.
- Floating correction strength is projected back to the original224 image.
  Conservatively projected protected pixels have zero alpha. Pixels outside
  alpha and on the projected protection mask remain exactly unchanged.
- Learning uses rendered error in the broader native correction region, with
  a matching experimental ITA+Lab MST calibration. Old MST parameters are not
  reused on changed measurements. The original unrestricted joint action-tree
  design, depth and 14 per-fit action libraries stay fixed.

### Framing is an explicit candidate change

The present desktop resizes the whole photo to256. A clean-photo preflight found
that only **20/54 passed its parent measurement stage**, before FaceOcc. The other
34 failed: 7 semantic-mask, 25 measurement and 2 nostril-measurement failures.
This is not a full end-to-end desktop success rate.

The shared preparation candidate therefore uses the already established fixed1.5
native face crop, detected from each actual input, before normalized256 masking.
The1000working-pixel requirement remains unchanged. No detector fallback or
threshold tuning is added. Unlike the earlier research path, parser and FaceOcc
inputs use original appearance, matching desktop preprocessing, without CLAHE.

This aligns masking logic and the intended operator, but **is not identical to
the currently deployed desktop geometry**. The desktop and Android are unchanged;
using this candidate later would require its matching framing/calibration bundle.
Upsampling adds no native detail. Correction outside the crop is unavailable,
so the method does not guarantee correction of the entire visible neck.

Research glasses mode is fixed to uncertain because per-photo clear/opaque labels
are unavailable. Predicted lenses remain protected; no labels are invented.
The existing explicit clear-lens/rim branch is preserved, not newly validated.

## Availability is a major limitation

| Preparation | Development | Later |
| --- | ---: | ---: |
| All attempted inputs | 420 | 336 |
| Usable actual-input measurement and correction | 246 | 205 |
| Usable clean photos | 22/30 | 18/24 |
| Conditions with a usable clean reference region | 308 | 252 |

There are **451 usable inputs and 305 failures** overall.505 inputs passed parent
preparation and received one FaceOcc forward;451 remained usable after the final
measurement/correction checks.485 projected alphas exist, including diagnostic
alphas from some failed measurements; failed rows never apply correction.
The fixed source list was not replaced with easier examples.

Eight development and six later clean attempts return unchanged because preparation
fails. They must not be counted as successful learned clean protection. Regions
are scored only where a successful clean-reference correction support exists.
The scoring union also includes the actual input's applied support, penalizing
both missed expected regions and unwanted changes within that union. This is
an unverified photographic-region reference, not complete facial skin truth.

## Correction results on the new common regions

Both comparison models use exactly the same new alpha and scoring mask per input.
“Parent” means the previous research joint tree's saved controls, with their old
feature provenance, applied through new alpha. It is not the historical desktop
baseline, nor a parent model fed incompatible new measurements.

Mean native-region RGB MAE; lower is better. Missing predictions/masks return
the input unchanged and remain in the end-to-end ledger:

| Region-scored conditions | No correction | Parent controls + new alpha | Newly aligned tree |
| --- | ---: | ---: | ---: |
| Development clean,22 | 0.00 | 1.59 | 1.59 |
| Development core,176 | 20.65 | 8.10 | 8.03 |
| Development stress,110 | 52.05 | 39.23 | 39.22 |
| Later clean,18 | 0.00 | 2.53 | 0.80 |
| Later core,144 | 21.88 | 9.12 | 9.76 |
| Later stress,90 | 56.01 | 44.33 | 43.95 |

**Do not compare these numbers directly with the old2.83/6.00:** geometry,
support, scoring and technical availability have changed. On conditions with
both predictions and reference regions, development core is5.37 to5.29
(147conditions); later core is7.42 to8.14 (128conditions). Later stress on the
51common predicted/scored conditions slightly worsens29.86 to29.92, despite the
small end-to-end stress mean improvement. This is not a uniform model improvement.

The aligned tree changes **2/22 usable development clean photos and2/18 usable
later clean photos**, versus2/22 and3/18 for parent controls on new alpha. Thus
both zero-clean screens still fail. Development core reference harms are1/176
versus parent2/176; later5/144 versus6/144. Stress harms are0/110 versus0/110 and
1/90 versus2/90. These counts include repeated conditions, not independent people.

The former later bright-face clean failure is unchanged, but two later clean
colour edits remain (7.98 and6.50 MAE). The development forehead darkening remains
24.19 on88 native reference-region pixels; another clean edit is10.77. The worst
later core regression adds29.62 MAE versus input. Full-scene error can dilute
these small but visibly harmful facial patches and is reported separately.

The recovered warm detector-fallback case now has a measurement failure and no
correction. That is a preparation no-op, not evidence the tree learned to reject
its previously harmful action; its original facial reference is still unavailable.

## Matching calibration and fitting

Exactly **56** matching ridge1 MST calibrations cover full/single/pair publisher
exclusions. Fitting-row MST excludes the row's publisher key and outer held key;
held development predictions exclude their publisher; later predictions use only
development calibration. The clean calibration pool is22photos across10publisher
keys. Later labels never enter fitting. No scientific admission flags are enabled.

Exploratory clean MST MAE is0.65 across22held development clean measurements and
0.75 across18later clean measurements. Different masks and available photos mean
these do not establish improvement over earlier MST results, independent accuracy
or fairness. Publisher groups are not verified identities across datasets.

Exactly **11** joint action trees were fitted. The full fit uses227usable,
reference-supported development conditions, including22clean originals. All220
repeated fitting-clean occurrences stay unchanged. The action libraries are the
parent's frozen per-fit libraries; there are no new target optimizer fits.
The12original features include ITA and MST, but no fitted split selected MST and
only one split across the11trees selected ITA. Scene lightness remains dominant.

## Verification and review

- Three generated-array tests passed in6.55seconds: native projection/protection,
  partial-alpha cost agreement with the renderer, and invalid-input rejection.
- Preparation checks pass for756scene replays,681normalized-image replays,
  451measurement replays,485alpha projections and560regional input metrics;
  10,903bound hashes. This verifies implementation, not mask truth.
- Learning checks pass for56calibration equations,2,270nested fitting features,
  31,780action costs,220clean constraints,165nodes,52,971split alternatives and
  756predictions;10,909source hashes. No verification refits models.
- Output checks pass for2,268RGB8 outputs and protection checks,1,680regional
  metrics and2,268scene metrics;10,913source hashes and all756attempt records.
- Viewed all59fixed mask boards and59fixed correction boards through15contact
  sheets each, plus four explicitly outcome-selected worst clean/core boards.
  Missed skin, partial/fragmented measurements and visible correction boundaries
  remain. No new annotation or repeat manual-review task was requested.

Code: scripts569–577, `src/model_training/aligned_correction_support.py` and
`tests/test_aligned_correction_support.py`. Private outputs:
`outputs/aligned_correction_preparation_v1`, `outputs/aligned_action_tree_models_v1`
and `outputs/aligned_action_tree_comparison_v1`. All older artifacts remain intact.

## Decision and next boundary

The pipeline alignment is implemented and reproducible. It exposes real masking
and availability limits that a borrowed-mask comparison cannot represent. It
does not finish the model, establish naturalness or justify integration.

Keep this as a versioned development pipeline/candidate. Before another model
variant, prioritize the remaining masking/measurement reliability and clean
wrong-action mechanisms, using existing saved traces and completed patch reviews
where applicable. Do not automatically repeat fits, change appearance/guards,
add fallback, tune thresholds, search datasets or start another annotation round.
No new fit is selected by this result.

No desktop/Android change, dataset redistribution, contact, external sharing,
publication, commit or push. Scientific admission flags remain false. All cohorts
are small, exposed and synthetic, and repeated conditions do not establish
independent real-world accuracy, fairness or true skin colour.
