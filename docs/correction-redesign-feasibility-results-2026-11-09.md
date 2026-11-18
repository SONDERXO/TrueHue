# Substantive correction redesign feasibility — 9 November 2026

## Result

The saved evidence does not yet justify selecting a substantive second
correction comparison. Do not train another tree or parser as an automatic next
step. This is a completed feasibility review with a negative readiness finding,
not a claim that automatic single-photo correction is impossible.

The reviewed alternatives are not unexplored fixes:

| Route | Existing evidence | Consequence |
| --- | --- | --- |
| Brightness spread and spatial asymmetry | 24 October fixed brightness comparison included quantiles/IQR, left-right and top-bottom brightness; all eight unchanged inputs still changed | Do not repackage coarse spatial brightness as a new illumination cue |
| Chromatic distribution | 30 October median/IQR extension added a held clean failure; 6 November covariance/IQR extension left all clean/core outputs identical | Another chroma summary has no established rationale here |
| Per-channel endpoints | 30 October improved recovery but retained a clean failure and visible boundaries | Endpoint fractions are already investigated and may depend on synthetic encoding |
| Face-local context | 8 November removed outside-crop sensitivity but worsened recovery and clean behavior | Cropping alone does not establish action direction |
| Green distribution | 9 November used in splits but produced identical evaluation outputs | Training variation and generator invariance did not establish transferable decisions |
| More synthetic coverage / nonharm constraints / local repairs | Expanded fitting and subsequent fixed comparisons still lost recovery or reproduced harm | More rows of the same kind or new leaf repairs are not automatically substantive |
| Better beard parser | SegFace fixed mask screen failed protection; correction traces show separate decision problems | Parser training cannot be presumed to resolve correction ambiguity |

These are different historical cohorts/contracts, not a pooled head-to-head
ranking. Failure of those implementations does not prove every related feature
family useless. A generic learned embedding, white-patch rule, Retinex label or
two-stage classifier would still need eligible data, operational definitions and
training-side evidence. This review has not verified any such replacement.

## New saved-fitting-only check

Script 700 read the previously verified fitting feature JSON and its authoritative
metadata verification receipt. It confirmed the feature-file hash, retained all
890 fitting conditions from 82 originals, and used only four raw Lab/ITA values
plus the four already extracted green summaries. Twenty reserved rows were not
used for analysis. No scene features, predicted MST or target costs were added
to this check; it is not an eight-versus-sixteen-feature comparison.

Fixed descriptive comparisons, using inclusive per-feature min/max bounds:

| Query | Reference marginal ranges | Query rows inside all eight ranges |
| --- | --- | ---: |
| Core overexposure | Clean | 39/71 |
| Core underexposure | Clean | 48/72 |
| Cool colour-only | Core underexposure | 37/73 |
| Warm colour-only | Core underexposure | 35/78 |
| Stress colour-only | Core underexposure | 34/71 |

No threshold was fitted, range guard activated or classifier trained. These
counts show why absolute summaries and simple range checks remain insufficiently
justified; they do not prove that a multivariate decision boundary cannot exist,
and outside-range membership does not prove a correction is appropriate. The
conditions are repeated synthetic variants, not independent people.

The earlier source-paired audit shows green falling/rising with exposure and
often unchanged under colour-only transforms. That is a diagnostic using each
source's clean original. The app does not receive that original. Turning the
paired difference into an input would leak information unavailable at inference.

Independent scalar membership replay matched all five comparisons. The receipt
binds the exact feature file, prior verifier, nine reviewed reports and script;
all bound hashes remained unchanged. It verifies metadata arithmetic and
provenance, not photographic quality or new feature extraction. Artifact:
`outputs/correction_redesign_feasibility_v1/audit_PRIVATE.json`.

## Recommended direction and input needed

Prioritise finding genuinely different correction-reference evidence over another
synthetic feature/constraint cycle. A concrete possibility to assess is controlled
exposure/white-balance capture for research: different captures of the same scene
with a designated photographic reference. Training can use reference pairs while
the app still receives one photo. A preferred rendering remains a photographic
target, not measured true skin colour. Real captures also introduce alignment,
movement, camera-processing and reference-choice issues; collection is not a
guaranteed solution and no training sufficiency or duration is claimed.

Before proposing acquisition, establish whether the user has a device with
manual exposure/white-balance controls and someone available for research photos.
That resource question has been asked. No new participants were contacted, new
images requested for upload, capture protocol executed, source admitted or
dataset acquired. A future pilot must have a bounded protocol, grouping, reference
criteria, rights and feasibility checks before any model training. Do not turn a
small capture pilot into a fairness benchmark or an app calibration requirement.

If collection is impractical, the next decision concerns a specifically evidenced
existing paired source or an explicit scope change. No external source has been
searched or qualified in this saved-record review. The old FiveK six-thumbnail
screen did not establish a ready reference cohort. No more feature trials are
selected merely because new evidence is inconvenient to acquire.

## State after this review

The working-model goal, face/visible-neck scope and automatic workflow remain.
Existing acceptance gates and all prior failures remain visible. Parser training
is deferred. No new fits, predictions, source-image/mask byte reads, image-model
forwards, renderings, final-holdout reads, runtime changes, downloads, contacts,
uploads, commits or pushes occurred. All artifacts are preserved. The final
8-group/24-photo holdout remains byte-unread.

See [completion specification](completion-specification-2026-11-09.md),
[design eligibility](correction-redesign-decision-brief-2026-11-09.md),
[training audit](training-exposure-colour-audit-2026-11-09.md), and
[green comparison](green-feature-correction-results-2026-11-09.md).
