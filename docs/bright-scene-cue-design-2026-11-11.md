# One bright-weighted scene cue: design and bounded readiness screen

11 November2026. The user authorised a concrete learning-design review after the
saved-tree diagnosis. This selects no new fitted model or production behavior.
Retain a single direct gamma/red/blue decision-tree regressor, ITA/MST, existing
facial features, same-photo inference and optional manual support.

## Alternatives already tested

The binary control-partition tree already used classification-induced splits and
failed; renaming it an exposure/colour/identity gate is not new input evidence.
Split control predictors, target normalization, key/layer balancing, relative
rendered costs, extra chroma distributions and nonharm leaf repairs also have
recorded failures. Their separate cohorts/results cannot be pooled as a ranking,
but none is an untried automatic repair. Do not rerun them here.

## One candidate input measurement

Finlayson and Trezzi, *Shades of Gray and Colour Constancy* (2004), define the
channelwise Minkowski mean. Their public primary paper links average-based and
maximum-based estimates and reports p=6 as useful on their calibration data:
https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/cic/12/1/art00008
The authors explicitly state that scene-colour assumptions can fail. Their
result does not validate rendered FFHQ images, skin correction or this tree.

Use a fixed sixth moment, not a search over exponents or bright-pixel thresholds:
mu[c] = mean((RGB8[c]/255)**6)**(1/6).
Add exactly two scene descriptors, log((255*mu[R]+1)/(255*mu[G]+1)) and
log((255*mu[B]+1)/(255*mu[G]+1)). The fixed +1 code convention matches the current
mean-colour scene ratios, keeps black inputs defined and is not a fitted epsilon.
Do not linearise or claim physical illuminant values: these are rendered-RGB
features motivated by the paper, not a reproduction of calibrated colour constancy.

Current scene ratios measure first moments. Sixth moments emphasise a different
part of the colour distribution; they are not implied by the current stored scene
means/green quantiles. Spatial brightness, covariance and generic chroma summaries
were tried; no sixth-moment cue implementation was found in the reviewed local
modules/reports. The old feasibility report mentioned white-patch rules only as
unverified possibilities. Algorithmic novelty is not claimed.

Hypothesis: scene bright-channel balance may help distinguish a global colour
perturbation from an ordinarily darker face, while the existing green/brightness
features retain exposure information. It is a hypothesis, not demonstrated need
classification. Do not replace the tree with a white-balance correction algorithm,
force identity, use recipe IDs at inference, or infer lighting from skin tone.

## Fixed readiness screen before any fit

Read exactly44 already prepared256px RGB arrays from the11 reviewed FFHQ bases
(identity/under/over/cool), bound by saved NPZ hashes. Excluded29863 stays excluded
in the48-role ledger. No originals, reserved pixels, PPR pixels or new generation.
Compute both descriptors and all paired changes on the complete roster, replay
current first-moment descriptors, and compare between-original dispersion with
the recorded same-source recipe response. Report overlap and failures without
inventing a decision threshold or treating range overlap as impossibility.

This screen uses known pairs descriptively, but clean-original differences must
never become inference features. It is already exposed development; no unseen or
person-disjoint claim. No MST fits, masks, new labels, control fits or model API.
Independent scalar replay must verify all88 descriptor values and33 paired
comparisons. No superiority or correction benefit can be concluded without a
prospective held-photo correction comparison.

Potential failure modes: bright coloured objects, skin/hair content, clipping,
white backgrounds, RGB processing and synthetic endpoint patterns. The cue may
encode this recipe rather than real camera bias. Record original/derivative
saturation counts; do not discard pixels, choose percentiles or replace cases.
Existing support limitations and unvalidated MST transfer remain disclosed.

## Prospective correction comparison, only if ready for specification

Keep the saved44 rows,11 photo-group folds40fit/4held, direct nominal targets,
renderer, depth4/seed42/minleaf1/unweighted squared_error and all existing checks.
Append the two cues to the16 inputs (18total); preserve all prior inputs exactly.
A potential bounded comparison would fit11 new trees/predict44 cases and compare
against SAVED16-feature results, without parent refits, all-data fits, sweeps,
gates, multiple exponents or feature selection. This is a declared scene-feature
method extension, not proof of adviser approval or a paper-method requirement.

Prospective checks: full44 coverage/protection; every recipe mean RGB and DeltaE
better than input; unchanged11 identity outputs; recipe means no worse than the
saved parent; report all harms and control errors. These are comparison checks,
not new universal paper barriers. A failure closes that candidate, not an
automatic p/threshold/weight/depth/recipe repair cycle. No execution is selected
by this document; readiness output must be reviewed first.

All prior outputs/failures preserved; final24 and older locks byte-unread. No
acquisition/contact/upload/commit/push/runtime or Android changes. A successful
small development comparison would still not complete Table2, tone-group/MOS/
on-device validation or establish physical complexion recovery.
