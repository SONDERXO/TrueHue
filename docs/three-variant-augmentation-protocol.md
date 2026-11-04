# Three-variant development augmentation specification

29 October 2026. The paper requires three distorted versions per source but
does not define their recipes. Adopt the following **engineering decomposition
for a versioned development candidate**, not a claim that the paper supplied
these exact three formulas. Preserve the baseline and prior failed versions.

Use the same Table2 numeric settings and reference-estimated severity:

1. `exposure`: direct-power gamma, then contrast about0.5, then brightness/255.
2. `color`: additive R=cyan_red/255 and B=yellow_blue/255; green unchanged.
3. `combined`: direct gamma, contrast, brightness, then additive R/B shifts.

All operations are on normalized encoded RGB. Clip once at the end, then round
to uint8. Save pre-clipping pixel/channel counts on reference generation
support. Combined must be byte-identical to the previous direct-gamma
sensitivity candidate. Do not lower severity or choose parameters after results.
Brightness/contrast units, additive channel interpretation and operation order
remain explicit implementation choices, not uniquely specified by the paper.
Direct gamma follows PDF38; the table's “midtone” wording tension is disclosed.

Keep one unchanged identity control per source in addition to the three
distortions. Generate only for the same20 technically usable human-accepted
original-rule-mask training references. Preserve reference concerns including
16033hair. No new source selection or claimed category balance. All variants
inherit source/duplicate group; no source crosses a later fitting fold.

Apply edits only on the unchanged reference generation mask. At measurement,
run detection and original rule-mask estimation on the actual variant pixels,
never borrowing reference geometry/features. Reference mask is used only for
generation, approximate target construction and diagnostics. Original controls
use their verified saved measurements and exact[1,1,1] target.

For each available input, use the frozen target-construction routine and
explicitly convert legacy gamma coordinates to direct gamma, preserving the
old report. Save failed inputs/targets, clipping, existing support screen,
input-only ITA/MST features and exact user reference notes. The lookup remains
experimental; this is not a new calibration. New variant masks are unreviewed.

This creates an80-attempt development candidate manifest, not admitted training
rows:20controls plus60distortions. Do not fit before pair dispositions are
frozen, promote by technical counts, train on held-out roles, or hide clipped
cases in an unclipped primary experiment. No recipe search, mask change,
threshold invention, model promotion or photographer evaluation.
