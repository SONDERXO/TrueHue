# Recovered false correction: saved-route diagnosis

7 November 2026. Completed the [frozen diagnosis](recovered-false-correction-diagnosis-protocol-2026-11-07.md)
of the newly harmful recovered mild-warm case. No new image-model inference,
training, target fitting, threshold change or model adoption.

The replay finds no mismatch in the checked measurement, exported routes, leaf
means or rendering. The model chooses inappropriate controls and the gate permits
them. Better detection enabled this decision; it did not make the existing
corrector reliable for the recovered case.

## The exposure-control trigger

The gamma route uses scene features only on this path:

1. Scene L* median50.1961 is below58.6275, then above43.7255.
2. Scene log(B/G)0.218297 is below0.221596.
3. That reaches gamma1.427846, a darkening control in this renderer.

The leaf contains87training rows from10publisher keys:29exposure_over,
29combined_cool_over and29combined_warm_over. Its prediction exactly matches
the raw training-target mean (range1.42529–1.42990), not an export/routing bug.
These are repeated photographic variants, not87independent people.

A scene-only replay of the same source's original clean scene has *identical*
L*10th/50th/90th percentiles, but log(B/G)0.257682. That falls on the other side
of the same colour-ratio threshold, giving the neutral gamma leaf1.0. Thus the
saved mild colour shift switches this gamma branch from neutral to strong
exposure correction without changing those lightness summaries. This establishes
the frozen model's branch mechanism for these scenes, not general physical
causation or the sole explanation for all correction errors.

The original clean facial measurement is unavailable. Only the gamma path can
be resolved from actual scene features; this is NOT a fabricated full clean
feature vector, gate action or end-to-end clean prediction. Across the14saved
variants of this source,9gamma paths resolve using scene features alone;5stop
when a missing facial feature would be required. The4available actual predictions
match the scene-only gamma replay where applicable. Other paths are not imputed.

## Colour controls and gate

The colour head selects red1.146909 / blue0.843193. Its route uses measured b*
(-9.3167) and scene log(R/G), reaching a leaf with18stress-design training rows
from8publisher keys. Leaf means match the saved raw targets. A mild-cast input
therefore receives controls associated with different training distortion regimes;
this is descriptive route evidence, not proof of irreducible ambiguity.

The benefit gate returns logit+0.338688, so correction is applied. Exact linear
logit accounting:

| Term group | Contribution |
|---|---:|
| Intercept |+0.385229|
| Five facial/contextual features |+0.666294|
| Seven scene features |-0.712835|
| Total |+0.338688|

The negative scene terms are outweighed by the intercept plus facial/contextual
terms. This accounting is not a causal feature ablation or a reason to choose a
new threshold. The contextual MST score is derived from the same Lab/ITA input,
not independent information. The gate still uses joint-corrector benefit labels
transferred to split controls; the earlier failed split-specific gate comparison
remains unchanged and must not be silently repeated or adopted.

All12input features are inside both head-fitting and gate-fitting univariate
ranges. A simple out-of-range guard would not catch this case; being inside
ranges does not establish joint-distribution adequacy. Five nearest standardized
gate training vectors are exposure-over variants with mixed saved joint-benefit
labels (three positive, two negative), not an independent uncertainty estimate.

## Which controls cause the visible damage?

Same actual distorted scene, same62predicted native pixels, four fixed arithmetic
renders. No oracle optimization or alternative policy was fitted.

| Diagnostic controls | Predicted-region RGB MAE | Full-scene RGB MAE |
|---|---:|---:|
| Neutral / unchanged |1.1129|2.01958|
| Gamma only |31.2581|2.05683|
| Gains only |8.7366|2.02900|
| Full saved controls |32.2258|2.05803|

The gamma component produces most of this observed darkening; gains alone also
harm this region. These changes interact and are not an additive causal attribution.
Disabling gamma alone would not restore the unchanged input's error. No diagnostic
render is selected as a replacement model.

The own predicted region is sparse, mostly forehead with small lower-face spots;
it is not human-confirmed skin. The original reference mask remains unavailable.
These diagnostic scores cannot become official reference-region accuracy or new
skin labels. Full-scene harm is real relative to the saved original photograph,
but its global mean dilutes a local change over50176scene pixels. Independent
arithmetic verifies the full-scene error increase equals the62/50176weighted
increase on the changed predicted region; all other pixels remain exact.

Viewed both full-scene and nearest-neighbour native-crop component boards. Local
darkening and hard patch boundaries are visible; native zoom adds no image detail.
Mask material truth, measurement representativeness and whole-face coverage remain
unresolved. The diagnosis does not show that filling or enlarging this mask is safe.

## Verification, scope and next bounded option

Scripts524–526 bind source/model hashes and replay actual-input Lab/ITA/MST,
12gate terms,2float32tree routes, both raw training-target leaf means,4component
renders and independent RGB errors, plus14saved same-source scene contexts.
The full render matches the previous candidate byte-for-byte; neutral is exact
identity. No new tests or pytest rerun were needed for this read-only diagnostic;
the42tests from the preceding repair remain historical, not newly rerun results.
All admissions/adoption flags remain false; no runtime or Android change.

A justified next experiment is **one gamma-head feature restriction**, excluding
the two scene chroma ratios from gamma fitting while preserving the gain head,
gate, targets, folds, tree capacity and all other inputs. It would test whether
this exposure head relies too strongly on colour as an exposure cue. Evaluate
all saved clean/core/stress cases, not just this photo: removing a useful cue can
harm exposure recovery, and the colour-control error will still need assessment.
This is a proposed bounded experiment, NOT implemented, fitted or approved by this
diagnosis. No threshold change, feature sweep, source expansion or automatic refit.

Private artifacts: outputs/recovered_false_correction_diagnosis_v1,
including diagnosis_PRIVATE.json, scene_only_gamma_context_PRIVATE.json,
verification_PRIVATE.json, scene_board.png and native_board.png. Prior models,
outputs and histories are preserved. Dataset research/noncommercial/citation/
no-redistribution terms remain; no contact, sharing or submission occurred.
