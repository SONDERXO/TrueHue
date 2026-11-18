# TrueHue: research-prototype methods and developmental results

12 November 2026. Working paper insert prepared from preserved records. This is an interim research milestone, not a replacement for the submitted proposal or a claim of a finished correction model. Numerical tables reproduce saved developmental results; no experiment was rerun for this draft.

## Suggested abstract text

This study investigates single-photo photographic restoration using facial colour measurements, the Individual Typology Angle (ITA), an experimental Monk Skin Tone (MST) estimate, and decision-tree prediction of gamma and red/blue adjustment parameters. A local research prototype supports inspection and optional manual refinement of separate measurement and correction regions. Developmental comparisons showed useful average exposure restoration, but gains were inconsistent across correction types and source photographs. A broader training-data comparison preserved usable unchanged references and improved mean reconstruction relative to uncorrected distorted inputs, while losing recovery relative to its frozen comparator. In a separate eleven-source controlled diagnostic, ordinary and revised tree designs continued to alter unchanged references and harm mild colour-cast inputs. Implementation and metric replay confirmed reproducibility of these outcomes but did not establish model validity. The present work therefore demonstrates a functioning experimental pipeline and documents unresolved correction generalization; independent final evaluation, expert appraisal, tone-stratified conclusions and qualified Android delivery remain incomplete.

## 1. Study objective and scope

The primary task is restoration of synthetically altered photographs toward their original photographic references. The uncorrected distorted photograph is the required baseline. Original images are photographic targets, not calibrated measurements of intrinsic skin reflectance; these experiments cannot prove recovery of a person's actual skin colour or correction of real smartphone camera bias. The intended final correction predictor remains one decision tree using ITA/MST and input-derived traditional colour statistics. Local single-photo operation is retained.

The proposed paper originally described facial correction. The developed research workflow includes visible-neck correction and optional manual support refinement as explicit extensions. Manual intervention is reported separately from automatic support estimation. Learned segmentation components already used in the support workflow do not make the correction predictor a neural model; the proposed additional neural correction-feature route was not selected.

## 2. Measurement, support and correction method

Measurement and correction masks have different purposes. Facial measurement excludes non-skin structures and estimates CIELAB statistics and ITA. Correction support may include the visible neck and uses its own protection and soft boundary blend. User-reviewed selections retain uncertainty around beard, hair, glasses, microphones and fine boundaries; review is not a guarantee of dense physical skin labels. Derivative masks in the eleven-source diagnostic were propagated through geometry-preserving photometric transformations, not newly predicted or individually reviewed for every derivative.

ITA is computed from measured mean L* and b*. Its mapped MST value is an experimental input estimate whose provenance and lighting sensitivity must be retained. Different historical mask, crop and mapping contracts are not interchangeable. The FFHQ working-frame application uses an existing fixed map under explicitly unvalidated transfer; it is not evidence of calibrated MST accuracy or underlying tone diversity. Reference information is used to construct supervision and scores, not supplied to single-photo inference.

For the controlled working-frame diagnostic, encoded RGB8 is converted to [0,1]. Direct correction raises each channel to a shared positive gamma, multiplies red and blue by their predicted gains, clips to [0,1], blends with the actual input using its saved alpha, and rounds to RGB8. Identity controls are [1,1,1]. The forward recipes use gamma 1/0.7 for darkening, gamma 0.7 for brightening, or red gain 245/255 for a mild cool cast. Nominal inverse controls follow the audited power/gain inverse. Quantization and boundary blending mean that nominal inverse controls do not imply exact final-pixel restoration.

The paper's Table 2 also includes brightness/contrast/channel-slider settings. Earlier work gave an explicit composite implementation and approximate bounded three-control targets, with clipping and residual reports. The simple diagnostic is a declared engineering subset, not completion of the full tone-dependent Table 2 experiment. Approximate composite recovery targets are not exact physical inverse parameters or proven global optima.

## 3. Data, allocation and evaluation

Experiments are reported as separate cohorts and contracts rather than pooled as a single benchmark. In the broad source-expansion comparison, the full fit used 1,117 conditions from 102 originals. A later reserved-clean design removed 227 conditions from twenty usable originals, leaving 890 fitting rows from 82 originals. Those reserved-clean roles are different from the untouched final holdout. Publisher/source groups are not verified person identities; synthetic variants and repeated fold appearances are not additional independent participants.

