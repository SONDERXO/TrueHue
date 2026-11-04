# Enclosed facial-mask hole check

30 October 2026. Implemented and checked a development-only enclosed-hole
completion operator. It preserves anatomical exclusions and outer mask
boundaries, but does not establish that every added pixel is skin. Visual
inspection found beard and glasses-related risks, so it is not enabled in the
demo, measurement pipeline or training data.

The [predeclared protocol](enclosed-hole-mask-protocol.md) uses one topological
rule: add only entire 8-connected missing components that touch neither the
frame boundary, an anatomical exclusion nor the exterior of the landmark face
outline. There is no hole-size threshold, color threshold or per-source rule.
If a missing region contains an anatomical exclusion, preserve that entire
region. The function accepts only the input mask, exclusions and outline;
reference images and masks do not influence additions.

`src/skin_masking/enclosed_hole_support.py` is a separate experimental module.
The original measurement contract, its MST lookup and existing masks remain
unchanged. This is an application-support candidate, not a replacement ITA
estimation mask or a guarantee of skin classification.

## Results on the exposed contour-development frames

Reused the existing twenty reference/color-probe source pairs. Their masks are
previous contour/YCrCb candidates, not newly approved production masks. Human
decisions and exact notes are preserved, including rejections. Of forty frames,
37 have geometry and three remain explicit missing-geometry failures. Fourteen
frames receive additions, totaling 5,286 pixels across both reference and color
frames. No failed frame is repaired by fabricating a mask.

Eighteen sources have geometry in both frames. On these pairs, color-mask
misses relative to the *original candidate reference mask* fall from 127,716
to 126,058 pixels: 1,658 pixels recovered, about 1.3% of the original missed
support. Two color additions fall outside that original reference mask.
These are aggregate support-agreement counts, not mask accuracy, subject-level
improvement or proof that the additions are skin. Reference candidates already
contain errors. Large shadow-related gaps connected to background are not
enclosed holes and deliberately remain unfilled.

Inspected `outputs/enclosed_mask_holes_v1/largest_additions.png`, showing the
four largest additions side by side with originals and existing masks. Source
2879 gains pixels in the beard/chin region; additions around glasses in 63207
and 20196 also need semantic caution. Existing mask errors are preserved, not
hidden. The geometry rule alone cannot distinguish facial skin from enclosed
hair, glasses or objects. Do not promote it from improved support agreement.

## Verification and next direction

Six meaningful topology tests check enclosed filling without outer expansion,
diagonal background connectivity, whole anatomical-hole preservation, whole
outline-crossing rejection, independent holes, invalid contracts, no mutation
and explicit empty-support failure. The **full suite passes 786 tests in
10.85 seconds**, with pytest's cache provider disabled to avoid the previously
observed cache-write warning.

`scripts/260_check_enclosed_mask_holes.py` verifies the parent's frozen hashes,
reconstructs existing masks from saved geometry, checks unchanged original
pixels, excludes anatomical/outline additions, independently checks full added
component membership and border connectivity, replays deterministic masks and
compares saved mask pixels. Results, overlays and hashes are in
`outputs/enclosed_mask_holes_v1/summary.json` and `verification.json`.

No new model fitting, MST inference, measurement features, reserved data,
source approval, target change or manual review request occurred. Demo behavior
is unchanged. More blind gap filling is not justified: it recovers little of
the missing support and risks correcting non-skin. Future mask work needs
better exclusion evidence for facial hair, glasses and occlusion, while keeping
the paper's color-rule method and recording any proposed method changes.
