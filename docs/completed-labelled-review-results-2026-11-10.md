# Completed labelled reviews — 10 November 2026

All30 cases now have saved user reviews. The earlier four missing saves are
resolved. Script729 writes a new audit in `outputs/labelled_annotation_audit_v2`,
preserving the first audit and all annotations.

The new audit verifies **37 revisions /30 distinct cases /10 publisher subjects**,
allthree conditions per subject, zero failed jobs and zero missing reviews. All30
latest selections are explicitly reviewed and have valid Lab/ITA measurements;
the smallest selection contains8,505 normalized pixels. Cases03 and18 were
explicitly reviewed without mask changes, which is valid. Additional revisions
do not become additional independent samples.

All37 bundles pass file membership, size/hash, task/report/payload/label/group
binding, exact stroke-to-mask replay, stroke/change counts, statistics and separate
Lab/ITA arithmetic checks. Allsix new contact sheets were viewed. The original
user edits are unchanged, generated fixtures excluded, and the exact native
manual method is retained. No independent pixel-level skin accuracy is claimed.

## What this permits next

Script730 packages the30 latest records and ten subject-held fold definitions:
each fold has27 fitting observations from nine subjects and allthree observations
of the tenth subject for evaluation. Every case appears in evaluation once;
subjects and their conditions never cross the fitting/evaluation boundary within
a fold. Scores remain their exact original decimal publisher references (2.4–9.2).
Each of thethree conditions has10 reviewed records. Annotation revisions remain
bound to their single source/task identity.

The proposed single empirical ITA→MST assessment is specified in
[the grouped design](refined-mst-grouped-design-2026-11-10.md): subject-balanced,
nonincreasing isotonic mapping, a fitting-subject median comparator, all30
subject-held predictions, no search or runtime promotion. Private rows/folds/
verification are in `outputs/refined_mst_grouped_design_v1`. This is prepared
development evaluation data, not an admitted production calibration or correction
training cohort. The existing threshold interface cannot manufacture missing
official-category support from decimal scores.

The measurements still show strong lighting dependence: within-subject ITA
ranges across conditions are78.3746–163.1326 degrees. Allten cool-condition b*
means are negative; the corresponding warm-condition means are positive. These
are observed measurements under the retained ITA formula, not calibration errors
or proof of an incorrect human selection. They must not be repaired by changing
ITA signs/formulas or silently choosing only warm cases. The grouped assessment
is needed to find out whether a mapping generalizes despite those effects.

No further mask-review request is pending for this snapshot. No mapping fit,
prediction or tree fit has run. No prior MST coefficients are transferred, and
the current overly bright demo is not changed by this preparation. Correction
references and the bounded correction comparison remain separate requirements.

Verification consists of the completed-data audit's exact replay assertions and
the packaging script's30-row/10-group/three-condition/27-versus3 fold checks. No
runtime code changed and no tests were rerun unnecessarily. All source original
images, final24photos and older locked allocations remain byte-unread in this
work. No model inference, acquisition, contact, upload, commit or push.
