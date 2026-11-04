# Fixed landmark-framing comparison

26 October 2026. Fixed before execution. Compare existing script91 first-success
crop landmarks with one full-native-image landmarker inference on the same53
source/input cases and two83184 sentinels. No new source, resizing or clean-to-input
landmark transfer. Keep the same detector boxes, original saved masks, model,
E/EC rules, margins, semantic/material thresholds and75% geometry gate.

Score exclusion overlap and labeled-skin coverage (including one-pixel-interior
sensitivity), cheek202/124, native point outcomes, geometry availability and32
cohort measurement statistics/features. Preserve all failures; no crop fallback
when full-image landmarks fail. Manually inspect all comparison boards and
the full-image landmark geometry on the annotated sources.

The comparison applies new E/EC exclusions/additions to the SAME legacy masks,
so previously excluded holes are not restored by merely changing landmark
framing. This isolates this ablation, not a complete rebuild of skin selection.
No original synthetic inputs, training table, human decision, hold, fold, runtime
policy or model may change. No fit or new final-evaluation claim. Full-image
inference returning a face is not proof of selected-person alignment; retain
the geometry gate and sentinel evidence. Do not choose a framing per image
after inspecting references. No parameter search or automatic promotion.

Independently replay saved candidates using cached geometry/category maps and
disk dilation, check finite measurement statistics/features and original hashes.
Added support is not automatically validated skin; unavailable paint cases do
not establish paint safety. Learned policies and human diagnostics remain
development departures from the proposal; neck/MST/finaldata/splits/expert
evaluation/Android requirements remain pending.
