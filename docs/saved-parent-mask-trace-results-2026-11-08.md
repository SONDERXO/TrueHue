# Where marked skin disappears — 8 November 2026

The main loss occurs in the face parser, before component association or
anatomical exclusions. This trace reconstructs the unchanged pipeline from
saved categories and landmarks. No detector, parser, occlusion model or correction
model was run or fitted. No application settings were changed.

## Findings

Five of the six annotated photos have saved intermediates. They contain 2,551
marked native pixels. The sixth photo failed landmark detection and is kept
separate; its 605 marked pixels cannot be traced through these stages.

| First stage excluding a marked pixel | Pixels |
| --- | ---: |
| Outside the actual-input crop | 0 |
| Parser does not classify it as skin or nose | 1,696 |
| Component association | 0 |
| Eye, brow and mouth guards | 6 |
| Nostril guard | 14 |
| Additional occlusion filtering | 148 |
| Retained in final diagnostic measurement | 687 |
| Total | 2,551 |

Of the parser's 1,696 excluded pixels, 1,494 are labelled background, 168 neck,
23 clothes, 8 hair and 3 lower lip. Neck exclusion can be appropriate for facial
measurement because some existing annotations include neck skin. These counts
are pipeline decisions, not verified per-pixel classification errors.

| Existing review | Marked pixels | Parser overlap | After anatomical and nostril guards | Final diagnostic overlap |
| --- | ---: | ---: | ---: | ---: |
| review_01 | 423 | 41 | 41 | 21 |
| review_02 | 479 | 140 | 140 | 129 |
| review_03 | 468 | 91 | 91 | 13 |
| review_04 | 567 | 49 | 49 | 48 |
| review_05 | 614 | 534 | 514 | 476 |

Final diagnostic overlap includes masks that failed the minimum measurement
requirement. Only 653 pixels are retained in usable measurements, as recorded
in the preceding reliability audit. Failed rows still leave the image unchanged.

All five visual trace boards were inspected. Forehead-only or fragmented parser
support is already present in several inputs. Component selection does not cause
the marked-skin losses in this subset. The occlusion filter makes a substantial
additional reduction in review_03, but cannot explain most overall loss.

## What this supports next

Focus the next intervention on the face parser, keeping object protection and
the correction model fixed. First inspect its preprocessing, crop coordinates
and the existing parser-comparison records for an identifiable implementation
mismatch. If no mismatch is found, specify one bounded parser-input comparison
before running any new inference. Do not automatically start a preprocessing
sweep, change the class list, remove guards, lower the pixel threshold or fit
another correction model.

This trace does not establish that lighting causes the parser failure, that a
different appearance transform will fix it, or that better masks alone will
resolve the four unwanted clean-photo corrections. Those photos have no manual
patch labels. Selected patches are not full-face ground truth and cannot measure
mask precision, fairness or independent accuracy.

## Reproduction and verification

- Script: `scripts/579_trace_saved_parent_masks.py`.
- Private outputs: `outputs/saved_parent_mask_trace_v1`.
- Reconstructed all five parent masks exactly from cached parser categories,
  component association, landmark exclusions and nostril guards.
- Verified all five native final-mask projections against saved masks, nested
  stage containment and disjoint accounting of all 2,551 marked pixels.
- Bound inputs and source code by SHA-256 and checked them before saving.
- No new annotations, training, inference, scientific admissions or app changes.

The trace preserves the completed correction experiment and all earlier artifacts.
