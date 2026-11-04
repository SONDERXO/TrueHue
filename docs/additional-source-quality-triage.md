# Additional-source quality triage — 30 October 2026

Inspected all 24 planning candidates using their existing saved reference,
reference-mask, distorted-input and input-mask boards. This narrows the missing
judgments before asking for another review. No new distortion, mask experiment
or model fit was run. These are assistant observations, not user approvals.

| Result | Sources | Meaning |
| --- | ---: | --- |
| Existing distorted technical hold | 5 | Recorded face/landmark failures remain; no distorted training admission |
| Visible concerns to resolve | 16 | Mask contamination, large gaps, blur, obstruction or reference-lighting concerns |
| More promising for focused judgments | 3 | 2434, 25517, 39083; still unapproved |

The five technical holds are 61590, 9572, 71785, 72367 and 58767. Four failed
the exactly-one-face requirement; 71785 lacked required landmarks. The existing
failure reasons are preserved even when a board displays partial support.

Visible problems elsewhere include selected reflective sunglasses (10567),
glasses (46277 and 2025), hair across the face (58767), tiny mask support (9572),
strongly fragmented distorted support (19067 and 11900), and low image detail.
These observations do not amend the original mask rules or create automated
source rejections. A warm-looking reference does not by itself establish a
wrong white balance; independent neutral-color truth is unavailable here.

## The smallest useful follow-up

The [focused three-source judgment page](../outputs/additional_source_reference_review3_v1/review.html)
is now ready, with separate decisions and notes for each scope and a JSON export.
No decisions are preselected or imported. See
[the boundary before another fit](broader-source-next-fit-boundary.md).

The first three cases on the [triage page](../outputs/source_planning24_triage_v1/triage.html)
are 2434, 25517 and 39083. Each needs three distinct judgments before use:

1. Is the saved original a usable color/detail reconstruction reference, with
   concerns preserved? This is not certification of true skin color.
2. Is its exact original-rule facial mask acceptable?
3. Is its exact displayed distorted mask acceptable, separately from the original?

2434 has nose/cheek holes in the distorted support. 25517 needs boundary and
small forehead-hole inspection. 39083 needs peripheral hair and mouth-boundary
inspection. The relatively broad masks are reasons to inspect these first,
not proof of accuracy. Do not propagate any future original approval to variants.
No previous user review is being repeated, and no 24-image review is requested.

All three existing distortions are clipped stress examples: clipped generation
support fractions are 33.67%, 42.43% and 37.66%, respectively. Even if all three
were accepted, they would not supply a recoverable normal-exposure training
cohort. Their separate original-reference judgments could inform a future frozen
paired-data design. Do not train a three-source candidate or start small tweaks.

## What this changes

The inventory's source count is not the main readiness measure: the saved
24-source sample contains substantial quality and processing attrition. This
is descriptive triage of a hash-selected planning list, not a representative
mask-accuracy estimate, a final cohort or proof that the other 383 sources fail.
These 24 have only light/medium experimental severity estimates; the dark-tone
coverage gap remains. Do not quietly replace failed cases to make a clean batch.

Before the next fit, freeze a broader source-selection and reference-quality
plan, a recoverable primary-versus-clipped-stress data design, and group-held
evaluation rules. The three leads are an initial quality checkpoint within that
work, not a new training experiment. Retain the independent MST calibration/
validation requirement and disclose historical exposure. No model-quality
improvement or completion is claimed by this triage.

## Verification

Scripts 286/287 record derivative-file access before reads, enforce training-role
membership, verify saved board/reference hashes against original preparation,
and preserve 24 per-source observations. Six four-row sheets were visually
inspected. All 48 decoded files were existing training derivatives; raw source
images and reserved evaluation pixels were not opened. No fitting admission,
human decision, model, lookup or demo preset changed. Full pytest was not rerun.

- [Exact technical records](../outputs/source_planning24_triage_v1/triage.json)
- [Scoped assistant observations](../outputs/source_planning24_triage_v1/assistant_observations.json)
- [Access ledger](../outputs/source_planning24_triage_v1/access_ledger.jsonl)
- [Hash verification](../outputs/source_planning24_triage_v1/verification.json)
