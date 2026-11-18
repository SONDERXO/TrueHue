# Practical correction-model evaluation protocol

12 November 2026. Prospective engineering assessment implementing the accepted completion contract. **No candidate or evaluation cohort is selected; no evaluation is executed.** This protocol does not rescore/reclassify previous trials. Model completion remains the priority; paper editing stays paused.

## 1. Target and comparison

Evaluate one justified frozen decision-tree correction candidate with compatible input measurement, ITA/MST, lightweight traditional features and renderer. Compare its corrected output with the uncorrected input against the same photographic reference. Keep face/visible-neck support and optional manual refinement; manual assistance must be recorded and cannot become reference-assisted features. A no-correction output can be a missed correction, not a failure of execution, but a system returning everything unchanged cannot qualify.

Report the old comparator if compatible and available. Beating all its recovery/error/benefit counts is not a future acceptance condition. No incompatible old output is silently recomputed to fill this comparison. Old frozen adoption criteria and FAIL/CLOSED outcomes are untouched.

## 2. Numerical assessment

For every attempted source/condition, record availability, input/output/reference identifiers, processing/model hashes and role. On the SAME declared reference/scoring region, calculate input and output RGB MAE and CIEDE2000. Report protected and outside-alpha equality relative to actual input. For known control targets report gamma/red/blue errors separately; do not invent parameter truth for editorial targets or equate blue error zero under constant targets with learned blue correction.

Define improvement d_i = input_DE_i - output_DE_i. Positive is benefit, negative is harm, and zero is unchanged error. Keep unrounded values; equality within the bound metric-replay tolerance is numerical equality, not a perceptual threshold. For a new execution, carry forward its verifier's justified arithmetic tolerance explicitly; do not choose one from model outcomes.

First average d_i within each source and named condition family, then average sources equally within that family. Keep exposure-under, exposure-over, red/blue colour-cast directions and declared combined families separate. Aggregate measures across all families are descriptive and cannot hide a failed family. Do not pool different reference definitions or mask/measurement contracts. Source-group counts are not verified person counts.

| Assessment | Future engineering criterion |
|---|---|
| Distorted-role restoration | Source-equal mean CIEDE2000 improvement must be positive in each declared target family. No new minimum percentage gain is invented. |
| Useful rather than numerical-only benefit | Visual assessment must confirm some useful correction within each family; tiny numerical gains alone do not establish practical benefit. |
| Already-good images | Apply the visual identity policy below. Report RGB/DE and changed pixels, without requiring byte equality everywhere. |
| Protection | Protected/outside-alpha pixels must remain exactly unchanged. |
| Numerical integrity | Reproduce controls, output and metrics under the frozen contract. This check alone does not establish quality. |

RGB MAE is a required secondary report: show family means, individual harms and disagreements with CIEDE2000. It is not silently promoted to a second universal nonregression gate. Any conspicuous disagreement must be examined visually and retained. Report all per-case d_i, harm/benefit/unchanged counts, largest deteriorations and missed corrections; no favorable subset or outcome-based drop. The criteria above are engineering choices for future work, not a claim that the proposal states them verbatim.

## 3. Fixed visual procedure

Use only frozen outputs from the chosen assessment cohort. Assess ALL usable identity pairs and ALL scorable distorted cases, not selected best examples. Complete visual ratings before displaying controls, numeric errors or model names. Save ratings before revealing which panel was corrected. This is panel-label concealment, not a claim of fully blinded reviewers; visible distortion/reference relationships may reveal treatment.

- Present side-by-side PNGs with equal dimensions and identical rendering. Primary view fits the entire frame with longest edge at most512CSSpixels, never upscales a smaller original. Provide matching native100percent inspection for both panels; do not sharpen, enhance, rewhite-balance or change masks for presentation. Record browser, display resolution, operating-system scale and whether colour settings/calibration are known. No calibration purchase/chart is required; unknown display characteristics limit the claim.
- Show A/B with input/output position assigned from the low bit of the last byte of SHA256(UTF8(protocolID+caseID)):0means input=A and1means input=B, using that exact fixed rule for all cases. Hide controls, recipe labels and scores. For distorted cases show the corresponding reference as R, clearly marked as a photographic target, not a third model output. Reviewers cannot supply reference information back to inference.
- Lock identical pan/zoom and assessment context. Do not use a different crop or selective region to hide spill/boundary problems. Existing mask overlays can be examined AFTER the initial appearance rating, with any resulting concern recorded separately.
- Before a run, name the reviewer(s) and their study role in its manifest. A researcher review is development appraisal, not independent expert MOS. No particular person is assumed to have participated and no outreach is authorized. If more than one declared reviewer participates, retain every original judgment; disagreement remains uncertain until resolved under the already frozen procedure, not by choosing a favorable rater.

### Identity rating

Answer: Is there a noticeable change in the skin's brightness, colour, natural appearance, boundary or protected-object appearance?

