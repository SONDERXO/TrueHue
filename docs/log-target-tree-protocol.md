# Fixed multiplicative-target regression comparison

30 October 2026. Existing recovery targets were already fitted per pair by a
bounded RGB optimizer; do not assume their strength is an unfitted mistake.
Test one alternative target coordinate system for positive multipliers:
natural logarithms of direct-exponent gamma, red gain and blue gain. Identity
maps to three zeros. Exponentiate leaf predictions before applying the existing
fitting-control identity protection. This changes split loss and leaf averaging
to multiplicative coordinates; it is an engineering hypothesis, not an equation
claimed from the proposal. All final outputs remain gamma/red/blue parameters.

Compare ordinary direct targets with log targets, both on depth 3/seed 42/
minimum leaf size 1 and the same five Lab/ITA/experimental-MST input features.
Reuse the exact 41 pairs and 26 source/known duplicate-group-held folds from
the accepted-clean-control plan. Each fold fits historical pairs plus eligible
new clean originals, excluding all rows of its held group. Do not tune a log
base, target weight, depth or threshold against these results.

Report historical 30, distorted 15, historical clean 15, additional clean 11
and combined 41 separately. Require zero changed held clean photos and benefit
versus unchanged; assess distorted benefit relative to the matched ordinary
target model too. Preserve failed candidates and the stronger historical-only
baseline. No automatic promotion even if this exposed-development gate passes.

Verify fitting-only targets, independent raw-tree refits, log-leaf inversion,
protected membership, source separation, all output pixels and metrics, and
exact ordinary-target parity with the preceding augmented depth-3 run.
No new mask, source, reserved data, calibration, review request or runtime
operator change. The working demo remains unchanged.
