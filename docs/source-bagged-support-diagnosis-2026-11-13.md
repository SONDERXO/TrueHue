# Visible support gaps in source59807: saved-photo diagnosis

13 November 2026. User supplied two A/B/Rscreenshots showing discontinuities on corrected skin and asked for photo analysis. Agent matched the reference against the11saved source thumbnails: **59807**, not39568. Exact saved cases42under and43over match both screenshots; B is output in both. Diagnosis uses only saved exposed256pxRGB/cache categories/support, not raw originals, new segmentation or a new correction prediction.

Visual artifacts: outputs/source_bagged_support_diagnosis_v1/59807_support_board.png; 59807_forehead_detail.png; 59807_right_edge_detail.png; 59807_neck_detail.png; 59807_saved_review_pairs.png. Agent viewed these and source_reference_contact.png. Enlarged crops use nearest-neighbour display only and do not restore native photographic detail. The ad hoc visual boards preceded the final hash/count receipt; do not claim a prospectively frozen experiment.

## What is actually wrong

1. **Upper forehead/hairline:** the correction boundary forms a relatively smooth upper-face cap while visible skin patches extend higher between the fringe. Adjacent cached parser labels are hairclass17. The correction alpha is zero beyond the cap, so these areas retain the distorted input while neighboring skin changes. This is an external coverage limit, not an enclosed hole that the existing hole-fill could repair. Low resolution and wispy hair make exact anatomy uncertain; no new anatomical ground-truth mask is asserted.
2. **Neck/outer skin boundary:** a narrow strip near the neckline lies outside the support. There are128parser-neckclass14pixels outside the saved mask. That is a parser count, not a validated count of missed anatomical skin. The enlarged photograph/overlay supports a real boundary-coverage concern. Fingers by the microphone are outside the face/visible-neck goal; their omission is not itself a requirement to expand to hands/full body.
3. **Transition:** face_width123 gives ceil(.03*123)=4pixel inward feathering. Of19031maskpixels,1679have0<alpha<1. It smooths the selected side only; it cannot correct omitted skin. Enlarging the feather width cannot supply missing support.
4. **Overcoverage also exists:** the whole-face outline includes glasses and part of the microphone. All saved explicit protected pixels are zero for this source. Those objects can change with the face. Blanket dilation/add-all-hair would worsen non-skin inclusion; the repair needs both skin additions and object exclusions.

## What it is not

All9970parser-skinclass1pixels and all1332noseclass10pixels are already inside the correction mask. Adding only parser skin would add no facial skin here. The broad outline also contains1175hair-labelled pixels, showing neither the outline nor the parser is an anatomical truth mask. Forehead completion needs more careful visible-skin support rather than trusting either unconditionally.

Saved reviewed and automatic correction masks are equal for59807; there are no manual-removal pixels and no protection strokes. This source did not lose user brush edits. The associated-ear rule adds0pixels here; the ears are largely obscured, and the existing ear extension does not address forehead/neck gaps. Measurement/ITA/MST were not changed by this diagnosis.

Independent alpha replay from the exact saved binary support matches bit-for-bit. Scalar counts match vectorized per-class counts. All named source/support hashes remain unchanged. Both under/over input packs differ from reference outside the saved mask at all46505outside pixels: distortions affect the full frame, whereas correction is limited to selected face/neck support. Thus missed skin can retain distortion. Hair/background remaining distorted is expected under limited skin-correction scope, not a requirement to correct the entire frame.

## Appropriate next support step

Prepare a separate **correction-only coverage preview for59807**: inspect selective inclusion of visible upper-forehead/neck skin and explicit microphone/non-skin protection at matching scale, keeping measurement, prior manual removals, current supports and all assessed renders immutable. Existing manual refinement is a practical way to represent additions/protection when automatic hair/skin labels are wrong; do not require a new annotation dataset or infer skin from colour alone. No exact new polygon, segmentation algorithm, dilation radius, threshold or runtime change is selected by this diagnosis.

Use a fixed diagnostic control to inspect coverage/transitions rather than reopening the failed ensemble or fitting another model. Any revised support needs its own immutable export/preview, before future separately specified evaluation; it cannot retrospectively repair this candidate's recorded FAIL. No44case mask redo is justified by this one-source diagnosis. A single subject does not establish mask-error prevalence or darker-skin performance.

Model controls remain a separate problem. This source's identity was given gamma.840625 and the cool case also gamma.840625; noticeable changes cannot be assumed to disappear when omitted skin is added. The complete ensemble review found no useful cool outputs and7noticeableidentities. Improving coverage is necessary engineering work, not evidence that this failed predictor becomes acceptable.

Receipt: outputs/source_bagged_support_diagnosis_v1/diagnosis_PRIVATE.json and verification_PRIVATE.json; scripts/record_source_bagged_review_and_support_diagnosis.py. No mask/model/measurement/runtime/Android edits, new fits/predictions, raw originals/final24/olderlocked reads. Approved ears and manual workflow retained; model unfinished/paper paused.
