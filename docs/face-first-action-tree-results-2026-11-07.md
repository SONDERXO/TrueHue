# Facial-root joint tree: fewer later clean edits, development regressions

7 November 2026. Completed the user-approved continuation and fixed
[facial-root protocol](face-first-action-tree-protocol-2026-11-07.md).
**Not adopted.** Later clean protection improves, but the candidate still edits
clean photos, introduces development failures and worsens stress recovery.

## Evidence and implemented change

The parent joint trees all split first on whole-scene median lightness. Most
parent clean errors occur in leaves whose action harms no fitting member, so
merely strengthening fitting constraints would not directly address them.
The current hypothesis was to make facial evidence precede scene context.

Only the root split eligibility changes: facial Lab, ITA or MST may be selected
there; descendants may still use all 12 inputs. Eleven trees were fitted on the
same ten held-publisher configurations and one full configuration. All eleven
choose **estimated MST** at the root. This demonstrates use of the estimated
MST input, not independent MST accuracy, true skin-colour measurement or fairness.

The 14-action libraries, every saved fitting cost, clean constraint, original
features/rows, depth-three limit, deterministic greedy objective, masks and
renderer stay unchanged. The candidate still has no separate gate, leaf-range
guard or posthoc leaf-neutralization rule. No additional target or image-model
fitting/inference occurs. The frozen scope is 756 attempts in two contexts;
borrowed/input-only native alternatives were not rerun for this candidate.

## Results

Mean per-photo RGB MAE in the existing reference regions; lower is better:

| Comparison | Retained gated model | Parent joint tree | Facial-root tree |
| --- | ---: | ---: | ---: |
| Development clean, 29 scored | **0.06** | 1.16 | 2.89 |
| Development core, 232 scored | 13.51 | **2.83** | 2.85 |
| Development stress, 145 scored | 23.76 | **21.06** | 24.87 |
| Later clean, 23 scored | **0.03** | 2.75 | 1.36 |
| Later core, 184 scored, fallback masks | 17.43 | 6.00 | **5.64** |
| Later stress, 115 scored, fallback masks | 36.23 | **33.97** | 34.76 |

No correction gives zero clean error. The conservative earlier policy also
preserves these clean photos, at the cost of much weaker recovery. Bold entries
above compare the three shown models only; they do not imply a safe winner.

- Later changed clean photos fall **5 to 1 of 23**. Four parent stress-colour
  clean edits are blocked; the severe clean brightening failure remains.
- Development changed clean photos rise **2 to 3 of 29**. One parent clean error
  is blocked, the darkened forehead persists, and two new clean edits appear.
- Later core reference harms fall **10 to 2 of 184**, while beneficial conditions
  remain **129 of 184**. The two remaining harms are colour-only versions of the
  same later photo that is wrongly brightened when clean.
- Development core harms rise **8 to 10 of 232**, with beneficial conditions
  increasing 165 to 168. Core mean error is nearly unchanged.
- Stress harms rise **2 to 4 of 145** development and stay **3 of 115** later.
  Eight previously beneficial parent stress actions in each context now produce
  no change; some other action outcomes also change.

Relative CIEDE2000 and equal-key summaries retain the mixed pattern. Later core
CIEDE2000 improves 2.82 to 2.61 and equal-key RGB MAE 6.01 to 5.66. Development
core CIEDE2000 changes 1.66 to 1.65 but equal-key RGB MAE worsens 3.00 to 3.02.
Stress CIEDE2000 worsens 9.30 to 10.32 development and 13.46 to 13.78 later.

These are repeated synthetic distortion conditions and already-exposed publisher
groups. Reference masks cover limited regions; lower RGB error does not mean
natural appearance, complete facial correction, calibrated true colour or
independent generalization. The 756 attempts repeat 54 original photos, not
756 people or independent photos.

## Severe cases remain

The worst development clean error is 31.37 RGB MAE; another new clean error is
29.06. The prior forehead darkening is 23.28 on 3,906 reference pixels. The sole
later clean failure remains 31.34 on 683 reference pixels. These are visible
facial patches, not negligible numerical changes.

The worst core regression still increases error by 54.57 versus distorted input
development and 29.30 later. The recovered warm fallback case remains harmful
in scene MAE, 2.01958 to 2.05683, with no original facial reference available.
These explicitly outcome-selected examples prevent treating improved aggregate
later results as adequate safety or readiness for demo integration.

## Checks and artifacts

Eight tests passed in 3.63 seconds after correcting a generated fixture that
had assumed lookahead. The algorithm remains greedy and requires immediate
split gain; the correction did not change the training rule or research data.
Tests cover facial-root eligibility, descendant scene splits and the parent
identity/clean/image-loss contracts. No research fit started before these passed.

Independent fitting verification passes: identical cached actions/costs,
49,980 action-cost replays, 71,681 eligible split alternatives, 165 nodes,
3,570 fitting-row routes, 290 repeated fitting-clean occurrences and 428 bound
source hashes. All 29 original fitting cleans are protected in the repeated
configurations; that is not 290 independent clean photos.

Output verification checks manual routing, PNG reconstruction with separate
arithmetic, metrics/aggregates, unchanged input bindings, outside-mask pixels
and source hashes. Completion counts and review evidence are stored privately.
All checks pass: 688 action replays, 742 RGB8 PNG replays, 728 reference metric
checks, 336 scene metric checks and 3,381 bound source hashes. Viewed all 57
fixed boards through 15 contact sheets and four outcome-selected worst clean/core
boards. The fixed board columns are reference, input, parent joint tree and
facial-root tree. No native-variant duplicate check is claimed for this run:
the other native contexts were intentionally not rerun.
Empty borrowed/input-only summary sections are compatibility placeholders,
not attempted evaluations or evidence of zero error. The legacy `supported`
field means features were available, not calibrated confidence or range support.

Code: `src/model_training/face_first_action_tree.py`, scripts564–568 and
`tests/test_face_first_action_tree.py`. Private outputs:
`outputs/face_first_action_tree_models_v1` and
`outputs/face_first_action_tree_comparison_v1`. Earlier artifacts are preserved.

## Decision

Keep both joint-tree candidates as development evidence; do not silently replace
the parent model based on the later subset. This fixed hierarchy shows that a
facial-first decision can reduce some wrong actions without losing core recovery,
but it does not solve unseen clean preservation or severe overcorrection.
No next feature/root variant, deeper tree, action-strength limit, gate, ensemble,
weight or threshold trial starts automatically. Any next repair must address
the remaining wrong-action mechanism and be specified separately.

No dataset search, new annotation, MST/target/gate/mask model fit, scientific
admission, Android/desktop integration, sharing, contact, publication, commit
or push. The correction model remains unfinished.
