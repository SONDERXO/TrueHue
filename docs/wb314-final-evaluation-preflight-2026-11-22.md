# WB314 freeze and final evaluation preflight

## Frozen build for the manuscript

On 22 November 2026, the researcher approved the severe-backlight example and agreed to hold further low-light tuning for the December 4 manuscript. The frozen local test build is TrueHue Soft Edge Test `1.0-wb314-soft-edge-test.5`, application ID `com.example.skintonecorrection.pickertest.soft`. The local APK and installed Huawei APK matched SHA-256 `04e2716d32df13cd3dbaa7efa2a28faff44f7eba86d8bb8329ecee32b0a7d5c4`. All eight installed assets matched their recorded hashes. The WB314 tree is `7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f`. The exact APK remains in the local evidence folder `outputs/wb314_low_light_candidate_v1/`. [Phone implementation and evidence](android-wb314-picker-2026-11-19.md#severe-backlight-exposure)

The 21 UT Austin portraits supplied 13 completed results and eight face-analysis stops. One of the six dim or backlit photos received a 3/8-stop lift. One stayed unchanged and four stopped at face analysis. The lifted case had zero newly clipped channels and zero changes outside support. The other 12 completed outputs and the four earlier Huawei fixtures matched version .3 byte for byte. All 25 JVM tests passed. This is development evidence for the frozen build. The supported claim is that the lift helped one severely backlit portrait and that difficult low-light face analysis remains a limitation.

The Laboratory for Image and Video Engineering at the University of Texas at Austin supplied the photograph collection. Cite both Ghadiyaram and Bovik's 2016 study and their 2015 dataset release when reporting the pilot. [IEEE study](https://doi.org/10.1109/TIP.2015.2500021) · [LIVE In the Wild dataset and required attribution](https://live.ece.utexas.edu/research/ChallengeDB/)

## Draft final scoring rules

The researcher approved the direction of one final subject-disjoint evaluation. The following details apply to the proposed half-stop method once the broader thesis-method revision and final roster are accepted. This draft protects the final set from tuning and leaves the existing development round bound to its 20 original WB314 comparisons.

The December 4 manuscript retains the original MST-related goal and can report the verified photo-correction results with the skin-tone estimation limitation. The current tree uses neither ITA nor the estimated MST field in a split. Independent MST estimation accuracy and correction performance by reference MST group remain pending. Acceptance of the manuscript's reporting scope leaves the proposed final procedure to be resolved through the thesis process.

| Item | Rule to fix before the final test |
| --- | --- |
| Roster | Bind release permission for edited stills and controlled expert viewing, subject ID, original photo ID, and independent MST reference label and provenance. Exclude people used in training, tuning, mapping development or development review. Record group sizes and any missing levels before processing. |
| Images | Use one original portrait per admitted subject where available. Keep all variants and any repeats of that subject together. Use the same six conditions for each portrait with no replacement based on output. |
| Conditions | Use `src/distortion_generation/camera_inspired_halfstop.py` on upright sRGB8 references. Apply the whole-frame linear-light multiplier `2**EV` and the stated red and blue factors, clip to the representable range, and round to RGB8. Apply the frozen Android correction to the resulting input using its automatic support. Retain the generation clipping count. |
| Restoration | Before correction, save an eligible reference facial skin mask per portrait. Score both the uncorrected input and corrected image against the same original photograph on that fixed mask at original dimensions. Use mean CIEDE2000 as the primary score. Record input error, output error and improvement as input minus output. Keep image RGB MAE in its own column and state whether the values are unit-scale or 8-bit code values. |
| Controls | Compare the raw five predicted parameters with the recipe's nominal inverse `[1, 2**(-EV), 1/red, 1/blue, 1]` and give MAE per parameter. Record the controls the app actually applied and the same MAE for them where available. Clipping and blending can leave residual image error even under the nominal inverse. Report gamma and chroma as neutral targets for these conditions. |
| Preservation and unsuccessful runs | Compare output against the actual input on protected and outside-support pixels using the app's mapped support. Record dimensions, changes, new clipping and identical outputs. Keep unsuccessful attempts in group denominators and name the reason. Summarize numerical restoration among completed outputs and show an additional all-attempted result assigning zero improvement to uncompleted cases. The latter represents the absence of a delivered correction. |
| Aggregation | Give equal weight to subjects within each condition, averaging any repeat photographs within subject first. Report per MST level and pooled groups 1–3, 4–7 and 8–10 with attempted and completed counts. Flag empty groups and report gaps in usable coverage alongside the scores. |
| Proposed 10% criterion | For each nonidentity condition with nonempty light and dark groups and positive group mean input error, divide each group's mean improvement by that group's mean input error and report the absolute between-group gap in percentage points. Compute the completed and all-attempted summaries with their respective denominators. Flag a gap above 10 points. Preserve negative improvement, which indicates harm. A zero denominator or empty group makes the percentage unavailable. Report absolute CIEDE2000 improvement and success rates alongside the relative gap. This is a proposed interpretation for approval. |
| MST estimation and expert review | Compare the app's inferred MST separately to the independent reference label on original portraits where measurement succeeds. Report label error and measurement availability. Use the existing expert instrument for one final appraisal of version-bound pairs after the engineering and quantitative checks. Keep expert quality ratings, preferences, and the earlier development feedback distinct. |

| Condition | EV | Red | Blue |
| --- | ---: | ---: | ---: |
| Identity | 0 | 1.00 | 1.00 |
| Colour only | 0 | 0.85 | 1.15 |
| Underexposure | −0.5 | 1.00 | 1.00 |
| Overexposure | +0.5 | 1.00 | 1.00 |
| Underexposure and colour | −0.5 | 0.85 | 1.15 |
| Overexposure and colour | +0.5 | 0.85 | 1.15 |

## Execution status

A generated-pixel check verified all six recipe roles, the nominal inverse values, and the masked CIEDE2000 metric. Identity and changes outside the scoring region yielded zero error on the scoring region. This checks the available recipe and metric code before final data arrive.

No eligible final subject has been admitted. The local intake history explains why the existing cohorts do not establish independent MST ground truth. The UT Austin pilot contributes everyday-phone cases, and MR2 and London contribute controlled studio evidence. Each has a different role and lacks the cleared independent reference MST roster required here. A public metadata check found no new source that established the required reference labels, permissions and independence together. [Existing cohort intake](wb314-completion-blockers-and-two-round-plan-2026-11-19.md#final-cohort-intake)

The final quantitative run and second expert appraisal remain pending. Formal reconciliation of the proposed split, condition settings, correction area and disparity rule remains open. The known Python-to-Huawei live-mask parity discrepancy and the experimental MST mapping remain qualification limits. The existing development Form and images retain their earlier binding. No final predictions, new photo processing, fits, questionnaire edits or invitations were made for this preflight.
