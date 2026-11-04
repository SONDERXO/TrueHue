# Whole-face edge blending results

1November2026. User asked for filter-like, more seamless coverage. Implemented
one fixed inward-only boundary blend on the current whole-face+neck support.
No mask-width/parameter sweep or correction-model training occurred.

## What changed

The correction mask stays filled across the selected face, including crossing
hair, eyes, brows, lips, teeth and objects as requested previously. A separate
floating-point alpha gradually reduces correction strength near its outer
boundary. Face and neck share ONE union alpha, avoiding a second artificial
fade at the jaw/neck join. The alpha never extends into pixels outside the
permitted binary support; explicit protected pixels remain protected.

The fixed width is max(2,ceil(3%of face width))pixels, with a smoothstep curve.
It is an engineering rendering choice, not a validated optimal width. The
interior retains full correction strength. No smoothing/reconstruction of skin
texture, color recovery model, contour expansion or background hole filling
was added. Measurement uses the same nostril-guarded facial binary mask and
does not use alpha. Its measurement contract remains
`1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7`.

## Try it

Both usual neck/face-feature launchers now use blended edges by default through
script350. The saved photo preview includes binary correction support,
measurement support, alpha, hard-edge demonstration and blended demonstration.
Use `--hard-edges` on script350 to retain the historical hard-edge comparison.
The original version4builder is saved beside its evidence. No old artifacts
were overwritten.

Fixed gallery: `outputs/seamless_support_v5/review.html`.
Panels: original, alpha, hard-edge operator, blended operator. Both output
panels use identical illustrative direct-gamma/red/blue settings(.85,1.05,.95),
not a trained prediction or a statement that these photos need correction.

## Verification and inspection

All16staged-reference masks were reused without new detection/parser inference.
Binary mask bytes and measurement statistics stayed exact. Every selected pixel
has positive alpha; interior alpha1matches hard correction exactly. Identity
settings reproduce originals; outside-support pixels remain exact.

All16contact-board rows were visually inspected. Soft application reduces the
abrupt treatment boundary in the displayed examples. This is a descriptive
visual finding, not professional appraisal, ground-truth mask accuracy or a
claim that every seam is gone. Neck boundaries can remain conservative, small
irregularities outside the filled facial outline remain, and wrong contour/
parser placement is not repaired by feathering. The region may intentionally
include glasses/objects inside the face; blending does not certify their color.
No holes exist within the filled face, but unsupported regions outside it were
not automatically filled across clothing, hair or background to hide gaps.

Standalone CLI smoke on25517completed. Full Python suite:
**888passed in11.60seconds**, cache disabled. Four added tests cover boundary
alpha, full-strength interior, no face/neck seam, identity preservation,
protected/outside pixels, empty support and full-frame finite alpha.

Implementation: `src/correction/seamless_blend.py`, updated script350 and
script351. Evidence: `outputs/seamless_support_v5/{plan,records,verification}.json`.
No source/measurement approval is inferred. No current desktop/Android correction
model was switched. Matching MST calibration remains unfinished.

## Training consequence

The binary support and measurement contract did not change in this step, so
blending alone requires no additional MST recalibration. The earlier nostril
change still requires one. Blended application is a new correction operator:
old hard-mask fitted targets and binary-generation reconstruction claims must
not be silently reused as exact blended inverses. Future paired data/target
objectives must explicitly include the alpha and score face/neck/feature and
boundary behavior. The current candidate data were already held against the
old measurement/support mismatch; no fitting was unblocked by this preview.
