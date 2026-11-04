# Completed eleven-mask review and paired training comparison

30 October 2026. Imported the user's exact downloaded decisions: **six accept,
five reject, zero pending**. All notes and timestamps are preserved. The six
accepted distorted examples pass technical admission checks, but adding them
to the fixed training procedure worsens clean-photo safety and total error.
The demo is unchanged and this candidate is not promoted.

| Distorted mask | Decision | Exact note |
|---|---|---|
| 62105 | Reject | (none) |
| 20648 | Accept | Did well on distorted photo, but lots of missing areas on face that didnt get captured |
| 56839 | Accept | (none) |
| 29880 | Reject | No facial coverage |
| 34227 | Accept | Lots of missing coverage in face. Plenty holes |
| 85815 | Accept | (none) |
| 72400 | Accept | Acceptable, but buggy face mask on the edges |
| 68073 | Reject | captured teeth and bad facial coverage |
| 75898 | Reject | Bad facial coverage |
| 75166 | Reject | the mask didnt cover the whole face, lots of holes |
| 34458 | Accept | (none) |

The instructions allowed imperfections the user judged usable, so the three
acceptances with concerns remain acceptances with those exact concerns. They
are not relabeled perfect masks. The five rejected distorted masks stay out
of fitting. Earlier approval of their original clean masks is separate and
remains unchanged; all eleven eligible clean controls remain available.

## Admission verification

`scripts/264_import_distorted_mask_review11.py` verifies the export schema,
exact manifest SHA256, all eleven decision IDs, frozen boards/source hashes,
training-role guard, duplicate-screen disposition, reference acceptance,
original image/mask hashes, minimum measurement support, current measurement
contract, input-only Lab/ITA/experimental-MST parity and available positive
approximate target fit. No approval transfers to another recipe or mask.

`scripts/266_verify_reviewed_pair_targets.py` independently verifies all six
accepted target curves, saved fit residuals and quantization, intersection
pixel counts, convergence/rank and exact notes. Direct-exponent conversion
reproduces the legacy operator at output-pixel precision. These targets remain
reference-informed, bounded local RGB fits, not exact inverses or runtime
reference access.

The accepted cases have clipping fractions from 0.0105 to 0.6182 in the saved
preparation reports. Clipped stress admission was already an explicit research
choice; the reviews do not remove information loss or certify true skin color.
No new distortion generation, mask editing or hidden exclusions occurred.

## Fixed source-held comparison

The [protocol](reviewed-six-pair-training-protocol.md) was recorded before
training. Compare the existing 30 historical pairs plus eleven clean controls
against the same fitting rows plus six reviewed distorted inputs. Both methods
are evaluated on the same 47 pairs using the existing 26 source/known duplicate
groups. All variants of each held source are excluded from fitting. Five input
Lab/ITA/MST features, ordinary direct gamma/R/B targets, depth 3, seed 42,
minimum leaf size 1 and fitting-control protection remain fixed.

| Measure | Existing fitting data | Add six accepted pairs | No correction |
|---|---:|---:|---:|
| Historical 30 CIEDE2000 | 8.091 | 9.362 | 10.076 |
| Historical distorted 15 CIEDE2000 | 16.181 | 16.905 | 20.153 |
| All clean changed /26 | 2 | 5 | 0 |
| New distorted 6 CIEDE2000 | 12.793 | 12.766 | 21.408 |
| Original 41 CIEDE2000 | 7.314 | 9.405 | 7.373 |
| Combined 47 CIEDE2000 | 8.013 | 9.834 | 9.165 |

Lower error is better. New distorted error changes very little, while clean
harm grows and historical performance worsens. New candidate clean failures
are 1398, 20648, 29880, 56839 and 68073. Both procedures fail the unchanged-clean
requirement; the paired candidate also fails overall benefit against unchanged.
Do not attribute this failure to an incorrect user review or silently remove
accepted sources to improve the reported score.

`scripts/265_compare_six_reviewed_pair_additions.py --verify` passes **52
independent tree refits and 94 image/metric replays**, fitting-control membership,
exact accepted additions, source separation, outside-mask preservation, aggregate
gates and parity with the original 41 baseline predictions. New experiment
scripts do not change core libraries; the last full-suite result remains
790 passing tests, not a new full-suite run for this experiment.

Evidence is saved in `outputs/distorted_mask_review11_import_v1/` (unaltered
export, decisions, accepted pairs and both verification reports) and
`outputs/six_reviewed_pair_comparison_v1/` (frozen plan, trees, membership,
predictions, image outputs, summary and verification).

The result adds reviewed paired training evidence but does not finish the
correction model. Weak experimental MST calibration, limited tone coverage,
accepted coverage concerns, clipping and repeated development exposure remain.
No reserved validation/test data, photographer form or demo change occurred.
Further work needs a justified training design that separates clean and
distorted appearances; another automatic promotion or source-specific exception
is not supported. No additional review is required to complete this import.
