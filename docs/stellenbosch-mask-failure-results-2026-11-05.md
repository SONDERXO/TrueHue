# Skin-parser failure isolated — 5 November 2026

The continued correction-development diagnostic identifies a concrete upstream
blocker: in all four available landmark cases from the highest sampled score
interval, the parser predicts **background over the entire anatomical probe**.
Those cases fail before FaceOcc or the final pixel-count guard. The other two
cases in that interval fail single-face detection. Lowering the1000pixel guard
cannot recover skin that the parser never selected.

## Diagnostic and results

Scripts438–439 followed the [fixed protocol](stellenbosch-mask-failure-protocol-2026-11-05.md)
on the same30saved crop cases, with no new inference or fits. Existing landmark
geometry supplies a facial probe minus eyes, brows, mouth and nostril exclusions.
It is a diagnostic coordinate region, not verified skin or a replacement mask.

| Existing descriptive score interval | Available probes / all attempts | Probe pixels classified as skin/nose |
|---|---:|---:|
| [1,3) | 6/6 | 81.63% |
| [3,5) | 6/6 | 74.64% |
| [5,7) | 6/6 | 52.47% |
| [7,9) | 6/6 | 26.65% |
| [9,10] | 4/6 | 0.00% |

Percentages pool normalized probe pixels within each interval, not people or
independent native samples. Intervals retain their original sampling meaning;
source decimals are unchanged, not rounded or converted into MST categories.
All47,949probe pixels in the four available highest-interval cases are classified
as background. This establishes an observed stage failure, not a population
performance estimate, proof of demographic bias, or its cause. Image brightness,
lighting, native detail and subject appearance are confounded in this small sample.

All30new boards were inspected by the assistant with source scores hidden.
Geometry often follows the facial surface, while parser skin support has large
holes. Geometry also includes glasses and occasional hair boundaries, so using
it directly would bypass the necessary contaminant protection. Some additional
lower-face losses appear after FaceOcc. It is therefore inaccurate either to
blame all missing skin on FaceOcc or to claim that replacing its mask with the
geometric probe fixes measurement validity.

## Development decision

The next repair target is **parser recognition under these input conditions**,
with detector failures retained separately. A prospective bounded candidate is
to separate a fixed segmentation-only appearance preprocessing step from the
original pixels used for colour measurement. Such a candidate would need its
own single declared transform and original-versus-candidate comparison on all30,
with glasses/hair/objects and lost skin inspected. It is not implemented or
activated by this diagnostic, and no sweep of preprocessing recipes is justified.
Colour statistics must remain tied to the original input; preprocessing for
recognition must not silently manufacture corrected colour measurements.

This is a specific repair direction, not another calibration-readiness audit.
Native detail, anatomical reliability, decimal-compatible MST evaluation and
lighting-dependent ITA remain separate limitations even if parser coverage improves.
The full intended ITA/MST/three-output correction model remains untrained here;
no old lookup is reused and no MST feature is omitted or fabricated.

## Verification and preservation

Verified all source/bound parent/artifact hashes;28class histogram sums and
skin/nose count identities; five aggregate strata;20exact saved semantic-mask
replays (including the below-pixel-minimum parent); all30attempts retained.
The eight original semantic-stage failures replay their failure reasons, and
the two detector failures receive no fabricated geometry. No new pixel selection
is admitted for measurement or training. Private gallery and evidence:
`outputs/stellenbosch_mask_failure_isolation_v1/review_PRIVATE.html` and
`outputs/stellenbosch_mask_failure_verification_v1/verification_PRIVATE.json`.
Photos, individual identifiers, source scores and manifests stay ignored/private
under the research/citation/no-redistribution conditions. No dataset was shared,
no author contact occurred, and the app/runtime/model files are unchanged.

Focused verification of the reused anatomical, semantic, nostril and face-outline
helpers passed24tests in1.85seconds. This is not a new full-suite run or a claim
that predicted geometry or parser classes are accurate skin annotations.
