# Why the restored corrections look patchy

8 November 2026. Inspected the four restored conditions from two originals using saved masks, blend maps and outputs. No retraining or new image-model inference.

**Both mask coverage and blending contribute.** The masks already contain holes or retain mainly the forehead. The final blend is then too narrow at native resolution to soften many of those edges.

## What the saved maps show

| Condition | Native crop | Blend width after scale conversion | Native corrected-support pixels | Partially blended pixels |
| --- | ---: | ---: | ---: | ---: |
| Development warm + overexposure | 49 × 49 | 0.96 pixels | 612 | 92 |
| Later overexposure | 56 × 56 | 0.88 pixels | 226 | 29 |
| Later cool + overexposure | 56 × 56 | 0.88 pixels | 161 | 19 |
| Later warm + overexposure | 56 × 56 | 0.88 pixels | 208 | 19 |

These are pixels with positive correction alpha, not verified skin pixels. The three later conditions reuse one original and are not independent cases.

- **Mask shape:** the development face has substantial internal exclusions; the later face is corrected largely on the forehead, with a small separate lower component in two conditions. Much of this shape is already visible in the saved parent mask. The additional predicted visibility/object exclusions further restrict it. Blending cannot recover excluded areas.
- **Blend scale:** the existing four- or five-pixel fade is computed in the 256-pixel processing crop. When mapped back to these small native crops, it represents less than one native pixel.
- **Projection/protection interaction:** native protection correctly overrides resized alpha to zero. This removes 157, 95, 65 and 97 locations that otherwise have positive interpolated alpha. Respectively 48, 21, 22 and 28 of those had alpha at least 0.5 before the veto.
- **Abrupt edges:** there are 285, 122, 86 and 128 horizontal/vertical adjacent pairs with an alpha change of at least 0.5. All but two of these pairs touch a protected pixel. These counts describe the saved alpha geometry; they are not perceptual-quality scores or independent samples.

The native projection reproduces the saved alpha exactly. This is not evidence of a coordinate mismatch. The geometry follows the current scaling and protection rules, but those rules leave abrupt transitions at this resolution.

Predicted masks are not ground truth: an excluded area may be intentional eye/mouth/object protection or missed skin. No new skin-accuracy percentage is claimed. Glasses remain uncertain; this inspection does not establish correct rim or lens treatment.

## One targeted fix to test

Apply a fixed **two-native-pixel inward fade after native projection and protection**, with no outward mask expansion. Keep all corrections, measurements and protected pixels unchanged. This directly targets the narrow final-resolution fade without admitting uncertain skin or objects.

The [four-condition pilot protocol](native-inward-fade-pilot-protocol-2026-11-08.md) fixes the rule before rendering another candidate. This is a proposed rendering diagnostic, not a model fit or adoption. Even if it softens edges, the missing facial coverage will remain and needs a separate mask decision.

## Verification and review

Viewed all four eight-panel boards: actual input, parent mask, permitted support, processing alpha, predicted visible face, protection, native alpha and native output. Independently replayed native projection, scalar adjacent-pair counts and bound hashes; all checks passed. The boards use nearest-neighbour enlargement to expose existing native pixels, not invent detail.

Scripts 641–642. Private outputs: `outputs/restored_mask_boundary_diagnosis_v1`. Zero new fits, inference or candidate renders; no runtime/demo changes, new annotation or final-holdout reads. The correction model remains unadopted.
