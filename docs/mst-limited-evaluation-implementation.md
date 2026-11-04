# Limited-scope evaluation tooling

28October2026. Implemented reporting infrastructure for the proposed scope;
adviser approval remains pending and no calibrator or correction model changed.

`src/evaluation/mst_validation.py` evaluates explicit held-subject predictions
against official1–10MST labels. It checks unique image IDs, consistent subject
labels, complete fold coverage, no held-subject leakage, valid categorical
outputs and a median baseline derived solely from fitting subjects. Every
measured image must have an explicit prediction orNone. Unmeasured inputs
cannot acquire fabricated predictions. Caller records are not mutated.

Outputs include image/equal-subject ordinalMAE, exact and within-one accuracy,
same-row paired baseline, support-qualified comparisons and separate baseline-only
metrics. Each is reported overall and byMST, recorded lighting and subject,
with attempt, failure, unavailable-prediction and unsupported-category denominators.
No prediction meansNone metrics, not0%accuracy. Empty categories remain visible.

Script146applies it without fitting to the completed fixed calibration evidence:
418attempts,396measurements,22processing failures,0available mapping predictions.
Of measured images,180have no other fitting subject from their category in their
held-subject fold. Overall accuracy and paired comparison are unavailable.
The396-image median-only baseline is retained separately and never presented
as paired candidate performance. Subject/category/lighting totals reconcile.

[Report](../outputs/mst_limited_evaluation_v1/review.html) ·
[Machine-readable metrics](../outputs/mst_limited_evaluation_v1/summary.json) ·
[Availability CSV](../outputs/mst_limited_evaluation_v1/availability.csv) ·
[Verification](../outputs/mst_limited_evaluation_v1/verification.json).

**620Python tests pass in14.25s**, including13newtests covering paired denominator
accounting, subject weighting, unavailable predictions, absent support, invalid
labels, subject leakage and silently dropped rows. Original saved input hashes
remain unchanged. This tooling is reusable when justified mapping predictions
exist; it does not fit one or establish scientific validity by itself.

Next gate remains actual review of the [limited-scope proposal](adviser-mst-limited-scope-proposal.md)
and a justified mapping/data decision. No approved method change, new label,
data admission, repeated calibration search or final model is claimed. Android
stays paused; CPM deferred; original reviews and holds remain intact.
