# Native versus 256x256 preprocessing

23 October 2026. Development comparison only. Follow-up to
[method decisions](method-decisions-2026-10-23.md).

## Results

All eight sources succeeded at native 224x224 and explicit 256x256 processing.
Native measurements exactly reproduce all four stored Lab/ITA values.

| Source | Native skin pixels | 256 skin pixels | ITA change, degrees | Mask agreement (IoU) |
| --- | ---: | ---: | ---: | ---: |
| 62331 | 31,034 | 38,586 | +0.772 | 0.930 |
| 12288 | 30,676 | 40,045 | +0.030 | 0.978 |
| 22211 | 24,468 | 31,021 | +0.900 | 0.957 |
| 51739 | 32,496 | 41,389 | +1.042 | 0.942 |
| 22454 | 29,866 | 38,092 | +0.568 | 0.954 |
| 19 (development-validation) | 32,453 | 39,319 | +3.862 | 0.908 |
| 6236 | 30,950 | 41,041 | -0.276 | 0.973 |
| 75027 | 29,495 | 38,703 | +0.130 | 0.956 |

Larger raw pixel counts partly reflect the larger image, not better coverage.
IoU compares the mapped native mask with the independently recomputed square
mask; neither is ground truth. All originals were square, so this does not
test non-square image warping.

## Procedure and checks

Script 49 resizes before detection using OpenCV INTER_LINEAR, the configured
256 square, YuNet threshold 0.85, fresh face crops/landmarks and
`v2_complete_mouth_v1`. Each branch measures its own selected pixels, retaining
the 1,000-skin-pixel minimum. Old boxes are not reused. Nearest-neighbor mapping
of native masks is used only for comparison, never for square measurement.

Saved evidence includes input images, full-image masks, face coordinates,
measurements, failures and hashes. Source/model/table hashes match before and
after execution. No correction model was loaded or fitted. The existing
224x224 training table and runtime defaults remain unchanged.

Codex visually inspected all eight boards. Boundary and exclusion changes
remain, with source19 showing the largest ITA shift. Hair/background inclusion
still exists in places, including source12288. These are estimation masks, not
corrected images, fresh human acceptance or measured segmentation accuracy.

## Targeted SCIN check

Of 368 head/neck plus at-distance metadata candidates, nine were found locally
and 359 were unavailable under the checked filenames. The fixed processing
bound was 24, one image per case; all nine available candidates were checked
at 256x256. All returned zero detected faces, and none entered training.

Codex inspected all nine previews: partial/obscured faces, close views of
neck/skin, other body parts and an upper-body scene. Case-level head/neck does
not ensure that a selected image is facial. Zero detections do not prove an
image contains no face. The 359 unavailable candidates remain untested, not
rejected. No new image download or human-review-label change occurred. No
eligible-cohort label coverage is claimed because none passed the check.

## Artifacts and next step

Completed follow-up: [existing distorted-input robustness check](square-distorted-input-results.md).
All 37 previously successful attempts remain successful at 256; the original
exclusion remains excluded. No training pairs were regenerated or model fitted.

- [Review boards](../outputs/square_preprocessing_complete_v1/review-index.md)
- [Evidence](../outputs/square_preprocessing_complete_v1/summary.json)
- [SCIN contact sheet](../outputs/square_preprocessing_complete_v1/scin_review_sheet.png)

Reproduce in a fresh directory:

```text
venv/Scripts/python.exe scripts/49_compare_square_preprocessing.py --output-dir outputs/square_preprocessing_new_run
```

The first run failed while serializing NumPy face coordinates after completing
measurements. Partial artifacts remain in `outputs/square_preprocessing_v1`.
The integer-coordinate fix and separate completed run above succeeded.

Next, check the 256 procedure on already-created development distortions before
building a separate square-resolution pair table. Regenerate features and masks
together; do not relabel the existing 224 table as 256. Keep clipped stress
separate. This does not resolve MST mapping or authorize final training. SCIN
needs further bounded suitability work; nine local failures do not establish
that the entire dataset is unusable.
