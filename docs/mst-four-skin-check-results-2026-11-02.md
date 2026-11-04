# Four labelled skin checks: actual human answers imported

2 November 2026. User completed the four-image check and saved MSTSKINCHECK.json
in outputs/mst_skin_check_four_v1/. Script385 imported the actual export, checking
manifest binding, exact four membership/order, unchanged source/mask/display
hashes and valid answer values. Original export preserved byte-for-byte under
outputs/mst_skin_check_four_import_v1/, with decisions.json and summary.json.

| Exact source | Human answer | Note retained |
|---|---|---|
| subject_1/PXL_20220922_174225452.jpg (MST2) | No selected non-skin, no obvious useful skin loss, judgeable | Small gaps, useful skin still present |
| subject_10/PXL_20220922_195501347.jpg (MST9) | Selected non-skin present, no obvious useful skin loss, judgeable | Stubble/facial hair caught, skin also present |
| subject_11/PXL_20220922_194114230.PORTRAIT.jpg (MST5) | No selected non-skin, no obvious useful skin loss, judgeable | This is great |
| subject_9/PXL_20220922_135619670.jpg (MST4) | No selected non-skin, no obvious useful skin loss, judgeable | This is great |

Original full notes/answer values remain unchanged in the imported export; table
notes are summaries. Three exact masks now have favourable human visual evidence.
Do not continue describing all four as never visually assessed. The fourth has
an explicit contamination hold: some skin being present does not make selected
facial hair acceptable for a skin-colour average. No new beard-specific model
or post-result mask tweak follows.

All four are considered judgeable by the reviewer, with no obvious useful-skin
loss reported. This is qualitative evidence on four saved 256-pixel masks, not
dense truth, measured pixel accuracy, verified lighting/true colour or blanket
approval of the other 19 measured photos/other photos of these people. Preserve
earlier known concerns, original 33 attempts/23 successes/ten failures and all
pre-existing review decisions. Human impressions and assistant observations stay
separate; no user answer inferred from the earlier assistant contact sheet.

## Decision

Complete this review and stop. Preserve three favourable exact-image judgments;
retain the MST9 hair-contamination case as held. No clean-only three-image fit,
automatic subject-wide admission, mapping or tree training. Four different people
at four different categories still cannot provide within-category different-person
support; after the explicit concern, the three favourable photos alone are not
a justified calibration cohort. Numerical interpolation is possible but would
not establish the intended mapping reliability.

This addresses part of the previously missing measurement-validity evidence;
it does not resolve cohort support, a justified evaluation scope or a task
adequacy criterion. Calibration/training flags remain false. No automatic next
batch, recruitment, reference replacement or same-subject tuning. The method,
models, correction masks and reserved roles remain unchanged.

Verification: strict importer completed; original-export checksum checked; summary
asserted three favourable/one selected-non-skin concern/four judgeable. No new
image processing, inference or fits. No pytest rerun for importing actual review
answers; existing synthetic importer harness had already passed. Panel evidence
update only, no panel approval or new algorithm adoption.
