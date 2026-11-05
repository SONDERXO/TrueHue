# Reusable object-protected correction preview: protocol

5November2026. User authorises work on the next development step. Build a reusable
photo preview with an explicit clear/opaque/uncertain glasses choice. Existing
models do not reliably classify lens transparency; do not fabricate a classifier.
Uncertain protects the whole predicted glasses region and visibly requires a
choice. Absence of the parser label is not validated absence of glasses.

Use unchanged full-face/neck, continuity, object-veto, clear-lens and blend modules
through one reusable composition API. No FFHQ IDs or image-based glass-type
thresholds in the API. Retain existing two-pixel rim approximation, other object
protection and separate measurement. Fail if required visibility is missing;
do not replace it with an all-visible mask. Preserve explicit caller protection.

Provide CLI support for an explicit image path and mode. New-photo processing
uses the existing parent detector/landmarks/parser, alignment and one fixed
FaceOcc CPU pass through the existing isolated environment. Freeze dependencies
before inference; retain stage failures. No model/dependency download. Save masks,
choice/provenance, alpha, illustrative output and a gallery. Do not change the
historical script350 launchers, frozen modules or Android model/runtime.

Validate first on all same12 saved FFHQ cases with no new inference. Reuse prior
assistant clear-lens designations16061/59807 with their provenance; others retain
opaque/uncertain handling. Require exact masks/alpha/output parity with418 and
exercise uncertain/clear/opaque handling on both clear examples and sunglasses.
This is software regression, not glasses classification or new admissions.
Retain every case and report known beard/hair/neck/reference limitations; no
new manual annotation task. Tests cover mode validation, required visibility,
explicit protection, uncertainty flag and measured support independence.

Do not automatically generate distortions, fit targets/MST/trees, recruit,
expand to new photos or create acceptance thresholds. Stop after the reusable
preview, bounded verification and remaining-issue ledger. MST remains deferred.