- **No noticeable change:** eligible preservation pass. RGB/DE differences may be nonzero.
- **Noticeable change:** preservation concern/fail for this identity case under the user's tiny-unnoticeable-change policy, even if someone prefers the new appearance. An identity reference did not require correction.
- **Cannot judge:** unresolved, never an automatic pass.

Do not use a universal DeltaE cutoff to infer invisibility. The selected viewing setup defines this practical assessment; it does not establish perceptual equivalence on every display or clinical significance.

### Distorted-case rating

Before unblinding, answer which panel is usefully closer to R: **A**, **B**, **no noticeable difference**, **both unacceptable**, or **cannot judge**. Separately mark any visibly unwanted artifact as **A**, **B**, **both**, **none**, or **cannot judge**. Record whether brightness, colour, boundaries/protection or detail drove the judgment. Only after the original ratings are saved, map the chosen panel to input/output: output preferred means useful benefit, input preferred means output worse, no difference means a missed/imperceptible correction, both unacceptable means unresolved usability, and cannot judge remains unresolved. An output-specific artifact remains a concern regardless of preference. A numerically improved output with an obvious unwanted artifact is not automatically accepted. No noticeable improvement can be a permissible missed correction; it is not evidence of successful restoration.

A candidate cannot be marked ready while a clearly worse appearance or an unresolved identity/visual case is being hidden by means. This is a conservative visible-harm rule, not zero numerical harm on every distorted case and not a new runtime veto. Preserve the case and stop the candidate's acceptance decision; do not repaint/relabel/drop it, change presentation after ratings, or train on the final case to erase the failure. This protocol declares no arbitrary allowed harm percentage. All families still need observed useful correction rather than only misses.

## 4. Availability, coverage and tone evidence

Retain every attempted row, including failed measurement, missing reference/support and unavailable correction. Distinguish model-available, reference-scorable, successful output, unchanged model decision and failure-policy no-correction. Report attempted/available/scored counts and failure reasons separately. A fallback may be scored when a target/support exists, but it is not a successful learned prediction or preservation. Never assign zero error to unavailable unscored rows.

Manual-support and automatic-support conditions must be named separately; don't silently use reference masks to repair failed inputs. Keep existing same-geometry propagation declarations where applicable. Current user reviews remain complete and are not reopened by this protocol.

Retain ITA/MST with actual provenance and disclose sensitivity/support limitations. Describe tone-group performance only where eligible independent grouping evidence exists; no new labels or complexion cutoffs are inferred from appearance or predicted values. A partial diagnostic with fixedblue targets or missing conditions cannot establish completion of the full retained exposure-and-colour task. This protocol does not choose augmentation recipes, generate new conditions or reopen the earlier broad programme.

## 5. Run binding, decision and stopping

The machine-readable template is outputs/practical_model_evaluation_protocol_v1/run_manifest_template_PRIVATE.json. Before any future run, bind a specifically justified candidate, exact feature/model/renderer/mapping hashes, source/derivative roles, reference/scoring-support semantics, family set, group allocation, numerical replay tolerance and reviewer/display presentation. Missing bindings mean the run is not frozen/executable; they are not reasons to invent values now. Do not choose a method, cohort or thresholds by scoring rejected old candidates under this protocol.

All fitting/calibration/choices remain inside eligible fitting roles. Newly opened, legitimately separate evaluation must follow a specifically declared later stage and include every outcome. Final24/older locked images remain byte-unread now. An exposed developmental pass is not independent final qualification; a future report must label which stage actually occurred. Exact old comparator targets do not become new gates by default.

Readiness requires numerical benefit and useful visual benefit in each declared family, all usable identity judgments consistent with the selected preservation policy, no concealed conspicuous visual harm/unresolved case, preserved protection, complete accounting, and reproducible processing. Record PASS/FAIL/UNRESOLVED per check and an overall NOTREADY if any required check is failed or unresolved. Missing subgroup/final/runtime evidence must limit the corresponding completion claim; no unavailable block can be ticked as completed.

Failure ends that fixed candidate assessment. No automatic extra model, threshold, loss/weight/depth/feature/data/mask or display variant follows. This protocol supplies no new training hypothesis and promotes no model. Model quality/independent qualification remain distinct from later app/Android parity, phone timing, expertMOS and manuscript tasks. Expert feedback may support separately documented development rounds under the existing policy; it is not banned, fabricated or substituted for untouched final evidence.

## Preservation

Accepted source: practical-model-completion-contract-2026-11-12.md. This is future-only. No historical protocol or result is changed; no oldcandidate rescored. PPRpaused, neuralextractor declined, existingdatasets-only, tree/ITA/MST/traditional/singlephoto/manual/neck retained. No images, cachedphotos, mask arrays or holdoutbytes read; no training, prediction, UI/app execution, source acquisition, contact/upload/commit/push/runtime or Android changes. Paper editing remains paused.
