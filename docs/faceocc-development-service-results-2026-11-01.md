# Preferred experimental measurement: reusable service and saved parity

1November2026. User requested continued progress after choosing FaceOcc as the
preferred experimental candidate. Implemented an isolated reusable measurement
service and replay runner from already saved evidence. This is engineering
integration, not another scientific trial, new data admission or model adoption.

## Implementation

src/ita_estimation/faceocc_development.py exposes:

- measure(image,detector,landmarks,parser,predictor,template): unchanged nostril
  parent measurement, cached landmarks, fixed input bridge, injected one-call
  predictor, inverse-validity veto and candidate features.
- evaluate_parent(...): the same bridge/veto from an existing parent result,
  enabling saved-logit verification without repeating detection or inference.
- contract(root): hashes parent contract, pinned weight/config/template,
  alignment/veto/feature/service code. No old lookup or model-family replacement.

PyTorch is not imported into the project environment; prediction remains an
explicit dependency supplied by the isolated pinned backend. The service does
not implement automatic downloads, alternative weights, threshold choices,
training or a shortcut to old MST. The supplied predictor must follow the frozen
RGB/ImageNet/CPUfloat32 contract; dependency injection itself is not backend
validation. Prior strict loading/model evidence remains separate.

Failures at parent, alignment, prediction or candidate measurement return
features=None, mst=None and an explicit stage/reason. Successful measurements
also return mst=None, actual_skin_validity=unverified, calibration_admitted=False
and training_admitted=False. They are technically available development vectors,
not assertions that every pixel is skin. Parent masks/reports remain intact;
the predictor receives an aligned-image copy. No stale parent features survive
a failed model/insufficient mask. Explicit per-image known holds remain in the
readiness ledger, not replaced by service success.

Service contract:
`89c7a3963dcc72bfa8c7b73433789b058093131662c88a6d30a7f25d791823fd`.
This new integration contract does not retroactively rename old evidence
contracts or transfer calibration. Active parent measurement1bdef31c remains
unchanged; no current demo/preview launcher imports this service.

## Reproduction without another model pass

Script382_replay_faceocc_development.py replayed all49existing attempt records
from the two FaceOcc diagnostic cycles. It uses saved originals/parent masks,
landmarks, template and logits only; no new raw source pixels or model forwards.

35successful cases exactly reproduce saved aligned images, candidate masks and
feature vectors.14parent failures never call the predictor and retain no features
or MST. All49stay unverified and unadmitted. Frozen baseline/model/preprocessing/
correction input hashes remain unchanged. This demonstrates integration parity,
not mask-quality, MST reliability or correction improvement.

Evidence: outputs/faceocc_development_service_v1/contract.json, records.json,
input_sha256.json and verification.json. The runner refuses overwrite, preventing
silent replacement of this evidence. It is a saved-evidence runner, not permission
to process a new batch. No raw-image CLI or automatic eligibility bypass added.

## Verification and next boundary

Four new service tests cover successful outputs remaining unverified/unadmitted,
parent immutability, stopping on parent failure, invalid predictor output,
insufficient support and end-to-end detection failure. Broader Python run:
911passed in29.48s, excluding tests/test_demo_desktop.py due to unavailable local
Tcl/Tk. This is not a full-suite pass. Earlier five focused service/veto checks
passed before the added detector-failure coverage; the broader run includes it.

The substantive blockers in faceocc-bounded-development-plan-2026-11-01.md remain:
actual-skin admission, defensible matching-MST evaluation scope and an admitted
correction cohort. The software is now reusable without replay-script duplication,
but it cannot manufacture that evidence. No new review burden, subject recruitment,
calibration, correction fitting, filtered cohort or runtime promotion was started.

Panel record: this service packages the already selected experimental component;
it adds no new scientific method choice. Preserve learned parsing/occlusion-veto/
MediaPipe alignment deviations and separate engineering parity from validation.
