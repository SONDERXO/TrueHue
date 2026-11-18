# Exact-sixty scene-summary diagnostic — 11 November 2026

The seven existing whole-scene summaries respond to the paired capture change,
but they are not qualified illumination estimates or photographic calibration
inputs. Every one of the fourteen photographic roles lies outside at least one
of the seven labelled-set marginal ranges. No new fit is justified by this
diagnostic alone.

Scripts 775–776 freeze the sixty reviewed source identities, assert separation
from final groups, and verify all sixty inherited JPEG hashes before decoding.
Each exact delivered JPEG is read once into memory and decoded once at 224×224;
all sixty succeed. These are full delivered frames, not normalized face crops or
recovered camera-original scenes. Assumed sRGB and absent ICC/EXIF limitations
remain. Original method/annotation/subject/label bindings are preserved alongside
the new summaries. Existing masks and features are not overwritten.

The unchanged seven-feature implementation yields these paired changes:

| Descriptor | Mean 1200 minus 600 | Positive / negative / zero pairs |
|---|---:|---:|
| logR/G | +0.019280 | 17 / 13 / 0 |
| logB/G | +0.041194 | 23 / 7 / 0 |
| Scene L*p10 | +11.947713 | 30 / 0 / 0 |
| Scene L*p50 | +14.104575 | 30 / 0 / 0 |
| Scene L*p90 | +14.875817 | 30 / 0 / 0 |
| Any-zero channel fraction | −0.000198 | 1 / 24 / 5 |
| Any-full channel fraction | +0.000100 | 8 / 0 / 22 |

This is evidence of a rendered-scene brightness response in the thirty matched
pairs, not thirty independent subjects or causal illuminant isolation. Background,
clothes, crop content, camera processing and reflectance remain confounded.
Colour-ratio changes do not have a uniform direction. Within-condition
across-subject spreads are retained in the private summary, rather than assuming
each lighting condition produces a content-independent scene value.

All fourteen photographic roles are outside at least one labelled-set scene
marginal; this is additional to the seven roles above the reviewed facial L*
maximum. These are different tests and must not be conflated. Marginal mismatch
flags extrapolation risk; it does not prove a cue is useless or that joint
support/accuracy can be inferred from marginal overlap. Photographic roles have
no supplied MST labels, so no photographic mapping accuracy can be evaluated.

Independent verification replays all 420 descriptor values from cached RGB
frames using explicit channel sums, hand-interpolated lightness quantiles and
clipping counts. It verifies 210 paired differences, ranges, signs and fourteen
photographic support records. All pass at 1e-10, without rereading original JPEGs,
image-model calls, fitting or prediction. No visual image review is claimed.

Private evidence: `outputs/reviewed_scene_diagnostic_v1`. This fixed diagnostic
is complete. No cue subset, threshold, model, normalization or penalty was
selected. Do not start another scene-feature fit or reopen the closed green/tree
comparison. No more masks or labels are requested for these completed queues.

The substantive unresolved issue is compatible labelled coverage and evidence
that an added cue separates illumination from scene/skin reflectance on the
intended photographic domain. The summaries do not supply that evidence. A next
design decision must address that gap before another calibration fit; no new
acquisition, intervention or experiment is selected here. Runtime promotion and
the working-model objective remain incomplete. Keep the decision tree, ITA and
MST and all original preservation gates.

No detector/parser/FaceOcc calls, fits, predictions, runtime/Android changes,
downloads, contacts, uploads, commits or pushes occurred. Sixty whitelisted source
photos were read; all final 24 and older locked images remain byte-unread. All
prior artifacts and annotations are preserved, with admission flags false.
