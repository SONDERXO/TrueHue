# Include skin around eyebrows during correction

31October2026. User requested that surrounding eyebrow skin be included so
untreated patches do not stand out. The default face/neck/features preview now
uses a separately versioned correction-only extension. Facial measurement
masks, Lab/ITA and the matching MST measurement contract are unchanged.

The previous measurement exclusions deliberately removed a wider eyebrow area
than the parser's eyebrow class alone. Adding only brow-hair pixels therefore
left some nearby skin untreated. The new extension adds predicted skin/nose
pixels in a small band around the selected brows: a single fixed radius of
ceil(2%of facial-mask width), minimum1pixel, restricted to the selected face
bounds. It does not fill every facial hole or add predicted eyes, glasses,
mouth interior, background or hair. Explicit protected pixels remain excluded.
The parser can still make mistakes; this is not guaranteed eye/skin truth.

Use `run_face_neck_features_preview.cmd` as before. Pink now includes the new
surrounding eyebrow skin as correction-only support. A before/after gallery is
saved at `outputs/peribrow_support_v2/review.html`: original; newly added skin in
yellow; previous support output; updated support output. Both output panels
use the same fixed illustrative settings, not a trained-model prediction.

On the21saved cases,19received additions,4415pixels total. No additional parser
inference or model fitting was needed. Measurement masks remain byte-identical
and output changes are confined to newly added skin. The six-reference contact
sheet was visually inspected; it shows inclusion of the gaps surrounding the
selected eyebrows. This is not a new user approval or quantified perceptual
quality result. No mask-radius search followed inspection.

Full Python suite: **874passed in13.41seconds**. Two added tests check surrounding
skin, unchanged measurement support, avoiding indiscriminate hole filling,
predicted eye exclusion and explicit protected pixels.

## Consequences for the staged comparison

The existing preferred-support cohort and30pairs use the earlier correction
region. Preserve them as version1 evidence; do not train from them as though
they used this revision. Their source/facial-mask decisions remain useful, but
combined-mask approval would apply only to those displayed version1 masks.
The previous reference-review page is labelled accordingly. Newly generated
full-region pairs will need matching revised correction masks and reference
generation/scoring regions before the one planned comparison. There is no need
to recalibrate MST solely for this correction-only change. The already
experimental lookup's validation limits remain. No demo model was switched.
