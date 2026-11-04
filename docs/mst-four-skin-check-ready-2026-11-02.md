# Four labelled skin measurements: simple human check ready

2 November 2026. User explicitly asked to proceed with verifying skin measurements
in labelled photographs, following the stop decision. This authorises preparing
this exact small human check, not calibration, processing a broader inventory or
changing the model. Unlike the completed FairFace preference review, these are
labelled MST-E images and exact saved candidate masks.

Script385 selects one saved technical success per each of four subjects from all
23 current FaceOcc MST-E successes, by lowest SHA-256 of
`truehue-mst-skin-check-v1|image_id`. No filtering by appearance, features, known
concerns or expected answers. Freeze selection before opening selected pixels.
All 33 original attempts/ten failures remain in parent evidence; four selected
successes do not replace the attempt denominator. No replacement if difficult.

Page: outputs/mst_skin_check_four_v1/review.html. Shows original 256-pixel saved
input, translucent green overlay and selected pixels alone. Three yes/no/cannot-
tell questions per exact mask: selected non-skin, obvious useful skin loss, and
whether the saved image permits a judgment. Optional note, no polygons. Existing
anatomical eye/brow/lip/nostril, hair and neck exclusions are expected, not defects.
All cases need answers before export. A contract-specific browser key preserves
progress where local storage is available; explicit JSON export remains required.

Export: truehue_mst_skin_check_four_decisions.json. Import with:

    venv\Scripts\python.exe scripts/385_prepare_mst_skin_check.py --import-review PATH_TO_EXPORT

Importer validates exact manifest binding, four ordered IDs, source/mask/display
hashes, decision membership and unchanged original sources. Rejects malformed or
altered binding before creating output. Preserves original export and all human
answers. No automatic admission, calibration or training; favourable judgments
provide only exact-image visual evidence, not approval of every pixel or other
photos of the same subject, true colour, independent validation or matching MST.

Assistant inspected all four boards: second contains apparent beard selection;
hair boundaries and pose/eye exclusions require care in the others. Assistant
observations are not prefilled human decisions. No actual review export has been
received. Do not silently turn answers into a clean-only fitting subset. Even
four favourable judgments would leave only four singly represented categories.

Verification: JavaScript syntax check passed; isolated temporary synthetic import
harness rejected an altered source binding, preserved a valid synthetic export
and kept both admission flags false. No synthetic answers written to actual
review/import evidence. Source preparation initially encountered a failed parent
attempt without an input path; handled absent input metadata, then built page
successfully before review. No new model inference or raw-image decode; display
generation from saved inputs only. No broader pytest run, runtime code unchanged.

Panel status: user-authorised small visual evidence procedure, not a dataset or
model adoption, not panel-approved. Original paper wording must be verified when
drafting a future letter. Original roles, masks, models and failures preserved.
Stop after this four-image check; any next activation requires new justified
scope rather than an automatic second review or same-subject fit.
