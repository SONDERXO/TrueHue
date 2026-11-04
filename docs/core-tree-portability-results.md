# Frozen correction tree: portable inference verified

27 October 2026. Returned to the paper's core decision-tree/on-device objective.
CPM and further paint-model conversion are deferred under the user's explicit
direction. Paint/makeup protection remains a documented limitation. Earlier
observations, original labels/reviews, individual source holds and folds remain.

Implemented a versioned JSON exporter and a standard-library-only evaluator in
`src/model_training/portable_tree.py`. The existing fitted tree is unchanged;
no new correction model was fitted, data regenerated or runtime mask selected.
See the [declared check](core-tree-portability.md) and
[saved scope decision](../outputs/core_tree_portability_v2/scope_decision.json).

## Result

The current artifact is
[decision_tree.json](../outputs/core_tree_portability_v2/decision_tree.json):
**2556bytes,7nodes,3splits,4leaves**. It preserves all four input feature names,
three target names, exact thresholds/leaf vectors and original model metadata.

The existing source model SHA256 remains
`04ddeb781ea106c6856c6724f061575da06496ef3f0449312cd9973272b1e518`.

| Check | Outcome |
| --- | --- |
| Original available feature rows | 23/23exact prediction and leaf matches:16train,3development,4clipped stress |
| Split boundary probes | 12/12exact matches; both sides of all3splits covered |
| Leaf coverage | All4leaves reached |
| Maximum parameter difference | 0 |
| Synthetic RGB correction comparisons | 23/23pixel-identical, with all pixels outside the fixed mask unchanged |
| Independent package-free CLI | Same prediction/leaf with Python `-I -S` |
| Existing excluded input | Retained as an excluded row; no substituted features |
| Python suite | **519tests passed in9.51s**, including28new schema/routing tests |

[Detailed parity record](../outputs/core_tree_portability_v2/verification.json)
and [final checks](../outputs/core_tree_portability_v2/final_verification.json).
V1is an intermediate export retained from before final loader validation;V2is
the current verified package. No raw input image was opened, no new source was
exposed, and no new image-quality result was measured.

## Numeric contract

The saved feature order is mean L*, mean a*, mean b*, ITA, all measured from the
actual input using the existing versioned estimator. The output order is gamma,
red gain, blue gain. No guessed MST category or reference-image measurement is
inserted. The transform remains the existing encoded-RGB gamma-then-gain rule.

Round each input to IEEE754float32 **before** routing. Keep thresholds as
float64; choose left when `input_float32 <= threshold_float64`. Keep leaf outputs
as float64. A double just above a threshold can round back to its float32left
boundary, so comparing unrounded doubles is not equivalent. For a future Kotlin/
Java port, the comparison corresponds to `input.toFloat().toDouble() <= threshold`.
This is a numeric specification, not a completed phone implementation.

The evaluator validates schema/version, names/order and graph integrity. It
rejects cycles/shared children, unreachable nodes, invalid indices, nonfinite
thresholds/features, float32overflow and nonpositive correction outputs. Named
features must exactly match the schema; no missing-feature imputation or silent
extra-column acceptance. Classification trees cannot be exported as correction
parameters. The evaluator copies validated nodes so caller mutation cannot
change its predictions.

## Run without sklearn or NumPy

From the project root:

```text
venv/Scripts/python.exe -I -S scripts/114_predict_portable_tree.py --tree outputs/core_tree_portability_v2/decision_tree.json --features-file outputs/core_tree_portability_v2/sample_features.json
```

This produces parameters and a leaf ID only. It does not run face detection,
extract image features, assign MST, modify an image or replace the existing
runtime. The supplied sample uses saved input measurements solely for parity.

Reproduce the export into a fresh output directory:

```text
venv/Scripts/python.exe scripts/113_verify_core_tree_portability.py --output-dir outputs/my_core_tree_portability
```

The exporter refuses an existing destination. Script115checks the canonicalV2
package, original hashes and isolated CLI result. The external CPM binary and
its historical reports remain untouched and unused by this work.

## Thesis status and next core work

This solves a software-dependency obstacle for the decision-tree component.
It does not make the old weak prototype a validated correction model or prove
Android end-to-end latency/memory. The old four-feature, small development
training recipe remains distinct from the proposed MST-conditioned final
method. Operational ITA-to-MST mapping is still unsupported by earlier subject-
held-out results; no lookup or ten-category accuracy claim is invented here.

Continue with a unified core-pipeline acceptance check: input-only detection,
measurement, explicit MST availability, correction parameters/application and
failure reporting. Keep no-correction comparisons and unchanged/mild harm
visible before final learner adoption. Existing data eligibility, reference
quality and split limitations remain; setting paint aside does not clear
previously rejected/uncertain cases. General makeup/paint protection is recorded
as a limitation rather than becoming a separate material-model milestone.
The earlier face/visible-neck request remains pending, not revoked. No Android
directory was created. Final dataset/evaluation and expert MOS remain unfinished.