The later reviewed FFHQ diagnostic uses eleven accepted original references, eleven identities and thirty-three controlled derivatives: forty-four available cases from forty-eight planned roles. Four roles from one user-rejected underexposed reference remain excluded in the ledger. All eleven actual support reviews were saved and audited; three contained painted edits and eight explicit unchanged selections. These are complete historical reviews, not pending annotation tasks. The four roles of each source were held together, producing eleven folds with forty fitting and four held cases each.

The ordinary baseline used a depth-four DecisionTreeRegressor, seed 42, minimum leaf size one, unweighted squared-error fitting and sixteen fixed input features. The bounded-search and spatial-feature comparisons were separately specified modifications with the same source folds and correction operator; neither was adopted. The spatial comparison added all thirty-six fixed descriptors, rather than selecting features using held outcomes. No final all-data model was trained from these comparisons.

RGB mean absolute error and CIEDE2000 are computed against the same photographic reference and scoring support for each matched comparison. For the working-frame FFHQ experiment, every actual-input alpha-positive pixel/channel contributes. Unchanged references, underexposure, overexposure and colour casts are reported separately, together with individual harms and protected/zero-alpha equality. Lower reconstruction error does not by itself establish perceptual naturalness, physical accuracy or fairness. Parameter error is interpreted against the declared control targets, not as MST-label accuracy.

The broad experiment's coverage accounting is:

| Cohort/layer | Attempted | Model input available | Regional score available |
|---|---:|---:|---:|
| development/clean | 30 | 22 | 22 |
| development/core | 240 | 161 | 176 |
| development/composite_stress_design | 150 | 63 | 110 |
| later/clean | 24 | 18 | 18 |
| later/core | 192 | 132 | 144 |
| later/composite_stress_design | 120 | 55 | 90 |

The full attempt denominator is 756; model input is available for 451 attempts and regional scoring for 560. These denominators are deliberately different. A row can retain a reference-scoring region and receive an unchanged failure-policy output despite unavailable actual-input measurement. Such scored fallback rows are not successful model predictions. Rows without reference support remain in the attempt ledger but lack a regional score. Fourteen unchanged-reference measurement failures are not learned clean preservation. The 24-photo final holdout and older locked allocations have not been opened for this milestone.

## 4. Developmental results

### 4.1 Broader training-data comparison

| Exposed cohort/layer | Uncorrected RGB | Aligned comparator RGB | Expanded candidate RGB | Uncorrected DE | Aligned comparator DE | Expanded candidate DE |
|---|---:|---:|---:|---:|---:|---:|
| development/core | 20.6482 | 8.0287 | 13.2747 | 7.6750 | 3.4406 | 5.1499 |
| development/composite_stress_design | 52.0480 | 39.2219 | 38.8709 | 19.6479 | 15.2563 | 15.2292 |
| later/core | 21.8780 | 9.7567 | 14.3375 | 8.1855 | 4.1886 | 5.6318 |
| later/composite_stress_design | 56.0128 | 43.9462 | 43.8632 | 21.0670 | 16.6843 | 16.8414 |

The expanded candidate preserved all forty usable unchanged references across the two exposed cohorts, compared with two unwanted edits in each cohort for the aligned comparator. Core reconstruction improved relative to uncorrected inputs, but worsened relative to that comparator. Core beneficial RGB outcomes decreased from 106 to 62 of 176 scored development conditions and from 84 to 51 of 144 later conditions. Core RGB harms decreased from one and five to zero. Stress results retained trade-offs, including worse later CIEDE2000 and fewer beneficial outcomes. The fixed comparison required preservation and retained recovery together, so the candidate failed and was not promoted.

These results supply positive exposed-development restoration evidence. They do not turn a failed adoption comparison into an accepted model or establish independent final performance. The earlier comparator likewise remains an experimental reference, not a validated fallback for deployment.

### 4.2 Separate reviewed working-frame diagnostic

Each row below contains eleven held-photo outputs. The three candidate columns are preserved comparisons, not a selection of a deployable winner. RGB values use code units; DE denotes CIEDE2000.

| Input role | Input RGB | Baseline RGB | Search RGB | Spatial RGB | Input DE | Baseline DE | Search DE | Spatial DE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Unchanged reference | 0.0000 | 17.0042 | 16.2146 | 17.4328 | 0.0000 | 5.8562 | 5.7335 | 5.9963 |
| Underexposure | 27.5404 | 20.4676 | 17.6021 | 18.5391 | 9.5749 | 7.1828 | 6.1666 | 6.5669 |
| Overexposure | 25.3998 | 12.2891 | 17.2908 | 14.2756 | 8.7053 | 4.2783 | 5.9195 | 4.8546 |
| Mild cool cast | 2.1413 | 17.2566 | 18.5255 | 15.8401 | 2.2693 | 6.0623 | 6.6566 | 5.7955 |

