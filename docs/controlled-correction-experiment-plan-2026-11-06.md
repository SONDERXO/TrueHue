# Controlled correction-model experiment plan — 6 November 2026

Subsequent explicit user choice: the isolated
[continuous-score candidate](continuous-mst-correction-protocol-2026-11-06.md)
replaces the integer feature for that experiment. The integer-adapter dependency
below still describes the retained integer-schema path, not a requirement for
the newly authorized continuous candidate. Real calibration, skin eligibility
and person-held evaluation dependencies remain for either path.

Status: design complete; photographic training is not activated. The user
authorized defining the experiment after the material-model suitability check.
This plan preserves ITA, MST and facial statistics with gamma/red/blue outputs.
It does not authorize substituting a reduced-feature method.

## Question and scope

Can a fixed three-output decision tree predict useful correction controls on
controlled photographic distortions when every input feature is available from
the distorted image under one compatible measurement contract?

The claim would concern recovery of a photographic reference under the declared
recipes, not physical skin colour, lighting invariance, clinical accuracy or
general performance on unobserved people. Existing exposed photographs can
support development diagnostics only. No current package establishes an
eligible full-method training cohort.

## Inputs and targets

Retain the ordered `MST_FEATURES` schema in `src/ita_estimation/mst_lookup.py`:
the existing measured Lab/ITA and endpoint features plus `input_mst_index`.
Freeze the exact feature-name list and measurement-contract hash in the future
execution manifest; reject missing/nonfinite values or a different order.
Measure original RGB values, not appearance-enhanced parser inputs. Never use
reference-image colour, reference MST, recipe identity or illumination labels
as inference features. Use the actual distorted-image masks, not borrowed
reference masks or intersections that hide missed regions.

Use the retained correction renderer and three positive controls: gamma,
red gain and blue gain. Existing target fits are conditional operator optima,
not automatic predictions or proof of reliable training labels. Targets must
be bound to their exact image, renderer, alpha and objective. A new support
contract would require a separately specified target-generation step; do not
reuse old controls under changed masks without establishing compatibility.

## Explicit MST decision

The contextual ITA + Lab experiment estimates a continuous score on 1–10.
The correction schema requires an integer index on 0–9. There is currently no
validated adapter or compatible real-data contextual fit. Therefore:

- Do not round, truncate, fill a median/zero, reuse historical incompatible
  thresholds, insert source labels, or pass a continuous score as an index.
- Do not silently omit MST or call a reduced-feature tree the retained method.
- Before photographic fitting, specify the category meaning and adapter from
  evidence appropriate to that meaning. Decimal publisher scores do not alone
  establish integer-category ground truth. If that cannot be justified, a
  continuous-score correction schema would be a separate explicit method
  decision with its own comparison, not an implementation shortcut.
- Fit any upstream estimator and adapter using outer-training subjects only.
  Generate downstream tree-training MST predictions with inner subject-held
  fits; predict the outer-held subject using only outer-training information.
  No held-subject label may enter calibration, adaptation or tree training.
  Any baseline, tuning or selection must also respect those boundaries.

This resolves the execution policy: missing compatible MST prevents a full
photographic fit. It does not pretend the scientific mapping is solved.

## Data roles and fixed comparison

Use the existing 12 photographic lineages and their 14-case recipe matrix only
as a possible development inventory: one clean, eight core and five stress
cases per source, 168 attempts. No new distortions, severity sweep or source
selection based on favorable outcomes is proposed. The common medium preset
is an engineering condition, not an MST label. The old 168 rows remain
unadmitted and their observed material/support failures remain recorded.

Before execution, justify source/reference and actual-input support eligibility
and freeze exact row roles. Keep every attempted case in evaluation accounting;
never replace failures or quietly reduce the denominator to successful rows.
Uncertain/excluded fitting rows need explicit reasons fixed before fitting.

Known duplicates, all descendants and all photographs of a verified person
must remain together. The 12 lineages do not establish 12 independent people.
With identity relationships unresolved they remain one unsplit development
holding block, so no defensible held-person fold count is specified now. Do not
invent a random image split. A later justified grouping manifest is required
before predictive evaluation can execute; new independent evaluation data are
not acquired by this plan.

One candidate only: retain the existing target-standardized tree procedure
(`src/model_training/target_scaled_tree.py`) and its imported fixed settings.
Freeze those settings verbatim with the future execution manifest. Compute
normalization and leaves using fitting rows only; no depth/seed/leaf sweep.
Compare candidate predictions with neutral controls (unchanged input). Show the
saved per-case oracle-fit recovery separately as a conditional capacity
diagnostic, never as a competing predictive model or feature source. Do not
reuse an old tree trained under an incompatible mask/feature contract as a
matched baseline.

## Evaluation fixed before execution

Report clean, core and stress layers separately, per source and source-equal
aggregates, alongside attempted/available/predicted counts. Include parameter
errors, rendered RGB8 MAE and relative CIEDE2000 on the full frozen reference
support, including skin regions missed by the distorted-input mask. Report
spatial support loss and changes outside reference support separately; these
are support diagnostics, not object-ground-truth accuracy. Inspect seams,
glasses and beard behavior without converting visual impressions into labels.

Retain failures as operational unchanged-input outcomes with explicit reasons;
also report their count separately. Report clean-image colour changes,
regressions, clipping and boundary-hit controls. No post-hoc favorable-only
average, acceptance threshold, automatic adoption or accuracy claim follows
from lower mean error. If executed later, fix visual inspection to the same
combined-cool-under core and stress-combined-under cases on every source,
including failed outputs. This plan activates no new review task.

## Work that can execute before photographic eligibility

A separately versioned generated-data harness can verify ordered full-schema
inputs, three-output portable-tree replay and rejection of unavailable MST.
Fixture integer categories would be explicitly fictional software inputs,
never photo-derived labels. Check group leakage rejection and fold-local
normalization on arithmetic fixtures. These tests cannot estimate correction
quality, resolve identity, qualify skin support or validate MST calibration.
No such new harness or fixture fit was executed in this planning step.

## Execution boundary and stopping point

Photographic execution requires a concrete compatible MST estimator/category
policy, justified support/reference roles, justified grouping and a frozen
manifest binding inputs, targets, code, settings and folds. These are substantive
dependencies, not a request to repeat metadata inventories. No count of current
eligible subjects or train/test rows is invented here.

No new fit, inference, image processing, mask repair, source admission, sample
expansion, runtime/Android change, contact or sharing occurred. Existing private
evidence and research/noncommercial, citation and no-redistribution terms remain.
The new document and its local links were checked; no scientific or software
test result is claimed for this documentation-only change.
