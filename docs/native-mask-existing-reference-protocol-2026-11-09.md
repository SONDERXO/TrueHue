# Cached native masks against completed human references — 9 November 2026

The user authorises skin-measurement/labelled-coverage review. Reuse the existing
six point and patch exports; no new annotation request, pixel label, model run,
mask change, threshold choice or calibration fit. This is a reference-evidence
audit, not a new parser comparison or independent validation cohort.

Bind the original six-review manifest, full-source prediction provenance, actual
point/patch exports and patch raster records. Join to the30native-readiness rows
by exact full-source JPEG hash, not by cropped-PNG hash or ID alone. Native crop
reference coordinates map to full-image coordinates by their original saved
bounds, with no resize/warp. Confirm pixel identity of each reference crop against
that exact decoded source slice. Every one of238points and36polygons must remain.

Read the original aligned clean masks and the new native-readiness masks for the
same photos. Keep separate:

- usable measurement: original pipeline outcome is available and a final mask exists;
- diagnostic final mask: exists but may fail the original guard;
- unavailable: no final mask, never borrowed parent/reference support or an
  all-negative successful prediction.

Compare point selection for labelled skin and unwanted material, user patch union
overlap, and paired old/new usable cases. Retain unavailable-point/patch counts
and all six attempts. Existing patches include neck regions and uncertain material
boundaries; preserve them without silently calling this face-only recall. Check
overlapping polygons once, preserve label/patch disagreements and make no dense
precision/recall or physical-colour claim. No user annotation is removed because
it conflicts with a desired outcome.

Independently verify coordinate scoring by both full-frame point lookup and
cropped-mask lookup, and patch overlap by explicit full-frame placement versus
the native reference crop. Verify source, original exports and masks unchanged.
Review all six saved-reference comparison boards, without altering pixels/masks.
No new minimum native area, IoU or colour-error threshold; no fitting/admission.

Use the result to decide what is actually supported. Six exposed deliberately
marked examples cannot validate all30cases, supply additional subjects or repair
missing labelled coverage. Preserve score/condition denominators from the full
30-case preparation. Final8group/24photos byte-unread. No new image-model calls,
downloads, contact, runtime update, upload, commit or push.