All three designs edited all eleven unchanged references. Each improved both mean exposure directions relative to the corresponding distorted inputs, but substantially worsened mean mild-cast reconstruction. The ordinary baseline harmed ten of eleven colour cases in RGB and eight in CIEDE2000. The spatial candidate harmed ten in RGB and nine in CIEDE2000. The complete case ledgers retain individual exposure harms rather than treating mean improvement as universal benefit. Protected and zero-alpha pixel invariants passed.

The bounded search reduced summed fitting control SSE by approximately 84%, but improved fitting did not produce reliable held-photo decisions. This distinguishes numerical training success from the paper's restoration question. The current sample has a constant blue-control target of one; zero blue parameter error is not evidence that blue correction was learned.

### 4.3 Measurement and representation findings

Known inverse controls in the saved target audit produced far smaller errors than learned controls on the same simple recipes, confirming a substantial prediction gap without proving a global rendering optimum. All forty-four input feature vectors were distinct; this excludes exact conflicting full-vector targets in those saved records but does not prove generalization. All eleven original references received the same MST estimate. Changes in two distorted variants do not constitute independent tone labels or demonstrated tone conditioning.

A separate gray-pixel engineering study used twelve generated conditions only. It found false material selections and numerical near-tie sensitivity and stopped before any photo screen or tree fit. Those fixtures are not portrait data or correction accuracy results. The neural-feature feasibility review was not selected. Neither route changed the app or contributes a new successful restoration result.

## 5. Discussion and limitations

The evidence shows that ITA/MST-informed tree-based correction can improve selected developmental restoration averages, while the tested models remain unreliable across correction types and source content. Improving masks, adding identity rows, expanding sources, reducing fitting loss and adding summaries did not by themselves establish the required transfer. This does not prove that every decision tree or traditional representation must fail.

The failure of a comparison's frozen engineering checks must be distinguished from the paper's primary uncorrected-baseline question. Exact unchanged-output preservation and nonregression versus a particular comparator were prospective criteria of particular comparisons; they are not silently rewritten as verbatim proposal requirements. Conversely, mean colour error worse than the uncorrected baseline directly limits restoration claims independently of the identity criterion. No failed criterion has been relaxed after observing results.

Coverage is limited by exposed development reuse, uncertain person independence, small source counts, incomplete blue/combined/severity coverage in the eleven-source diagnostic, lighting-sensitive MST estimates, differing historical processing contracts and uncertain support boundaries. The present results cannot support a complete tone-group fairness conclusion. A future primary protocol must explicitly resolve the proposal's MST-E evaluation-versus-calibration wording, executable Table 2 interpretation and disparity formula before the corresponding evaluation. None requires inventing skin-tone labels or physically measured intrinsic colour.

## 6. Prototype status and interim conclusion

The current desktop workflow demonstrates local processing, separate support inspection, optional manual refinement and saved exports. Source inspection confirms that current displayed-mask measurements and historical model controls can have different provenance. Refining the displayed mask does not retrain the correction tree or recompute those historical controls. Therefore successful editing and saving must not be described as correction-model validation. The desktop demo does not run the rejected candidates reported above.

The milestone is a functioning research prototype with reproducible developmental evidence and unresolved correction quality. No trained candidate is promoted by this draft. A validated final model, compatible frozen end-to-end evaluation, genuine photographer MOS and measured Android correction delivery remain incomplete. No expert scores, significance claims, final fairness conclusion or completion date are supplied. The working-model objective remains open; preparing this milestone does not automatically redefine the study as a limitations-only thesis.

## Evidence for insertion and review

All exact table values are linked to their saved JSON sources in the milestone's metrics and provenance files. Narrative evidence: [consolidated training decision](consolidated-training-design-decision-2026-11-12.md), [broad expansion results](expanded-correction-training-results-2026-11-08.md), [reviewed FFHQ baseline](reviewed-ffhq-restoration-results-2026-11-11.md), [bounded search](bounded-training-comparison-results-2026-11-11.md), [spatial comparison](spatial-input-correction-results-2026-11-11.md), [support audit](completed-ffhq-support-results-2026-11-11.md), [target audit](correction-training-target-audit-results-2026-11-11.md), and [scope realignment](correction-model-and-paper-realignment-2026-11-11.md). These internal records support this insert; the final manuscript must retain its original bibliography and cite adopted published methods rather than substitute internal filenames for literature citations.
