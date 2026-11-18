# Source-matched controlled supervision specification — 11 November 2026

**Specification only: no images generated and no model fitted.** This is one
proposed supervision change on the same seven accepted reference photographs.
No new dataset, mask-review round, calibration project or model family is added.

## What changes and why

The last candidate fitted arbitrary source/editor relationships. Its seven
sources supplied only two catalogue-darkening examples, no explicitly isolated
colour perturbations, and many singleton correction leaves. It edited three held
reference inputs despite satisfying all fitting identity constraints.

The proposal replaces that fitting supervision with **identity plus three
controlled counterparts of each same accepted reference**. It does not simply
append more positive examples while claiming that original examples were absent.
Each fitting reference contributes the unchanged photograph, a darker version,
a brighter version and a red-attenuated version. The original photographic source
roles remain evaluation-only, preserving a check on whether controlled training
helps the actual earlier correction problem.

The recipes and synthetic-restoration structure are not novel; previous closed
experiments already used them. The difference is the reviewed reference/support
context and the replacement of editor-intent fitting pairs with source-matched,
known-operator supervision on these seven bases. This is a limited development
comparison, not newly discovered illumination information or a guaranteed repair.
It must not regenerate the old82-source/756-evaluation experiments or silently
claim that a recipe change solved their failures.

## Exactly three proposed counterparts

Use existing core functions, fixed `medium` engineering preset, on the whole
delivered RGB8 frame (generator alpha=ones). For `u = RGB8/255`:

| Counterpart | Existing implementation | Unrounded transform |
|---|---|---|
| Underexposure probe | `development_roles.core_exposure`, under | `u ** (1/0.70)` |
| Overexposure probe | Same function, over | `u ** 0.70` |
| Colour attenuation | `core_colour_recipe.render_rgb`, cool/none | `u * [245/255, 1, 1]` |

Round to RGB8 with the existing round-to-even implementation. No additive offset,
contrast, new strength, warm/combined counterpart, recipe sweep or new action
catalogue. Colour attenuation also lowers some brightness; it is not a physically
pure chromaticity change or a calibrated camera white balance. Record forward
clipping, quantisation/endpoints and unchanged transformations without filtering
by how easy they are to restore. Do not assume analytic inverse controls yield
exact recovery after RGB8 rounding and local alpha blending.

These are explicitly chosen diagnostic recipes using an existing common preset,
not the literal full Table2 procedure and not tone-dependent severity. `medium`
does not assign any person an MST category. The paper's tone-dependent three-
recipe implementation remains a separate documented method issue; this small
experiment cannot be called completion of that entire requirement.

## Inputs, masks and measurements

Use only the seven existing accepted editor-reference pixel bundles and their
reviewed geometry/support. A synthetic derivative is the same image geometry
with RGB changed. Propagate its own base's reviewed geometric mask/alpha and mark
it **propagated same-geometry annotation**, not a fresh human save or an automatic
detector result. This is a declared manual-template-assisted controlled experiment,
consistent with the user's optional manual route, not an automatic-mask success.
Do not rescue a failed automatic run or transfer masks across distinct photographs.

Recompute every new input's Lab/ITA and green features from its actual transformed
native crop, resized to256 with the existing bridge; retain the1,000-pixel guard.
Compute scene summaries from its actual transformed full frame. No clean feature,
paired difference, reference label or recipe ID becomes a model input.

Apply the existing fixed external isotonic mapping to the21 new ITAs, recording
support and clipping. No mapping fit, contextual substitution or fabricated
photographic MST reference. Existing fourteen vectors remain immutable. The old
held photographic sources use their own independently reviewed masks/features;
never substitute the reference mask for a held source's support.

The generator changes the full simulated frame. Correction remains confined to
the existing local face/neck alpha. Protected/zero-alpha pixels must equal the
**actual distorted input** after correction, not the pristine reference. Regional
scoring must not hide or mislabel that deliberate correction-scope distinction.

## Grouping, budgets and comparison

Seven bases yield21 proposed derivatives. Together with seven existing identity
roles, there are28 controlled roles; add the seven original photographic source
roles for35 available evaluation roles. The eight-group ledger contains40
attempted roles, with all five904 roles unavailable because no accepted matching
base exists. Do not replace904 or change the intended person.

Seven folds each fit six bases × four controlled roles =24 rows and evaluate
the held group's identity, three counterparts and original source = five rows.
Every derivative stays with its publisher group. Original photographic sources
are never fitting rows in this proposed comparison. Skip the904 fit. Retain
the exact depth4 learner,16feature definitions,14actions and native cost renderer.
Equal row weight1 gives each fitting publisher total weight4; no tuned weights or
duplicated identity rows. Identity/corruption balance changes from1:1 to1:3 as
part of this supervision package, so any effect is not an isolated causal claim
about augmentation independent of weighting.

Preparation would require21 new images,21 input-derived MST applications and
294 fixed-action cost values, with zero detector/parser/FaceOcc calls. Target
costs use all positive native application-alpha pixels and the clean base at
the same coordinates. Do not add continuous target optimization or new actions.
Preparation ends with cached arithmetic/geometry/statistic/cost verification
and image review; it does not implicitly execute the seven proposed tree fits.

Before fitting, keep these separate prospective questions explicit:

- Do held controlled counterparts improve RGB and DeltaE over uncorrected input,
  separately for all three recipe types?
- Are all seven held identity images unchanged, with protection preserved?
- Do the same seven original photographic sources avoid worsening their frozen
  prior mean RGB32.0028875772 and DeltaE12.0310912291? Report every harm and missed
  benefit; synthetic success must not conceal worse photographic correction.
- Are all35 available outcomes and40 attempted roles retained, with no held
  group influencing recipes, fitting features or target selection?

No source/per-person fairness or physical-tone claim follows. The already
exposed data and small publisher groups remain developmental. A positive result
would not itself qualify the final model, Android, MOS or the final holdout.

## Verification and next action

Scripts791–792 freeze and verify seven exact reference-base bindings, three fixed
existing recipes, the21-image budget, all40 roles, seven24/5 folds, exclusion of
all original sources from fitting and the unchanged tree/action definitions.
Private package: `outputs/source_matched_restoration_design_v1`.

The next action, if selected, is **controlled data preparation only**. No image,
fit or prediction was produced by this specification. No automatic repair cycle,
new sources, calibration tuning, annotation request or feature search is selected.
All prior artifacts and failed comparisons remain intact. Decision tree, ITA/MST,
face/visible-neck scope and manual option stay. No original photo bytes, model
calls, downloads, contacts, uploads, commits, pushes or runtime/Android changes;
final24 and older locked images remain byte-unread.
