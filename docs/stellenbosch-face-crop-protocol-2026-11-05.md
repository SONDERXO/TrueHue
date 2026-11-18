# Fixed face-first input bridge: same30 Stellenbosch cases

5November2026. User explicitly authorises the proposed face-crop check. Retain
the failed whole-frame30-case package unchanged. Use exactly its selected source
bytes, subject keys, decimal scores and three conditions; no replacement,
expansion, category rounding, calibration or model training.

Before new inference freeze this protocol, dependencies and all source/baseline
hashes. Reuse each saved whole-frame256detector box as geometry, not a source
skin mask or source label. Map box coordinates to native image coordinates.
Take one square centred on that box, side ceil(1.5 times the larger native box
dimension). Shift an edge-crossing square inside the source without padding;
fail if it cannot fit. No margins/crops are tried in response to results.

The crop is an exact native-pixel slice. Then the existing measurement path
resizes that crop to256 INTER_LINEAR and re-runs the unchanged .85 single-face
guard, ordered landmark helper, parser/anatomical/nostril exclusions,1000-pixel
normalized-frame guard and pinned aligned FaceOcc logit>0 validity veto.
One CPU pass per available aligned parent in the existing isolated environment.
Failures remain. Existing helper fallbacks are unchanged, not extended.

This is a NEW effective source-to-measurement contract: native source→fixed ROI→
existing service. The service code/weights stay unchanged, but the old whole-frame
contract/lookup cannot be claimed equivalent. Preserve the prior source-score
policy: supplied continuous MST targets, no integer categories or fitted scores.

For each ROI record box mapping, native bounds/size, upscale factor and exact
slice check. Project the final binary mask to the crop's ORIGINAL pixel grid
with nearest-neighbour resize and place it in native source coordinates. Record
selected native-grid locations and area-equivalent source pixels alongside the
normalized count. Neither is an effective independent sample-size estimate.
Upsampling cannot create facial detail or establish skin/colour/score validity.
Do not invent a native adequacy cutoff or promote normalized1000-pixel success
to calibration admission. All reports remain actual-skin unverified, MSTNone,
calibration/training admitted false. Do not lower the existing guard.

Inspect all30private source/native-crop/measurement/selected-pixel boards.
Record hair/beard/glasses/neck/clothing/skin-loss/light/low-resolution concerns
without dense accuracy or human approval claims. No new human annotation task.
No publication/sharing of dataset images, source labels or per-person manifests.

Verify exact crop/mapping/source identity, saved service/mask/feature replay,
native projection/count arithmetic and preserved decimal/subject membership
without refits/new forwards. Retain all baseline/source/archive/historical hashes.
Stop after this single bridge comparison; no crop sweep, larger batch, automatic
calibration, integer-label adapter, runtime switch, author contact or dataset rejection.
