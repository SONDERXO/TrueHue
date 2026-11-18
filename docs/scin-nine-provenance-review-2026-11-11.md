# Nine-case SCIN provenance reconciliation — 11 November 2026

All nine locally inventoried cases have exact primary case, label, selected-image
and download-log joins. None is newly admitted for calibration, and no pixel
screen is selected. Their historical `training_candidate` intent is not an
explicit current training partition or verified person-independent cohort.

Script 778 preserves both raw MST labels, both raw gradability flags, exact image
slot/path and historical selection. Primary case/label/question CSV hashes match
the earlier retention-checkpoint bindings. There are three agreeing pairs, five
one-category disagreements and one three-category disagreement. Both raw
gradability flags are True in all nine cases (eighteen fields). No labels are
averaged, swapped or selected based on desired results.

## Gradability interpretation resolved from official documentation

The supplied question CSV uses negative cannot-rate wording, while the column
name says gradable. This was recorded as an ambiguity in the initial immutable
reconciliation. The [official SCIN schema](https://github.com/google-research-datasets/scin/blob/main/dataset_schema.md)
describes the India/US gradability fields as whether the annotator could determine
MST from the case images, and their MST fields as trained layperson estimates.
Accordingly, True is retained as gradable; it is not silently inverted from the
question template. This resolves the field-meaning question, not disagreement
between labels, facial support or intrinsic physical tone accuracy. Public
documentation was checked; no dataset images or new dataset package was fetched.

The same schema identifies `case_id` as a case identifier. The local CSV supplies
no separate verified cross-case person identifier. Case grouping can prevent
within-case leakage, but must not be described as proven person independence.
Labels apply at case level, potentially informed by multiple images; that is not
independent proof that one selected face crop alone is an accurate reference.

## Historical selection and allocation

The old selection script explicitly prefers the India label and uses US only as
a fallback to choose broad training groups. Every exact selected-image row here
matches the India label. That historical convenience is not a prospective policy
for the current calibration task. All selected images for these same cases are
counted in the private ledger; only the exact nine inventoried image slots were
reconciled. No additional image is opened or acquired.

No exact image ID has a matching entry in the checked source-preparation
partition table, correction redesign allocation, correction duplicate dispositions
or duplicate-candidate pair list. The source-preparation duplicate-pair CSV is
empty. Missing entries mean **not established by these records**, not duplicate
clearance, unseen status, safe allocation or an unrestricted right to repurpose
other cohorts. No original pixels were hashed or compared. Local aliases remain
aliases rather than additional independent cases.

## Readiness decision

The cohort still lacks a defensible calibration-reference policy for the six
disagreements, confirmed cross-case/person grouping, duplicate clearance and
explicit fitting/evaluation allocation. Current-method facial support, brightness
range and source quality also remain unmeasured. The three agreeing cases alone
have labels3,3,8 and do not supply balanced coverage. Selecting only them would
not resolve the task. No ad hoc annotation request or invented true label follows.

Do not start a calibration fit or generic mask-review queue from these nine
records. Before any pixel work, prepare a research design specifying how both
annotators' outcomes are retained and evaluated, what case-level rather than
verified-person-level grouping permits, and what an exact-nine duplicate/support
screen could establish. If those limitations cannot support the intended claim,
the cohort must remain exploratory rather than being declared a final reference.
This review selects no label policy, screen, fit or acquisition.

Private evidence: `outputs/scin_nine_provenance_review_v1`, including an additive
official-schema clarification preserving the initial question-wording caution.
Primary joins, status counts and metadata bindings pass verification. Zero image
bytes, image hashes, inference calls, fits or predictions. All previous artifacts
remain intact, final24 and older locked images remain byte-unread, and all
admission flags remain false. Decision tree, ITA/MST and single-photo inference
remain required; runtime and Android are unchanged. No contact, upload, commit
or push occurred.
