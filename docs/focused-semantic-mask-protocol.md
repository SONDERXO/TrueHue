# Reviewed-source semantic mask comparison

29 October 2026. Freeze this development comparison before candidate inference
on the 24 annotated training references. Use no reserved training-check,
development-validation or final-test sources. Preserve baseline images/masks,
decisions and exact concerns. No extra user photo selection is requested.

Use the already local, provenance-checked 19-class ResNet18 face parser with
unchanged preprocessing and weights. Run on the saved 256-square reference.
Require exactly one face under the existing detector result and use its
unchanged rectangular bounds; do not rescue detection failures by choosing a
face retrospectively. Parser failure yields explicit unavailable masks.

Compare three masks: saved baseline; removal-only baseline intersected with
parser skin/nose and detector bounds; parser skin/nose restricted to those same
bounds. The last is the candidate and may add facial pixels outside color
threshold support. It does not depend on MediaPipe landmarks. All other parser
classes, including eyes, brows, mouth, glasses, hair, clothing and neck, are
excluded. No morphological filling, threshold tuning or manual pixel repair.
Keep the existing 1000-pixel count only as a technical support flag, not an
accuracy gate. Parser labels are predictions, not human ground truth.

Save categories, masks, added/removed counts and image boards. Compare candidate
overlap with rejected versus accepted baseline masks descriptively, never as
pixel precision/recall: annotations are source-level suitability judgments.
Record failures and runtime. No candidate ITA/MST inference, target generation
or correction tree fitting. This candidate changes the measurement definition;
its version and dependency fingerprint are separate, and the existing MST
lookup is not calibrated for it. Dense parser portability/latency remain an
Android delivery concern rather than assumed compatible deployment.

Human comparison must preserve accepted-mask concerns and inspect added skin,
removed spill and foreign-object handling. A numerical coverage increase is
not improvement. After a candidate is frozen on this development set, evaluate
the reserved training check under a separate recorded phase. Until then keep
those images out of candidate inspection. Do not promote by larger area alone.
