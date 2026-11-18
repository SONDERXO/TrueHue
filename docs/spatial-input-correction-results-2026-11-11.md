# Spatial input redesign: completed correction comparison

11 November 2026. **FAIL / CLOSED / NOT ADOPTED.** The user allowed a justified input-feature redesign. One spatial natural-scene-statistics family was specified, implemented, checked on generated fixtures, prepared on cached development inputs and evaluated once. This is a completed new input-representation comparison, not a restart of a closed trial.

## Rationale and scope

Unlike the previous global moments, quantiles, coarse face halves, green distributions and p6 bright-scene cue, this family measures locally normalized luminance coefficients and neighboring products. The published BRISQUE work motivates this spatial representation but does not establish exposure direction or complexion separation. Our descriptor is independently implemented with declared boundary/resampling conventions, without its learned quality-score regressor or any pretrained correction model. No novelty or original-implementation parity is claimed. Source: [Mittal, Moorthy and Bovik, 2012](https://live.ece.utexas.edu/publications/2012/TIP%20BRISQUE.pdf).

Retained one ordinary sklearn decision tree per held-photo development fold, ITA/MST, gamma/red/blue outputs, old16features, targets, source folds, rendering and actual-input support. Added ALL36fixed descriptors,52total; no feature subset or hyperparameter search. Exactly11depth4/seed42/minleaf1/unweighted squared-error fits,40fit/4held each. All11fits completed before any held scoring. Parent ordinary16input model was not refitted. No bounded-search follow-up or all-data fit.

## Preparation and validation

Fifteen generated-only mathematical tests passed. They verify independent Gaussian-window arithmetic including borders, moment identities, symmetry/scaling, flat and one-sided cases, invalid inputs, determinism/nonmutation and same-histogram/different-arrangement sensitivity. One pytest-cache permission warning did not affect tests. Twelve separate generated fixture arrays were excluded from all scientific data. Generated responses are not accuracy or skin-tone evidence.

Exactly44cached256x256input arrays were used to prepare descriptors, no raw/original photos. Full cached archive hashes were checked; only input_rgb8 was loaded for extraction. All44oldfeatureprefixes/targets remain exact, all11folds retain source separation. No degenerate product distributions or shape-grid endpoints; all33derivatives change at least26descriptor coordinates. Maximum observed descriptor call25.4ms on this desktop, not phone latency; no Android speed claim. Independent132coefficient-window checks maxerror4.34e-12; verifier checks1584float32 additions and352AGGDmean identities.

## Held-photo correction results

RGB errors below are lower-is-better on unchanged alpha-positive scoring regions. These44roles derive from11photos, not44independent people. All48attemptroles remain accounted for;29863excluded by existing user appearance decision.

| Role | Uncorrected RGB | Saved16input RGB | Spatial52input RGB | Uncorrected DE | Spatial DE |
|---|---:|---:|---:|---:|---:|
| identity | 0.0000 | 17.0042 | 17.4328 | 0.0000 | 5.9963 |
| exposure_under | 27.5404 | 20.4676 | 18.5391 | 9.5749 | 6.5669 |
| exposure_over | 25.3998 | 12.2891 | 14.2756 | 8.7053 | 4.8546 |
| colour_cool | 2.1413 | 17.2566 | 15.8401 | 2.2693 | 5.7955 |

Underexposure improves relative to input and saved baseline. Overexposure improves relative to input but worsens versus saved baseline. Cool-cast meanRGB/DE remains much worse than uncorrected input, despite improvement versus the failed baseline. All11originals are edited, with slightly worse meanerror than the saved baseline. RGB harms versus uncorrected: identity11/11, under2/11, over5/11, cool10/11; DE harms11/4/4/9. These outcomes independently fail the restoration aim for mild colour inputs; failure does not depend only on exact identity preservation.

Coverage/protected/zeroalpha checks PASS; per-recipe improvement, parent preservation and identity checks FAIL. ControlsMAE gamma.22572428/red.01421638/blue0, blue targetconstant1 rather than learnedblue correction.23of75splits use new descriptors.28outputs are byteidentical to parent;16change,8RGBbetter and8RGBworse versus parent. Input-dimensionality changes also affect sklearn feature tie ordering, so this is the operational fixed-family comparison, not a causal attribution of every changed output to a specific spatial feature.

Independent verifier837 reproduces161nodes,69301greedy split options,44held routes/renders/RGB/CIEDE2000/protection outcomes and all fixed checks, with0refits. All44caseboards freshly viewed on4contact sheets. Visible failures include brightening unchanged39568/52445/59807 and darkening colour-only/overexposed46795. Existing beard/hair/glasses/microphone support limitations remain disclosed and unchanged. This is assistant visual inspection, not photographer MOS or new user approval.

## Disposition and paper implications

This candidate is closed and not adopted. No scale/channel/window/distribution-grid/feature-subset/depth/weight/loss/guard/search-budget rescue or new mask/data campaign follows automatically. The descriptor implementation is engineering-tested, but its tested use does not solve the correction problem. No proof that all spatial or learned representations or every decision tree must fail is made.

The primary task remains synthetic-original restoration with one ITA/MST-informed tree. PPR is optional and paused; no Baidu action is required. The present development cohort has no independent MST labels, constant original MST estimates, fixed-strength/constant-blue targets and only11source groups. It cannot establish fullTable2coverage, MST-conditioned benefit, fairness, final accuracy or model completion. Historical broader failed datasets remain closed; do not reopen them merely to increase sample count.

No further justified candidate is selected by this result. The approved input-redesign scope remains available, but a subsequent proposal must identify genuinely different inference-available information and a specific correction rationale; naming another summary, embedding or larger dataset is insufficient. Preserve the working-model objective and report this failed route honestly. No new user mask review or adviser approval is needed.

No raw/original photos, final24 or older locked image bytes were read. Cached references/masks/alpha were loaded only for this fixed scoring/render comparison after allfits completed. No newimage-modelweights, mapperfits, acquisition, contact, uploads, commit/push, runtime or Android changes. Existing app behaviour remains unchanged.

Design: spatial-input-representation-design-2026-11-11.md. Preparation: spatial-input-representation-preparation-2026-11-11.md. Frozen comparison: spatial-input-correction-comparison-protocol-2026-11-11.md. Private outputs: spatial_input_generated_feasibility_v1, spatial_input_preparation_v1 and spatial_input_correction_comparison_v1.
