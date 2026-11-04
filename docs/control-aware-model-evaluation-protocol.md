# Frozen candidate image replay

28 October2026. Declared after the single fixed model build and before image
evaluation. Use the saved `control_aware_model_build_v1` model without changing
it. Evaluate every existing core attempt:30training-source probes,3external
development probes from one already exposed source,4clipped stress probes and
the retained original failed input. No new source, mask, target, parameter,
threshold, fit or admission.

Reuse exact input images, source references, input-derived correction masks and
common source scoring masks from the existing core runner check. Predict solely
from cached distorted-input features, apply the unchanged gamma/gain operator,
and independently verify outside-mask pixels stay identical. Compare candidate,
no correction and saved original runtime metrics under the same source mask.

All30training-source outputs are seen-source/diagnostic outputs of the all-row
fit, not source-held-out evaluation. The8held IDs still never fit, but sharing
sources with fitting IDs prevents claiming source independence. Keep22eligible
and8held denominators separate. External3from one previously exposed source
and clipped4remain separate; neither is used to select/revise the model or
overrule its failed primary source-held-out recipe gate. Do not aggregate these
cohorts into a final accuracy score. Original unavailable input remains failed.

Save all available corrected outputs and eight source boards for visual review.
This is bounded development replay, not calibrated skin truth, a fresh final
test, expert MOS, phone execution or final model adoption. The active runtime,
Android work-on-hold direction, original reviews and CPM deferral remain intact.
