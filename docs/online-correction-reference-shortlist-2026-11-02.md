# Online correction-reference search

2 November 2026. User authorised investigating existing online datasets instead
of new recruitment. Public documentation screening only: no participant images
downloaded, agreements signed, authors contacted, processing or training run.
No dataset or thesis-method change is adopted. Existing training admission remains
unchanged. Counts below describe publishers' datasets, not usable TrueHue rows.

## Decision

No immediately verified, permission-cleared full-face true-colour reference set
was established. The strongest measured-face lead is CHROMA-FIT; the closest
edited-photograph alternative is MIT-Adobe FiveK. They answer different questions.
Keep both as research leads, not approved training sources. Hyper-Skin is a
secondary scientific reference with a more specialised data format/access burden.

| Candidate | Verified documentation | Access and fit | Decision |
|---|---|---|---|
| CHROMA-FIT | About 2,300 face photographs / 209 people; indoor and outdoor captures; forehead/forearm instrument measurements | Official lab/paper verified; functioning image download, recipient licence, exact participant links and rendering/profile information not established. Instrument readings do not certify each photo's pixels | First measured-face lead, not admitted |
| Hyper-Skin | Paired facial spectral data and synthetic camera-response RGB; 51 subjects | Official repository requires digitally signed EULA and affiliation. Publication examples limited to specified subjects. Synthetic RGB is not a smartphone reference capture; spectral-to-colour assumptions need assessment | Secondary lead; no access request submitted |
| MIT-Adobe FiveK | 5,000 RAW photographs, five edited renditions each; people and other scenes; output TIFFs in ProPhoto RGB | Publisher offers individual files and research use under two file-specific licences. Exact terms and portrait/identity/tone coverage still need screening. Do not treat ProPhoto values as sRGB | Practical photographic-restoration lead, not measured true-colour truth |
| MSKCC Skin Tone Labeling | 64 patients, 4,879 dermoscopic images; MST/Pantone and colorimeter information; publisher states image CC-BY | Actual face/neck portraits needed by TrueHue are not established in this released image set. Non-lesional sites do not imply portrait images | Do not acquire 5.5 GB bundle for facial-correction targets |
| Leeds skin colour characterisation | Spreadsheet of measured XYZ and corresponding RAW/JPEG RGB values | Published downloadable artifact is an XLSX, not an established released portrait collection; permissions need inspection | Useful colour-characterisation background, not a correction-image cohort |
| Beyond-RGB | Scene colour reference and illuminant spectrum documented in official repository | General scene dataset; sufficient suitable portraits, skin labels and data licence not established | Lower priority; do not assume chart presence supplies facial skin truth |

The Hyper-Skin abstract reports 330 cubes whereas the repository introduction
reports 306. Preserve the discrepancy; do not resolve by guessing or infer an
available usable count before inspecting an authorised release.

## What the evidence can and cannot establish

A measured forehead colour is a local measurement under an instrument's conditions,
not a replacement RGB colour for every facial pixel. Facial shading, highlights,
camera response, illuminant, white point and colour profile must be accounted for.
Neither standard office lighting nor professional editing establishes neutral
colour in a released portrait. Do not recolour all skin to one measurement.

FiveK's editing objective is pleasing photographic appearance. It could support
restoration toward a declared photographic target, not proof of intrinsic colour
recovery. Its complete editing operations also exceed TrueHue's three-parameter
operator; do not assume every before/after pair is representable by gamma/red/blue.
One source target plus predeclared synthetic distortions is a different experiment
from learning its original edit; neither is activated here.

None of these findings supplies matching calibrated MST automatically. No
conversion of measured ITA/Lab into invented MST labels, compatible-old-lookup
assumption, runtime method replacement or claim of ten-tone coverage follows.

## Concrete next investigation

1. For CHROMA-FIT, establish an actual official release/access route and recipient
   use/publication terms; inspect whether metadata ties measurements to exact
   portraits, documented capture/rendering and participant IDs. If no route can
   be verified, mark access unresolved rather than calling it freely downloadable.
2. For FiveK, inspect both actual licence texts and publisher metadata before a
   small, fixed portrait feasibility sample. Freeze selection independently of
   TrueHue outcomes and editor preference; establish duplicates, identity grouping,
   profile conversion, skin-tone evidence and restricted photographic claim first.
   Do not download the entire approximately 50 GB archive for screening.
3. Stop acquisition if neither route supports the intended reference claim. Do
   not substitute aesthetically attractive web portraits, a small favourable
   source fit, or an unsupported claim that measured labels validate all pixels.

Any proposed expansion beyond FairFace/SCIN correction data must be entered as a
proposed dataset/scope change in the panel register before activation, with exact
original-paper wording verified later. This shortlist has not selected or activated
such an expansion; no frozen delivery-package source documents were changed.

## Primary sources checked

- [CHROMA-FIT official lab publication](https://research.fit.edu/idl/publications/)
- [CHROMA-FIT paper](https://openaccess.thecvf.com/content/WACV2024W/DVPBA/papers/Pangelinan_The_CHROMA-FIT_Dataset_Characterizing_Human_Ranges_of_Melanin_for_Increased_WACVW_2024_paper.pdf)
- [Hyper-Skin official repository, access and publication restrictions](https://github.com/hyperspectral-skin/Hyper-Skin-2023)
- [Hyper-Skin author abstract](https://arxiv.org/abs/2310.17911)
- [MIT-Adobe FiveK publisher, research licence links and colour format](https://data.csail.mit.edu/graphics/fivek/)
- [MSKCC publisher and release description](https://api.isic-archive.com/doi/mskcc-skin-tone-labeling-dataset/)
- [Leeds deposited characterisation data](https://zenodo.org/records/5532176)
- [Beyond-RGB official repository](https://github.com/shirawerman/Beyond-RGB)

CVF direct opens returned HTTP 403; indexed publisher paper text and official lab
record supplied CHROMA-FIT documentation. No successful full PDF fetch or binary
verification is claimed. No tests run: documentation search only.
