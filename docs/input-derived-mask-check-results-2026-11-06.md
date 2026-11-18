# Input-derived masks: end-to-end experimental results

6 November 2026. Completed the [frozen protocol](input-derived-mask-check-protocol-2026-11-06.md)
on the same development-exposed 24 originals / eight publisher keys / 336 saved
whole-scene inputs. No new subjects or model, gate, MST or target fits. The saved
frozen_split_candidate_v1 bundle is unchanged. This is an experimental pipeline
check, not Android integration, new independent validation or production adoption.

The automatic path still improves average selected-region reconstruction error,
but loses substantial benefit when masks must come from the distorted input.
Detection failures, variable support, changed colour measurements and gate actions
all contribute to this combined pipeline comparison; it does not isolate a single
causal component. Clean-image preservation repeats the earlier result.

## What changed

Each actual distorted 224-pixel input independently passed through source-face
anchoring, native crop, redetection/landmarks, CLAHE parser-copy and aligned CLAHE
FaceOcc-copy. Original RGB supplies colour statistics. Detector 0.85, visibility
logit > 0, the 1000 normalized-measurement-pixel guard and existing assets remain
fixed. Candidate inference and application never use the original mask or crop.

Project each candidate mask back to its own native scene coordinates; render the
predicted three controls directly on those pixels. No mask fill, feathering or
corrected-RGB resize. Borrowed-support comparators use the previous saved controls
and original native mask, with this same renderer. Thus these numbers differ
from the previous 256 working-crop report and must not be mixed with that table.
The native scoring grid is not a new lower measurement guard or independent N.

## Availability and retained failures

| Layer | Attempts | Input-derived measurement available | Original reference region available |
|---|---:|---:|---:|
| Clean | 24 | 23 | 23 |
| Core | 192 | 177 | 184 |
| Stress | 120 | 75 | 115 |
| Total | 336 | 275 | 322 |

288 parser forwards; 276 CPU FaceOcc forwards, all successful as model calls;
275 final measurements/features. Failures: 30 source-anchor, 18 crop-redetection,
5 degenerate geometry and 8 insufficient-pixel failures (seven before FaceOcc,
one after). All 61 return the actual distorted input unchanged; none are removed
from attempt counts. Two core variants of the originally unavailable source
recover a measurement; their full-scene scores exist, but original-region scores
remain unavailable. No reference region is fabricated for that source.

The inherited preparation console says '/30' although it processes 336 records;
this is old display text, not the denominator. JSON records and summaries bind
336 attempts. Scientific admissions remain false for every input.

## Matched native-region reconstruction

RGB MAE in 0–255 codes. All paths use the same original native reference region,
including unchanged fallbacks. Reference-region denominators are 23 / 184 / 115;
unsupported originals remain in attempt counts, without a fabricated error penalty.

| Path | Clean MAE | Core MAE | Stress MAE |
|---|---:|---:|---:|
| Unchanged distorted input | 0 | 21.3913 | 54.6626 |
| Borrowed mask, ungated | 3.2351 | 3.6955 | 24.6431 |
| Borrowed mask, gated | 0.02774 | 15.4275 | 24.1107 |
| Input-derived mask, ungated | 3.2351 | 7.4392 | 38.1722 |
| Input-derived mask, gated | 0.02774 | 17.7450 | 37.7131 |

Input-derived gated equal-key MAE: 0.02659 / 17.6367 / 37.5054.
Its relative CIEDE2000 means: 0.03013 / 6.8035 / 14.9001; borrowed gated:
0.03013 / 6.0285 / 10.3349. These are relative reconstruction measurements on
an imperfect original support, not segmentation or physical skin-tone accuracy.

Gated harm versus unchanged: one clean, two core, zero stress cases on available
reference regions. The gate acts on 1 / 39 / 54 cases by layer. 22/23 measurable
clean photos are exact no-ops; the unavailable clean input is also unchanged.
The same 24 clean pipeline statuses repeated, with exact masks, geometry,
features and gate decisions on the 23 available originals. No new clean harm was
introduced by this pipeline switch. Ungated harms are 23 / 28 / 3 by layer.

The gate suppresses 110 core and 18 stress predictions that would improve the
reference-region RGB error. Failures also suppress correction, so low harm counts
must be read together with availability and residual error. 15 core and 41 stress
MST predictions saturate the allowed score range; none of the clean ones do.

## Mask agreement, visible output and scene scores

Among successful paired masks, median native-mask intersection-over-union is
1.000 clean, 0.775 core and 0.7045 stress. This measures agreement with an
imperfect original mask, not skin accuracy. In 39 core and 53 stress reference-
available cases, gated correction changes pixels outside that original mask:
811 / 2500 native pixels summed across cases. Those are neither verified skin
nor automatically object errors; no dense material truth is available.

Viewed all 72 preselected clean / combined_cool_under / stress_combined_over
panels across all 24 sources, including failures and predicted-mask overlays.
Forehead-only regions, missing cheeks, glasses/reflection uncertainty and hard
corrected-region boundaries remain. Some severe inputs return unchanged where
the borrowed-support output could correct a selected region. Some successful
outputs still visibly contain corrected islands. Whole-face output quality and
object protection are therefore not established by the selected-region gains.

Full-scene RGB MAE, over all 24 / 192 / 120 attempts:

| Path | Clean | Core | Stress |
|---|---:|---:|---:|
| Unchanged | 0 | 22.8356 | 59.6245 |
| Borrowed gated | 0.000241 | 22.7897 | 59.3554 |
| Input-derived gated | 0.000241 | 22.8036 | 59.4412 |

Most scene pixels are background/clothes/chart outside the facial application
region, so these small global changes are context diagnostics, not a facial-
correction success score. Full-scene gated harm counts are 1 / 2 / 0 as well.

## Verification and disposition

276 saved visibility-service replays checked final mask construction. Script 516
verified source/artifact hashes, no training/evaluation-key overlap, 275 actual-
input feature/MST/gate/portable-control replays and native mask projections;
1680 exact saved render/metric replays; gate action/fallback semantics; unchanged
pixels outside the application mask; and all 24 clean-pipeline repeats. No fits
were made during verification. 40 focused tests passed in 38.65 seconds.

Private artifacts: outputs/input_derived_mask_check_v1 (inference),
input_derived_correction_v1 (outputs and review_PRIVATE.html),
input_derived_assessment_v1 (verification), input_derived_visuals_v1 (fixed review).
Scripts 513–517 reproduce the stages. Existing inputs, frozen model and prior
results were preserved. This comparison is closed without retry or tuning.

The next priority is input-mask reliability and correction-region coverage,
rather than a larger correction tree. A next repair must target a specified
failure mechanism and preserve object exclusions; simply filling holes or
lowering guards is not justified. No further intervention, subject expansion,
refit, runtime integration or new review task is activated by this result.
No claim of a finished model, fairness, arbitrary-lighting generalization or
highest-interval coverage. Dataset research/noncommercial/citation/no-
redistribution conditions remain; no contact, sharing or submission occurred.
