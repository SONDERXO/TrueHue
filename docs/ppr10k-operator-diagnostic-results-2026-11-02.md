# PPR10K: three controls capture much of the change, with visible limits

2 November2026. User explicitly authorised the recommended same-six-photo
gamma/red/blue diagnostic. **All six fitted faces moved closer to editor A,
but the expert look was not fully reproduced.** The wedding faces are visibly
pinker/flatter; some indoor shadow/colour differences remain. This supports
continued consideration of the operator, not automatic training or adoption.

Gallery: `outputs/ppr10k_operator_diagnostic_v1/review.html`.
Script: `scripts/392_ppr10k_operator_diagnostic.py`.

## Fixed diagnostic

Same six source/editor-A pairs from groups1398/1487 as script391, no new photos,
editor switching, discarded results or replacement batch. Input hashes verified
before processing. Numeric inputs are original embedded-sRGB TIFFs: RGB16 source
divided by65535 and RGB8 target divided by255, without source preview quantisation.
No dataset downloads or external contacts in this diagnostic.

Before fitting, source-only assistant polygons and the solver contract were
saved to `protocol.json` (SHA256
`7e6d7edcc96b039c313a963478dd8ee6f3724165820ac0e294f812474b670588`).
Selected the woman in each wedding frame and the single prominent indoor face.
These are approximate hand-selected face regions, not exact anatomical masks,
skin truth, new detector/parser/FaceOcc results or user annotations. They include
eyes/lips/makeup and can include hair or miss face edges. Neck is excluded.
This deliberately isolated face diagnostic does not replace the adopted
whole-face+neck correction support or its inward blending.

8x8 image blocks alternate fitting/checking within each polygon. The shared
`transform_rgb` operator applies gamma then red/blue gain, green gain fixed1,
with clipping. Each photo has one identity-start bounded least-squares run,
gamma/red/blue each in[0.25,4], minimising encoded-sRGB squared RGB error.
Tolerance1e-12; maximum2000 evaluations; no alternative objectives, mask tuning,
crop search, starting-point search or model/feature sweeps. All6 solver runs
converged with no active parameter bounds. This is a local numerical fit;
global optimality is not proved.

The editor target is supplied to choose each photo's parameters. These are
**target-aware per-photo approximations, not automatic predictions**. Spatial
check blocks come from the same photograph and share nearby content; they do
not measure generalisation. Both groups were publisher-validation and are
already TrueHue development-exposed. No source/subject-independent evaluation
or new skin-tone coverage is claimed.

## Results

Mean relative CIEDE2000 difference on check blocks, lower is closer to the
expert target. These compare image appearance in documented sRGB, not measured
skin-colour truth. No validated acceptable-error threshold was declared.

|Frame|Face-region pixels|Gamma|Red gain|Blue gain|Original difference|Fitted difference|
|---|---:|---:|---:|---:|---:|---:|
|1398_0|3823|1.741|1.106|1.022|17.35|5.61|
|1398_1|3618|1.796|1.090|1.031|17.42|5.31|
|1398_2|4048|1.754|1.098|1.042|16.86|6.18|
|1487_0|628|1.286|0.954|1.376|8.67|2.97|
|1487_1|1133|1.324|0.930|1.496|8.66|5.01|
|1487_2|1210|1.499|0.993|1.288|11.69|3.68|

Equal-weight mean of the six image means:13.44 ->4.79, a64.3% reduction.
This is descriptive of these six related photos; no significance or population
accuracy claim. RGB MAE, mean/median/p95 relative DeltaE and fit/check/all-region
metrics are saved in `results.json`; regional pixel counts are explicit.

Assistant visually inspected all six source/fitted/expert crop boards:

-1398_0/1/2: large brightness change captured, but fitted skin appears pinker
and flatter than the expert target. Expert contrast, highlights, lips and
surrounding colour are not reproduced exactly.
-1487_0: yellow facial cast reduced substantially; shadow and surrounding
scene remain different.
-1487_1: improvement with residual uneven shadows/colour, a small downward
face, fringe and neighbouring teddy-bear detail. Residual95th percentile9.72
retains poor local agreement rather than hiding it behind the mean.
-1487_2: face brightness/warmth moves toward target; residual hair/face-edge
and tonal differences remain.

Temporary output changes only the approximate polygon with hard edges. Visible
cutouts and unchanged neck/background are diagnostic rendering limitations;
they are not results from the adopted continuity/blending implementation. The
gallery does not claim a finished seamless portrait correction. Small faces
are enlarged with nearest-neighbour sampling so no new detail is implied.

Source/target stems, dimensions and visual scene correspondence match, but no
pixelwise registration certification or warp was performed. Misregistration,
approximate region placement, makeup/hair and small-image quantisation can
contribute to residuals. They cannot all be attributed to operator capacity.
Only one selected face per wedding photo was tested, not both faces or necks.

## Verification

All6 saved float outputs independently replay exactly using
`clip(source**(1/gamma)*[red,1,blue],0,1)` and polygon composition. Fit/check
partitions are disjoint and cover the face region; outside-region float pixels
remain unchanged. Six check-block metrics independently recalculated, matching
saved results. Known-parameter synthetic recovery passed with parameter error
below1e-7, checking solver/operator compatibility. Existing operator tests:
`venv\Scripts\python.exe -m pytest tests/test_synthetic_transform.py -q -p no:cacheprovider`
->14passed/0.39s. This is focused verification, not a new full-suite run.
`verification.json`, per-photo NPZ replays and artifact hashes are saved locally.

## Decision

The three controls are useful for broad brightness/colour approximation on this
sample, with remaining visible differences. Do not call them equivalent to the
expert edits or export these fitted parameters as automatic training labels.
No justified training cohort or reliable MST mapping follows from this result.
This bounded diagnostic is complete; no automatic expansion, clean-only fit,
new user review, correction-tree training or runtime integration.

Retain ITA + calibrated MST + facial statistics -> decision-tree gamma/red/blue
correction. Six oracle parameter fits occurred; zero MST/calibration fits,
zero correction-tree fits and zero detector/parser/FaceOcc passes. Existing
Python/Android demos, reserved roles and immutable delivery snapshots unchanged.
DAST/STW replies remain pending as user-reported, without inbox monitoring.
