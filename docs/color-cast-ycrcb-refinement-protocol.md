# Single-factor YCrCb refinement for color casts

29 October 2026. Diagnostic inspection of the20color-only inputs shows loss at
the HSV gate even where existing YCrCb thresholds retain much of the original
reference support. Reference support is used only to diagnose/scoring loss,
not to build candidate masks. Freeze this one input-only refinement before
candidate generation: remove the HSV intersection, retaining the exact
face-local YCrCb bounds,5x5open/close/close,largest component then existing
eye/brow/complete-mouth exclusions. No oval restriction, extra filling, parser,
reference fallback, new thresholds or per-image parameter tuning.

Run both the20saved original references and their20color-only inputs with each
frame's own existing detector box and first-success margin landmarks. Rebuild
the original HSV AND YCrCb arm exactly to verify baseline parity. Missing
geometry is unavailable. Save color gates, exclusions, geometry and both masks.
Predicted oval is a diagnostic boundary only, never candidate input support.

Report source-matched support screen, reference/input overlap and outside-oval
pixels. More support is not accuracy, and the old reference is not pixel truth.
Candidate reference changes require regression review too; existing human
acceptance is not transferred. No candidate ITA/MST, target fits or tree fits.
The current lookup is not calibrated for this new measurement definition.

Prepare a small review packet only after reporting complete denominators:
up to six old-fail/new-pass sources by fixed SHA256(`color_ycrcb_review_v1/`+ID),
plus up to two regression/risk cases (old-pass/new-fail first, then greatest
increase in color-input outside-oval pixels; tie by same hash). Deduplicate.
This is a purposive development review, not an independent evaluation or an
admission rule. Show original reference/baseline and candidate reference, plus
color input/baseline and candidate input. Ask whether the candidate pair is
usable and preserve concerns. All other candidate masks remain held.

Reserve a separate training check only after policy freeze; keep the current12
reserved and validation/test closed now. Preserve all original notes and
failed cases. Do not promote merely from a retention gain.
