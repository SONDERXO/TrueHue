# Received Stellenbosch dataset: local integrity and metadata check

5November2026. User reports an author reply granting access, requiring citation,
research-only/noncommercial use and no sharing with other groups or individuals
without consent. User downloaded/extracted the release in Downloads. The reply
was supplied in chat, not independently read from an inbox. No follow-up needed
or sent; the author says further information may not be available.

Initial discovery found285subject folders,21,375JPEGs and285label JSON files.
A sampled JPEG header is224x224RGB. Labels include fractional scores and numeric
strings. These are preliminary metadata observations, not pixel screening or
calibration admission. This protocol precedes the full integrity/header census.

Leave the archive and extraction in Downloads, read-only. No moving, copying,
deleting, normalising or executing dataset contents. No dataset upload, public
gallery, per-subject labels or manifests in Git. Local metadata/author-terms
evidence goes under ignored `outputs/stellenbosch_received_data_v1/`; only generic
reader code/tests, this protocol and aggregate results may be tracked.

Check archive membership, extracted file sizes/CRCs, SHA256 identities, subject/
pose/lighting filename structure, per-subject label schema/type/range and JPEG
headers (dimensions/mode/profile flags), without decoding image pixels or running
detection/segmentation/FaceOcc/calibration/trees. Archive matching is local
consistency, not a publisher-supplied checksum or authentication guarantee.

Preserve each label's raw JSON bytes/hash and value/type; parse numerical strings
only into a separate exact decimal representation for analysis. No rounding,
binning, integer-only subset or fake ten-category assignment. The retained
threshold calibrator currently requires official integer labels1–10; fractional
source scores require an explicit compatible target/evaluation policy before
fitting. Do not silently change that calibrator or the retained MST feature.

Use publisher folder IDs only as source-local subject keys. Keep all75images of
each subject together, no train/evaluation allocation or cross-dataset person
independence claim. Header verification does not establish actual facial detail,
full-face/neck availability, current mask eligibility or colour calibration.

Retain every discrepancy rather than silently fixing/removing it. Record author
conditions locally and make the no-redistribution rule clear for the public repo
and any proposed partner transfer. No new calibration/sample-processing batch
is activated by this integrity check. Next bounded visual/measurement preparation
must predeclare selection and the decimal-MST policy; preserve all earlier evidence.
