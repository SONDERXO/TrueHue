# Green-channel design readiness — 9 November 2026

**Design selected; not yet fit-ready.** The single selected intervention adds
facial green-channel p10, median, p90 and log contrast to the twelve current
inputs. Exact definitions and the bounded comparison are frozen in the
[design](green-channel-correction-design-2026-11-09.md).

This is a new input representation, retaining the ITA/MST path, saved actions,
cost objective, clean/colour constraints, depth, roles, veto and facial exception.
No source expansion, new recipes, head/gate changes or local split repairs are
included. The matched fitting parent is the global colour-nonharm model.

## Checks completed

Script 681 verified the parent aggregate against its verification receipt,
joined the exact fitting/reserved case IDs to saved preparation records and
checked outer held-publisher exclusion, reserved separation and closed-holdout
group exclusion. Full fitting remains 890 conditions, 82 originals and 34 groups.
The same twenty reserved clean vectors remain outside fitting.

All 910 normalized image/mask pairs needed by those roles exist. This checks
file existence only; image and mask bytes were not read or decoded. All 910
normalized images have inherited hashes in the parent source bindings. Only
227 normalized measurement masks have inherited hashes; **683 do not**. Do not
quietly treat the latter as historically hash-verified masks.

On an artificial 16x16 RGB ramp, all fourteen existing recipes were checked
with full and nonuniform blended alpha (28 recipe checks). All three colour-only
recipes preserve the green channel exactly in both scopes (six checks), and
the exposure/combined recipes change green. Repeated execution is deterministic.
The four proposed summaries also match exactly across the artificial colour-only
variants when support is fixed. These are generator checks, not extra training
images, real-photo robustness, source-held accuracy or model improvement.

The existing L quantile, Lab-chroma covariance and channel-endpoint feature
definitions were inspected. None supplies this exact facial green distribution.
Those prior negative trials are retained; green may still fail for similar
reasons, especially actual-input mask changes and complexion/illumination
ambiguity. The proposal is not a claim that more features necessarily help.

## Required preparation before fitting

The immediate technical work is one frozen **fitting-side feature preparation**,
not eleven fits yet:

1. Preserve parent artifacts and use a new output folder. Access only the exact
   fitting and reserved-clean IDs listed in the readiness artifact. Never expand
   by scanning all image directories or reading held-out photos for this step.
2. Verify inherited image hashes. For each normalized mask with an inherited
   hash, verify it before use. For the 683 without one, establish provenance by
   replaying the finalized mask from the bound cached parent/parser/FaceOcc
   artifacts and original coordinate contract, with **no new model forwards**.
   Require exact normalized-mask parity where reproducible; also verify its
   bound native projection and original four facial measurements. Newly hashing
   an unbound mask today alone does not establish its historical integrity.
3. If cached provenance cannot be reconstructed, mark preparation incomplete
   and report exactly what is missing. Do not accept matching four averages as
   proof of identical support, regenerate a different mask, or discard the row.
4. Extract the four fixed features with the same upstream 1,000-pixel guard.
   Verify formulas independently and report actual-input paired behaviour by
   clean/exposure/colour/combined family using fitting sources only. Source-paired
   clean deltas are diagnostics, never inference inputs. Distinguish fixed-pixel
   green invariance from measured-mask changes.
5. Review whether the training-side evidence supports the selected design.
   No substitute quantiles/channels, hand-picked thresholds, outcome-tuned
   cutoff or subset rescue is permitted. No evaluation feature extraction or
   fitting until preparation passes and the specific comparison is authorised.

The provenance repair is a concrete input-integrity requirement discovered by
this preflight, not a new model hypothesis or another correction experiment.
The broad completion goal remains unchanged. The design stage does not resolve
the separate mask-quality qualification or runtime compatibility requirements.

## Artifacts and limits

`outputs/green_channel_design_readiness_v1/readiness_PRIVATE.json` saves exact
roles, input/mask paths and inherited hash coverage. Its verification receipt
binds metadata/code/design inputs and the readiness artifact. It is a
self-check of the described joins and synthetic assertions, not an independent
image-feature or model-performance verification.

Zero real-photo/mask byte reads, feature extractions, new fits, image-model
forwards, evaluation predictions, correction renders, holdout reads or runtime
changes occurred. No DINO execution, external contact, upload, commit or push.
All 24 final holdout photos remain byte-unread; previous artifacts are preserved.
