# Online reference access and portrait metadata check

2 November 2026. User authorised checking CHROMA-FIT availability and FiveK
licences/portrait coverage. Public documents and metadata downloaded only; no
participant image, RAW, TIFF or thumbnail downloaded, no model processing/fitting,
no contact or agreement submission. No dataset adopted.

## Results

**FiveK can support a small photographic-reference feasibility investigation.**
It is not a verified true-skin-colour dataset and does not resolve calibrated MST.
Parsed the publisher's 5,000-row HTML table: 1,341 entries tagged person(s), 1,089
nature, 1,869 man-made object, 300 animals, 366 unknown and 35 abstract. Person tags
are not verified portraits, distinct people, eligible masks or tone coverage.
No claim that the other tags cannot contain people. Lighting/location/time tags
are descriptions, not independent colour calibration.

Read both publisher research licences and downloaded their file membership lists:
2,690 Adobe entries and 2,310 Adobe/MIT entries. Exact source identifiers of all
1,341 person-tagged entries map to one list: 695 Adobe and 646 Adobe/MIT, with no
overlap or unmapped person entries. The licences limit granted rights to the
recipient's own research without commercial benefit; copies/substantial portions
must retain applicable copyright and licence notices; contributor names cannot
be used for endorsement. Preserve both attribution and the publisher citation.
This is a recorded reading of the source terms, not an independent legal opinion
or permission for commercial app distribution of dataset photos.

The publisher provides individual DNG inputs and five output TIFF links per
source; full archive download is unnecessary. Outputs are 16-bit ProPhoto RGB.
Future sample work must retain original files/profiles and use an explicitly
documented colour-managed conversion. Do not interpret their numeric values as
sRGB or choose whichever editor produces the best TrueHue score.

**CHROMA-FIT remains an access lead, not an available training source.**
The official Identity Lab publication page describes the dataset; the lab site
and publication page checked did not expose a dataset download or recipient
licence link. The official contact page provides a lab contact. This limited
search does not prove the dataset is unavailable everywhere. Obtaining data or
terms may require an inquiry; no inquiry was sent. Author contact would require
the user's explicit instruction. Measured participant colour does not make each
published photograph a calibrated image target.

## Recommended next bounded step

Use FiveK only for a **small source-feasibility sample**, not training. Before
images are acquired, freeze exact sample membership from the saved person-tagged
inventory independently of TrueHue outputs, retain failed/unsuitable cases, and
state a photographic-restoration claim. Define a fixed editor/rendition rule,
colour-management procedure, grouping/duplicate assessment and eligibility checks
for actual face size, blur, clipping, lighting, coverings and measurement skin.
No source becomes eligible because it looks attractive or carries a person tag.

No sample count or selection is activated by this metadata check. Do not quietly
replace FairFace/SCIN, generate targets, fit on five old anchors, or reuse old MST.
If a sample is activated, record the proposed extra-dataset role in the panel
change register before processing. The retained ITA + calibrated MST + facial
statistics to gamma/red/blue decision tree stays unchanged; reliable matching MST
remains separately unresolved. Access and artistic edits alone are not sufficient
to claim that this plan will produce a reliable automatic correction model.

## Saved evidence and verification

outputs/online_reference_access_20261102_v1/ contains publisher HTML, both exact
licences and membership lists, fivek_metadata.json (all person-tagged source IDs,
input URLs and publisher tags), licence_coverage.json and sha256.json. These are
documentation/metadata, not photos. An initial console summary encountered a
Windows default-decoding error; rerunning reads as UTF-8 completed the link and
licence mapping. No image operation was involved in that error.

Verification: 5,000 parsed rows; category counts sum to 5,000; all 1,341 person
source IDs mapped to one published licence list. File hashes saved. No tests run
for documentation/metadata work; runtime and frozen delivery-package inputs unchanged.

Primary sources:

- [FiveK publisher and metadata](https://data.csail.mit.edu/graphics/fivek/)
- [Adobe research licence](https://data.csail.mit.edu/graphics/fivek/legal/LicenseAdobe.txt)
- [Adobe/MIT research licence](https://data.csail.mit.edu/graphics/fivek/legal/LicenseAdobeMIT.txt)
- [Adobe membership](https://data.csail.mit.edu/graphics/fivek/legal/filesAdobe.txt)
- [Adobe/MIT membership](https://data.csail.mit.edu/graphics/fivek/legal/filesAdobeMIT.txt)
- [Identity Lab publications](https://research.fit.edu/idl/publications/)
- [Identity Lab contact page](https://research.fit.edu/idl/contact-us/)
