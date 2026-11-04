# Input-only correction coverage — 22 October 2026

Follow-up: [guarded fill and broader checks](guarded-correction-support-results.md)
reduce expansion near boundaries and document remaining hair/paint failures.

A geometric fill removed most of the large central patch in the color-shift
development example. It also expanded correction outside the original region,
so it remains a candidate experiment, not the default pipeline.

## Cause and candidate

In the color-shift variant of FairFace 19, the raw HSV gate rejects 19,834
pixels of the original generation region inside the detected crop; YCrCb rejects
4,671 (overlapping with HSV). After cleaning, the candidate mask rejects 20,201;
largest-component filtering removes another 181 and anatomical exclusions remove
25 of the remaining pixels. Another 486 original-region pixels are outside the
detected crop. The primary loss here starts at the color gates, rather than at
the mouth exclusion. Counts describe this example, not all images.

The candidate forms a convex hull around the input's existing skin support and
then removes its eye, eyebrow and complete-mouth exclusions. This bridges gaps
without using a clean reference, known distortion parameters or clean mask.
It cannot extend past the input support's hull or detected crop. Empty and
degenerate support fails explicitly. No threshold ranges were tuned.

Only the correction application mask changes. The ITA/Lab estimation mask,
four input features, saved tree and predicted parameters remain unchanged.
There is no refitting or feathering in this comparison. Original hard-correction
images were reproduced exactly. Source masks enter only subsequent scoring and
diagnostics, not selection of the candidate support.

## Results

| Mean color difference (lower is better) | Original support | Filled support |
| --- | ---: | ---: |
| Development: 3 variants of one source | 7.609 | 6.483 |
| Clipped stress: 4 pairs, not independent | 13.916 | 13.969 |

Development RGB MAE changed from 0.06295 to 0.06240. Coverage of the fixed
generation region rose from 75.6% to 96.4% on average. In the color-shift case,
coverage rose from 35.6% to 97.2%, and color error fell from 8.227 to 4.898.
The dark variant improved slightly; bright/warm in-region error was unchanged.

The fill also increased pixels outside the generation region: development mean
350 to 673, stress mean 377 to 1,230. Outside-region RGB error rose from 0.00109
to 0.00199 on development and 0.00156 to 0.00463 on stress. The generation region
is not human ground-truth skin; these counts show changed support, not a measured
non-skin false-positive rate. Visual inspection of all three development sheets
and stress source 22454 shows the large patch improves, but expansion near
feature boundaries and the face outline requires care. Narrow seams and model
parameter errors remain. No expert aesthetic rating was collected.

## Verification and decision

Seven pairs attempted, seven succeeded; earlier failed pairs remain in the
original exclusion table. 415 tests passed, including exclusions, geometric
bounds, nonmutation and explicit failure for invalid support. Saved model and
input hashes, unchanged features, original masks and baseline images were
checked. The reserved final test set was not used.

Run `venv/Scripts/python.exe scripts/30_compare_correction_support.py` from the
project root. Outputs are in `outputs/correction_support_v1/`: comparison PNGs,
original/filled masks, corrected images, gate diagnostics, metrics, failure ledger
and hashed summary. The script refuses to overwrite a previous run.

Keep this candidate isolated. It was developed after viewing validation results,
so these scores are exploratory, not fresh held-out evidence. Do not claim a
final 6.48 thesis score or generalization improvement. Before adoption, compare
coverage and spillover on a broader development set with independently reviewed
skin/non-skin boundaries, including previously rejected hair and geometry cases.
Any change to estimation masks would separately require regenerated features and
versioned retraining. The approved proposal remains the target; no methodology
change is asserted by this experiment.
