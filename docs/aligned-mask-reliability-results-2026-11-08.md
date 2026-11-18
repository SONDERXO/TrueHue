# Saved-mask reliability diagnosis — 8 November 2026

The next development target is reliable skin measurement. The latest correction
model remains frozen and unadopted. This diagnosis uses existing outputs and the
completed six-photo patch review: no fitting, inference, new labels or app changes.

## Where inputs fail

Of 756 attempted inputs, 451 have usable measurements and 305 fail:

| Recorded reason | Inputs |
| --- | ---: |
| Too few selected skin pixels | 110 |
| Initial detector does not return exactly one face | 75 |
| No predicted facial skin overlaps the chosen face | 57 |
| Detector inside the measurement stage does not return exactly one face | 30 |
| No native correction support remains | 20 |
| Degenerate facial geometry | 11 |
| Required landmarks unavailable | 2 |

By stage: 75 initial-anchor failures, 176 parent-measurement failures and 54
final-masking failures. These are repeated synthetic conditions from 54 original
photos, not 756 independent people. Fourteen clean originals fail measurement;
leaving those unchanged is failure handling, not learned clean-photo protection.

## Comparison with the completed skin patches

The existing 36 polygons contain 3,156 native pixels across six clean photos.
Matching uses source hashes and exact original crop coordinates, not resized
screenshots. The latest usable measurement masks retain 653 pixels (20.7%).
Saved diagnostic masks, including failed measurements, retain 687 (21.8%).
Applied correction support covers 699 (22.1%). These are different quantities.

| Photo | Marked pixels | Parent diagnostic overlap | Final diagnostic overlap | Usable overlap | Outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| review_01 | 423 | 41 | 21 | 0 | Too few pixels after occlusion filtering |
| review_02 | 479 | 140 | 129 | 129 | Measurement available |
| review_03 | 468 | 91 | 13 | 0 | Too few pixels after occlusion filtering |
| review_04 | 567 | 49 | 48 | 48 | Measurement available |
| review_05 | 614 | 514 | 476 | 476 | Measurement available |
| review_06 | 605 | unavailable | unavailable | 0 | Landmarks unavailable |

For the five photos with saved parent masks, parent overlap is only 835 of 2,551
marked pixels (32.7%); final diagnostic overlap is 687 (26.9%). Much of the
missing marked skin therefore precedes the extra occlusion filter. That filter
also removes marked pixels, particularly in review_03. This localizes losses;
it does not establish which parser, landmark or geometric rule caused them.

Visual inspection of all six saved comparison boards confirms forehead-only
or fragmented coverage in several photos. Review_05 has much broader coverage.
Review_04 passes with only 52 selected native pixels, despite passing the
1,000-pixel check in the enlarged processing image. Enlargement does not create
additional original detail, and that check alone cannot establish reliability.

Some marked patches include neck skin, while the measurement targets facial
skin. These selected patches are a limited reference, not full-face ground truth.
The overlap percentages do not measure precision, contamination, overall mask
accuracy, independent generalization or fairness. Do not optimize a threshold
against these six exposed examples.

## Remaining clean-photo correction errors

Four clean photos still receive unwanted edits. Their native measurement areas
are 588, 125, 424 and 242 pixels; their correction areas are 716, 88, 451 and 181
pixels respectively. None has a manual patch annotation. Consequently this
audit cannot attribute these wrong actions to inaccurate masks. Both mask
reliability and action selection remain unresolved.

## Recommended next bounded step

Trace the existing parent-mask construction on the five annotated photos with
saved intermediates. Separate parser skin support, component association,
landmark exclusions and nostril removal; report where marked skin is lost.
Use cached categories and landmarks, with the correction model, detector,
thresholds and occlusion weights fixed. Keep review_06 as a distinct landmark
failure. Do not lower the pixel threshold or retrain correction merely to make
more cases pass. A specific repair should follow the trace evidence.

## Reproduction and checks

Script: `scripts/578_audit_aligned_mask_reliability.py`.
Private final outputs: `outputs/aligned_mask_reliability_audit_v3`.
Earlier v1/v2 diagnostic outputs are preserved; v3 adds parent-stage overlap.
The script refuses to overwrite its output directory.

Verified all bound input hashes, six exact source/crop pixel matches, independent
653/3,156 overlap reconstruction, 756-input failure accounting and four clean
errors. Viewed the six-board contact sheet. No new research fit or model forward
was run. Dataset permissions and scientific admission settings are unchanged.
