# Full-face coverage repair — 30 October 2026

Implemented a separate, usable full-face mask preview that addresses the holes,
rectangular spill and cropped chin/forehead seen in the recent review. The user
explicitly authorized reusing the existing local face parser for masking:
“Allow the existing parser for masking.” ITA + calibrated MST + decision-tree
correction remain the retained downstream method. This changes the former
rule-based masking stage; it is not silently described as the same old method.

## Result and how to view it

[Before/after gallery: 24 cases](../outputs/semantic_face_coverage_v1/review.html).
Each row shows the photo, old color mask, new mask overlay and new binary mask.
The fixed scope is six recent reference images, their fifteen new primary
inputs, and three already exposed glasses/occlusion diagnostics. No reserved
evaluation images were accessed. All24 produced candidate masks.

Double-click `run_face_mask_preview.cmd` to choose a photo and open its saved
mask preview. This standalone tool does not run ITA/MST or image correction.
It uses the existing square256 processing size and reports the original and
preview dimensions. The original photo is never overwritten. CLI form:

```powershell
venv\Scripts\python.exe scripts/306_preview_face_mask.py --image "photo.jpg" --open
```

The recent nose/cheek holes disappear in the inspected25517 and77101 inputs.
The new masks follow the chin rather than the old detector rectangle, and
include forehead skin that a landmark oval alone omitted. Hair boundaries and
sunglasses are better excluded in the displayed cases. These are development
visual findings, not pixel-ground-truth accuracy or approval of all new masks.

## The implemented change

1. Retain the existing exactly-one-face detector and landmark provider. Landmarks
   are translated once from detector-crop to full-image coordinates.
2. Run the existing pinned19-class local BiSeNet model. Select predicted skin
   and nose only; predicted eyes, brows, lips, mouth, glasses, hair, ears, neck,
   clothes, hat and background remain excluded.
3. Associate predicted skin components with the selected landmark face. Retain
   matching forehead and lower-face components, even if glasses or exclusions
   separate them. Discard unassociated skin components elsewhere in the frame.
   Do not crop those retained components back to the tight detector rectangle
   or landmark oval.
4. Apply hard eye, brow and filled outer-mouth landmark exclusions. Optional
   explicit non-skin vetoes remain hard exclusions. Never fill across a
   forbidden predicted class to make a larger, cosmetically complete mask.
5. Save both a binary mask and a separate inward-feathered edge alpha. Alpha
   cannot bleed into excluded pixels and is not silently used as ITA support.

The geometric-only intermediate is retained separately in
`outputs/anatomical_face_coverage_v1/`. It filled holes but selected glasses and
facial hair. It is not the final preview mask. The semantic implementation is
`src/skin_masking/semantic_face_coverage.py`, using the geometry helper in
`src/skin_masking/anatomical_face_coverage.py`.

The parser asset is unchanged: existing local ResNet18 ONNX, SHA256
`0d9bd318e46987c3bdbfacae9e2c0f461cae1c6ac6ea6d43bbe541a91727e33f`.
No model download, new training dataset or dependency installation occurred.

## Remaining quality limits

Geometry alone was insufficient, which is why parser use was explicitly
discussed and authorized before semantic implementation. Parser predictions
are also imperfect. In61590, glasses are removed but beard/facial-hair pixels
can remain. In10567, sunglasses are excluded, but a small hat-area strip is
still predicted as skin. The parser has no distinct beard or paint class;
same-class touching occluders can remain. Features can also be imperfectly
localized in blurred/profile photos. Off-frame face regions cannot be recovered.
Thus this is a concrete improvement for the recent visible-skin examples, not
a guarantee that every photograph has complete, perfectly excluded facial skin.
Neck coverage remains a separate unfinished requirement.

All six contact sheets covering all24 cases were inspected. No new user mask
approval is invented from those observations or transferred from old decisions.
No additional large manual review batch is requested by this change.

## Calibration and deployment boundary

The original mask-dependent measurement contract remains exactly
`051dfb175e1356776ea59ebb5c3d63a7e1130de49d5787a7e75b7c0fa135db73`.
Its matching experimental MST lookup and the existing correction demo were
not changed. The new preview reports that it is incompatible with that old
lookup. No new mask is fed into it, no correction tree is refitted, and no
corrected image or completion claim is inferred from better coverage.

Using this new support for measurement requires a new bound measurement
contract, matching MST calibration/validation and consistently prepared
features/targets. Preserve old masks, model evidence and exact review decisions.
Existing generated inputs were made on the OLD generation masks; simply
replacing their application masks does not make a consistent new training set.
The pending broader-source comparison therefore must not be executed under
silently changed masks or features.

## Verification

Nineteen new tests cover full geometric support, boundary clipping, hard feature
and explicit veto exclusion, color independence, invalid geometry, disconnected
forehead/chin support, unrelated components, every forbidden parser class,
input immutability and explicit failures without fallback.

Full suite: **817 passed in11.65seconds**, using
`venv\Scripts\python.exe -m pytest tests/ -q -p no:cacheprovider`.
Script307 reconstructs all24 saved masks from saved categories and landmarks,
checks hard exclusions and inward alpha exactly, preserves source/baseline/model
hashes and verifies the original measurement contract. Its class-exclusion
counts are construction invariants against predicted classes, not semantic
ground truth. A separate CLI smoke run on25517dark matches its pack mask exactly.

- [New masks and class maps](../outputs/semantic_face_coverage_v1/records.json)
- [Independent saved-mask verification](../outputs/semantic_face_coverage_v1/verification.json)
- [Single-photo CLI smoke preview](../outputs/semantic_face_mask_cli_smoke_v1/review.html)
