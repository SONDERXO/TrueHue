# Gap-cue tree with approved ear support: development results

12 November 2026. **FAIL / CLOSED / NOT ADOPTED.** All44researcher ratings are saved in revision d88b0567e26e4f28beecbfb9a53062e4.json. Downloads/correction-review-ratings (2).json exactly matches that revision. Independent A/B outcome mapping agrees on all44cases. Original choices and comments are preserved, including any wording ambiguity; none was recoded for a pass.

## Clear exposure progress; colour and preservation still fail

| Primary family (approved ear alpha/region) | Mean input DE minus output DE | Visual results |
|---|---:|---|
| exposure_under | 8.976605 | {'output_preferred': 11} |
| exposure_over | 8.034151 | {'output_preferred': 10, 'both_unacceptable': 1} |
| colour_cool | -0.036057 | {'no_noticeable_difference': 5, 'input_preferred': 3, 'output_preferred': 3} |
| identity | -2.537791 | {'noticeable_change': 5, 'no_noticeable_change': 6} |

All22held exposure cases recover the nominal inverse controls within1e-12and improve CIEDE2000. The user preferred11/11underexposure outputs and10/11overexposure outputs; one overexposure pair was bothunacceptable with a colour concern. This is successful exposure evidence on the fixed medium synthetic diagnostic, not completed severity/tone/real-world qualification. It must not be erased by the overall failure or reported as a universal model success.

Colour-cool has9numericalbenefits/2harms, but mean primaryDEimprovement is negative(-.0360567) because large harmful cases outweigh small benefits. Visualratings:3outputpreferred,5nonoticeabledifference,3inputpreferred. Cool RGBMAE rises2.14334->4.91457. This supports the user's concern about weak/unhelpful colour changes while also retaining the harmful cases. A missed/imperceptible change is not a useful correction merely because a score improves.

Identityratings:6nonoticeablechange,5noticeablechange. Three identityoutputs are numerically unchanged; the visual policy does not demand exact pixels for the others. Of the5noticeable cases,2are gamma brightening(54632,59807),3are red-gain-only changes(16061,49131,53146). Thus the remaining preservation failure is not exclusively brightness. The16061selectednoticeable judgment has a comment saying the change is small/not that noticeable;29617cool(inputpreferred)has a comment saying both look the same. These are preserved raw reports, not silently relabelled. They do not change the overall numericcolourfailure and other clear concerns; no repeat review is required to establish NOTREADY.

The user's overall comment about very small changes must not be used to increase strength globally: all22exposurecontrols already match the known inverse targets, and21outputs were preferred. Altering the strength would be a different candidate and could undermine exposure recovery. Colour decisions and remaining identity failures require specific diagnosis; syntheticchannelgainsettings and weak/mixed leaves do not establish a reliable practical colour response.

## Two scoring contexts kept distinct

The fixed original-alpha diagnostic is separate from primary enlarged-ear scoring. It also has negative cool meanDEimprovement(-.0237984), so this colour failure cannot be attributed solely to adding ears. Its exposure means are+9.014043(under)/+8.063705(over). These are diagnostic comparisons under explicitly different regions, not interchangeable scores or a way to rescue the primary failure. Saved old-model metrics remain descriptive and historical adoption decisions unchanged.

Numericalintegrity passed440fittingroutes,44heldroutes,11supportreconstructions,88render/metricreplays, exact protection/outsidealpha and frozenartifacthashes. Model fitting was10newtrees plus exact firstcandidate reuse, with all fits before scoring.48attempts44available4excluded29863. The six-feature edit footprint shows actual development transfer for these gamma cases; it remains sensitive to processing and no causal claim that every improvement comes from the features alone is inferred from primary changedsupport.

## Next and submission target

The November14target is completepaper/model/development, not a prototype milestone; exact time is unspecified. This candidate remains unqualified for a finished-model claim. Deadline pressure cannot relax colour/identitycriteria or use the finalholdout to repair it. Keep the positive exposure evidence as a result, preserve the failed candidate, and limit the next recommendation to a saved-record diagnosis of colour decisions and the two remaining wrong-gamma identity/cool pairs. No automatic globalstrength,featuregrid,newfit/maskreview/oldcandidatepromotion or change to exposureANDcolour scope follows. A new repair still needs a prospective rationale; no completion date is guaranteed.

Approved ear support stays incorporated. Paperediting remains paused under the current model-first priority; submission planning does not by itself authorize inventing completed final/MOS/Android evidence. Blue targets are constant; combinedconditions/severities/tonegroups/freshindependentvalidation remain incomplete. Existing reviews are complete; there is no new annotation batch.

Artifacts: outputs/histogram_gap_source_held_comparison_v1/final_development_assessment_PRIVATE.json and assessment_d88b0567e26e4f28beecbfb9a53062e4.json; exact downloaded evidence copy retained. The earlier numerical summary's PENDINGvisualfield is preserved as historical output; the finalassessment records completion. This turn read saved JSON only:0newfits/predictions/images/masks/NPZ/final24/olderlocks/runtimeAndroidchanges. One final tree/ITA/MST/traditionalfeatures/singlephoto/face-neck/optionalmanualrefinement retained.
