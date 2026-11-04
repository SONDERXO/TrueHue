# Paper-method mask ordering refinement

29 October 2026. User explicitly requests staying within the thesis method.
Keep learned semantic-parser comparisons as diagnostic history, not the final
masking replacement. Preserve ITA, calibrated MST, input facial statistics and
decision-tree gamma/red-gain/blue-gain correction as required by the paper.
The scope describes HSV/YCrCb and detailed text YCrCb; this experiment retains
the existing documented HSV AND YCrCb implementation without new thresholds.

Freeze this single rule-based experiment on the 24 reviewed training references:
use the same existing color candidate and morphological cleanup; obtain the
same first-success margin landmarks; constrain color support to their face
oval BEFORE largest-component selection; then apply existing eye, brow and
complete-mouth exclusions. Do not expand colors, fill extra holes, use parser
predictions, invent hair/glasses labels or rescue unavailable geometry.

Compare saved baseline, removal-only baseline clipped to the oval, and rebuilt
component selected inside the oval. Require the unchanged exactly-one detector
face. Keep unavailable landmarks, insufficient support and source unsuitability
explicit. 55166 is rejected by the user's monochrome-reference instruction;
its mask may be diagnostic but never eligible for correction training.

Save color candidates, exclusions, ovals, masks and landmark arrays so outputs
can be independently reconstructed. Report support/containment counts only;
no pixel ground truth or new candidate reviews exist yet. Do not claim numerical
mask growth/removal as accuracy. Preserve baseline/user annotations and leave
the reserved training-check, validation and final test closed.

The ordering changes measurement pixels and therefore has a separate contract.
No reuse of the existing calibrated-lookup identity, candidate MST thresholds,
distortion regeneration, correction-tree fitting or default activation occurs.
Do not change the original measurement code merely to make contract hashes
match. Assess remaining quality/calibration/data requirements before promotion.
