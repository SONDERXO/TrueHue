# Proposed four-condition native inward-fade pilot

8 November 2026. Diagnostic rendering only; agree this specific pilot before producing candidate outputs.

## Fixed intervention

Use exactly the four conditions identified before the boundary diagnosis: `case_22__combined_warm_over` and `eval_07` exposure-over, combined-cool-over and combined-warm-over. Use their saved actual-input masks, native alpha, protection, controls and original scoring regions. No source-photo sampling, new model inference or fitting.

Let `S = (old_native_alpha > 0) AND NOT protected`. Pad `S` with one zero pixel before computing Euclidean distance to its complement, then remove the padding. Define `t = clip(distance / 3, 0, 1)` and `fade = t²(3−2t)`. Set `new_alpha = minimum(old_native_alpha, fade)` inside `S`, zero elsewhere. Reapply protection as zero.

This gives two partially blended native pixel layers before full strength at distance three. The edge width is fixed, not selected from a sweep. The minimum prevents increasing alpha anywhere; do not dilate, fill holes, change measurement masks or borrow clean-photo masks. Keep all three correction controls unchanged.

## Checks and interpretation

Render four candidate outputs. Independently verify the alpha formula, `0 ≤ new_alpha ≤ old_alpha`, zero alpha outside the previous support and on protected pixels, unchanged protected/outside-support RGB values, and exact rendering.

Report native alpha jumps of at least 0.5 and correction-residual edge differences before/after, positive-support/partial-alpha counts, and RGB/CIEDE2000 against the same references and scoring supports. View all four side by side at native size and nearest-neighbour enlargement. Do not change scoring regions or select another width after seeing results.

A favourable pilot requires fewer abrupt alpha transitions in all four, no new protected/outside-support changes, and visual review consistent with softer edges. Record any loss of reconstruction benefit without hiding it. These four selected conditions cannot establish general improvement, clean-photo safety, naturalness or mask accuracy; they do not qualify a model for adoption. This rendering change would also differ from the alpha used in saved training costs, so pilot outputs must not be treated as a validated end-to-end pipeline.

If the pilot fails, preserve it and stop without a width sweep. If it helps, propose a separately fixed full replay before any runtime change. Keep the final eight-group, 24-photo holdout byte-unread. No integration or automatic follow-up fit is part of this pilot.
