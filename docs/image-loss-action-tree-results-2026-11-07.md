# Joint image-loss tree: stronger recovery, clean generalization unresolved

7 November 2026. Completed the user-approved
[action-tree redesign](image-loss-action-tree-protocol-2026-11-07.md), rather
than another feature or gate adjustment. **Average distortion recovery improves
substantially, but the candidate fails the zero-clean-edit requirement and is
not adopted. The correction model remains unfinished.**

## What was implemented

One tree now learns correction and no correction together. Its split objective
is rendered RGB8 reconstruction error, with a hard constraint that every clean
fitting example stays unchanged. Each leaf selects exact identity or one of 13
training-derived correction actions. The correction actions are the mean saved
target for each fitting distortion recipe, not a runtime recipe lookup. Runtime
uses only the 12 original image features, including ITA and estimated MST.

The tree retains depth three and minimum one row per leaf. It searches fitting
float32 midpoint thresholds deterministically; there is no hyperparameter sweep.
Exactly ten original held-publisher folds and one full model were fitted. The
candidate replaces the separate exposure/colour heads, external gate, later
clean-leaf overrides and range guard. These components remain intact in the
previous models. This is an integrated architecture comparison, not proof that
one individual change causes all of the gain.

The reused evaluation ledger records `supported: true` whenever features are
available. This is only a compatibility field, not confidence, range support
or evidence that an action is safe; this candidate has no range guard.

Five constructed-example tests passed in 2.13 seconds. They verify mixed-root
separation, clean feasibility despite aggregate benefit, conflicting identical
features, identity tie-breaking, invalid inputs and renderer-cost agreement.
Four valid tiny generated trees were fitted in these tests; they use no research
photos. Research fitting consists of the specified 11 joint trees only.

## Main comparison

Mean per-photo RGB MAE in the existing reference regions; lower is better:

These distortions are synthetic and all comparison cohorts have already been
exposed during development. The reference regions are limited mask measurements,
not complete facial ground truth. Correcting a measured patch can lower this
error while leaving a visibly unnatural face or untreated surrounding regions.

| Comparison | No correction | Retained model + gate | Previous conservative policy + gate | New joint tree |
| --- | ---: | ---: | ---: | ---: |
| Development clean, 29 scored | **0.00** | 0.06 | **0.00** | 1.16 |
| Development core, 232 scored | 20.73 | 13.51 | 15.05 | **2.83** |
| Development stress, 145 scored | 52.54 | 23.76 | 45.91 | **21.06** |
| Later clean, 23 scored | **0.00** | 0.03 | **0.00** | 2.75 |
| Later core, 184 scored, fallback masks | 21.39 | 17.43 | 19.34 | **6.00** |
| Later stress, 115 scored, fallback masks | 54.66 | 36.23 | 50.66 | **33.97** |

The new tree lowers core error versus input in 165/232 development conditions
and 129/184 later fallback conditions. Reference-scored core harm counts are
8/232 development and 10/184 later, compared with 9/232 and 2/184 for the retained
model. Thus the later mean improves while the number of harmed conditions grows.
Stress benefits occur in 115/145 and 72/115 conditions, with 2 and 3 harms.

Changed scored clean photos are **2/29 development and 5/23 later**, versus 3/29
and 1/23 for the retained model, and zero for the conservative policy. All three
native mask contexts repeat the same five clean failures; these are five photos,
not fifteen people. Preserving clean fitting examples still does not reliably
preserve clean photos from unseen publisher groups.

Relative CIEDE2000 and equal-key means also improve on distorted inputs:
development/later core CIEDE2000 is 1.66/2.82 versus retained 5.24/6.70;
equal-key RGB MAE is 3.00/6.01 versus retained 13.27/17.33. Stress CIEDE2000 is
9.30/13.46 versus retained 9.99/14.37. These are relative photographic-reference
metrics, not calibrated true skin colour or naturalness measurements.

## Mask conditions and severe errors

