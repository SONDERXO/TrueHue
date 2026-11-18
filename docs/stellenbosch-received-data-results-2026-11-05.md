# Stellenbosch release received: access resolved, metadata verified

5November2026. The user supplied Rensu Theart's reply stating the dataset was
shared, and reported downloading/extracting it. The terms supplied are:

- Cite the source paper when using the dataset.
- Research purposes only, not commercial purposes.
- Do not share the dataset with other groups or individuals without consent.

This records the author reply provided by the user, not an independently verified
inbox receipt or a broader legal clearance. No follow-up was sent; the author's
statement that more information may not be available is retained. Do not transfer
the release to a public repository, public gallery, partner or other individual
without the necessary author consent. No new account, agreement or payment.

Citation: Success K. Mbatha, Marthinus J. Booysen and Rensu P. Theart,
[Skin Tone Estimation under Diverse Lighting Conditions](https://doi.org/10.3390/jimaging10050109),
Journal of Imaging10(5),109(2024). The previous access-request and source-search
records remain historical snapshots; their waiting/unsent wording is superseded
by the user's sent report and this receipt record, not silently rewritten.

## Delivered files, checked in place

Located `Skin-Tone Estimation Data` and its archive in the user's Downloads.
The nested data root ends in `raw data (published)/1-285`. The archive and all
extracted files remain at their original locations; nothing was moved or copied
into the repository. Script429 followed the
[recorded protocol](stellenbosch-received-data-protocol-2026-11-05.md).

| Check | Observed result |
|---|---:|
| Publisher subject folders | 285, numbered1–285 |
| JPEG images | 21,375 |
| Images per subject | 75 |
| Pose folders per subject | 5, each with15images |
| Subject label JSON files | 285 |
| Extracted files matching archive membership/size/CRC | 21,660/21,660 |
| Archive size | 215,717,506bytes |
| JPEG header dimensions and mode | All224×224RGB |
| Embedded ICC / EXIF found | 0 / 0 |
| Integrity/schema discrepancies observed | 0 |

These counts match the paper's reported release size. File/CRC checks establish
consistency with this locally received archive, not a publisher-supplied checksum
or a claim of author authentication. SHA256 records bind the archive/files for
future use. JPEG headers were inspected; pixels were not decoded or visually
screened. Header readability does not certify full JPEG decoding or usable faces.

Despite the folder name, the delivered224px files must not be assumed to be
camera-original full-resolution images. Crop/pose/detail and compatibility with
the existing256px measurement path need bounded image-level examination before
admission. Lack of an ICC profile does not establish calibrated sRGB or skin truth.
Filename condition codes are preserved without inventing physical interpretations.

## Label compatibility: preserve scores before fitting

The label schema is `monk_scale_value.json` with a `value` field. Stored types:
53integers,214floats and18numeric strings. All285parse as finite scores within
1–10; observed range1–9.7.168subjects have fractional scores and117integral scores.
This is a scalar distribution, **not ten integer-category counts**.

The generic reader preserves each raw value/type, exact decimal representation
and JSON-byte hash. Numeric strings are parsed into a separate analysis field;
the files themselves are unchanged. No rounding/binning, fabricated labels,
integer-only subset or category assignment was performed. A score below10 does
not justify claiming an empty rounded category10; no rounding policy exists yet.

The retained `threshold_calibration.py` currently requires official integer
labels1–10. This delivery cannot be silently passed through that interface.
Before calibration, predeclare a decimal-compatible target/evaluation policy
consistent with the source and the retained MST design, and record any change.
This is an integration question, not a reason to discard the fractional cases
or reuse the failed old calibration. No calibrator or final feature schema was
changed in this check.

Subject keys come from publisher folders. All75photos of a subject must remain
together in any eventual allocation. No split, recognition, cross-dataset person
verification or unseen-final status was inferred. A new release and permission
solve access; they do not automatically establish actual-skin measurement or
calibration eligibility on every image.

## Private evidence and next step

Ignored local evidence: `outputs/stellenbosch_received_data_v1/`. It contains
private per-subject raw score records, file identities, header/CRC results and
the terms/protocol record. These manifests and the dataset must not be staged
for the public repository. Only generic code/tests and aggregate documentation
were added to the source tree. The private summary's publication/redistribution
flag refers to dataset material, not permission to publish cited research results.

14focused metadata-reader tests passed in0.15seconds, including preservation of
fractional/string scores and rejection of invalid/nonfinite/boolean labels.
285CSV/JSON subject records agree; the source inventory and archive hash remain
unchanged. This was not a full-suite run. No image inference, target fitting,
MST calibration, correction-tree training or admissions occurred.

The next concrete step is one predeclared bounded visual/current-measurement
preparation sample with the decimal-score policy made explicit. Keep its failures
and respect subject grouping; do not process all21,375photos or fit immediately.
The old nineteen-subject review stays complete and unchanged. The new source
can now supply substantive evidence rather than another review of old records.
Thesis drafts, runtime models and frozen prior experiments remain unchanged.
