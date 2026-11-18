# One colour-distribution feature comparison: no clean-image improvement

6November2026. The user-authorized feature intervention is complete. Four
input-only chroma-distribution features were appended to the five retained
Lab/ITA/continuous-MST features. This does not resolve clean preservation:
**all29clean and all232core outputs are byte-identical to the original tree**.
Only seven stress outputs change. The candidate is not adopted.

## Fixed comparison

Follow the [frozen protocol](chroma-feature-correction-protocol-2026-11-06.md).
Reuse the existing a*/b*interquartile ranges and population covariances L*with
a*/b*, computed from each distorted input's original RGB on the same borrowed
measurement support. No reference, recipe, condition or source score enters
the added feature calculation. All406images with support have available
distribution features; the nine undefined-ITA cases still cannot predict and
remain unchanged fallbacks. Fourteen original-failure attempts lack support.

Keep the original unweighted fitting objective, depth3, seed42, minleaf1,
357training-eligible rows, saved nested subject-key-held MST traces, targets and
420attempts. The rejected balance objective is not combined with the feature
change. Ten new correction trees, zero new MST/target fits, masks or distortions.
This is still the restricted fixed-support development diagnostic, not the
whole-face application pipeline or scientific admission.

| Layer | Scored / attempted | Original tree RGB8 MAE | Added-feature RGB8 MAE |
| --- | ---: | ---: | ---: |
| Clean |29/30|10.3689|10.3689|
| Core |232/240|18.8434|18.8434|
| Stress |145/150|34.0350|33.9329|

RGB8errors are on the0–255channel scale. All29clean cases still worsen versus
unchanged input. Core regressions remain98of232and stress regressions28of145.
Equal-key candidate MAEs are10.3815clean,18.9758core and34.0813stress. Relative
CIEDE2000 is unchanged for clean/core and changes12.8428→12.8343for stress.
These small stress-average differences are not significance or a useful repair.
Unavailable original cases remain outside numerical-error denominators; the
nine feature-failure outcomes remain within the scored stress denominator.

Across the10trees, split counts are15L*,31b*,9ITA,6predicted MST,7L*/a*
covariance and2b*IQR. Thus some new features were used, but they did not change
clean/core predictions. No split uses a*IQR or L*/b*covariance in this fixed
comparison. This does not establish those features are universally useless.

## Verification and decision

Script484performs the one comparison. Script485independently checks406feature
vectors using sorted linear quantiles and direct covariance products, all406
portable/rendered outputs and metrics, all10fitting means/stds, exact training
membership and unchanged bound source/artifact hashes. No refits are used for
verification. All29clean original/baseline/candidate boards were inspected;
baseline/candidate identity is supported byte-for-byte, not just visually.

Existing distribution/target-scaled/portable tests: **35passed in6.62seconds**.
No new full-suite or device test is claimed. Private artifacts:
`outputs/chroma_feature_correction_v1/`; verification and clean boards:
`outputs/chroma_feature_assessment_v1/`. Existing models, sources and results
remain preserved. No admission, runtime/Android update, publication or contact.
Research/noncommercial, citation and no-redistribution terms remain.

Close this feature comparison. Do not continue adding feature subsets or
adjusting depth/weights on these exposed results until clean error improves.
The fixed shallow regression still pools neutral and non-neutral targets;
neither balancing nor this feature addition fixed that. Before another fitting
intervention, distinguish model capacity/training-objective limits from missing
inference information using the saved fitting/held traces. No automatic next
fit, threshold-based identity gate or new dataset is activated here.