Later borrowed-mask core MAE is 2.45, actual-input-mask MAE is 6.33, and
fallback-mask MAE is 6.00. Corresponding stress means are 20.21, 36.38 and 33.97.
Borrowed-mask results therefore overstate recovery relative to actual-input
processing. Do not pool these repeated contexts or hide missing measurements.

The two previously diagnosed clean failures remain harmful: the held development
forehead is darkened (22.93 RGB MAE on 3,906 reference pixels), and a later clean
face is brightened (31.34 on 683 reference pixels). The worst development core
regression increases RGB MAE by **54.57** versus its distorted input; the worst
later core regression increases it by **29.30**. These are explicitly selected
worst cases, not additional independent evaluation photos. The four diagnostic
boards show visible dark/bright patches and hard boundaries.

The recovered warm fallback case is also still changed harmfully in full-scene
error: 2.01958 input to 2.05599 output. Its original facial reference is missing,
so no facial reconstruction error or benefit is asserted for that case.

## What the redesign establishes

The training algorithm can protect all fitting clean photos while retaining
useful correction: the full fit's mean training MAE falls from 27.66 unchanged
to 2.91, with all 29 fitting cleans unchanged. The evaluation-only best available
action per fitting row averages 2.03; this uses reference knowledge and is not
an inference method. These training figures must not be presented as validation.

The held results support further work on this architecture instead of returning
to the unsuccessful feature-removal sequence. However, it still sometimes
selects a wrong exposure action on an unseen clean or distorted photo. The
learned splits remain dominated by scene-lightness cues; making ITA/MST available
does not establish that the fitted tree actually uses them. Neither feature
occurs in the splits of these 11 fitted trees. This is an important limitation
of this candidate, not a change to the retained thesis input requirements.

The fixed 14-action library also quantizes controls and cannot represent every
correction. Its construction, tree depth, hard fitting constraints and exposed
cohort are all part of the tested design. No claim of optimal architecture,
independent real-world accuracy, fairness or completed correction follows.

## Verification and artifacts

Independent training verification passes: **49,980** rendered action-cost checks,
**81,146** split alternatives, **165** nodes, **3,570** repeated fitting-row routes,
**290** clean fitting occurrences and **423** bound source hashes. The 290 counts
reuse the same 29 original clean photos across fitting configurations.

Independent output verification manually traverses saved trees, reconstructs
RGB8 outputs with separate arithmetic, checks image/reference/mask bindings,
all reported metrics/aggregates, original outside-mask pixels, source hashes
and 23 duplicated native clean outputs. Exact output completion counts are in
the private `verification_PRIVATE.json`.

Output checks pass: **1,281** actions, **1,414** RGB8 PNG replays, **1,372**
reference metric checks, **1,008** scene metric checks and **5,395** bound source
hashes. Viewed all **63 fixed boards** through 16 contact sheets and all **four
outcome-selected diagnostic boards** at original board size. Hard boundaries
and fragmented correction remain visible even in some lower-error outputs.

Code: `src/model_training/image_loss_action_tree.py`, scripts559–563 and
`tests/test_image_loss_action_tree.py`. Private outputs:
`outputs/image_loss_action_tree_models_v1` and
`outputs/image_loss_action_tree_comparison_v1`. All 1,428 attempts are retained;
they represent 54 original photos with repeated distortions and mask contexts,
not 1,428 independent photos or people.

## Decision

Keep the joint tree as a development candidate because it recovers substantially
more distortions. Do not promote it to the demo: unseen clean protection and
severe wrong-action errors remain blocking problems. Future work should focus
on how these wrong exposure actions are selected, while retaining the recovery
gain and testing clean preservation explicitly. No next fit, action-strength
change, safety threshold, feature change or gate attachment is automatically
authorized by this result. The completed fixed comparison stops here.

No new MST/target/gate/detector/parser fits, new annotations, dataset search,
scientific admission, Android/desktop change, sharing, contact, publication,
commit or push. All older artifacts are preserved.
