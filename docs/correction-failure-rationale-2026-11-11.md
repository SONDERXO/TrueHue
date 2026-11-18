# Correction failure paths and one objective proposal — 11 November 2026

The saved results support testing a **training-objective change**, not another
data search, extra identity flag or inference boundary. The rationale is unequal
raw RGB-loss opportunity combined with held-input confusion. This is not proof
of cause or a demonstrated repair. No new fit or alternative prediction occurs.

Scripts797–798 inspect the saved seven trees,24 fitting rows per fold,35 held
outputs and the existing action-cost matrices. Repeated fitting appearances are
not counted as independent examples: each role has seven unique images appearing
in six fitting folds,42 appearances per role,168 total appearances.

## What the training objective sees

| Fitting role | Mean identity cost | Mean best-catalogue cost | Share of available absolute RGB reduction |
|---|---:|---:|---:|
| Identity |0|0|No correction benefit; hard fitting constraints apply|
| Underexposure |26.02555|0.67922|50.09%|
| Overexposure |23.63813|0.73698|45.26%|
| Colour attenuation |2.41245|0.05934|4.65%|

The three corruption types have equal row counts, but correcting an exposure
example offers roughly10times the absolute RGB reduction of correcting a mild
colour example. These figures are catalogue opportunity budgets, not a causal
decomposition of every learned split. They show what an absolute-error objective
rewards; they do not imply a defect in RGB metrics or a guaranteed improvement
from equalizing opportunities.

Saved mean fitting selected costs are5.79428 underexposure,2.36695 overexposure,
1.30307 colour and0 identity. Hard identity constraints are satisfied in fitting.
The held colour and identity failures therefore remain generalization failures,
not missing labels or a demonstrated arithmetic bug.

## What the held paths show

All six harmed colour cases land in fitting leaves containing exposure examples
only. All six edited reference cases land in leaves without fitting identity
examples. Five of seven held same-base identity/colour pairs share a leaf. The
model often cannot distinguish their small colour difference from the context
that led to an exposure action. More severe correction actions are available,
but availability does not establish that the input features select them safely.

The feature set and source content still matter. Changing an objective supplies
no new illumination information or guaranteed separation. These findings do not
justify adding a post-hoc guard or tuning a threshold on the failed cases.

## One candidate worth specifying

Propose a fixed **relative rendered-loss** objective using existing fitting costs:

- For each nonidentity fitting row with positive uncorrected cost `C0`, use
  `relative_cost[action] = raw_cost[action] / C0`.
- Keep fitting identity rows and their exact zero-cost feasibility constraints
  unchanged. Do not divide identity rows by zero or introduce an epsilon/threshold.
  The current21 corruption rows all have positive `C0`; an unexpected zero must
  be recorded rather than assigned a made-up scale.
- Compute this only on the fitting subset. Neither held costs nor references
  enter prediction. Inference remains the same single decision tree on the same
  sixteen input features; no second model, condition input, gate or lookup is added.
- Preserve raw costs, the fixed catalogue, features, mapping, depth, folds,
  recipes, masks and renderer. Evaluate in original RGB/DeltaE units using the
  same criteria, not normalized scores selected to make the candidate pass.

This gives each distorted fitting row an identity baseline of1 and makes harmful
actions on small-error cases costly relative to doing nothing. It is still a
weighting-related change; do not disguise that or claim a wholly new method.
There is no normalization-strength search. It may merely move the tradeoff and
fail reference preservation or useful recovery, which must remain visible.

The prior key/layer-balanced experiment normalized continuous parameter targets
and balanced source/layer contributions in parameter-MSE regression. It already
failed and remains closed. The present proposal concerns per-example
identity-baseline normalization of rendered finite-action costs, a different
arithmetic objective in the checked implementation. That distinction is a reason
for a narrowly specified test, not proof that another balancing intervention will
work or permission to repeat old candidate families.

## Scope and next action

The next deliverable should freeze this **one objective comparison** against the
already saved raw-loss result: seven candidate fits, the same35 held predictions
and40 attempted roles, unchanged colour/exposure, original-source, identity and
pixel-protection checks, and a single-comparison stop. Do not rerun the raw parent,
change recipe strengths, seek more sources, or add masks. No fit is authorized
by this rationale review; this is a concrete candidate to specify, not an adopted
model or replacement acceptance rule.

Independent checks pass168 saved training appearances,35 held contexts, seven
pair-path joins and four loss-budget summaries. Private evidence:
`outputs/correction_failure_rationale_v1`. No image bytes, model calls, fits or
new predictions were used. All previous results stay intact. The paper can use
this as a correction-objective diagnostic without claiming intrinsic tone or
fairness. Retain ITA/MST, the final decision tree and manual option. The app,
Android, final24 and older locked images remain untouched; no acquisition,
contact, upload, commit or push occurred.
