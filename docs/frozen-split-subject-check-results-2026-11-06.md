# Frozen correction candidate: separate-subject results

6 November 2026. Completed the fixed recipe and prospective bounded check in
[frozen protocol](frozen-split-subject-check-protocol-2026-11-06.md).
One experimental bundle was saved before processing the evaluation photographs:
one ITA+Lab ridge on 29 original development measurements, two depth-3 split
heads on 357 supervised rows and one benefit gate on 397 available rows.
The training features are saved own-key-held MST predictions; gate labels use
saved own-key-held joint-corrector benefits. This preserves the known gate-to-
split transfer mismatch. Four new estimator fits; zero new target fits.

## Separate selection and availability

Metadata-only selection froze eight publisher keys not among the 20 recorded
pixel-exposed keys, two per interval [1,3), [3,5), [5,7), [7,9). Each contributes
three fixed conditions: 24 original attempts and 336 synthetic attempts. All
highest-interval release keys were already exposed, so [9,10] transfer is untested.
No evaluation images, scores or outcomes entered fitting. These are separately
selected within-release publisher keys, not independently verified identities.

23 original measurements succeeded; one landmark/preparation failure remains
unscored across all 14 cases. Seven of eight keys have all three measurements.
23 parser and 23 CPU FaceOcc forwards; 23 saved service replays. There are 322
scored cases, 318 with correction features and four undefined-ITA stress cases
returned unchanged. Failure denominators remain 24 originals / 336 attempts;
available-case error does not assign a numerical penalty to unavailable cases.

## Correction outcomes

RGB MAE is in 0–255 codes, measured only on the saved original measurement mask.
Clean means no additional synthetic distortion; originals retain their actual
lighting. No intrinsic skin colour or illumination-neutral reference is asserted.

| Layer | Scored / attempted | Unchanged MAE | Split ungated | Split gated | Gated harms vs unchanged |
|---|---:|---:|---:|---:|---:|
| Clean | 23 / 24 | 0 | 3.1983 | 0.02736 | 1 / 23 |
| Core | 184 / 192 | 21.2622 | 3.6882 | 15.3168 | 2 / 184 |
| Stress | 115 / 120 | 54.2105 | 24.3407 | 23.8226 | 0 / 115 |

Gated equal-key RGB MAE: clean 0.02622, core 15.1496, stress 23.5477.
Gated CIEDE2000 means: clean 0.02998, core 5.9845, stress 10.2174;
unchanged core/stress 7.9553 / 20.6500. These are relative reconstruction errors,
not segmentation accuracy or physical skin-colour accuracy.

The gate preserved 22/23 clean images byte-for-byte; the remaining clean case
changed. It corrected 43/184 core and 90/115 stress cases. It skipped 116 core
and 17 stress cases where the saved ungated prediction would have reduced RGB
error. Thus clean preservation still trades against useful correction. Ungated
clean/core/stress harms: 23/23, 27/184, 4/115. No threshold adjustment followed.
90/318 available synthetic MST predictions saturated the permitted score range.
On original clean measurements alone, source-score MAE was 0.6675 over 23/24
available images. This is a separate exploratory association, not full-range
MST validation or evidence of intrinsic-colour accuracy.

## Visual review and verification

Inspected all 24 original source/native/mask boards and all 72 fixed clean,
combined_cool_under and stress_combined_over panels, including failure panels.
Masks remain fragmented in several cases; forehead-only regions, missed cheeks,
glasses/reflections and uncertain material boundaries persist. Corrected islands
can visibly contrast with uncorrected surrounding facial skin. A lower selected-
region error therefore does not establish an acceptable whole-face photograph.

Script 512 checked source/artifact hashes, training/evaluation key disjointness,
saved own-key-held training vectors and strict benefit labels; both heads'
training normalization and raw leaf means; gate weighted normalization; 318
feature/MST/gate/portable prediction replays; and 966 exact saved render/metric
replays, including unchanged pixels outside each mask. These checks do not prove
mask truth. 32 focused split/gate/scene/continuous-interface tests passed in
5.97 seconds. No verification refits were performed.

The reused original-measurement implementation/settings/assets are frozen; its
new execution binding ce5e92da... differs from the original training run's
19c20126... because the source dependencies differ. This is policy reuse,
not a claim that distinct source executions have identical contract hashes.

## Scope and next decision

This is encouraging separate-key evidence for conditional fixed-support
synthetic reconstruction. It is not a finished automatic correction model.
Original masks/crops are borrowed for synthesis, features, application and
scoring; masking was not rerun on distorted inputs. Background/chart scene cues,
224-pixel sources, mask contamination, limited subject count, the highest-range
gap and development-driven model selection constrain generalization.

Retain the frozen bundle as an experimental checkpoint, not production adoption.
The next recommended engineering test is a separately frozen end-to-end check
that derives masks from actual distorted inputs and assesses visible output
coverage/boundaries; its conditions and comparison need definition before running.
Do not silently smooth/fill masks, refit on these eight now-exposed keys, tune
the gate, expand the cohort or integrate the candidate into Android.

Private local artifacts: outputs/frozen_split_candidate_v1,
frozen_split_subject_check_v1, frozen_split_subject_evaluation_v1,
frozen_split_subject_assessment_v1 and frozen_split_subject_visuals_v1.
Scripts 507–512 reproduce selection, fitting, inference, evaluation and replay.
All scientific admission flags remain false. Dataset research/noncommercial,
citation and no-redistribution conditions retain. No runtime, Android, contact,
sharing, publication or submission action occurred.
