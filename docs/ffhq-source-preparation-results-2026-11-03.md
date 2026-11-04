# FFHQ photographic sources: bounded preparation complete

3 November 2026. User explicitly authorised progressing with FFHQ photographic
sources and deferring ITA-to-MST work. This supersedes the earlier planning-only
restriction for this bounded source acquisition/screen. It does not remove MST
from the retained method or authorise full-model training with invented labels.
DAST is removed from the active acquisition route at the user's request; no
payment, waiver request or further contact was made.

## What was done

The official FFHQ repository was pinned at revision
`4826aa6ea77aa7f1a7802b938ed7c40afb985cda`. Its downloader specification was
parsed as literal data, not executed. The script's Git blob matches the saved
official tree. The official metadata file downloaded successfully:267,793,842
bytes; publisher MD5 `425ae20f06a4da1d4dc0f46d40ba5fd6`; SHA256
`1be5c2d1a78196d45a9600558c04b46dffefa217b7c664d5be38ed28a4d9a0ee`.
Its70,000 records were read to select sources. This is new source acquisition,
not a repeated audit of the older MST cohort.

Before any image download, fixed12 publisher-training IDs by sorting
SHA256(`TrueHue-FFHQ-source-v1:`+ID) and taking the first12 with different original
photo URLs. No selection by apparent tone, lighting, attractiveness, segmentation
success or target error. IDs:54632,39568,29617,29863,16061,52445,32685,53146,
48879,49131,59807,46795. This small source-feasibility sample is not an adequate
training/evaluation cohort, representative tone sample or participant count.

All12 aligned1024×1024 RGB PNGs downloaded, total15,856,019 image bytes. Publisher
file MD5/byte counts, decoded pixel MD5 and dimensions were verified. No photos
failed and none were replaced. The original Drive metadata endpoint returned
HTML; the alternate public Drive download endpoint returned the byte/checksum-
verified file. No accounts, agreements, credentials, unverified mirrors or
dataset code execution were used. No full image archive was downloaded.

## Source gallery and actual visual evidence

- Gallery: `outputs/ffhq_source_visual_assessment_v1/review.html`.
- All12 contact sheet: `outputs/ffhq_source_preparation_v1/source_contact_sheet.jpg`.
- Attribution/role ledger and assistant observations are in the visual-assessment
  folder; exact raw files and metadata are under
  `data/raw/ffhq_source_preparation_v1/` (ignored by Git).

The assistant inspected all12 on the saved contact sheet. This is an initial
source screen, not full-resolution reference approval, skin annotation, mask
admission or calibrated lighting assessment. Each remains a candidate with its
concerns retained. No user annotation/review task was activated.

| Source | Retained observation |
|---|---|
| 54632 | Cap/head covering, beard, tight lower crop |
| 39568 | Hair at face edge and directional shadows |
| 29617 | Sunglasses and hand covering cheek/jaw |
| 29863 | Dim/uneven appearance, beard, head covering |
| 16061 | Glasses/reflections, lower neck partly clothing/crop |
| 52445 | Tight face crop, clothing near lower edge |
| 32685 | Downward pose/fringe, neck partly collar |
| 53146 | Strong directional light/shadow, head covering, tight crop |
| 48879 | Profile/oblique pose and hair near face |
| 49131 | Relatively frontal/unobstructed, support still unverified |
| 59807 | Glasses and microphone near lower face |
| 46795 | Strong outdoor light/bright background, pose/crop concerns |

No concern was silently removed and no favourable-only cohort was fitted.
No photo was assigned an MST category or declared correctly lit/true colour.
Apparent quality on a thumbnail is not enough to settle fine detail, clipping,
padding or suitability of an original as a photographic target.

## Attribution, grouping and colour limitations

The selected images have seven Attribution and five Attribution-NonCommercial
licence records. Each exact author/photo/licence URL is preserved in
`attribution_and_source_ledger.csv` and the gallery. FFHQ metadata/docs use
CC BY-NC-SA4.0; individual photo conditions remain separate. This is local
noncommercial research preparation, not clearance for every possible release.
Publisher alignment/cropping and scaled display are identified; TrueHue has
not changed the source bytes/colours. No raw files were published.

All12 have different original photo URLs and different original pixel hashes.
That does **not** prove12 different people or cross-dataset independence.
Person grouping remains unset; publisher train/validation is not adopted as
TrueHue's final person-disjoint split. Acquisition/inspection makes these images
development-exposed, never unseen final appraisal. Existing reserved allocations
and older exposures remain unchanged. No recognition or re-identification model
was used; FFHQ disallows facial-recognition development.

No embedded ICC profile was reported by Pillow for these12 PNGs. Exact RGB
decoding was checked against publisher pixel hashes, but that does not certify
colour calibration. Alignment/crop and possible padding need examination before
face/neck support admission. A cropped-out neck cannot be manufactured by mask
dilation or generated pixels. This source check did not perform such a repair.

## Current decision and next step

**Source preparation succeeded; training admission is still false.** Use the
same fixed12 sources for a separately recorded mask/support feasibility check
before choosing references or generating distorted pairs. That check can proceed
without a calibrated MST lookup: save exact masks, selected-face/neck association
and alpha, keep failures/occluder concerns, and make no category or automatic-
correction claim. Do not infer current mask approval from FFHQ's resolution.
Do not launch another photo batch or replace difficult photos automatically.

ITA-to-MST calibration is explicitly deferred at the user's instruction. No fake
category, reference label substituted as a model feature, direct-classifier
replacement or lookup reuse is introduced. The full retained method still needs
compatible MST before its eventual training/evaluation. Source feasibility and
mask work are distinct progress that does not depend on solving MST first.

FFHQ supplements the proposal's stated FairFace/SCIN source approach; record
this dataset-role change in the panel register rather than silently changing the
paper. User-authorised development acquisition is not panel approval or final
training-dataset adoption. Submitted proposal/dated working thesis drafts remain
unchanged in this task.

## Verification

Scripts408–410 preserve the protocol, selection-before-pixels, attempts, raw
checksums, gallery, assistant observations, attribution CSV and verification.
Five isolated downloader tests passed in2.19seconds with fake network responses:
exact bytes/checksum, truncated/oversized data, wrong checksum and HTML rejection.
No broad/full-suite run is claimed. Attribution/source JSON/CSV membership and
all12 file hashes were checked. The integrated plan's23 sources and seven parent
manifest hashes remain unchanged. Zero segmentation/landmark/FaceOcc inference,
target fits, MST calibration, tree fits, synthetic variants, model predictions,
manual annotation requests, runtime changes or contacts.

Official sources:
[FFHQ documentation and individual licences](https://github.com/NVlabs/ffhq-dataset),
[pinned acquisition specification](https://github.com/NVlabs/ffhq-dataset/blob/4826aa6ea77aa7f1a7802b938ed7c40afb985cda/download_ffhq.py).
