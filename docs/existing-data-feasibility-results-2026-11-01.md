# Existing-data feasibility decision

1 November 2026. User requested the existing-data alternative because recruitment
and signed permissions are impractical now. No participants are required for
this audit. Script359 checked saved metadata and file existence only; it decoded
no images, downloaded nothing and fitted nothing. It did not access reserved
correction pixels or change allocations, labels, masks or demos.

**Decision: existing data is not ready for a new retained-method training cycle.**
This is an evidence/readiness finding, not proof the method cannot work or that
new participants are compulsory. Do not start another same-subject fit.

## What was confirmed

| Source | Confirmed supply | What prevents immediate admission |
|---|---|---|
| Four additional MST-E subjects | All337 unique files exist locally; categories2/4/5/9 | Historically exposed; no matching current-measurement admission; do not treat as untouched final evaluation |
| Full MST-E | 19 dataset subjects | Categories7/10 each still have one subject; cannot independently support all ten categories |
| Historical local SCIN downloads | 184 images,167 case IDs, training-candidate roles | Repeated case IDs; case IDs are not verified people; most images are outside the head/neck shortlist |
| Saved SCIN head/neck-at-distance shortlist | 368 records, nine with confirmed prior local paths | Six local cases disagree between annotators; three agree:two at3,one at8; face/reference suitability and duplicate clearance unresolved |
| Additional FairFace inventory | 389 sources outside old32/preferred18 | No official MST labels or verified person separation; historical processing/reference failures retained |
| Actual R1 review | 16 decisions plus two technical holds | Conflicting source-quality notes, measurement contamination, no independent true-colour evidence |

Across all184 local SCIN download records,53 image records have agreeing labels,
130 disagree and one is one-sided. These are image counts, not independent
subjects. Agreeing image categories1–8 have2/12/8/8/3/2/1/17 records respectively;
none agrees at9/10. The full368-record head/neck metadata pool has151 agreements,
216 disagreements and one unavailable label pair; no agreement at9/10 either.
Do not select just the agreeing labels as a shortcut or choose the annotator
whose label makes the model look better. Both annotations and gradability remain
in the evidence. Head/neck tags do not establish a visible usable face.

The earlier nine-local count referred to the head/neck shortlist, not the total
download collection. Both denominators are now explicit. File existence is not
successful decoding or image-quality verification. No new availability is
claimed for unrecorded paths elsewhere on disk.

## What a limited existing-photo study could honestly claim

For synthetic photographic reconstruction, a clear accepted original can be the
target without proving intrinsic skin reflectance. Missing a colour chart alone
does not forbid every development experiment. The five cautious photographic
candidates2434/25517/62000/9654/69407 remain possible target evidence, not a new
five-source cohort or authority to repeat the stopped small-cohort trials.

Keep the user's blur/brightness/shadow concerns for70911/37251/71429/37071/29321,
even where a dropdown says accept. Preserve beard contamination39083, glasses
bridge74882, outer forehead gap77101, and conflicting35986 judgments. Generic
"photo's great" notes are not independent lighting documentation. The approved
enclosed-hole repair does not resolve reference quality or measurement contamination.

A limited study would report return toward an accepted photographed appearance,
not true skin-colour recovery, robust real-world correction or ten-category
validation. It still requires a declared, matching MST development feature
policy and admitted data under the retained method. None is established by
reusing the old incompatible lookup, putting official reference labels into
input features, removing MST, or fitting another handful of the same photos.

## Bounded next step without recruitment

Do not request another general review or restart this metadata audit. If the
user chooses to pursue existing-data development, the next concrete protocol
should be an **eligibility-only audit of the four named additional MST-E
subjects**, not calibration or tree fitting. Their337files are a fixed existing
scope; no replacement subjects and no newly selected SCIN batch by favourable
labels. Preserve every attempted file, failure, original category/lighting,
exposure, and both old/current review scopes. Subject-level separation and
official duplicate-key reconciliation must be frozen before any image processing.

Admission would check actual selected skin and occluders under the unchanged
measurement contract, using a predeclared review workload/selection rule before
opening pixels; no post-error filtering or retries. No image set or sample rule
is frozen by this metadata-only report. It would determine whether eligible
additional subject support exists at2/4/5/9. It cannot fix7/10, establish new
untouched people, validate illumination invariance or automatically permit a fit.
SCIN remains held until person/duplicate, label-disagreement and face-suitability
policy are concrete; the184 local images are not automatically an expansion queue.

If that eligibility evidence is insufficient, stop and document the limitation.
If sufficient, a separate single-cycle development protocol must specify actual
admitted groups, matching-MST use, limited claims, acceptance criteria and one
evaluation/stopping decision before fitting. Reliable final ten-category claims
remain unavailable. No adviser wait is imposed on software/metadata work; no
participant contact, signatures or recruitment is undertaken by this plan.

## Reproducibility and checks

Run scripts/359_audit_existing_data_feasibility.py from the project root.
Evidence: outputs/existing_data_feasibility_v2/summary.json,
mst_additional_subjects.json, scin_readiness.json,
scin_historical_downloads.json, reference_dispositions.json and input_sha256.json.
The initialv1 artifact is preserved; v2 adds full-local SCIN agreement counts
and distinct-case denominators. Script refuses overwrite and checks all saved
input hashes unchanged before writing. Count assertions passed. Paths use
existing saved records; no raw datasets were uploaded.

No pipeline code changed; pytest was not rerun for this metadata-only audit.
Last broader run remains894passed/12.31s excluding desktop GUI tests due to
unavailable Tcl/Tk, not a full-suite pass.
