# Depth-four correction results — 8 November 2026

One extra decision level restored some useful corrections, but brought back an unwanted edit to a clean photo. The candidate failed the fixed requirements and has not been adopted.

## What changed

Completed exactly 11 correction-tree fits with maximum depth four instead of three. All expanded training rows, saved costs, features, correction actions, clean constraints and 56 MST calibrations stayed unchanged. No new MST fits, masks, image-model inference or parameter sweep. The full fit still uses 1,117 repeated conditions from 102 references across 42 publisher groups.

Evaluation used the same 756 conditions from 54 originals. The [protocol](depth-four-correction-protocol-2026-11-08.md) retained the original aligned model as the acceptance comparator; improvement over the rejected expanded depth-three model alone is insufficient.

## Main results

Lower RGB reconstruction error is better. “Beneficial” means lower error than the distorted input within the fixed scoring region, not a human judgment of naturalness.

| Check | Original aligned model | Expanded depth three | Expanded depth four |
| --- | ---: | ---: | ---: |
| Changed usable clean photos, development | 2 / 22 | 0 / 22 | **1 / 22** |
| Changed usable clean photos, later | 2 / 18 | 0 / 18 | 0 / 18 |
| Core RGB error, development | 8.03 | 13.27 | 11.78 |
| Core RGB error, later | 9.76 | 14.34 | 12.12 |
| Core beneficial conditions, development | 106 / 176 | 62 / 176 | 74 / 176 |
| Core beneficial conditions, later | 84 / 144 | 51 / 144 | 67 / 144 |
| Core harms, development | 1 / 176 | 0 / 176 | 1 / 176 |
| Core harms, later | 5 / 144 | 0 / 144 | 0 / 144 |

Compared with expanded depth three, depth four gained 12 beneficial core outcomes in development and 16 on later photos, losing none of that comparator's beneficial core outcomes. These are repeated synthetic conditions, not additional people. Average core error remains better than leaving inputs unchanged (20.65 and 21.88), but worse than the original aligned comparator.

Core CIEDE2000 colour error shows the same partial recovery: 5.15 to 4.61 in development and 5.63 to 4.91 on later photos, still above the aligned comparator's 3.44 and 4.19. Core harm/benefit counts under this metric match the RGB counts above.

| Stress result | Original aligned model | Expanded depth three | Expanded depth four |
| --- | ---: | ---: | ---: |
| Development RGB error | 39.22 | 38.87 | 39.08 |
| Later RGB error | 43.95 | 43.86 | 43.87 |
| Development CIEDE2000 | 15.26 | 15.23 | 15.28 |
| Later CIEDE2000 | 16.68 | 16.84 | 16.84 |
| Development beneficial conditions, either metric | 45 / 110 | 40 / 110 | 40 / 110 |
| Later beneficial conditions, either metric | 43 / 90 | 35 / 90 | 35 / 90 |

Stress harm counts remain zero in development and one later under both metrics. The worst later stress RGB excess over the distorted input rose from 24.86 in the aligned/depth-three models to 26.10. The 14 clean measurement failures remain unchanged through the failure policy and do not count as learned clean-photo preservation.

## The clean-photo regression

The unwanted edit is `case_28__clean`, a previously exposed development case. The new fourth decision uses whole-scene upper brightness (`scene_l_p90`). It routes this clean photo into a branch containing 56 fitting conditions and **no clean fitting examples**. That branch applies gamma approximately 1.428, visibly darkening the limited forehead correction region. Its regional RGB error is 24.56, versus zero when left unchanged.

The fitting clean constraints still all pass. They cannot protect a clean evaluation photo routed into a correction branch with no clean fitting examples. This is a saved-route observation, not proof that excluding scene brightness alone would solve generalisation.

## Decision

Rejected under the unchanged joint requirements: one unwanted clean edit, higher core errors and fewer beneficial outcomes than the original aligned model, and worse stress colour error. The extra level provides evidence that decision capacity was limiting some recovery, but does not resolve the safety/recovery trade-off.

Keep both candidates frozen. Do not automatically try depth five, relax clean requirements or open the separate eight-group, 24-photo holdout. No runtime or demo integration has occurred.

The next development decision should address how correction-only branches handle clean photos unlike the fitting examples, rather than continuing a depth sweep. Any alternative needs a specific protocol before fitting. Current evidence does not establish a reliable solution or a completion date.

## Verification and limits

- Independently confirmed exact parity of every fitting row, feature, cost, action, clean flag and frozen calibration with expanded depth three.
- Replayed 11 trees, 285 nodes, 338,221 greedy split options, 1,100 repeated fitting clean constraints and 756 predictions. All passed.
- Independently verified 756 rendered outputs, 560 regional and 756 scene metric records, protected/outside-alpha pixels, 20,135 source hashes, colour summaries and harm/benefit transitions. All passed.
- Viewed all 59 fixed boards on 15 contact sheets and four explicitly outcome-selected diagnostics. Partial coverage and patchy correction boundaries remain visible; this is not visual inspection of every output.
- Focused tests: **8 passed in 2.18 seconds**.

Previously exposed evaluation groups, synthetic distortions, acquisition-specific scene cues, uncertain skin masks and incomplete highest-tone coverage remain limitations. RGB/CIEDE2000 reconstruction is not true skin colour or perceived naturalness. These development checks do not fulfil the proposal's final evaluation design or establish fairness.

Scripts 622–625. Private artifacts: `outputs/depth_four_correction_models_v1` and `outputs/depth_four_correction_comparison_v1`. Legacy filenames `face_local.png` and diagnostic titles saying “expanded” refer here to the expanded-data depth-four candidate, not a face-local feature model. No new image-source or holdout reads were required for fitting; evaluation replay used only the existing prepared evaluation images.
