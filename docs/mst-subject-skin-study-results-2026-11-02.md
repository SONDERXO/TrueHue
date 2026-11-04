# Existing-subject skin study: review complete, stop before fitting

2 November 2026. User completed the planned review. Actual export
outputs/mst_subject_skin_study_v1/truehue_mst_subject_skin_decisions.json imported
by script388. Schema, completion, exact new-image membership/order, input/mask
checksums, full manifest binding, all display/source hashes and frozen plan
verified. Original export preserved byte-for-byte; prior four human answers and
notes remain unchanged. No synthetic answers used.

## What the review found

19 fixed people/images: 14 new human judgments, four preserved prior judgments,
one processing failure with no invented judgment or replacement.

| Result from structured answers | Count | Subjects |
|---|---:|---|
| Favourable exact-image visual answers | 11 | 0,1,11,12,16,18,2,4,6,7,9 |
| Non-skin selected or image uncertain/not judgeable | 7 | 10,13,14,15,3,5,8 |
| Original parent face-detection failure | 1 | 17 |

Four selected-non-skin answers: subjects10/15/5/8. Facial hair explicitly noted
on10/15/8; subject5's selected-non-skin yes remains even though its note says the
mask is great and questions lighting. Preserve field/narrative tension. Dark
photos were not judgeable for subjects13/14; subject3 was uncertain due to
pixelation/sharpness. Subject15 was also uncertain about judgeability.
No obvious useful-skin loss reported in the 18 judged images; this is human
qualitative feedback, not measured pixel accuracy or a no-skin-loss guarantee.

Subject4 has favourable structured answers but its note explicitly questions
lighting. Retain the mask impression without promoting the photo as a qualified
colour reference. All raw notes remain in decisions.json/original_export.json.
Earlier assistant concerns, including subject12 hair and subject7 chin extension,
stay separate and unresolved rather than overwritten by human preference. Do not
describe the 11 favourable responses as 11 objectively verified clean masks.

## Person support and decision

| MST category | Favourable structured-answer subjects | Count |
|---|---|---:|
| 1 | 16,18 | 2 |
| 2 | 1 | 1 |
| 3 | 0 | 1 |
| 4 | 7,9 | 2 |
| 5 | 11,6 | 2 |
| 6 | None | 0 |
| 7 | None | 0 |
| 8 | 2 | 1 |
| 9 | 4 (lighting uncertain) | 1 |
| 10 | 12 (assistant concern retained) | 1 |

These counts report structured responses, not final calibration admissions.
Only categories1/4/5 have two visually favourable different people before other
evidence concerns. Two is a structural minimum, not adequate precision or validated
mapping. Other categories lack matching different-person support in this fixed
sample. Full official inventory still has single subjects at7/10 regardless of
mask quality. One photo cannot establish robustness across a person's lighting.

**Decision: STOP before MST calibration or correction fitting.** The fixed study
has now supplied real visual evidence and identified specific problems. It has
not established a justified broad matching calibration cohort or task-adequacy
protocol. Do not fit the favourable subset, quietly drop difficult categories,
replace failed photos, re-review the same people, tweak masks/thresholds or launch
another sample automatically. No same-subject repeated isotonic trial.

This is not proof the entire available dataset or ITA/MST method is unusable.
It is the bounded study's honest limitation. Do not keep describing these 18
exact masks as unreviewed. Any future research activation must introduce new
substantive evidence or an explicitly justified scope decision, not rename the
same work. Preserve retained ITA + calibrated MST + facial-statistics decision
tree, correction masks/models/demos and reserved-data locks. No recruitment or
adviser wait is imposed by this result; professional review remains after a good
initial correction model.

## Evidence and verification

outputs/mst_subject_skin_study_import_v1/ has original_export.json, decisions.json
and summary.json including per-category subject support. Strict import passed;
original-export checksum rechecked, all19 outcomes asserted as11/7/1. No new
image inference/processing, calibration, lookup export, correction fit, tests or
runtime changes for this import. Earlier seven focused importer tests and UI
harness remain historical checks, not newly rerun. Panel evidence update only;
no new algorithm adopted or panel approval claimed.
