# PPR10K fixed sample: useful appearance examples, not training-ready

2 November 2026. The user explicitly authorised the proposed bounded inspection.
All six fixed source/editor-A pairs were acquired, decoded and visually inspected
by the assistant. No user review task, replacement batch, model inference,
calibration, operator fitting or correction-tree training was performed.

## Result in simple terms

**PPR10K is a promising photographic-reference source.** The selected expert
edits show useful brightness and colour improvements. They do not prove true
skin colour, provide MST labels, or establish that TrueHue can reproduce them.
There are zero training admissions. This inspection ends here without an
automatic larger sample or fit.

Local gallery: `outputs/ppr10k_inspection_v1/review.html`.
Machine-readable findings: `inspection_results.json` in the same directory.

## Fixed selection and access

Publisher documentation/tree pinned to
`239490b8a8e917f2c29e3016ee2f6543c3c1bfba`.
Current official Drive folder:
<https://drive.google.com/drive/folders/1kB2OSAGy8uc0xUXaMKoPB0HMSc-rkrLW>.
Its `train_val_images_tif_360p` folder exposes `source.zip` and three editor ZIPs.
Used unaugmented source and editor A only, without switching editors by outcome.

Script391 inventories the source/editor-A ZIP central directories using HTTP
byte ranges. Each has 11,161 unique TIFF stems, with exact stem-set agreement.
Before downloading or decoding any image, `frozen_sample.json` fixes two groups:
rank common group IDs by SHA256 of `TrueHue-PPR10K-v1:` plus the group ID;
take the first two groups and first three numeric frame IDs within each.
Selection did not use face visibility, successful processing or attractiveness.

- Group1398: `1398_0`, `1398_1`, `1398_2`.
- Group1487: `1487_0`, `1487_1`, `1487_2`.
- All six pairs retained; no acquisition/decoding failures or replacements.

Byte-range reads avoided full downloads of the 12,079,675,100-byte source and
4,639,852,620-byte editor-A archives. Image extraction/verification stages read
7,019,722 and 3,084,725 bytes respectively, in addition to directory/access reads.
`zipfile` verifies each selected member's CRC; local SHA256 hashes are recorded.
Publisher scripts were saved/read, not executed. No account, agreement form,
author message or dataset upload was involved.

## Terms, grouping and evaluation exposure

The [official README](https://github.com/csjliang/PPR10K) specifies noncommercial
research use for the dataset; repository Apache code licensing is separate.
Keep acquired photos and derivatives local/ignored. This is a research inspection,
not blanket reproduction clearance for a public thesis/gallery or commercial app.

The publisher groups related photographs by filename prefix. These are not
verified globally unique person identities. Two groups do not establish two
different people, independent subjects or skin-tone coverage.

The pinned publisher `utils/split_train_val.py` assigns group IDs below1356 to
training; others to validation. Inventory matches8,875/2,286 files. Both chosen
groups are publisher-validation groups. They remain in this fixed inspection,
but these exact six photos are now development-exposed and must not later be
called unseen final evaluation. This does not alter any existing TrueHue
FairFace/MST/SCIN allocation. Broader identity/duplicate relationships are unknown.

## Colour and pair checks

All six sources are RGB16 TIFFs; all six editor-A targets are RGB8 TIFFs.
Matched dimensions are540x360 or360x540. Every actual TIFF has an embedded
`sRGB IEC61966-2.1` profile, checked with Pillow/LittleCMS, agreeing with the
[publisher export instructions](https://github.com/csjliang/PPR10K/blob/239490b8a8e917f2c29e3016ee2f6543c3c1bfba/docs/dataset_usage.md).

Original TIFFs remain byte-preserved. Viewing copies round source values divided
by257 to RGB8; targets retain their RGB8 samples. No gamut conversion is needed
for these verified sRGB profiles. Gallery boards are viewing artifacts, not
numeric targets. No calibrated monitor or instrument-truth claim is made.
Scene layout appears corresponding, but no pixelwise registration was measured.
Human-region masks were not acquired or treated as skin masks.

## All six visual findings

| Pair | Source conditions and expert edit | Qualification |
|---|---|---|
|1398_0|Two seated faces, glasses on one face, apparent makeup on the other; dark studio scene. Editor brightens faces, white clothing and scene details.|Visible faces; multiple-person selection, glasses and makeup remain measurement concerns.|
|1398_1|Same two-person scene with tilted faces and glasses. Editor lifts facial brightness and white clothing.|Useful appearance comparison; not a clean independent person/reference.|
|1398_2|Both faces more frontal; glasses absent in this view. Editor brightens faces and clothing.|Stronger facial visibility in this fixed sample, but makeup/styling and unknown true colour remain. No admission.|
|1487_0|Wider seated indoor portrait under a strong yellow cast. Editor reduces yellow and changes overall brightness/contrast.|Face small at360p; fringe/headwear and makeup. An appearance example, not a measured reference.|
|1487_1|Same indoor scene, changed pose, small face and hair near eyes. Editor reduces the yellow cast.|Limited facial detail; related photo, not new independent evidence.|
|1487_2|Downward smiling face with hair/hat; foreground haze/reflection. Editor reduces warmth and changes scene colour.|Detail/occlusion/haze concerns retained; not selected as a clean reference.|

These are assistant observations, not user approvals, dense annotations or
objective preference/colour-accuracy measurements. Apparent people within a
group recur; no demographic or MST labels inferred from appearance.

## Can gamma/red/blue represent these edits?

The broad directions—brightness and red/blue balance—match the operator's purpose.
**How closely it can reproduce the facial edits remains unverified.** The
existing operator applies one gamma to all channels, then red/blue gains; green
gain stays one (`src/distortion_generation/generate_distortions.py`). It cannot
express arbitrary saturation, highlight/contrast curves, local adjustments or
full-scene edits. PPR10K's documented Lightroom augmentation/export workflow
includes controls beyond those three parameters.

Expert targets also change clothing/background, while TrueHue corrects the
selected face and neck. Full-image disagreement would therefore not by itself
prove failure of TrueHue's intended operator. A future justified comparison
would need trustworthy selected-face correspondence and scoring support, colour
handling and a declared approximation criterion. None is silently supplied by
human-region masks or these six visual judgments. No inverse parameters,
synthetic targets, face measurements or target-fit quality were computed.

## Verification and retained method

All12 TIFF SHA256 values, embedded sRGB profiles, expected16/8-bit types and
six exact pair dimensions checked. File times confirm the frozen selection
predates all selected TIFF downloads; all six paired boards visually inspected.
`sha256.json` preserves artifact hashes. These are acquisition/artifact checks,
not new model validation. No pytest run was needed for an isolated inspection;
the previously recorded broader test results remain historical.

Retain ITA + calibrated MST + facial statistics -> decision-tree gamma/red/blue
correction. Reliable MST and automatic correction remain unfinished. PPR10K is
an additional investigated source, not an adopted thesis dataset or pipeline
change. Existing demos, protected/reserved roles and frozen delivery snapshots
remain unchanged. Both DAST/STW inquiries remain user-reported sent, awaiting
replies; no duplicate messages or inbox monitoring.
