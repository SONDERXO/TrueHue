# Colour fitting versus source-transfer diagnosis

13November2026. User authorized the next recommended step after the fixed panel audit. The bounded step distinguishes errors already present in fitting from additional held-source errors, using saved feature vectors, targets, native replays and leaf records only. outputs/blue_axis_fitting_transfer_diagnosis_v1 preserves results and verification. No new training, prediction, pixel decoding or review occurred.

| Role | Fitting occurrences with nominal controls | Held sources with nominal controls | Fitting mean control SSE | Held mean control SSE |
| --- | ---: | ---: | ---: | ---: |
| Identity | 0/110 | 0/11 | 0.000426 | 0.000680 |
| Underexposure | 110/110 | 11/11 | approximately0 | approximately0 |
| Overexposure | 110/110 | 11/11 | 0 | 0 |
| Red-cast | 0/110 | 0/11 | 0.000761 | 0.001562 |
| Blue decrease | 0/110 | 0/11 | 0.000640 | 0.000699 |
| Blue increase | 110/110 | 11/11 | approximately0 | approximately0 |

Nominal-control agreement uses the existing1e-12 arithmetic tolerance, not a visibility criterion. The110 fitting occurrences repeat10sources across11folds; they are not110 independent photographs. Control SSE is descriptive and cannot substitute for image metrics or user judgments. Identity numerical changes were all judged acceptable in the completed review; do not reclassify them here.

The red/blue-decrease blend exists in every fold's fitting leaves, before held-source transfer. Red-cast error approximately doubles on held sources; blue-decrease error increases only modestly from an already nonzero fitting error. Thus current failure combines fitting under-resolution with source transfer; attributing all dilution to unfamiliar photographs is incorrect. No fold contains an exact281feature-vector collision with conflicting targets in its fitting records. This rules out exact feature equality as the explanation in this finite set, not statistical confounding or insufficient information for generalization.

Everyfold has root centered target SSE gamma2.70918367/red0.01388310/blue0.03203416. Gamma accounts for about98.3%of total raw-target root variation. This is a scale asymmetry in the frozen objective, not proof that reweighting would repair the learned colour branches or transfer. Exposure is already resolved, and further splits use conditional residuals. The diagnosis does not select a target scale, threshold, depth, feature subset or alternative objective.

History check: clean-training-capacity-audit-2026-11-06.md already documented mixed fitting leaves in older pipelines. correction-capacity-comparison-results-2026-11-06.md used unweighted target normalization and unlimited capacity, achieving clean fitting preservation but harming21of29held clean photos. split-control-predictors-results-2026-11-06.md tested normalized separate exposure/colour trees and improved average errors while leaving clean changes and mild-cast failures. Those different cohorts/features/gates do not prove all such methods impossible. They do mean normalization, more depth or split heads are not automatically a distinct untried repair. No repeat of these experiments or reinterpretation of their old gates is authorized by this diagnosis.

**Recommendation:** close this blue-axis recipe rather than spend another review or fit on an unsupported strength/capacity adjustment. Preserve the earlier accepted recipe as the development baseline, with its incomplete blue/qualification status explicit. A subsequent model proposal needs a concrete inference-available correction-axis distinction or a distinct learning mechanism, a history check and bounded generated feasibility before fitting. There is currently no evidence-backed next training recipe selected. This is an unresolved research requirement, not model completion or a requirement that the user supply another rating batch.

The separate perceptual discrepancy also remains: nominal blue-increase recovery does not guarantee human output preference. A new training method cannot be claimed to fix that merely by improving fitting control recovery. All66 ratings and the candidate's NOT_READY/CLOSED status remain unchanged; no gate relaxation or user-error assumption.

Earlier accepted recipe, approved59807manual/ears and existing artifacts remain intact. No raw-original/locked-holdout content or manifests, Android or manuscript changes. No fairness claim from the unlabelled exposed cohort. Darker-skin priority retained; modelunfinished/paperpaused/November14complete-deliverytargetatrisk/exacttimeunspecified.
