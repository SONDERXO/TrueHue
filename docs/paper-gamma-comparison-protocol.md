# Direct-gamma convention: fixed matched-source comparison

29 October 2026. Implement direct-power gamma separately from all legacy
operators, models and targets. Proposal PDF38 states gamma below1 brightens.
Legacy reciprocal gamma and saved trees remain unchanged. An explicit converter
maps a legacy correction gamma to its reciprocal with red/blue gains unchanged,
preserving the predicted pixel curve. Do not flip numeric meanings underneath
old artifacts or Android parity tests.

Before new input generation, freeze these20sources: exactly the technically
usable accepted original-rule-mask references from accepted_training_pair_audit_v1.
Keep their existing experimental reference severity, original square pixels,
generation support and baseline measurement algorithm. Exclude all held-out
roles and reserved check sources. Preserve user concerns and all old variants.

Compare the original Table2 composite with a separate direct-gamma sensitivity
variant using the same numeric Table2 settings and all other legacy assumptions:
contrast about0.5, brightness offset/255, additive R/B shifts/255, final clipping.
Only exponent direction changes. These remaining conventions are documented
engineering assumptions; this is not an exact reconstruction of Table3 nor the
complete three-distorted-version training design. Do not select parameters by
results or present a larger/brighter mask as better skin selection.

For each new input, run the unchanged single-face/skin-mask measurement on its
own pixels. Never copy reference masks/features for inference. Reference mask
is used only for synthetic generation and diagnostic support scoring. Report
clipping, frame failure, existing exploratory support screen and input features.
The unchanged experimental MST lookup may supply a clearly labeled development
input feature only when measurement succeeds; it is not newly validated.

Fit approximate recovery targets with the unchanged bounded legacy optimizer
on the input/reference mask intersection, then explicitly convert the gamma
parameter to direct-power semantics. Preserve the original optimizer report
as legacy coordinates and verify the converted correction curve agrees. These
are reference-informed target optimization calls, not learned-model fits or
exact inverses of brightness/contrast/clipping.

No automatic training admission or promotion. New distorted masks remain
unreviewed. Preserve exact identity controls separately. Report matched old/new
denominators, changed masks and all failures. No new recipe search, severity
tuning, final evaluation, active model replacement or photographer review.
