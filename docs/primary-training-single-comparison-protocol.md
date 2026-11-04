# One planned comparison after primary-mask review

30 October 2026. Freeze this design before importing the new review. The data
candidate set comprises 26 existing original controls, 11 original three-variant
primary candidates and 50 supplemental gamma candidates. Those 61 distorted
masks remain pending; acceptance is not presumed. The 52 clipped new variants,
17 screen-held new variants and earlier 21 approved clipped stress inputs are
preserved separately. Existing experimental clipped fitting remains authorized.

## Fixed method and fitting membership

- Measurement: original square256 HSV AND YCrCb mask, existing morphology/largest
  component, required anatomical/complete-mouth exclusions and minimum 1000
  selected pixels. Do not enable hole filling or reordered application support.
- MST: unchanged matching experimental lookup. Its scientific validation remains
  incomplete; freezing it does not make it a validated final calibration.
- Features: the existing five Lab/ITA/MST values plus six exact input R/G/B
  endpoint fractions, in the frozen endpoint candidate's order.
- Regression: one depth-3 tree, seed 42, minimum leaf size 1, unweighted rows,
  ordinary direct gamma/red/blue targets and fitting-only identity protection.
- Candidate fitting: original controls plus exact newly accepted primary rows
  that pass frozen technical/role/target/provenance checks. Reject/uncertain/
  blank masks and technical holds stay out. No clipped rows enter this one
  proposed *primary* fit; their earlier stress fits/results remain preserved.
- Gamma-only controls use the declared algebraic float inverse, with quantization
  residuals disclosed. Original color/exposure component targets remain bounded
  approximate fits. Validate recipe-specific semantics, not just positive numbers.

## Source-held comparison and reporting

Use the existing 26 source/known duplicate groups. Every variant and original
of the held source stays out of candidate fitting. Reuse that source's frozen
endpoint baseline tree rather than select a favorable fold. Retain each original
clean row only once; do not double-count the duplicate control records in data
preparation. Check exact image aliases and target consistency before freezing
the final accepted row list and folds.

Evaluate both procedures on the identical union of original 47 cases and newly
accepted primary cases. Report separately: 26 clean originals, newly accepted
lightening, darkening, original color/exposure components, earlier 21 stress
cases, original 47 and full matched union. Report source-equal summaries as
well as case counts; different numbers of variants are not additional subjects.
Show measurement failures and their denominators, target/quantization residuals,
mask concerns and estimated severity coverage. No dark-severity or independently
validated MST-stratification claim is supported by this preparation.

All sources are already exposed development. Reserved roles remain locked;
this one source-held comparison is not final independent thesis evaluation.

## Gates and stopping rule

Keep zero correction-induced changes to held clean inputs. Require improvement
against unchanged on accepted primary distortions and the matched overall set.
Report both baseline comparisons and stress results even if unfavorable; no
claim of improved stress behavior unless those results support it. A gate pass
alone does not trigger automatic deployment. A release still needs matching
MST validation, end-to-end/mask evidence and a deliberately frozen independent
evaluation protocol.

If this fixed comparison fails, stop the small-model experiment cycle. Record
the failing strata and decide whether data/reference assumptions or the retained
method limit the intended claim. Do not tune weights, depth, feature thresholds,
recipes, source exceptions or review labels against the result. Do not start
photographer collection before the correction model is finished; use the existing
Google Form then. The working demo remains unchanged during preparation/review.
