# Reduced training-only mask review

29 October 2026. Replace the immediate 418-image human workload with 24
diagnostic reviews. Preserve all old decisions and artifacts. This is a
purposive development sample, not a representative accuracy estimate.

Use only the already processed, duplicate-screen-clear training queue. Select
without replacement or shared duplicate groups in this order:

1. Four successful references with largest skin-mask/face-box occupancy.
   Occupancy is a contamination warning proxy, not evidence of hair or clothing.
2. Four measurable input/reference pairs with lowest reference-mask retention.
   This is a mask-change warning proxy, not a reference-mask rejection.
3. Four references with unavailable landmarks, by fixed hash ordering.
4. Two references with empty or insufficient skin selection, by fixed hash.
5. Two references failing the single-face requirement, by fixed hash.
6. Eight successful pair candidates from remaining training sources, by hash.

Hash ordering is SHA256 of `focused_mask_review24_v1/` plus image ID, then ID.
Rank ties use that ordering. Insufficient strata must fail rather than silently
replace their quotas. No model prediction, target residual or human preference
determines selection. Review only the reference and its existing mask now;
distortion-review flags are retained for later follow-up. Accept/reject/uncertain
refers to the displayed reference/mask, never all variants or fitting eligibility.

Reserve 12 other training sources, with disjoint duplicate groups, by SHA256
of `focused_mask_check12_v1/` plus ID. Do not display their images in this review
or use their outcomes to design mask changes. They are a later training-only
check after a mask candidate is frozen, not an untouched final evaluation or
guarantee of person separation. They already have pipeline-processing exposure.

Use 24 annotations to identify recurring failure mechanisms before changing
the mask. Freeze any proposed change, compare against the unchanged baseline,
then inspect the separate training check. Additional review should be limited
to ambiguous or changed cases. Unreviewed sources stay unapproved; exploratory
model experiments must remain separate from reviewed evidence. Validation and
final test remain closed. No automatic admissions, calibration changes, new
MST thresholds or model promotion follow from this review selection.
