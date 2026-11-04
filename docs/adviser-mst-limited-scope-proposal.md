# Proposed limited MST evaluation scope — for adviser review

28 October2026. The student explicitly confirmed adviser approval of this limited evaluation scope in chat. Approval is recorded as user-reported confirmation, not an independently received adviser message. This does not validate a mapping or approve every subsequent experiment.

## Decision requested

Retain the proposed architecture—facial measurement→ITA→ten-label MST mapping→
decision-tree gamma/red/blue correction—but qualify the evaluation claims to
match the available independent-subject support. Approve or revise the data
roles, limited reporting scope and contingency below before final thesis claims.

This proposal does not remove MST, merge its categories or substitute the
continuousITA/Labdevelopment baseline for the proposed final model.

## Evidence motivating the request

The square256development cohort contains418historically reviewed MST-E images
from15subjects.396measurements succeed;22failures are retained. Existing images
and outcomes have been inspected during development and cannot be described
as an untouched final test.

| Official MST | Measured subjects | Category-level independent comparison |
| --- | ---: | --- |
| 1 | 2 | Structurally possible, small sample |
| 2 | 2 | Structurally possible, small sample |
| 3 | 2 | Structurally possible, small sample |
| 4 | 1 | Unsupported with current reviewed cohort |
| 5 | 1 | Unsupported with current reviewed cohort |
| 6 | 2 | Structurally possible, small sample |
| 7 | 1 | Unsupported with current reviewed cohort |
| 8 | 2 | Structurally possible, small sample |
| 9 | 1 | Unsupported with current reviewed cohort |
| 10 | 1 | Unsupported with current reviewed cohort |

Two subjects/category is merely the minimum structural condition for holding
one subject out while retaining another. It is not a power justification or
evidence of adequate representation. The full official MST-E metadata also
has only one subject atMST7andMST10. Repeating photos does not increase subject
count. Unrepresented subjects or previously rejected photos are not automatically
admitted to remedy these counts.

The current fixed midpoint/isotonic-center calibration recipe failed: category
centers pool and no supported full ten-category lookup is available. Measured
skin-patch ITA also varies markedly across photographed conditions even after
student-reviewed placement away from glasses. Mask/reflection/lighting/pose
effects are confounded. A smaller reporting scope does not fix these failures.

## Proposed reporting scope

1. Keep all ten official categories in source metadata and any eventual mapping
   interface. Do not relabel, merge, omit failures or fabricate thresholds.
2. Describe existing MST-E results as **mapping-development evaluation**, with
   full prior-exposure disclosure. Subject-held folds prevent same-subject
   fitting/evaluation overlap but do not make the data untouched.
3. For any future operational calibrator, report pooled subject-held results
   with exact availability/subject/category denominators. Report supported
   category comparisons forMST1,2,3,6,8separately. Results forMST4,5,7,9,10remain
   exploratory/limited-support and must identify folds lacking that category
   in calibration. Never call this validation across all ten skin-tone categories.
4. Retain well-lit and poorly-lit results separately under the all-condition
   primary development scope. A restricted well-lit-only method requires a
   separate explicit scope decision; no operational lighting filter exists.
5. Separate mapping accuracy from downstream correction quality. A correction
   experiment on held source images does not independently validate MST labels,
   and MST-E does not enter correction-tree fitting. FairFace/SCINcorrection
   sources remain subject to their original reference/mask/eligibility decisions.
6. Report the no-correction baseline, correction parameterMAE, CIEDE2000and
   unchanged/mild harm counts under a declared source-grouped design. No
   ten-category correction-disparity/fairness claim without corresponding
   independent labeled support and adequate denominators.
7. ExpertMOSand actual Android timing remain separate uncompleted evaluations;
   neither is inferred from Python tests or desktop artifacts.

## Calibration versus evaluation data roles

The proposal calls MST-E evaluation-only in its scope but explicitly derives
the lookup from MST-E in the method. Proposed clarification: MST-E may support
mapping calibration/development under subject-held evaluation; it is excluded
from correction-tree training. Previously exposed images cannot be retrospectively
declared the final independent mapping test. A new independent final mapping
evaluation requires suitable new subjects/provenance. If unavailable, disclose
the lack of independent final mapping validation rather than claiming it.

## Preconditions to resume final-model construction

Adviser agreement on reporting scope is necessary for this proposal, but it
does not validate a calibrator. Before assigning MST to correction training
inputs, freeze a justified mapping method and measurement contract, verify its
held-subject performance against a fitting-subject median-label baseline,
report category support/lighting/failures, and qualify its use appropriately.
The completed failed recipe remains part of the record; do not simply repeat it.

Any different lookup method or normalization must be declared before fitting
and evaluated without changing labels/exclusions to improve results. Do not
insert source/reference MST as if it were an input-time estimate. No permission
to silently relax these requirements is requested here.

## Honest deadline contingency

If no defensible mapping is established before the November6working cutoff,
report the MST-based pipeline as an implemented/partially implemented research
prototype with a failed/unvalidated mapping stage and completed development
experiments. Present directITA/Labtrees only as explicitly different baselines.
Do not describe a complete, effective ten-category correction system. Obtain
adviser direction on acceptable deliverables or further study requirements.

## Suggested thesis wording if this scope is agreed

“MST mapping was investigated using previously exposed MST-E development data
with subject-held evaluation. Independent category support was limited: five
categories had only one reviewed subject. Consequently, category-level findings
are reported with explicit support limitations and are not interpreted as
validation of performance across all ten MST categories. The initial fixed
calibration method did not produce a deployable lookup.”

Update the last sentence only if subsequent actual evidence warrants it; retain
the failed experiment in the history.

## Response to record

- Whether this limited evaluation scope and exposure disclosure are acceptable.
- Whether the proposed calibration/evaluation role clarification is acceptable.
- Required changes to mapping method, independent data or completion claims.
- Acceptable deadline deliverables if a validated mapping remains unavailable.

No response has been obtained or message sent by Codex. This draft is prepared
for the student to review and share. [Detailed design](mst-calibration-evaluation-design.md),
[calibration result](mst-square256-results.md), [reviewed-region evidence](mst-reviewed-regions-results.md),
[machine-readable support table](../outputs/mst_limited_scope_proposal_v1/support.json).
