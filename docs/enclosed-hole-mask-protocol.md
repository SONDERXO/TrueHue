# Enclosed mask-hole development check

30 October 2026. Test one topology-only completion rule on the already exposed
20-source contour/YCrCb development frames. A missing component may be added
only when it is enclosed by the existing mask, has no frame-border connection,
contains no anatomical exclusion pixel and lies entirely inside the landmark
face outline. Use 8-connected background components. Do not set or tune a hole
size, color threshold or source-specific exception. Preserve every existing
selected pixel, including existing errors; this is not a new skin classifier.

Anatomical holes remain open: if a connected missing region includes an eye,
eyebrow or mouth exclusion, skip the entire region. Missing geometry stays an
explicit failure. Enclosed hair or an object could still pass this geometric
rule, so no human approval, skin correctness or mask promotion is inferred.

Reconstruct masks/exclusions from saved frame-local geometry. Reuse only the
40 exposed reference/color probe frames and preserve their final decisions.
Report added pixels, skipped anatomical/background regions and reference/color
support agreement separately; reference masks are diagnostics, never an input
to completion or ground truth. Do not run MST, change measurement features,
fit trees, open reserved data or modify the demo. Save overlays for inspection.

Verify synthetic topology invariants, exact existing-mask reconstruction,
unchanged original pixels, additions within outline and outside exclusions,
retained failure frames and deterministic saved masks. This development-only
operator has its own version and does not change the original mask contract.
