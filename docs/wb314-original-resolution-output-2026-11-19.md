# Original-size output implemented

The user requests corrected files at the original dimensions and aspect ratio, without resizing or stretching the output photograph. The research runner now renders the existing predicted controls on the original decoded RGB pixels. It does not enlarge the 256-pixel corrected preview to create the output.

## Processing and geometry

The model and mask service still analyze the same internal whole-frame 256x256 image. That preserves the frozen predictor's existing input contract, feature ordering and decisions. The internal analysis can have square geometry; it is not the saved main photograph.

`src/correction/original_resolution.py` maps only application alpha and protection back to the original frame. Alpha uses bilinear interpolation restricted to nearest-neighbour positive-support membership, with nearest-neighbour protection overriding it. Pixels outside that mapped membership or inside retained protection have zero alpha. This limits interpolation spill but does not make coarse masks into verified native-resolution masks.

The existing pointwise luminance/chroma renderer then processes original pixels in strips of 128 rows, bounding temporary memory. Identity controls return an independent exact copy after validating the masks. Neither original pixels nor the rendered output are resized, cropped, padded or geometrically warped. Output uses lossless RGB8 PNG, preserving the decoded pixel geometry; this is not a promise to preserve JPEG encoding bytes or all source metadata.

`scripts/run_wb314_photo.py` now saves:

- `primary_correction.png`: original-size primary output.
- `separate_headroom_candidate.png`: original-size separate alternative when available, never substituted into the primary.
- `analysis_correction_256.png` and its separately labelled analysis alternative: the actual low-resolution model results for diagnosis.
- Original-resolution application alpha and protection alongside the existing analysis masks, report and manifest.

The existing headroom controls are calculated on the 256-pixel analysis. Their use on original pixels is an illustrative separate alternative, not a guarantee of original-resolution highlight protection. The two earlier cap screens remain failed. The frozen tree, features, model weights, masking rules, manual-ear support and original trained predictor are unchanged. Desktop/Android app defaults and expert-review materials are unchanged.

## Completed checks and delivery

**24 focused generated tests passed in 16.09s**, with one pre-existing NumPy import deprecation warning. They include portrait, landscape and square geometry, exact agreement between striped rendering and the existing full-array pointwise renderer under nonidentity controls, original pixel preservation outside application/protected areas, identity detail preservation, input immutability and failure before correction on invalid masks. The generated runner integration exercises original-size primary and separate-alternative exports. No new model/photo study was used for these tests.

For the two already selected user photos, the prior native run's artifact hashes, source hashes, controls, alpha and protection were reused. Two original-size PNGs were exported without another trained-model call, mask inference or fit. Both cached decisions were identity, so both PNG round trips exactly equal the decoded originals at their original dimensions. Both source files remain unchanged. These are original-resolution exports, not new model predictions or evidence of correction benefit. The earlier square previews remain preserved as historical artifacts.

Local delivery: `output/wb314-original-size-2026-11-19/START_HERE.html`. It links the full-size files and displays proportional previews with automatic height. Browser display scaling does not change saved image dimensions. Local detailed receipts and bindings: `outputs/wb314_original_resolution_v1/`. Photos, original paths, per-photo records and masks remain local; only source and aggregate checks are published.

## Remaining limits

Original dimensions and aspect ratio are now preserved by the research output path. This supersedes older statements that no original-resolution render adapter exists. Automatic mask boundaries still originate at 256 pixels, and no real nonidentity original-size result has yet been qualified for appearance. The two real exports are identity results; generated nonidentity tests establish software consistency only. No HD detail is invented, and native mask accuracy, normal-photo correction necessity/benefit, independent MST appraisal and device qualification remain incomplete. No additional experiment, inference queue, retuning or repeated appearance review is selected here.
