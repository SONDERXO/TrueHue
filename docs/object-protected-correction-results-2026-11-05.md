# Object protection added to development correction masks

5 November2026. User requested avoiding correction on objects. This supersedes
the earlier choice to correct objects inside the face outline. The revised
development mask protects predicted objects and occlusions while retaining
normal facial features and associated visible neck. It does not change the
measurement mask or ITA/MST features.

**[Open the old/new comparison gallery](../outputs/ffhq_object_protection_v1/review.html).**
Panels are original, previous correction green, revised correction green,
newly protected pixels pink, and fixed illustrative correction. The last panel
uses .85/1.05/.95, not learned predictions.

## Implementation

The new reusable module `src/skin_masking/object_protected_correction.py` applies
a removal-only layer after existing full-face/neck construction and hole
filling. It protects parser-labelled background, glasses, earrings, necklaces,
clothing, hair and hats. Saved FaceOcc visibility also vetoes occluded facial
areas, including some objects the parser calls skin. It uses raw visibility,
not the measurement mask's eye/brow/mouth/nostril exclusions. Normal facial
features remain eligible for correction when not predicted occluded.

Protected holes remain holes. The hard veto is passed to inward blending so
protected pixels have zero alpha and unchanged output bytes. No new pixels
are added to the former support. FaceOcc's face-only visibility does not veto
the entire neck; parser and explicit caller protection apply there. Neck
objects misclassified as neck can still remain. The parser has no dedicated
beard class, and beard-specific model work is still held.

The [protocol](object-protected-correction-protocol-2026-11-05.md) and dependency
hashes were recorded before mask processing. Script417 uses all12 saved FFHQ
cases, categories, logits and mappings. There was zero new model inference,
threshold adjustment, model search or manual object tracing. Previous outputs
and the pinned mask modules remain unchanged. This is a new correction-support
candidate, not an Android or desktop runtime/model replacement. Existing
script350 launchers still show the historical whole-face policy; use this new
gallery for the revised policy, not those launchers as evidence of protection.

## Inspection of all twelve revised boards

The assistant inspected all12 saved256px working boards. Pink is predicted
protection, not an annotated object mask or accuracy measurement.

| ID | Removed correction pixels | Assistant observation |
|---|---:|---|
| 54632 | 344 | Small boundary exclusions; beard remains included in correction; measurement concern unchanged |
| 39568 | 244 | Mostly boundary trims; some chin/neck edge skin may also be removed |
| 29617 | 4850 | Sunglasses and most hand boundary excluded; thin contact edges remain uncertain |
| 29863 | 8421 | Large head-covering spill excluded; beard measurement problem remains |
| 16061 | 3673 | Glasses/lens region and some fringe excluded; fine rims uncertain |
| 52445 | 973 | Hairline/chin trims; some useful skin may be lost; neck remains unavailable |
| 32685 | 815 | Fringe trimmed; possible skin loss and uncertain collar/neck fragments remain |
| 53146 | 663 | Cap-adjacent and side/chin edges trimmed; hard-light limitation remains |
| 48879 | 4333 | Broad hair-covered temple/cheek region protected; some diagonal hair may remain |
| 49131 | 58 | Small boundary changes; face/neck broadly retained |
| 59807 | 5729 | Glasses and most microphone face overlap excluded; lower microphone/neck boundary uncertain |
| 46795 | 1148 | Fringe/side/chin trims; high-collar and very limited neck support remain |

Protection is visibly useful on the known object cases, but neither this screen
nor software checks proves every object is excluded. Useful skin can be removed
at the same boundaries. These failure/uncertainty cases are retained; none is
replaced or automatically admitted.

## Verification and limits

All12 revised cases completed. Each passed subset/no-added-support, unchanged
measurement, zero protected alpha, unchanged protected/outside output pixels,
exact neutral identity, and independent alpha-equation/RGB8 rendering checks.
The new tests cover enclosed objects surviving hole filling/blending, a
skin-labelled occluder, retention of facial features, face-only visibility not
erasing neck, explicit protections and unavailable/invalid visibility.
**37 focused tests passed in1.88seconds.** This is not a full-suite run or
scientific validation.

The new package has per-case masks, veto, mapped visibility, float alpha,
demonstration and artifact hashes. Its input ledger verifies the earlier FFHQ
package, original photos and historical pinned sources/manifests unchanged.
Photo attribution remains in the linked original source gallery/ledger.
No photos/models were published. No training admissions, synthetic variants,
target fits, MST labels/calibration or tree fits. ITA-to-MST stays deferred and
retained in the intended method. The submitted proposal and working thesis
drafts were not edited; the user-requested policy change is recorded in the
[panel register](panel-change-register.md), without claiming panel approval.
