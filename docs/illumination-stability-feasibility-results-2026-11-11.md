# Illumination-stability design feasibility — 11 November 2026

An exact paired-invariance constraint is unsuitable for the current global
affine ITA/L*/a*/b* calibrator: on these recorded measurements it would force a
constant raw score. This finding does not establish that approximate stable
calibration, nonlinear estimation or MST estimation generally is impossible.
No new calibrator or fit is selected.

Scripts 772–773 examine only the existing thirty matched 600/1200 feature
differences from sixty reviewed captures. For an affine raw score
`score = intercept + beta · features`, identical estimates across every matched
pair require `D beta = 0`, where each row of D is a paired feature difference.
The paired difference matrix has four columns and rank four. Its nullspace is
therefore zero: all feature coefficients must be zero for exact invariance.
The intercept remains free, yielding a constant raw estimator that cannot
represent the subjects' distinct reference scores.

The finding holds for all thirty pairs, each nine-subject fitting allocation
(27 pairs, with the held person excluded), and each lighting family separately.
After invertible column RMS scaling, overall singular values are approximately
9.05577, 4.80705, 3.17219 and 2.19603; condition number4.12369. This is not a
numerical near-zero rank decision. Scaling here is a diagnostic coordinate
change, not a proposed inference normalization or fitted calibrator.

An independent stdlib verifier reconstructs feature differences as exact rational
numbers from the recorded decimal values and checks nonzero four-by-four
determinants in all fourteen geometries. It verifies thirty pairs, fourteen
rank witnesses and RMS scales without regression, predictions or image reads.
The exact-rank conclusion applies to the recorded rounded features. It is not a
robustness analysis for uncertain masks, sensor noise or physical skin colour.
Clipping could make some affine outputs identically saturated; that does not
provide a varying accurate illumination-invariant calibration design.

A soft paired-stability penalty could trade accuracy against stability. This
review does not evaluate such a penalty or establish that it meets the frozen
original-condition preservation checks. Choosing its strength from the exposed
results would reopen a tuning search without independent evidence. Strict
invariance and the actual advancement gates are different requirements; failure
of strict affine invariance does not prove the gates mathematically unattainable.

The prior observed tradeoff remains: added brighter examples reduce their
underestimation while degrading original conditions. A new fit of the same four
statistics with an untested penalty is not yet a justified next experiment.
Neither a switch back to the original model nor removal of ITA/MST qualifies
the photographic inputs. The final correction decision tree remains required.

Recommended next work is to assess whether **genuinely additional single-photo
illumination information** is already available, with credible provenance and
compatible labelled coverage, before selecting another calibration design.
Scene metadata or neutral-looking regions must not be assumed to measure
illumination: scene content and reflectance can confound them. Subject IDs and
capture-condition labels may organize training/evaluation but cannot supply
inference inputs. No new cue, source acquisition, estimator or experiment is
selected by this review. Existing annotation tasks are complete; more mask edits
are not requested. Seven photographic inputs still exceed reviewed brightness
coverage. Full photographic transfer and identifiability remain unestablished.

Private evidence: `outputs/illumination_stability_feasibility_v1`. Zero fits,
predictions, image reads, image-model calls or runtime changes. No acquisition,
contact, upload, commit or push. All prior artifacts remain intact; final 24 and
older locked images stay byte-unread. The failed fixed comparison stays closed
and all application/admission flags remain false.
