# FaceOcc coordinate and loading checks

1 November 2026. User authorised tracing input preparation and checking isolated
loading. Completed source-derived alignment math, inverse-mask mapping tests and
strict checkpoint loading. No study-photo inference or runtime adoption.

## Verified coordinate contract

faceocc_coordinates.py reproduces the pinned source POS least-squares calculation
for five ordered landmarks and their matching3Dtemplate. The source order is
two eye centres, nose and two mouth corners; full source landmark/template
correspondence is required, not guessed from array length. It applies the source
y-flip h-1-y, estimates translation/scale and constructs the fixed256affine:
scale116/s; dx128-tx*scale; dy128-(h-ty)*scale. The source h versus h-1 distinction
is preserved rather than silently corrected. Degenerate inputs fail explicitly.

Binary model-mask inverse mapping uses the invertible affine, nearest sampling,
zero outside-domain values and an independently warped source-validity mask.
Predictions on reflected/padded input cannot become source-image measurements.
The upstream image alignment uses reflected-border sampling with border blur;
this local module implements coordinate/mask logic, not the entire upstream
image-preparation path. Do not describe it as full gallery preprocessing.

Three synthetic tests passed: known projection yields expected affine;
integer-translation round trip restores the original mask and excludes padding;
degenerate template/mapping fails. These checks establish mathematical consistency,
not automatic face alignment quality, subpixel segmentation accuracy or correct
anatomical correspondence. General resampling need not round-trip exactly.

Source attribution and MIT text retained in docs/third-party/faceocc-LICENSE.txt.

## Isolated CPU loading succeeded

Created outputs/faceocc_inference_env_v1 using Python3.14; main project venv and
requirements remain unchanged. CPUtorch/torchvision and segmentation-models-
pytorch0.5.0/SafeTensors dependencies were installed only there. Full environment
freeze is in outputs/faceocc_loading_v1/environment-freeze.txt; exact versions
and executable are in verification.json. This local runtime is not the publisher's
training environment and no training reproducibility is claimed.

Script365 reconstructs the architecture from pinned source, with
encoder_weights=None to avoid fetching a second encoder. Strict load passed:
zero missing/unexpected keys. Verified checkpoint SHA remains
5d6d27a9cb221692425840a80eb4efc07e6245670b233e2eb618e83fd9b7caf6.
An all-zero synthetic RGB input normalised with the published ImageNet mean/std
produced finite1×1×256×256logits; repeating the CPU forward pass matched exactly.
No synthetic logits are interpreted as skin-quality or accuracy evidence.

Eight focused project tests passed in4.10s: coordinate mapping, existing nostril
measurement and correction continuity. No full-suite rerun for this isolated
readiness work; prior896test run excluded desktop GUI(Tcl/Tk unavailable).

## Remaining implementation boundary

The pinned training preparation uses3DDFA-style68landmarks and a3Dtemplate.
TrueHue's existing MediaPipe landmarks are not proven interchangeable. The
reference evaluation reads prepared COFW inputs and does not resolve that bridge.
No FaceBoxes/3DDFA weights or source-template binary were acquired in this stage,
and no additional detector or landmark model is adopted. No arbitrary full-frame
resize, detector margin or MediaPipe-point substitution was used for inference.

Before study-photo testing, choose and document source-faithful landmark/template
preparation OR an explicit TrueHue-specific correspondence adaptation. The latter
must be marked an adaptation with fixed anatomical correspondences and a synthetic
forward/inverse geometry check, not claimed as upstream preprocessing. Do not
search several crops and keep the best visual result. Inspect resulting inputs
before any claims about the occlusion model.

**Decision:** checkpoint loading ready; end-to-end study-input contract still
incomplete. No measurement masks/features/lookup/calibration/correction changed.
The intended later diagnostic remains current preferred measurement AND visible-
face veto, fixed threshold, exact25attempt membership and no filtered refit.
Beard-specific work remains held; binary visible face does not guarantee beard
exclusion. Panel register updated as an experimental component, not adoption.
