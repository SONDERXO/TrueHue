# Four candidate sources: fixed-variant and measurement checks

24 October2026. Follow-up to [source screening](source-screening-followup.md).
No training/model/runtime change; human review decisions remain unchanged.

## Procedure

Tested14272,39108,3705 and84897 using the same five fixed dark, bright/warm,
color-shift, unchanged and mild-brightening settings. Sources were resized to256
before generating on hair-clean baseline source masks. Every saved input was
measured separately using baseline HSV-and-YCrCb and fixed YCrCb-only masks,
with paired face geometry, morphology and anatomical exclusions.

The existing material/hair checks and additions-only correction boundary were
held fixed. No reference-mask feature substitution, per-image estimator choice,
threshold tuning or correction-model prediction was used.

## Results

All20 attempts had usable geometry, valid numerical measurements under both
estimators and available experimental correction support. Numerical success
does not establish broad or uncontaminated measurement coverage.

| Source | Unclipped screen passes | Quality holds | Clipped stress | Disposition |
| --- | ---: | --- | --- | --- |
| 14272 | 5 | None | None | Strongest follow-up candidate; all five settings pass the fixed screen. |
| 3705 | 4 | Color shift | None | Color-shift measurement still loses substantial skin coverage. |
| 39108 | 2 | Dark, color shift | Bright/warm:508 pixels | Source/reference boundary needs review before any admission. |
| 84897 | 4 | None | Bright/warm:5 pixels | Promising for four unclipped settings; keep bright/warm stress-only. |

Totals:15 numerical screen-pass candidates, three quality holds and two stress
cases. **None was admitted to training in this step.** Fifteen is not a count
of approved clean references;39108's source concern affects its suitability
beyond the two variants that triggered the numeric screen.

## Estimation reliability versus correction coverage

3705/color-shift retains19.5% of the generation region in the baseline estimator,
61.7% with YCrCb-only measurement, and78.0% in correction support. It still fails
the fixed regional screen under both policies. More measured pixels do not
automatically make its mean Lab/ITA representative.

39108/dark and color-shift have broad overall estimation coverage but lose too
much correction support in the lower-left regional check. The source mask may
include material near jewelry/collar boundaries. This is **not proof of true
facial skin loss**; inspect those reference pixels before calling it a masking
failure. Under the user's face-and-neck requirement, actual neck skin is a
desired correction target, not by itself a reason for exclusion.

14272 has broader baseline measurement across all five settings.84897 also
retains broad coverage in all settings, with bright/warm isolated for clipping.
These findings support follow-up, not generalization, calibrated skin color or
an approved final cohort. YCrCb features are saved separately and never silently
replace baseline features in the existing decision tree.

## Visual assessment

Codex inspected all20 rows on four boards.14272 retains some facial-hair/jaw
and lighting considerations but has useful broad support;84897 has a downward
pose and small boundary uncertainties.3705/color remains visibly fragmented.
39108's lower-left source/support boundary includes uncertain nearby material.
No new expert or human annotation was created. The original pending human
decisions and append-only development exposure history remain intact.

## Next step

Completed follow-up: [nine proposed additions staged alongside frozen22](development-expansion31-stage.md).
The31-row proposal has eight source-group fold plans; no model was fitted or
master/human eligibility status changed.

Prepare a separately versioned **controlled-development expansion** using14272's
five screen-pass pairs and84897's four unclipped pairs as proposed additions.
Preserve their pending/final-thesis status and per-source caveats. Consolidate
their provenance, input-only features and source-group allocations before any
new fitting. This would stage nine proposed pairs from two new sources, not
prove a31-row training cohort is sufficient or formally approved.

Retain all20 attempt records. Keep the two clipped cases outside fitting and
the quality-held/reference-uncertain cases visible. Do not silently drop3705's
color failure, promote39108 because two rows pass, or pool new YCrCb features
with old HSV/YCrCb features. The next learning comparison still needs fixed
source-grouped checks, unchanged controls and no-correction baselines.

Neck localization/correction is not implemented by this facial measurement
study. Its [recorded requirement](face-and-neck-correction-requirement.md)
remains part of the intended implementation and thesis editing record.

## Evidence

- [Four full variant boards](../outputs/candidate_variants_v1/review-index.md)
- [Both estimators and all20 attempts](../outputs/candidate_variants_v1/summary.json)
- [Per-variant disposition](../data/manifests/candidate_variants_v1/screen_disposition.json)
- [Saved-data verification](../outputs/candidate_variants_v1/verification.json)
- Script67: `scripts/67_check_candidate_variants.py` (refuses overwrite).

Verified exact20 saved generation recipes, clipping/inverse targets,40 separate
Lab/ITA measurements,40 retention records and tracked original model/source/
review hashes. No reserved-test or external development-validation source was
used. The four sources were already logged as development-exposed in the prior
screen. They cannot later be presented as a fresh final holdout.

Existing full suite: **464 passed**.
