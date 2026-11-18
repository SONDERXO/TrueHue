# Saved blue-axis colour discrepancy diagnosis

13 November 2026. User authorized diagnosis of saved controls, routes and ratings after the completed NOT_READY review. scripts/diagnose_saved_blue_axis_colour.py; outputs/blue_axis_saved_colour_diagnosis_v1. **660 fitting route replays and66 held route replays agree with the saved native results; populated leaf means and model hashes also verified.** No trainer, image-array library, fitting, rendering or new candidate prediction was used.

## Red-cast and blue-decrease: correction axes are blended

Ten of11same-source red-cast/blue-decrease pairs receive exactly identical three-control vectors. All11red-cast inputs and10of11blue-decrease inputs reach the same leaf as their corresponding acceptable identity. This is model routing/leaf occupancy evidence, not a new inference-time identity oracle.

For10red-cast cases the destination contains mixed red-cast and blue-decrease fitting targets, often also identity targets. That produces insufficient red restoration plus an unnecessary blue increase. No red-cast or blue-decrease held case receives its complete nominal control vector. The remaining red-cast case54632 routes to a pure blue-increase destination, reducing blue rather than restoring red; its DE and RGB errors both worsen. This is not a wrong gamma problem: gamma remains1 for the colour cases.

For blue-decrease, all11DE errors improve but only8RGB errors improve; unwanted red gain offsets some of the intended blue restoration. Only2outputs were visually preferred and9showed no noticeable difference. For red-cast,9DE errors improve but only3RGB errors improve; visual outcomes are1output/7no-difference/3input. These saved measures already show metric disagreement alongside poor correction-axis separation. Numerical family eligibility was not evidence of good colour restoration.

The mixed destinations include the relevant fitting targets; the result is not explained solely by a held source reaching an unrelated pure exposure leaf, as in older closed experiments. However, one pure wrong-colour route remains. This diagnosis does not establish that a depth change, objective change, larger tree or different feature subset would transfer reliably; no such fit is selected.

## Blue-increase: nominal control recovery does not settle visual usefulness

All11blue-increase cases reach pure blue-increase fitting destinations and receive the nominal inverse gamma1/red1/blue245/255 within1e-12. Both DE and RGB errors improve for all11. Nevertheless the completed review reports1output preference,7no-noticeable-difference and3input preferences. Those three input-preferred cases also have numerically correct nominal controls and improved metrics.

Thus diluted learning or a wrong inverse direction does not explain these three preferences. Prior independent RGB8 rendering, panel assignment and protection checks passed; this scalar replay found no route/export mismatch. It is still not evidence that the user's judgments are wrong. Numerical errors measure a specified skin-support region, whereas the review displays whole cropped panels; clipping, quantization, partial correction and viewing conditions can also limit what a nominal inverse means. These are possible considerations, not established explanations of the preferences. No new images, regional metrics, display measurements or user comments were collected to distinguish them. The relevant whole-image clipping counts vary substantially and cannot establish a common perceptual cause or reveal where clipping falls inside the scoring region.

## Decision

Keep the blue-axis candidate NOT_READY/CLOSED/NOT_ADOPTED. Preserve all judgments and the earlier accepted recipe. Do not strengthen all corrections, rewrite leaves, remove identities, substitute RGB for the frozen DE gate, tune a new cutoff or repeat ratings to obtain acceptance. In particular, a global strength increase cannot repair the distinction between insufficient mixed red/blue corrections and already nominal blue-increase controls.

A justified further step, if requested, would first specify a bounded descriptive audit of the existing rendered input/output/reference panels and the already selected scoring/support regions to investigate the numerical-versus-whole-panel discrepancy. It must preserve ratings and gates, avoid new fitting/rescoring of old models, and not treat a favorable region as a rescue. Actual panel decoding, extra metrics or another visual task were not selected or executed in this saved-metadata diagnosis. A new training method requires a separate concrete rationale addressing correction-axis separation and transfer; this result alone is not authorization for a grid.

The cohort remains exposed and unlabelled for independent tone-group evidence; no darker-skin bias reduction is established. Existing manual ears/approved59807support, historical artifacts and failures are unchanged. No raw-original or locked-holdout content/manifests, Android or manuscript access/change. Model unfinished, paper editing paused, November14 complete-delivery target at risk/exact time unspecified.
