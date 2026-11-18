# Concrete correction-input design and readiness result

11 November2026. Reviewed the actual learning alternatives and one published
input cue. The result is one prepared comparison specification, not a fitted
replacement. Decision tree, ITA/MST, original-photo restoration, single-photo
inference and manual support remain. No masks or reviews need repeating.

## Why this design

A new exposure/colour/none classifier would reuse the same summaries and repeat
an earlier classification-induced partition approach that failed. Likewise,
standardizing output targets or splitting exposure/colour heads is not an untried
fix. Those historical methods remain closed and are explicitly cited in the plan.

The proposed change instead adds two full-scene sixth-moment colour ratios to
the existing16 inputs. This is a distinct measurement of the already captured
image, placing more influence on bright pixels than the existing channel means.
The rationale comes from Finlayson and Trezzi's primary paper, not from selecting
a favourable exponent on FFHQ. Fixedp6 is a literature-motivated engineering
choice, not proven optimal here. This uses rendered RGB8 and a fixed+1code ratio
convention, so it is not a physical illuminant estimator or a literal reproduction
of their calibrated-image study.

Source: [Shades of Gray and Colour Constancy](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/cic/12/1/art00008).
The paper links mean/max statistics through channelwise Minkowski means and
states that scene-colour assumptions may fail. Its success on different images
does not establish TrueHue correction benefit or justify replacing the tree
with an automatic white-balance algorithm.

## What the fixed screen establishes

All44 cached prepared inputs yield finite descriptors:88new values; all704parent
feature values remain unchanged in the18-value vectors. All33 paired comparisons
are retained. The11cool pairs decrease the red/green descriptor; blue/green stays
unchanged, as expected for the red-only recipe. The original mean-based ratio
also responds: paired responsiveness alone is not evidence of new superiority.

Across the11 originals, the p6red/green standard deviation is0.069068 versus
0.047615 for the existing first-moment ratio. The average cool shift is-0.039827
versus-0.039672. Thus this cue does not improve that simple red-signal/scene-
variation comparison; no such improvement is claimed. Blue/green dispersion is
smaller,0.046020 versus0.067038, but the fixed blue target is constant and that
fact supplies no demonstrated blue-correction task. Recipe marginal ranges
overlap. None of these descriptive statistics is a classifier, a fitted threshold,
a multivariate impossibility proof or an adoption gate.

The p6measurements are operationally ready for a conditional-information test,
not validated as useful. Any eventual improvement could reflect synthetic RGB8
encoding or scene content rather than real camera correction. The same scene's
clean reference is used only for supervision/analysis; paired differences never
enter the inference vector. There is no input distortion label, reference photo,
subject ID, inferred neutral-patch label or new MST reference.

Independent scalar math.fsum replays verify132channel moments,88descriptor values,
704preserved inputs and33pair deltas. All pass. The screen uses only hash-bound
cached pixel packs, no original/locked photo reads, image models, mapping fits,
correction training or new image generation. No visual-quality claim is made.

## One prepared comparison

Keep44rows/11photo-held40fit4eval folds, nominal targets, renderer, depth4/seed42/
minleaf1/unweighted squared_error and scoring support fixed. Append these two
features only. Compare11candidate fits/44held outputs to the SAVED16-feature
baseline; do not refit the parent, pool with PPR, create an ensemble or fit all44.
This tests incremental predictive value conditional on existing features, not
whether the cue is a reliable illuminant estimate on its own.

Frozen prospective checks in the prepared plan require complete coverage and
protection; every recipe mean RGB and DeltaE better than uncorrected input and
no worse than the saved parent; all11 identity outputs unchanged. Preserve every
individual harm and parameter error. These are checks for this comparison, not
universal paper requirements. The exact-identity engineering check is distinct
from the paper's restoration-benefit question, which must also be reported.

No comparison was executed by this design/readiness review. A failed result must
close this candidate without another exponent/threshold/weight/depth/guard/recipe
variant. Software readiness and literature motivation are not passing scientific
results. This plan is a proposed scene-feature extension; no adviser approval,
production adoption, fairness/physical-tone claim or paper completion is inferred.

All prior records/failures preserved; final24 and older locks byte-unread. No
acquisition/contact/upload/commit/push/runtime/Android changes. Working correction
quality remains unresolved. Existing reviews are complete; no new user input is
required to define or implement this particular fixed comparison.
