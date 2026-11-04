# Retain the paper's MST method

28 October2026. User decision: **retain the paper's MST method**. This resolves
the earlier question in favor of the proposal; no approval to replace MST with
continuous ITA/Lab is assumed. Existing four-feature trees remain historical
development baselines. Android is on hold while Python is prioritized.

## Verified proposal requirements

Read the original `C:/Users/NYTHAN/Downloads/Thesis Proposal Document.pdf`
without editing it, using the PDF skill and an isolated reader installation.
Text extraction of PDF62–63 confirms:

- ITA maps to official MST categories1–10 using an MST-E-calibrated lookup.
- Computed ITA **and mapped MST** enter the correction model with facial-region
  color statistics.
- The decision-tree outputs remain gamma and red/blue multipliers.
- The paper also specifies MST-stratified splitting and category-dependent
  synthetic severity. Current fixed-severity/native224development data do not
  implement those requirements.

The original PDF hash is recorded in the audit. No table layout or figure
rendering claim is made from text extraction. PDF12–13calls MST-E evaluation-only,
while PDF62–63explicitly uses it for calibration. This is a real proposal
data-role ambiguity. It must be made explicit with calibration/evaluation
separation and historical exposure disclosure; this checkpoint assigns no new
subjects and sends no MST-E images into correction-tree fitting.

## Implemented interface

`src/ita_estimation/mst_lookup.py` defines a versioned lookup artifact and
`mst_model_features`. No real thresholds are supplied or exported.

The interface checks nine strictly ordered finite calibration thresholds,
explicit boundary semantics and MST ordering10→1as ITA increases. It binds the
lookup to the exact measurement-contract SHA256 and requires declared disjoint
calibration/validation subjects plus a passing validation-report declaration.
**Checking those declarations is not independent scientific validation**:
the referenced report, its protocol and actual metrics must be verified before
a real artifact is used. No real artifact currently satisfies the deployment
requirement. The current core runner remains honestly marked MST unavailable.

The new five-feature schema is input meanL*,a*,b*, inputITA and
`input_mst_index`. The index is the mapped official1–10label minus1, matching
configured0–9indices. MST is computed from the actual distorted-input ITA;
the builder rejects extra reference-label fields and missing lookup/mismatched
measurement contracts. Canonical JSON payload hashing identifies lookup
content; byte-level file hashes must also be recorded when an artifact is saved.
No original reference MST is silently inserted as an inference feature.

Twenty-one tests use explicitly synthetic thresholds/subjects and check order,
boundaries, mutation independence, invalid artifacts, missing validation,
subject overlap, input contract matching and no four-feature fallback. These
fixtures are not calibration data and establish no actual mapping accuracy.
**595Python tests pass in12.15s.** No runtime/default model was changed.

## Existing SCIN label support

Audited the companion label CSV as well as the cases CSV. Both contain5033unique
case IDs with no unmatched case. Separate India/US annotations and gradability
flags are preserved; Fitzpatrick/race is not converted to MST.

| Recorded annotation relation | All5033cases | Head/neck + at-distance368cases |
| --- | ---: | ---: |
| Both usable and agree | 2008 | 151 |
| Both usable and disagree | 2996 | 216 |
| Only one usable | 16 | 0 |
| Neither usable | 13 | 1 |

The151agreement cases in that metadata pool contain7MST1,89MST2,41MST3,
7MST4,2MST5,1MST6,3MST7and1MST8; no agreement cases atMST9or10. This is a
coverage observation, not a proposed agreement-only admission rule. Selecting
only agreement cases would introduce a new selection bias and cannot be used
to claim balanced ten-category coverage.

Only9of the368candidate image paths are locally available under the checked
download filename conventions. These are the previously inspected local cases,
not9newly accepted faces. Case-level body-part tags and at-distance shot type
do not establish a usable face, reference, mask or independent subject. No new
image was opened/downloaded, no annotation selected over another, no historical
India-based selection overwritten and no source admitted.

[Metadata audit](../outputs/mst_retention_checkpoint_v1/summary.json) ·
[Independent reconciliation](../outputs/mst_retention_checkpoint_v1/verification.json).
Script137checks input hashes and writes a new audit without changing labels.

## Next implementation gate

Lock one paper-consistent256measurement contract before calibrating a lookup;
do not transfer earlier224/larger-detector thresholds under a new name. Retain
the negative historical mapping findings and subject-support limitations.
Declare calibration/evaluation roles and validation procedure before another
mapping fit; all prior exposure remains disclosed. Define how conflicting SCIN
annotations will be handled before any data selection or model evaluation.
Then construct every correction training feature row through the MST interface
using input-derived measurements and the frozen lookup, with source groups and
original exclusions preserved. Resolve the paper's group boundaries and
brightness/contrast versus three-output operator details before final synthetic
generation. No guessed severity groups or final-performance claim follows here.

The decision now is fixed: complete and evaluate MST rather than quietly remove
it. Mapping quality, data eligibility, final evaluation, neck coverage and expert
MOS remain unfinished. CPM stays deferred and paint/makeup remains a limitation.
