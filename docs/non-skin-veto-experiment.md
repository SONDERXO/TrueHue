# Fixed non-skin veto across three mask stages

24 October 2026. Tested one fixed removal-only rule on all75 saved variant attempts and earlier24 labeled pixels on clean/global-color-shift images. The rule helps some contamination but is not ready for adoption. Original masks, inputs, user decisions and training records are unchanged.

## Rule fixed before execution

Intersect each existing mask with the local multiclass segmenter's face-skin or body-skin categories. Remove predicted background, hair, clothes and other categories. Source-generation categories come from the clean source; measurement/correction categories come from each actual distorted input. No threshold/morphology changes, face-oval geometry, hand-drawn witness regions, reference measurements or new paint classifier are introduced. The same operation is used in all three stages.

Retaining body-skin avoids deliberately discarding all neck skin, but does not locate the selected person's neck or separate another person's skin. The current face-constrained source masks remain face-stage masks; visible-neck support is not implemented.

## Findings

| Inspected concern | Original witness pixels | Candidate witness pixels | Interpretation |
|---|---:|---:|---|
|31154 source generation, hair/background|614|363|Partial removal, contamination remains|
|31154 accepted bright measurement/correction|624/624|589/589|Large residual remains|
|31154 accepted unchanged measurement/correction|624/614|363/363|Partial removal only|
|31154 accepted mild measurement/correction|620/611|360/360|Partial removal only|
|60162 source generation, background|45|0|Tested background patch removed|
|63870 accepted controls, fabric measurement|692|0|Tested fabric patch removed|

Witness rectangles are the earlier Codex-inspected diagnostic regions, not exhaustive ground-truth masks. Zero overlap does not prove the remaining mask is clean.60162 measurement/correction already excluded its chosen patch before this rule; the generation layer is what changes there.63870 generation/correction already excluded its chosen fabric patch; the measurement layer changes.

All75 candidate mask/brightness measurements remain numerically available. Coverage against the unchanged original source-generation region passes68/75 versus70/75 before this rule:47217 dark/color newly fail (these were user-rejected/uncertain, not accepted pairs). Using the reduced generation denominator also passes68/75. Denominator shrinkage is not evidence of recovering skin.63870 dark loses substantial visible facial support; it was already held. No previously excluded or rejected case is promoted.

Codex inspected all15 source-generation before/after comparisons and targeted31154/63870/47217 variant boards. Source contamination remains visible in some cases; hair classified as skin can survive the rule. All30 detailed boards are available for user review; not every candidate variant was independently visually approved in this run.

## Earlier hair/paint regression

The original24 user labels were reused at their exact224-image coordinates, plus the same coordinates under a global color shift. These are48 observations, not48 independent annotations or area-accuracy results.

- Clean correction retains12/12 labeled skin points before and after, with paint0/3, other0/5. Hair remains1/4 selected.
- Shifted correction retains12/12 labeled skin points with paint0/3, other0/5 and hair0/4 before and after.
- Clean measurement retains11/12 skin points; selected hair decreases3/4 to1/4. Shifted measurement retains8/12 skin points; hair decreases1/4 to0/4. The veto does not restore missing skin.
- Generation retains11/12 skin points and1/4 hair points; paint remains0/3. The same clean-source generation mask is reused for the shifted probe.

No labeled skin selections were newly lost at these few points. This does not rule out facial skin loss elsewhere (as63870 dark demonstrates), and paint exclusion is not guaranteed across images.

## Review and next decision

Open [the comparison gallery](../outputs/non_skin_veto_v1/review.html). Left is original, right is candidate. Review retained facial skin as well as residual hair/clothing/background. Valid own-neck skin is not automatically contamination. The page does not change or record your prior decisions.

Keep the seven accepted-note cases on their separate technical holds.31154 is demonstrably unresolved.60162/63870 have encouraging witness-level removal, but still need full changed-mask review and, if the policy is accepted for further experimentation, fresh end-to-end generation and consistent feature extraction. Do not promote them from these comparisons alone. The original planned fourth fold therefore remains empty; no reallocation or fivefold fitting occurred.

These75 inputs were generated using OLD source masks. Candidate measurements on them are a diagnostic ablation, not a new consistent training dataset. No new distorted inputs, predicted corrections or model-performance claims were produced. A changed generation mask requires regeneration and rechecking clipping, masks and features before training.

## Verification and thesis record

Independent checks reproduced15 generation intersections,150 input-mask intersections and75 feature sets from saved category maps. Every candidate is a subset of its original mask. Prior model, review, label, input, feature-schema and ledger hashes remain unchanged. **464 tests passed**. No model fitted or runtime adoption.

The explicit semantic veto on estimation/generation is a new experimental method distinction. The current runtime estimator remains unchanged, and operational MST, face-and-neck correction and final dataset/reference/evaluation requirements remain pending. The original proposal is not amended.

[Fixed policy](../outputs/non_skin_veto_v1/policy.json) | [All metrics and labeled observations](../outputs/non_skin_veto_v1/summary.json) | [Independent verification](../outputs/non_skin_veto_v1/verification.json)

Follow-up: [isolated consistent two-source regeneration](non-skin-two-source-regeneration.md). Four candidates await changed-mask review; no fitting.
