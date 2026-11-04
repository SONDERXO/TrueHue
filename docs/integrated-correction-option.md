# Integrated correction option — 23 October 2026

Follow-up: [mask versus parameter diagnosis](mask-vs-parameter-results.md)
separates the remaining overcorrection from residual mask failures.

`material_hair_veto_v1` is now available as a named Python development correction
option. It uses the existing guarded color check plus MediaPipe hair removal.
The raw semantic face-skin mask is not used. Estimation and the trained tree
remain unchanged; no training or dataset expansion occurred.

## Correct one image

Run from the project root:

```text
venv/Scripts/python.exe scripts/39_correct_image.py --image "path/to/photo.jpg" --mask-policy material_hair_veto_v1 --output-dir outputs/my_correction
```

The output folder contains `corrected.png`, `comparison.png`, both estimation
and correction masks, and metadata with features, parameters, policy version,
model checksums and timing. Existing output folders are never overwritten.
The original input file is not changed. Inference makes no network calls.

The available policies are `estimation_mask_v1` (legacy application mask) and
`material_hair_veto_v1`. Select the new option explicitly; the command defaults
to the legacy policy. Missing segmentation weights, invalid statistics or
unavailable landmarks fail explicitly, without falling back to another policy.
Failures are recorded in `failure.json` when an output folder can be created.

For regions that must remain untouched, add:

```text
--exclude-mask "path/to/protected_regions.png"
```

This mask must match the decoded input dimensions; every nonzero pixel is
protected from correction. It can mark paint or any other region, even if the
original skin mask includes it. It affects correction only, not estimation.
The automatic color check excludes the reviewed paint points but is not a
universal paint detector. It checks proposed additions and retains existing
baseline support. No guarantee is made for unmarked, unreviewed painted areas.

## Controlled integration check

The exact single-image runtime was exercised on all 24 existing controlled
attempts, using both policies. Results:

- 23 successful pairs, producing 46 corrected policy outputs.
- The original excluded source22454/color-shift remains excluded under both
  policies: only231 skin pixels versus the1,000-pixel minimum.
- Zero unexpected failures; no missing-feature imputation or policy fallback.
- Identical estimation masks, features and predicted parameters across policies.
- All seven prior validation/stress outputs reproduce the earlier legacy and
  semantic-hair-veto images exactly; application masks also match.
- All48 frozen point observations on12 clean/shifted review inputs match the
  earlier hair-veto results. Every reviewed paint point remains unselected and
  its output pixel is exactly unchanged.

| Mean color error, lower is better | Legacy | New option |
| --- | ---: | ---: |
| Development validation:3 variants,1 source | 7.609 | 6.643 |
| Separate clipped stress:4 pairs | 13.916 | 13.741 |

The16 training pairs were checked separately as reconstruction diagnostics,
not held-out evidence (mean5.637 legacy versus5.484 new). The stress set is not
independent; its input-only color error was7.227 in the original prototype run,
so correction still makes those examples worse despite the slight improvement
over legacy. This is integration verification, not a newly trained or validated
thesis model.

## Visual review

All eight source boards were inspected by Codex, covering the23 successful
controlled pairs. The original source19 color-shift patch is substantially
reduced. Residual cheek/forehead boundaries remain in12288 and22211, lower-face
patches remain in22454, and bright/warm stress examples51739 and6236 visibly
overcorrect. Some darker/shaded inputs still show uneven correction. These are
technical observations, not human approval or expert aesthetic scores.

The supplemental16798 painted input was also inspected: the reviewed painted
pixels remain unchanged, but full paint boundaries have not been human-annotated.
Source29962 remains rejected for training; its correction demonstration does
not change that decision. No source eligibility or earlier human label changed.

Start with [the visual review index](../outputs/integrated_correction_v1/review-index.md).
Each source board shows reference / input / legacy / new option, one variant
per row. Supplemental point-input comparisons are linked there too.

## Implementation and verification

- `src/correction/correct_image.py`: input-only estimation statistics, prediction,
  versioned correction masks and explicit protected pixels.
- `scripts/39_correct_image.py`: reusable runtime and single-image command,
  reusing the frozen detector/complete-mouth estimator through the existing
  preparation adapter. This remains a development runtime, not Android code.
- `scripts/40_validate_correction_option.py`: controlled and frozen-point checks.
- `scripts/41_make_correction_review_boards.py`: source boards and review index.

436 tests passed, including feature/parameter invariance, removal of baseline
hair, preservation outside the application mask, explicit paint protection,
unknown policy rejection and failure without required dependencies. A real
single-image command and the full integration run also succeeded. Output/input,
model, source-manifest and frozen-label checksums are recorded.

Validation artifacts are in `outputs/integrated_correction_v1/`: attempts,
expected failures, metrics, point results, per-image outputs, hashes and a
completed run-status file. Re-running a script requires a fresh output location
or a separately versioned run; artifacts are not silently replaced.

The option is integrated for controlled development, not promoted as a final
method. Resolve the documented uneven masks and overcorrection before expanding
training. No MST mapping, approved methodology, reserved test set, model weights
or Android files were changed by this integration.
