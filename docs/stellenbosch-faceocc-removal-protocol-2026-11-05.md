# Saved FaceOcc removal inspection — 5 November 2026

User authorises the proposed before/after comparison. Keep all30cases from the
single parser-appearance candidate. All25available FaceOcc cases are compared;
five unavailable parent/detector cases remain explicitly unavailable, not zero
removal successes. No selection by final pass or source score.

Reconstruct existing original-pixel alignment from saved landmarks and pinned
template; require exact saved aligned-image parity. Reuse hash-bound logits and
logit>0, unchanged inverse mapping. Recompute parent intersection and compare
exact final masks. Separately map an all-positive aligned mask through the same
validity mapping: removed parent pixels outside this coverage are mapping-domain
loss; the remaining removed pixels are rejected by the saved model prediction.
This decomposition is a software-stage diagnosis, not skin or occlusion truth.

Generate private three-case boards for all30, scores hidden: original input,
parent overlay, kept overlay, removed red overlay, original aligned input with
positive model mask overlay. Unavailable stages clearly labelled. Inspect all
ten boards, focusing on visible forehead/cheek/chin skin versus glasses, hair,
features and low-signal uncertainty. Do not annotate dense truth or compute
accuracy from visual judgements. Record observations separately from inference.

Verify hashes, exact mask intersection, disjoint kept/removed partition,
coverage-vs-model decomposition and aggregate denominators without forwards or
refits. No enhancement of FaceOcc inputs, threshold/mapping change, veto removal,
calibration, training, app update or dataset redistribution. Stop after selecting
one evidence-based repair direction; no automatic repair sweep or admission.
