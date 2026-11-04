# Patchy output: fixed-operator information-loss audit

30 October 2026. Reuse all 141 verified full-path lossless/JPEG runs without
changing masks, models, features or parameters. Compare learned output with
the previously saved reference-fitted target through the same actual support.
This target is a diagnostic oracle, not a new inference predictor or a globally
optimal fit to the compressed pixels.

For the retained direct-gamma/red/blue operator, zero input channels remain
zero under every positive parameter triple. Green=255 also stays 255 because
green gain is one. Outside application support all channels are fixed. Compute
their disjoint unavoidable RGB-MAE contribution on original reference scoring
pixels. Do not call this a CIEDE2000 bound, estimate physical sensor clipping
from JPEG endpoints, or conclude every visible artifact has one cause.

Verify the RGB floor against learned and saved-target outputs, exact endpoint
invariants, pixel reconstructions, scoring denominators and frozen hashes.
Inspect the already identified 1398 medium JPEG85 patch case side by side.
Keep all cases, including clean controls and failures, in reported denominators.
No target fitting, smoothing, hidden color reconstruction, source exceptions,
new mask approval, reserved data or demo change. The task is to distinguish
prediction error from limits of the existing operator before designing fixes.
