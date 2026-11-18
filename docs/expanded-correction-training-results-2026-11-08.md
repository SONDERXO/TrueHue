# Expanded correction training results — 8 November 2026

Adding more training photos helped the model leave clean photos alone, but reduced its ability to repair distorted photos. The candidate failed the requirements agreed before training and has not been adopted.

## What changed

- Added 80 technically usable originals from 32 publisher groups to the previous 22 originals from 10 groups: 102 fitting references across 42 groups.
- Added 810 usable distorted inputs and the 80 clean inputs: 890 new fitting rows. The full model used 1,117 rows, including the original 227.
- Completed the fixed 11 correction-tree fits: ten old-group-held development folds and one full fit.
- Kept the existing 56 MST calibrations, old features, action choices, masks, tree settings and evaluation cases fixed. No new MST fits or parameter sweep.
- Evaluated the same 756 conditions from 54 originals. Repeated conditions and folds are not independent photos or people.

See the [fixed protocol](expanded-correction-training-protocol-2026-11-08.md) and [input preparation results](expanded-input-preparation-results-2026-11-08.md).

## Main results

Lower error is better. RGB error measures the difference from the original photo in the fixed scoring regions; it does not measure perceived naturalness or true skin colour.

| Check | Previous model | Expanded candidate |
| --- | ---: | ---: |
| Unwanted clean edits, development | 2 / 22 | **0 / 22** |
| Unwanted clean edits, later photos | 2 / 18 | **0 / 18** |
| Core RGB error, development | 8.03 | 13.27 |
| Core RGB error, later photos | 9.76 | 14.34 |
| Core RGB harms, development | 1 / 176 | 0 / 176 |
| Core RGB harms, later photos | 5 / 144 | 0 / 144 |
| Core RGB beneficial outcomes, development | 106 / 176 | 62 / 176 |
| Core RGB beneficial outcomes, later photos | 84 / 144 | 51 / 144 |

All 40 clean photos with usable measurements were left unchanged. Another 14 clean photos had measurement failures and remained unchanged through the failure policy; those are not evidence of learned clean-photo protection.

The candidate still improved average core RGB error over leaving distorted inputs unchanged: 20.65 to 13.27 in development and 21.88 to 14.34 on later photos. However, it repaired fewer cases successfully than the previous model.

The second colour metric, CIEDE2000, showed the same core trade-off: development error rose from 3.44 to 5.15 and later error from 4.19 to 5.63. Core harm counts fell to zero under both metrics.

| Stress comparison | Previous model | Expanded candidate |
| --- | ---: | ---: |
| Development RGB error | 39.22 | 38.87 |
| Later RGB error | 43.95 | 43.86 |
| Development CIEDE2000 | 15.26 | 15.23 |
| Later CIEDE2000 | 16.68 | 16.84 |
| Development beneficial outcomes, either metric | 45 / 110 | 40 / 110 |
| Later beneficial outcomes, either metric | 43 / 90 | 35 / 90 |

One later stress case still became worse under both regional metrics. Across all evaluation attempts, whole-scene RGB harm counts were zero for development clean/core/stress and later clean/core, with one later stress harm remaining.

## Decision and limitations

The fixed requirements demanded clean preservation **and** no loss of recovery against the previous model, separately on both cohorts. Higher core errors, fewer beneficial outcomes and worse later stress colour error mean the candidate fails. We have retained it for research, without integrating it into either demo.

The clean result is a useful development milestone, not proof of general clean-photo safety. These evaluation groups have already been exposed during development. The separate eight-group, 24-photo holdout remains unopened; a failed candidate does not qualify for opening it.

Mask quality remains unverified. Visual review still shows partial facial coverage, patchy corrections and visible boundaries. In one selected improvement example, a smaller patchy edit reduced numerical error relative to the parent without establishing an acceptable-looking correction. Glasses and beard boundaries remain uncertain. Synthetic distortions and studio acquisition cues limit generalisation. Fresh highest-score groups were unavailable, so this does not establish fairness across all skin tones. The common-medium diagnostic recipes also do not yet fulfil the proposal's three tone-dependent recipe design or final evaluation split.

## Verification

- Independent training replay passed: 11 fits, 9,790 new feature rows, 137,060 new action costs, 1,100 repeated clean constraints, 163 nodes and 252,369 candidate split options. The clean occurrences include repeated use of the same originals.
- Confirmed all old fitting prefixes, frozen MST calibrations and 756 prediction features/exclusions stayed unchanged.
- Independently verified all 756 output images, 560 regional metric records, 756 scene metric records, protection/outside-alpha equality and 20,131 source hashes. Additional colour summaries and harm/benefit transition checks passed.
- Viewed all 59 fixed review boards on 15 contact sheets, plus four explicitly outcome-selected diagnostic boards. This was not visual inspection of every rendered condition.
- Focused tests: **8 passed in 2.79 seconds** (`test_image_loss_action_tree.py`, `test_aligned_correction_support.py`).

Scripts: 613–617. Private artifacts: `outputs/expanded_correction_models_v1` and `outputs/expanded_correction_comparison_v1`. The inherited candidate filename `face_local.png` is a legacy evaluator filename; this comparison retained whole-scene features.

## Next step

Use the saved action traces to explain which previously useful corrections were lost and whether the fixed action choices or tree decisions caused the loss. That diagnosis needs no new fit or holdout access. Keep the candidate frozen and do not start another sweep or relax the acceptance requirements after seeing these results.
