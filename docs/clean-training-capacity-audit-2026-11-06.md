# Clean training failures: targets and rendering pass; depth-limited pooling remains

6November2026. The requested examination is complete without new fitting.
Script486audits all saved fitting rows for the original, balanced and
chroma-feature candidates. It uses independent float32routing, reconstructs
raw leaf values from fitting targets and checks the clean inputs/neutral renderer.

## Findings

For each candidate there are261clean training-row occurrences across10folds.
These are repetitions of the29available originals in different training folds,
not261independent photographs or people.

- Every clean target is exactly gamma/red/blue `[1,1,1]`, with an exact-neutral
  target status. Saved clean inputs equal their references.
- Applying those neutral controls reproduces the clean image byte-for-byte.
- All3213training routes per candidate match an independent float32traversal.
  All80raw leaf means per candidate match the appropriate unweighted or
  weighted fitting targets. No export/routing/leaf-mean mismatch was detected.
- Each fitted tree uses all eight leaves at depth3. Every clean training route
  reaches that depth limit. All261clean training routes per candidate receive
  non-neutral controls and produce changed pixels.

| Candidate | Clean training-occurrence RGB8 MAE | Held clean RGB8 MAE |
| --- | ---: | ---: |
| Original five features |9.4144|10.3689|
| Key/layer-balanced objective |2.9908|8.0101|
| Nine features with chroma distribution |9.4144|10.3689|

Training means above average the repeated fitting occurrences, not held
predictions or equal-key evaluation. Held values come from the completed
comparisons and retain their29scored-photo denominator. The balanced candidate's
lower fitting error does not imply clean preservation or better generalization.

The audit detects no target, neutral-renderer, route or raw-leaf implementation
error in these checked components. It does not certify all software, mask
validity, target suitability or scientific assumptions. Combined with mixed-leaf
and exact-vector checks from the earlier diagnosis, the saturated shallow trees
show a concrete capacity limitation: neutral examples are pooled with nonneutral
targets even within fitting data. The ordinary squared-error objective does
not impose an exact-neutral constraint. This is not proof that a deeper tree
will generalize, or that the existing features uniquely determine correction.

## Recommended next experiment, not executed

One capacity-ceiling comparison can distinguish fitting capacity from held-key
performance: original five features, original unweighted target normalization,
same357trainable rows/10nestedfolds/upstreamMST/targets/support/420attempts,
seed42/minleaf1, with only max_depth changed from3toNone. It is one declared
comparison, not a depth search or a proposed deployable model. Do not combine
balanced weights, added features, identity gating or favorable filtering.

Report both fitting clean neutrality and held clean/core/stress outcomes. If
clean fitting improves but held clean images remain harmed, record that the
capacity change permits fitting without resolving predictive separation.
Do not keep enlarging/sweeping until this exposed sample appears successful.
If fitting still fails, examine remaining exact ties/target mixing before
claiming missing physical information. No held-key labels may enter fitting.
No such new tree was fitted in this audit.

## Verification and scope

Private audit: `outputs/clean_training_path_audit_v1/`, including route records,
leaf depths, training errors, source and artifact hashes. Across three saved
candidates:9639independent training-route checks,240leaf-mean checks and783
clean-target/input/neutral-renderer checks. All bound candidate artifacts remain
hash-identical. No production function changed and no additional pytest run
was needed; previous focused test results remain historical.

Zero new model/target fits, image inference, masks, admissions, runtime/Android
changes, source transfer, contacts or submission. This remains the exposed,
borrowed-support, measured-region diagnostic. Private author research-only,
noncommercial, citation and no-redistribution terms remain.
