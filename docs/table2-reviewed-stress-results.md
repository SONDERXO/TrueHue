# Reviewed Table 2 stress experiment

28 October 2026. Imported the user's exact six-source review into a separate
hash-bound record. 22211 and 22454 accepted; 51739 rejected because its mask
accepts facial hair from another person. 62331 accepted with a small hole below
the nose, 6236 accepted with a little background included, and 75027 accepted
with a hole below the nose. Concerns are retained verbatim. No mask was edited
and no earlier review overwritten. These acceptances concern the displayed
development masks/scenes; they do not establish expert color or MST truth.

## Fixed evaluation

Admitted ten pairs to the separately authorized experimental stress path:
five accepted sources, each with an identity control and one reference-MST-
estimated Table 2 distortion. Two sources have light and three medium severity;
none has dark severity. Rebuilt five held-source/known-duplicate-group folds
after excluding both 51739 rows. Cross-source person identities are unverified.

Exactly five trees were fitted: depth3, seed42, minimum leaf1, no weights or
hyperparameter search. Each fits eight pairs from four sources and predicts
two pairs from the held source. Inputs are the same-contract square256 Lab
means, ITA and experimental distorted-input MST index. Outputs remain gamma,
red gain and blue gain. Table 2 targets are reference-informed approximate fits.
Identity targets are exactly one. No reference features enter predictions.

| Equal-source fixed-reference-mask CIEDE2000 | No correction | Held-source tree | Fitted oracle |
| --- | ---: | ---: | ---: |
| All ten pairs | 9.251 | 8.629 | 4.963 |
| Five distorted inputs | 18.502 | 14.538 | 9.926 |
| Five unchanged inputs | 0.000 | 2.721 | 0.000 |

Every source has the same two variants, so these means give each source equal
weight. Metrics assume decoded sRGB and estimated reference masks; they measure
relative reconstruction, not calibrated skin-tone accuracy or external testing.
Oracle results are capacity diagnostics and do not measure learned performance.

**The candidate fails the predeclared identity gate.** 62331's unchanged image
is altered to CIEDE2000 13.603 by parameters approximately
(1.4930, 1.0369, .9506). The other four unchanged images remain pixel-identical.
Both held light distortions receive identity parameters and remain uncorrected.
All five comparison boards were inspected: medium correction leaves conspicuous
patches and boundaries where the distorted mask drops skin. Mean improvement
does not make this candidate suitable for adoption.

## Verification and preserved failure

Script154 initially stopped at JSON export because its call omitted the required
provenance argument, after fitting the first fold. That incomplete attempt remains
in `outputs/table2_stress_evaluation_v1`; it is not an evaluation result. Corrected
the call and ran the frozen recipe to completion in V2. No quality setting changed
in response to results and no full-data deployment model was fitted.

Script155 independently reloads five saved trees and JSON exports, verifies ten
predictions, confirms every leaf's target mean from fitting rows, checks source
exclusion, reconstructs all corrected pixels and all reported metrics, checks
outside-mask preservation and verifies the gate. Source/evidence/target hashes
remain intact. The software check passes; the model-quality gate fails.

[User review](../outputs/table2_stress_evaluation_v2/user_review.json) |
[Frozen fitting plan](../outputs/table2_stress_evaluation_v2/fit_plan.json) |
[Results](../outputs/table2_stress_evaluation_v2/summary.json) |
[Independent verification](../outputs/table2_stress_evaluation_v2/verification.json) |
[Comparison boards](../outputs/table2_stress_evaluation_v2/review-index.md)

The full software suite passes **692 tests in 11.70 seconds**.

Script156 traces the saved routing without refitting. Unchanged62331 lands in
a leaf containing only fitting source6236's light distortion and inherits its
brightening target. Each held light distortion lands in a leaf containing only
unchanged fitting examples and receives identity parameters. This directly
explains these three predictions in the fixed trees; it does not prove that
the method is impossible. [Exact routing evidence](../outputs/table2_stress_evaluation_v2/route_diagnosis.json).

Next recommended work is a predeclared expansion of reviewed source/control
coverage, addressing this cross-source routing confusion before another model
comparison. Avoid post-hoc quality-gate changes. Five exposed sources and weak MST coverage cannot
support a final thesis-complete model claim. Active runtime remains unchanged;
Android paused, CPM deferred.
