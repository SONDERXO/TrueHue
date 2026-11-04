# Fixed MediaPipe-to-FaceOcc bridge prepared

1 November 2026. User authorised the fixed bridge and aligned-input inspection.
The source template is acquired and an explicit TrueHue adaptation now produces
input crops for the frozen saved diagnostic. No FaceOcc segmentation inference
on study photos, mask adoption, calibration or correction fitting in this phase.

## Exact adaptation and evidence

The994-byte source similarity_Lm3D_all.mat came from pinned source revision
8d86c9a2c1a0094dbc1a1e5467413b49f8936b32. Script366 verified the blob against
the previously pinned Git tree and saved SHA256/provenance beside the weights.
No additional detector/landmark model or dataset was acquired.

New faceocc_mediapipe_bridge.py fixes these correspondences, before viewing
aligned study inputs: midpoint33/133, midpoint362/263, point1, point61, point291.
These are MediaPipe eye centres, nose and mouth corners. The pinned68-point
source template is reduced with upstream eye36/39,eye42/45,nose30,mouth48/54
zero-based indices, preserving original order. No iris substitution, per-pose
anchor choice, crop margin or radius search.

The bridge uses the previously checked source POS calculation and affine,
linear image sampling, reflected borders and source-style blurred border region.
Forward/inverse affine and each original/aligned anchor are saved. Future mask
inverse mapping must still exclude padding through the separate validity mask;
reflected image content cannot become measurement evidence.

This uses existing MediaPipe evidence instead of the original3DDFA generator.
It is a methodological preprocessing adaptation, **not upstream landmark or
crop equivalence**. It adds no learned network and changes no active mask.

## Single fixed preparation result

Script367 froze the exact25attempt IDs, source/template/code/protocol hashes,
then processed saved square256images/landmarks.17aligned inputs available;
eight original failures remain without retry or replacement. No raw-source
remeasurement or inference. All source/artifact hashes unchanged. Anchor
forward/inverse replay passes at1e-8absolute coordinate tolerance.

All17paired original/aligned boards inspected across five contact sheets.
Inputs remain facial crops suitable for an exposed engineering diagnostic.
Side-profile crops can place the nose near the edge; some forehead/hair is
cropped, and reflected background appears in several views. Covered-mouth
landmarks remain estimates, not visible mouth annotations. These are limitations,
not evidence of equal landmark accuracy, equivalent training distribution or
independent image-quality acceptance. No alternate anchors/crops were tried.
The diagnostic must preserve these inputs and report any resulting mask failure.

Evidence: outputs/faceocc_bridge_v1/plan.json, summary.json and review.html;
models/faceocc_candidate_v1/template_provenance.json. Summary saves forward and
inverse matrices, anchor locations, aligned-image hashes and parent-failure reasons.
Five coordinate/bridge tests passed in0.34s, including two new checks for fixed
anchor/template order and explicit failure on invalid correspondence. Existing
strict CPU loading/synthetic-forward result remains in outputs/faceocc_loading_v1/.
No broader/full test rerun claimed for this preparation.

## Decision and next bounded task

Fixed input preparation is ready **for the one diagnostic only**. The next task
is to freeze model inference/mask mapping against these exact aligned files,
the pinned checkpoint, fixed logit>0 rule and current preferred measurement
baseline; all25attempt dispositions remain. Annotate actual skin/occluder
diagnostics before viewing predictions. Save logits, validity mapping, retained
fractions and all failures. Do not swap in the rejected face-outline candidate.

Readiness does not mean model quality or Android feasibility passes. No old MST
lookup/approval transfers; any resulting feature candidate needs its own contract.
No calibration/tree fit, automatic runtime promotion, beard-specific model or
new participant collection. Correction masks/rendering remain unchanged. The
panel change register records the explicit landmark preprocessing adaptation.
