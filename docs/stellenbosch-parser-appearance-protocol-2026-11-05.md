# One segmentation-only appearance candidate — 5 November 2026

User authorises the proposed parser-recognition repair diagnostic. Retain all30
fixed Stellenbosch crop cases and source scores; no expansion or replacements.
The28saved single-face landmark cases are the only parser attempts; the other
two retain their original detector failures, without invented landmarks.

One fixed candidate only: original256BGR to encoded OpenCV Lab, CLAHE on L only
with clipLimit2.0 and tileGridSize8x8, then Lab to BGR. Use this copy solely as
input to the pinned19class parser. No grid, gamma, colour-balance or model sweep.
This is an explicit preprocessing adaptation, not upstream model equivalence or
physical white balance. Conversion may change rendered chroma through quantisation
and gamut conversion; do not claim colour preservation of the enhanced copy.

Use original256pixels for landmark geometry, existing skin/nose component
association, eye/brow/mouth/nostril exclusions, final Lab/ITA/endpoints and FaceOcc
alignment. Unchanged1000normalized-pixel minimum. No raw-colour measurement from
the enhanced copy. No geometric fill/fallback when the parser still misses skin.

Recompute parent masks/stats on original pixels. For successful parents, reuse
any old FaceOcc logits ONLY when original aligned pixels exactly match the saved
input and pinned logit hash. For newly available parents without old logits,
one fixed CPU FaceOcc forward on original aligned pixels; no brightened FaceOcc
inputs and no all-visible substitution. No repeated model forwards for old inputs.
Retain all failures, unavailable targets and regressions. This candidate requires
a new effective contract; no reuse of old MST lookup, fit or runtime switch.

Report parent/final availability by original score strata with full denominators;
baseline/new class counts on the SAME fixed anatomical probe; added/lost mask
regions; native-grid counts; masked statistics from original pixels. None of these
is segmentation accuracy or calibration admission. Inspect all30boards (ten
contacts), labels hidden: original input, parser copy, old final mask, new final
mask, new parser additions to old skin/nose support (pink). Missing masks explicit.
Check glasses/reflections, hair, facial features and boundary losses.

Freeze this protocol, scripts, helper/tests and parent/source/model hashes before
inference. Verify saved masks/service/stats/native projections and original-byte
preservation without refits or new inference. Dataset evidence is private ignored
under research/citation/no-sharing terms. Stop after this single candidate result;
no threshold relaxation, next candidate sweep, calibration/tree fit or app update.
