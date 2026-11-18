# Source-matched correction comparison — 11 November 2026

**The candidate fails the controlled-colour and identity-preservation checks and
is not adopted.** Better underexposure recovery and slightly better original-
photo averages do not offset those failures. This fixed comparison is complete
and closed, with no automatic retuning or additional data project selected.

Scripts795–796 execute exactly seven depth4 fits,24 controlled training rows
from six publisher groups per fold, and35 held predictions. The original seven
photographic source roles are evaluation-only in every fold. The five904 roles
remain unavailable in the forty-attempt ledger, with no904 fit. Features,
mapping, fourteen actions, learner and renderer are unchanged; no new mapper,
image model or action search is used.

## Controlled held cases

| Case type | Input RGB → output RGB | Input DeltaE → output DeltaE | Benefit / harm / unchanged |
|---|---:|---:|---:|
| Underexposure |26.0255 →7.5603|9.0354 →2.5665|5 /0 /2|
| Overexposure |23.6381 →21.2974|7.9137 →6.9944|3 /4 /0|
| Colour attenuation |2.4125 →22.4116|2.3226 →7.5916|1 /6 /0|

Counts agree for RGB and DeltaE within each controlled recipe. Although mean
overexposure error improves, four of seven overexposure cases worsen. The
colour-only mechanism suffers a substantial mean increase, not a small numerical
failure: most mild red-attenuation inputs are sent to exposure-strength actions.
The frozen requirement that each controlled recipe improve fails in both metrics.

The known catalogue can restore these examples much more accurately when the
reference is used to select the action, but that target-aware supervision does
not make the input-only tree choose the right action on a held group.

## Preservation and original-photo transfer

Six of seven held reference/identity images are edited; only787's reference is
unchanged. This is worse than the preceding comparison's three edited references.
All protected and zero-alpha pixels are unchanged relative to the actual input.
Fitting identity constraints remain satisfied; their preservation does not
generalize to these held references. The identity check fails without changing
its definition or tolerance.

| Seven original photographic sources | Uncorrected | Prior photographic-supervision tree | Controlled-supervision tree |
|---|---:|---:|---:|
| RGB MAE |37.603367|32.002888|31.278045|
| DeltaE |13.241710|12.031091|10.929120|

The original-source mean nonworsening checks pass. Three original sources improve,
two worsen and two remain unchanged in both metrics.330 worsens from RGB17.021
to39.970 and DeltaE6.185 to13.084.455 worsens from RGB12.225 to20.892 and
DeltaE5.659 to8.028. These harms remain visible rather than being hidden by the
average benefit.1117 and1188 remain unchanged;767,787 and990 improve.

Overall checks: complete35/40 coverage accounting, original-source mean
nonworsening and pixel protection pass; per-recipe mean improvement and identity
preservation fail. No passing criterion overrides a failed one.

## Visual and arithmetic verification

All35 held input/output/reference detail panels across seven group boards and
the five-role blocked904 ledger were viewed. Underexposure restoration succeeds
on several examples; overbrightening or unnecessary darkening is visible on
references and mild colour cases. Existing small-native-face and interpolation
limitations remain; these enlarged views do not add image detail. This review is
diagnostic assistant inspection, not human expert MOS or a new mask approval.

Independent verification checks63 recorded nodes,6,214 possible split options,
leaf action optima, all35 held routes,35 full native render replays, RGB and
standard CIEDE2000 metrics and every frozen check. All pass without verifier
refits. Training records exclude every original photographic source and the held
publisher group. Thus the result is not explained by a demonstrated arithmetic,
rendering or role-leakage bug.

Splits use L*seven times, a*six, ITA five, green log-contrast five and four other
existing scene/green features once each. MST remains constant and unused; no
meaningful MST conditioning or fairness result is claimed. Exact geometric mask
propagation/manual-template assistance remains declared; this does not validate
an automatic masking pipeline or the complete tone-dependent Table2 study.

## What this means for the correction model and paper

The supervision change improves one restoration type but still does not reliably
separate mild colour/identity cases from exposure adjustments on held content.
That is direct correction-model evidence; neither more accurate calibration nor
additional mask marking is shown to resolve it. The result does not prove all
decision trees or the photographic-restoration objective impossible.

Record this as an exposed-development comparison and limitation in the paper,
separating synthetic controlled results, original photographic transfer and
identity preservation. Do not pool their baselines, replace failed checks with
mean improvement, or claim a completed final model. The user's working-model goal
remains unmet. No negative-results-only thesis outcome is substituted by default.

The fixed comparison stops here. No guard, classifier, alpha/feature/weight/depth
sweep, recipe replacement, calibration redesign, source search or further mask
queue is selected. A subsequent intervention would need to address the observed
correction-direction confusion with a concrete rationale; it cannot be an
automatic repair of these held cases. All previous failed experiments stay closed.

Private evidence: `outputs/source_matched_restoration_comparison_v1`. Seven
models,35 outputs/predictions, metrics, full-frame and detail boards, verification
and the blocked ledger are preserved. Existing cached paired pixels were used;
no original JPEG/TIFF, final24 or older locked photo bytes were read. No
image-model calls, mapper fits, acquisition, contacts, uploads, commits, pushes
or runtime/Android changes. The current demo—including its brightness issue—is
unchanged. Retain ITA/MST, the final decision tree and the authorized manual option.
