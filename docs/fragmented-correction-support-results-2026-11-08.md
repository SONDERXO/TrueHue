# Where facial correction coverage is lost

8 November 2026. Four saved conditions from two originals; no new inference or fit.

**The main loss comes from the parser labelling locations inside the geometric face as background.** The correction pipeline then treats those locations as protected. Face visibility removes additional areas, but is not the main cause in these cases.

## Saved-stage evidence

| Condition | Geometric face pixels | Retained for correction | Background-labelled inside face | Removed by semantics only | Visibility only | Both |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Development warm + overexposure | 18,005 | 14,473 | 3,406 | 3,481 | 44 | 7 |
| Later overexposure | 14,784 | 4,245 | 9,912 | 8,721 | 588 | 1,230 |
| Later cool + overexposure | 14,952 | 3,285 | 11,305 | 10,013 | 274 | 1,380 |
| Later warm + overexposure | 14,511 | 3,880 | 9,970 | 8,122 | 635 | 1,874 |

Counts are on the 256-pixel processing frame, not native image pixels or independent samples. The three later conditions reuse one original. Background labels cover approximately 66–76% of the geometric face in those conditions. These percentages describe predicted labels within a geometric region, not verified skin error rates.

The geometric whole-face builder initially includes the outline independently of the fragmented measurement mask. Thus the final forehead-only shape is not simply caused by reusing a measurement mask as correction support. The later semantic hard veto recreates much of the same missing coverage. The excluded semantic classes here are almost entirely background, with small predicted-hair contributions; none of these saved maps contains a glasses-class label. That does not mean the glasses are absent or correctly handled.

Visual review shows background-labelled internal facial regions and substantial lower-face omissions. The visibility maps often retain more of the face than the final support. Reconstructed support and protection exactly match the saved outputs, so no inconsistency in stage composition was found. This does not establish correct parser preprocessing or scientific mask validity.

## Next recommended check

Audit the **existing parser input/output contract** before changing the mask policy: checkpoint architecture and class order, actual channel order and normalisation, resizing/crop alignment, and conversion from model output to saved labels. Compare the code with locally available model provenance/documentation and the saved preparation traces. Use cached artifacts first; no new model inference, dataset search or annotation is part of that check.

The trace identifies where coverage disappears, but not whether the cause is a model limitation, preprocessing mismatch or another upstream issue. Do not remove background protection, fill the holes, dilate the mask or infer clear lenses automatically. Those changes could admit objects, frames or occlusions. If the contract is correct, propose a separately bounded parser-development intervention with explicit protection checks rather than another correction-gate fit.

## Verification and scope

Script 644 rebuilt the whole-face support, continuity and object/visibility protection using saved categories, landmarks and visibility. All four final masks and protected maps exactly match their originals. Disjoint semantic-only/visibility-only/both partitions reconcile, class counts reconcile, and source hashes pass. Viewed all four stage boards. Private outputs: `outputs/fragmented_correction_support_trace_v1`.

No masks or runtime behaviour changed. Zero fits, model inference, new photos or annotations. The final 24-photo holdout remains byte-unread and the correction candidate remains unadopted. Existing research-use/privacy restrictions apply.
