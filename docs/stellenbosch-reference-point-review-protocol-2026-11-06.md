# Small reference-skin review — 6 November 2026

User authorises the proposed small local reference review. Prepare six fixed
difficult/control examples from existing new-source outputs, not new photos:
case04(glasses/cool),case21(beard/warm),case25(dim forehead/cool),case30(dim
fragment/warm),case16(broad facial-support control),case29(parent-landmark failure).
These are deliberately exposed diagnostic examples, not random independent
validation or a class/subject-balanced cohort. Cases29/30share one subject.
Freeze membership and image/source/model/mask hashes before preparing review UI.
No replacement if an image is hard to judge.

Show original224context plus original native crop with nearest-neighbour zoom;
do not show predictions, source scores, previous judgements or enhanced images.
Mark individual native-grid pixel centres, not interpolated256pixels or full
polygons. Up to50points per image is a UI safeguard, not an accuracy sample-size
rule. Labels: skin, hair_or_beard, object_or_other, uncertain. Avoid claiming
precision at mixed edges; uncertain is valid. A marked image needs at least one
definite point; an unjudgeable image may have only uncertain/no points and must
include a short reason. Do not force both skin and non-skin points or full masks.

Actual reviewer identity/code and all six completion statuses are required on
export. No default answers, assistant-prepopulated marks or generated decisions.
Persist drafts locally with plan-specific keys; explicit JSON export is the
actual response artifact. State that the user has seen prior model outputs, so
prediction hiding now is not independent/blinded evaluation. No image sharing.

Strict importer binds exact schema, plan hash, case/image hashes and membership;
reject duplicate/extra/missing cases, contradictory duplicate pixel labels,
boolean/noninteger/out-of-range coordinates and invalid status/labels. Compare
actual definite point coordinates with the frozen final mask on the native grid;
failed pipeline output is unavailable, not predicted non-skin. Summarise skin
point inclusion and unwanted-point inclusion separately with uncertain/excluded
and unavailable counts. These are sparse-point agreements, not segmentation
accuracy, skin coverage, colour validity, independent native sample estimates,
calibration admission or a licence to tune on the points.

Freeze source/mask bindings and keep all parent/source packages byte-identical.
Prepare importer and meaningful synthetic tests without creating an actual
review export. Synthetic UI harness must never write human decisions. Stop
awaiting the user's real export before any measured point comparison. No new
model inference, threshold changes, fits, sampling batch, runtime update,
recruitment or author contact. All images/IDs/labels/manifests/review outputs
remain ignored local files under research/noncommercial/citation/no-sharing terms.
