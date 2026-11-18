# One aligned FaceOcc appearance candidate — 5 November 2026

User authorises the proposed controlled recognition-input comparison. Use all30
fixed cases from the parser-appearance package. Exactly its25successful parents
receive one candidate FaceOcc pass each; the five earlier failures remain with
no replacement/fallback. No parser, detector or landmark inference is repeated.

Reconstruct the original aligned input with existing landmarks/template and
require exact parity with its saved aligned image. Apply the existing tested
Lab-L CLAHE clip2/grid8 helper to a COPY of that aligned256BGR input, after
alignment. This is the only new candidate; no alternative order/settings/sweep.
The helper is named parser_input historically, but here serves only as the same
fixed recognition appearance transform. Feed this transformed aligned image to
the pinned CPU FaceOcc model once. Keep logit>0 and original inverse transform,
validity veto, parser-derived parent mask and1000normalized-pixel guard unchanged.

Final measurements, Lab/ITA, endpoints and native projection use original crop
pixels. No enhanced colour measurement, physical white balance, intrinsic truth,
geometric fill, veto bypass or fabricated MST. The transformed model input is
not claimed equivalent to upstream training preprocessing. Bind a new effective
contract including transform order and original mapping. No old lookup transfer.

Compare all30original/candidate statuses with full denominators, parent/final
counts, saved-logit and mask replays, native-grid counts and original-pixel stats.
Report both newly kept and newly removed mask regions. No ground-truth accuracy
claim from larger masks or technical passes. Retain all failures/regressions.

Generate and inspect all30private boards, scores hidden: original; original
aligned input; enhanced aligned input; old final overlay; candidate final overlay;
candidate additions pink/losses cyan. Inspect skin loss and object/hair/glasses
leakage. All dataset images/labels/identifiers remain ignored private local files,
research/noncommercial+citation/no redistribution. Freeze protocol/scripts/helper
and parent/source/model hashes before inference. Stop after one comparison;
no automatic next transform, batch, calibration, tree fit, admission or app change.
