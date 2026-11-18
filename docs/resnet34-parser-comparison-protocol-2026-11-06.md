# One alternative parser comparison — 6 November 2026

User authorises one alternative face parser on the fixed difficult photos.
Select yakhyo face-parsing ResNet34 ONNX, not a model/backbone sweep. Baseline
is the frozen ResNet18 whole-face measurement from the new-source package,
NOT the unadopted upper-face/background-recovery candidate. This is a larger
BiSeNet-family backbone variant with the same19labels, not a new beard class,
independent training-data family or guaranteed material-recognition improvement.

## Acquisition and rights/provenance

Official asset ID328506789,93,632,554bytes, GitHub release digest
`5b805bba7b5660ab7070b5a381dcf75e5b3e04199f1e9387232a77a00095102e`.
Verify exact bytes/digest before loading; preserve failure/partial artifacts and
refuse overwrites. Pin metadata and author sources to existing source revision
8a4729d95118d0e97c44185f9bdef3d6bfeaaf99. Upstream software MIT notice and published
model/dataset lineage are recorded, not blanket commercial clearance. Local
research/noncommercial only; no images uploaded for inference or dataset sharing.

Primary sources: https://github.com/yakhyo/face-parsing and its pinned LICENSE,
README, onnx_inference.py and utils/common.py. Use existing reviewed OpenCV CPU
adapter: BGR→RGB,512INTER_LINEAR,ImageNet mean/std, primary19class logits,
argmax then nearest category resize. Strict finite/shape checks; no new packages,
remote code execution, runtime replacement or changed source modules.

## Fixed comparison before new inference

Use exactly the six reference-review cases04/21/25/30/16/29, membership/image
hashes bound to that manifest. One alternative parser forward per saved original
crop transformed by the same fixed parser-only CLAHE Lab-L clip2/grid8step.
Existing baseline categories and whole-face masks stay frozen. Case29can receive
a parser category output but its missing landmarks/final mask remain unavailable;
no new detector/landmark/FaceOcc forward or fabricated geometry rescues it.

For the five available geometry/visibility cases, rebuild unchanged full-face
semantic skin/nose component association, anatomical/nostril guards and1000pixel
parent minimum using alternative categories. Reuse original aligned enhanced-
FaceOcc logits, exact matrix and original-pixel Lab/ITA statistics. Keep all
parent/model/final failures, with unavailable prediction distinct from negative.
No upper-face cutoff, background inclusion, hole fill, label-based mask repairs,
threshold change or source-score feature is allowed.

Compare actual238reference points, preserving all original denominators and
unavailable cases. Record parser-stage skin/nose selection separately from
final masks to localise gains/losses. If an alternative parent/final becomes
unavailable, report lost coverage and paired-row summaries; do not turn missing
predictions into correct exclusions or favourable conditional error. Include
skin gained/lost and unwanted additions/removals, plus hair/object breakdowns.
These points are development-exposed, sparse and include neck skin outside the
face-only measurement scope; not segmentation accuracy or independent test.

Inspect all six original/old/new/added-lost boards, with scores hidden, for dark
skin omissions, glasses/reflections, beard/hair leakage and the control. A better
pooled point fraction is not acceptance. Save all cases/failures and negative
findings; no model/severity/preprocessing sweep follows. Verify saved masks,
original statistics, source/actual-export/model hashes and native projections
without another inference pass.

Stop after this one controlled alternative. No real MST/tree fitting, cohort
admission, app change, new review workload, source expansion, contacts or
redistribution. Private outputs and model assets stay ignored; thesis method
and panel register record experimental status without approval claims.
