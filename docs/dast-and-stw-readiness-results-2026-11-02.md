# DAST examples and STW metadata: concrete new data leads

2 November 2026. User authorised the recommended follow-up work. This is source
readiness inspection, not permission to send messages, train, replace models or
process an entire new cohort. Findings below improve on the earlier literature
shortlist: real DAST samples and STW annotation metadata were obtained.

## Practical result

**Continue investigating DAST for controlled correction/reference evidence and
STW for MST labels as separate roles.** Neither is admitted yet, but both offer
substantive new evidence; do not claim that no online route exists or that new
participant recruitment is the only option. No guarantee these sources will make
the retained ITA/calibrated-MST/tree method reliable.

| Source | Actually checked | Remaining issue |
|---|---|---|
| DAST | Entire official example archive: 36 JPEGs, three people, three instrument files/15 measurements; all images decoded and visually inspected | CST not MST; original files, linkage, viewing conditions and recipient terms need clarification |
| STW | Public annotation CSV: 42,312 unique paths, all ten label values, 3,587 provider identity keys, no conflicting label per key | Counts differ from paper; source licences, actual identity grouping, sample skin validity and existing allocations need reconciliation |
| PPR10K | New official Drive landing page accessible, older official folder returns404; repository's noncommercial dataset terms reviewed | Expert edits are appearance targets, not measured skin truth; usable data/sample access and operation compatibility not established |
| Rendered WB | Chart-referenced target documentation and public example link checked in preceding search | Portrait coverage and recipient terms unresolved; no full scene dataset acquired |

## DAST: all public samples retained

Pinned official repository revision 74f0aecc9ddd754d126114dedf06bef01c239a71.
Downloaded example-data.zip (8,043,401 bytes); its Git blob SHA-1 and byte size
match the pinned tree; archive CRC verified. Local files were extracted with
path-containment checks. No source archive scripts executed. Thumbs.db is an
unchanged inert archive artifact, not used as data.

All three people (001/002/036) have twelve publisher JPEG examples. All 36 are
796x1024, with no embedded ICC profile or EXIF. These are not the full TIFF
release described by the publisher. Acquisition sRGB documented by the authors
does not establish these examples as pixelwise colour truth. Gallery displays
the JPEGs as provided; no calibrated colour conversion is claimed.

24 exact CSV filename matches. All twelve subject002 filenames have an extra
`-0` suffix compared with the CSV. A unique possible suffix-removal linkage was
recorded but **not applied**. Four subject002 CSV entries also lack camera/exposure
values; no values guessed from image brightness or filenames.

Three CMF instrument files contain five measurements each. Header whitespace
differs; script389 strips field-name whitespace for parsing and preserves source
files. Initial inspection stopped at that header difference before report creation;
corrected parsing completed with all15 rows retained. Numeric Lab/XYZ records
are internally closer to a D65/10-degree interpretation (maximum Lab-component
residual 0.0351) than D65/2-degree (0.5888). This consistency check is not independent
certification of the instrument observer setting. Verify illuminant, observer,
normalisation and anatomical labels before comparing them with image Lab.

Assistant inspected every portrait on three contact sheets. All three subjects
have facial hair to consider for measurement. Apparent exposure differences are
visible, including very bright and very dark examples. Nominal views differ in
appearance between cameras; subjects are not perfectly motionless/aligned. Do not
use corresponding frames as pixelwise truth without justified registration and
photometric handling. No hair model, parser/FaceOcc inference, image skin means,
ITA, MST conversion, synthetic pair generation or parameter targets computed.

Earlier paper-versus-table count and exposure-label inconsistencies remain open.
Do not convert exposure settings directly into gamma targets. CST labels are not
MST labels, and three public examples do not establish coverage of the full release.

## STW: actual metadata is accessible, with important qualifications

Pinned repository revision 172e4906de9e91d7cee1090e63a34db95fe03f69.
Public official core Drive folder and splits subfolder reachable. Downloaded only
all_annotated_data.csv (metadata), not images.zip or underlying images. Read-only
audit found no duplicate paths and no conflicting class per `new_tokens` key.

| MST label | Image rows | Provider identity keys |
|---|---:|---:|
| 1 | 1357 | 107 |
| 2 | 6305 | 437 |
| 3 | 5525 | 634 |
| 4 | 2484 | 530 |
| 5 | 1281 | 435 |
| 6 | 2104 | 355 |
| 7 | 6863 | 358 |
| 8 | 8342 | 386 |
| 9 | 5627 | 241 |
| 10 | 2424 | 104 |

These are parsed metadata counts, not verified independent people or qualified
skin measurements. The paper reports42,313 images/3,564 people; downloaded CSV
has42,312 rows/3,587 provider keys. Treat as a release discrepancy, not resolved
by deleting/merging rows. Provider identity keys can fail to identify the same
person across datasets. Labels are human image/identity annotations, not physical
skin-colour measurements.

Sources include1,031 FairFace rows. No FairFace photos decoded, labels merged into
TrueHue or reserved roles changed. Exact overlap/exposure and cross-source person
checks are mandatory before any new pixel use or role freeze. Older TrueHue
estimated tones cannot be silently replaced by these annotations. Repository
states work in progress and source-specific licensing; a public CSV/Drive folder
does not establish permission for every component. No STW code executed or
SkinToneNet model acquired; retained ITA + calibrated MST + facial-statistics
decision tree unchanged.

## Next action made concrete

Unsent inquiry drafts: dataset-access-clarification-drafts-2026-11-02.md. Request
DAST full-resolution files, recipient terms and metadata/measurement clarification;
request STW release reconciliation and annotation/source rights details. Sending
requires explicit user instruction. The current generic research authorisation
does not authorise emailing authors, registering accounts or signing terms.

Do not start another user annotation batch or fit until those real source/role
questions are resolved and one bounded protocol is justified. Dataset-only
changes remain proposed investigations for panel tracking, not adopted methods.

## Evidence and verification

outputs/dast_sample_readiness_v1/ includes archive, pinned Git trees, original
examples/CMFs/CSV, sample_audit.json, all36-image gallery, contact sheets, STW
annotation CSV/metadata audit and public access-page snapshots. PPR10K revision
239490b8a8e917f2c29e3016ee2f6543c3c1bfba pinned for documentation. Script389 is
inspection only. Counts and input checksums verified. No pytest run for this
acquisition/audit; no pipeline module changed, new inference or fitting. Existing
reserved evaluation data untouched.

Primary sources: [DAST](https://github.com/dasec/DAST-SkinTone-database),
[STW](https://github.com/vitorpmh/STW),
[PPR10K](https://github.com/csjliang/PPR10K),
[Rendered WB](https://yorkucvil.github.io/projects/public_html/sRGB_WB_correction/dataset.html).
