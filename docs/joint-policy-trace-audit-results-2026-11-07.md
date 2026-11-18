# Why the joint-control repair loses useful corrections

7 November 2026. Completed the [saved-trace audit](joint-policy-trace-audit-protocol-2026-11-07.md).
No model fitting, new correction rendering, image-model inference or annotations.
The model and apps remain unchanged.

## Simple explanation

There are **three separate problems**, so one gate adjustment will not resolve
everything:

1. **The brightness tree can mistake a naturally dark scene for an artificially
   darkened photo.** The remaining clean failure passes the range checks but
   receives a strong brightening control. The existing gate correctly blocks it.
2. **The range checks stop many useful corrections.** They account for most of
   the useful retained-model actions lost after adding the conservative policy.
3. **The old gate also rejects useful modified-control actions that remain
   available.** Removing it would recover some of these actions, but would also
   allow the clean-photo failure above.

“Useful” here means lower saved RGB reconstruction error in the existing scoring
region. It does not mean a complete, natural-looking corrected face.

## What causes the remaining clean error

The full saved gamma tree uses whole-scene median lightness at all three splits
on this photo's route. Its value, 30.19608, falls below thresholds 58.62745,
43.72549 and 30.39216, reaching a leaf with gamma **0.66649**. A direct exponent
below one brightens the image. The colour controls are both exactly one.

That leaf contains 98 fitting rows from 29 original photos and ten publisher
groups: 96 artificially underexposed conditions and two colour-only conditions.
It contains **no clean fitting examples**. All 29 corresponding clean fitting
photos reach other gamma leaves (28 in one leaf, one in another). The exported
gamma equals the raw mean target; there is no checked leaf/export arithmetic
error. The later photo's publisher group is excluded from fitting.

The query passes all 12 individual feature ranges in both heads. That demonstrates
the limit of this range rule: individual ranges do not establish that a particular
combination of features represents a distortion rather than a clean photo.
The resulting bright facial patch causes **35.75 RGB MAE** on its 683-pixel
reference region. The gate's saved logit is -0.83681, so the gated output is
unchanged. The tree route supports an absolute-lightness shortcut explanation;
this is not a controlled causal test of background colour or illumination.

## Two different sources of lost recovery

These counts cover conditions, not independent photos or people.

| Saved comparison | Useful modified actions rejected by old gate | Previously useful retained actions lost to range checks | Previously useful retained actions lost to neutral leaves |
| --- | ---: | ---: | ---: |
| Development core, 232 scored | 79 | 14 | 3 |
| Later fallback core, 184 scored | 78 | 21 | 1 |
| Development stress, 145 scored | 5 | 83 | 2 |
| Later fallback stress, 115 scored | 2 | 53 | 0 |

The first column is a different set of actions from the last two columns:

- **Gate rejection:** the modified controls would reduce error, but the unchanged
  gate chooses no correction. The 79 development core conditions come from 25
  original photos in nine groups; the 78 later conditions come from 19 photos
  in eight groups. Their mean available reductions are 23.05 and 22.57 RGB MAE
  respectively. These are selected beneficial subsets, not overall performance.
- **Policy loss:** the old gate was already allowing a useful retained-model
  correction, but the new controls become neutral. For core inputs this happens
  17 times development and 22 times later; the range rule explains 14 and 21.
  For stress inputs, the range rule explains 83/85 and 53/53 lost actions.

Most useful core actions rejected by the gate involve underexposure: 73/79
development and 54/78 later. The remaining rejected core actions involve
overexposure. This does not authorize selecting a new exposure threshold.

The development gate was learned for the earlier joint predictor and transferred
to the split predictor; the later frozen gate was learned for the original split
controls. Neither was trained on the new neutral/support policy's benefits.
These two contexts remain separate. Retraining a matching gate could address
some gate rejections, but cannot restore corrections already removed by the
range rule, and would still need to protect unseen clean photos.

## Visual and numerical checks

- Replayed all **688** available gate logits and decisions in the two contexts.
- Independently checked **728** reference-scored condition classifications out
  of **756** attempts, category totals, recipe counts, source/key counts, selected
  examples and means. Missing features and references remain in the ledger.
- Reconstructed the focal 98-row leaf and all 29 paired clean routes; checked
  fitting exclusions and **53** bound source hashes. Verification passes.
- Viewed all nine explicitly outcome-selected diagnostic boards: the clean
  failure and largest saved benefits rejected/lost in each context and layer.
  Visible hard mask boundaries remain, including in outputs with lower RGB
  error. This limits any claim of perceptual improvement.

Code: scripts `553_audit_joint_policy_traces.py` and
`554_verify_joint_policy_trace_audit.py`. Private outputs:
`outputs/joint_policy_trace_audit_v1`, including classifications, fitting traces,
verification and diagnostic boards. No new pytest run was needed for this
saved-artifact audit; the previous nine-test policy suite remains historical.

## Development decision

Keep the conservative joint policy as a reference, not an adopted model. Do not
remove the gate or relax the range checks on the strength of these selected
beneficial examples. A gate-only retraining is not a complete repair: it leaves
the exposure shortcut and range-related recovery loss unresolved.

The next model proposal should address **exposure grouping first**, while
preserving exact neutral colour controls and reporting both gated and ungated
clean behaviour. One justified hypothesis is to test whether the gamma tree can
recover exposure without its three absolute scene-lightness percentile inputs;
the original ITA/MST and facial measurements would remain. This is a proposed
bounded intervention, **not an authorized fit or a proven solution**. Its exact
control/support policy and leakage-separated gate evaluation must be frozen
before any run; do not quietly combine it with another sweep or relax the
zero-clean requirement. No specific next candidate was trained in this audit.

All findings remain exploratory: repeated exposed groups, synthetic distortions,
uncertain masks, limited reference regions and photographic RGB error do not
establish true skin colour, naturalness, independent accuracy or fairness.
