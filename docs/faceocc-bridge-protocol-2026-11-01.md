# Fixed FaceOcc input adaptation

1November2026. User authorised bridging TrueHue landmarks to FaceOcc. This is
an explicit new preprocessing adaptation, not source-faithful3DDFA reproduction.
Freeze anchors: midpoint33/133, midpoint362/263, nose1, mouth61, mouth291.
Order matches source template reduction: eye36/39,eye42/45,nose30,mouth48/54
(zero-based68-template indices). No iris substitution, adaptive crop, hull,
margin, pose-specific rule or alternative landmark model. Use saved square256
inputs and saved MediaPipe points from the frozen25attempt screen only.

Acquire the pinned994-byte source template and verify Git-blob/SHA256 provenance.
Use existing source-derived POS scale116/s and fixed256output; preserve source
pixel-coordinate convention, linear image warp, reflected border and border
blur. Track real-source validity separately for any future inverse mask warp.
Degenerate/missing inputs fail; no fallback. No anatomy/template fitting or tuning.

First create aligned inputs and anchor overlays for all17saved successes;
retain eight prior failures. Inspect every aligned input before segmentation.
Save forward/inverse matrices, anchors, source hashes and algebraic replay.
No automatic technical pass means anatomical equivalence. If alignment is
materially unsuitable, stop and report; do not try alternate anchors/crops.

This phase does not run FaceOcc on study images, adopt masks, change correction,
calibrate MST or fit trees. Its deliverable is a checked input bridge and gallery
for the next frozen model diagnostic. No broader subject validation is implied.
