# Broader FaceOcc annotation set ready; comparison pending annotations

1November2026. User authorised broader evaluation. The new fixed protocol is
docs/faceocc-broader-evaluation-protocol-2026-11-01.md. This permits a new
evaluation cycle, not reopening threshold/model/crop selection or MST fitting.

Script372 froze24attempts before pixel reads:12additional FairFace train sources
from the389-source inventory,8same-subject MST-E metadata entries outside the
previous25diagnostic IDs,4known challenge cases74882/39083/29321/77101. The
additional-source selection is deterministic by declared hash and does not filter
on old source acceptance, technical success, clipping or experimental tone.
Training-role access checks and duplicate-group uniqueness enforced. All reserved
FairFace development-validation/final-test roles remain closed.

23still images are available for annotation:12additionalFairFace,7MST-E and
4exposedchallenges. One selected official MST-E entry,
subject_10/PXL_20220922_195601107.TS.mp4, cannot be decoded as a still image.
It is retained as a decode failure, not replaced or described as missing.
Initial selection used official keys without an extension/success filter.
All24attempts are preserved in selection/manifest/access records.

The eight nominal MST-E selections concern the same four historically exposed
people; no independent-subject claim. FairFace groups do not verify distinct
people. No official MST labels are invented for FairFace; selectedMST-E labels
are2/4/5/9, not ten-tone coverage. Record observable scene conditions during
annotation and report missing support without refilling the set. Known challenge
images preserve prior rejections; diagnostic use is not training admission.

## User annotation task

Open outputs/faceocc_broader_annotation_v1/review.html. It shows only original
whole-frame square256images, no old masks, FaceOcc outputs or model scores.

1. Enter an annotator name/code.
2. Choose Clear facial skin. Click around several visible interiors where
   possible—forehead, cheeks and chin—then Finish polygon. Exclude eyes, brows,
   lips/mouth, hair and nostril interiors from skin patches.
3. Mark relevant unwanted regions near/on the face: hair/beard, glasses/covering/
   objects, or neck/clothing/background. Avoid only annotating easy distant
   background. Keep labels disjoint; uncertain edges get separate patches.
4. Record scene tags (unknown allowed), gradability and notes. Ungradable images
   need a reason and remain in the denominator. Gradable images need both clear
   skin and relevant unwanted-region patches. No decision implies mask approval.
5. Download truehue_faceocc_broader_patches.json into the review folder.

Browser storage is manifest-bound. Export requires all23available image records
and finished draft polygons; one technical failure is automatically preserved.
Script373 binds exact membership/image hashes, annotator/tags and coordinates,
rejects self-intersecting polygons and conflicting overlaps, then freezes the
actual export. It does not run inference. No actual user polygons or tags have
been received or manufactured at this checkpoint.

Dense interior patches permit local pixel-area evidence, **not full-mask accuracy**.
Do not claim whole-mask precision/recall/IoU, verified skin colour, category fairness
or independent validation. The annotator may remember older predictions, so
materials are prediction-hidden, not an independent blind study.

## Next dependent work

After actual annotations are imported/frozen, run the fixed model/baseline
comparison once; report all24outcomes, failures, uncertain/ungradable cases,
clear-skin loss and unwanted-patch selection per image/lane/condition. Keep
checkpoint, bridge, threshold and minimum pixels fixed. No hidden removal of
bad cases. No comparison inference has run for this new set; no baseline parser
or landmarks were generated either. Annotation preparation only decoded/resized
the originals. Old mask and source decisions remain intact.

Evidence: outputs/faceocc_broader_annotation_v1/selection.json, manifest.json,
access_ledger.jsonl, images/ and review.html. Selection is24/available23/failure1;
all source/model changes still unadopted, panel register updated. No new fits,
lookup export, correction change, deployment or participants.

Verification: JavaScript syntax and synthetic-only DOM harness374passed for
incomplete-export protection, polygon coordinate scaling, navigation, local
storage and exact23record/failure export. No test decisions written to disk.
Two importer tests passed in0.33s for pixel-centre rasterisation, bounds,
self-intersection, conflicting labels and binding. Broader Python run:
905passed in13.40s, excluding tests/test_demo_desktop.py because Tcl/Tk is
unavailable. This is not a full-suite pass. Exact24memberships,23prepared-image
hashes and all frozen metadata/protocol/UI-source hashes verified unchanged.
