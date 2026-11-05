# Object-protected correction: bounded saved-output comparison

5 November2026. User explicitly requests avoiding correction on objects,
superseding the earlier policy that included objects within the facial outline.
Keep normal facial features and associated visible neck; protect predicted
background, glasses, earrings, necklaces, clothing, scalp hair and hats.
Beard has no dedicated parser class and is not silently declared detected.

Use all same12 FFHQ cases from `outputs/ffhq_mask_support_v1/results.json`, with
their saved parser categories, FaceOcc logits/mapping and original correction
support. No new model inference, crops, thresholds or search. Record hashes and
this protocol before mask processing. Keep all failures and originals. Save a
new package, never overwrite the whole-face experiment or its assessments.

Apply a removal-only protection layer AFTER hole filling. Parser classes
0/6/9/15/16/17/18 are protected globally. The inverse-mapped, validity-checked
FaceOcc logit>0 visibility veto applies to the geometric face plus parent
non-neck correction support, including objects misclassified as skin. Neck
outside the face outline is not vetoed just because a face model omits it;
parser/explicit protection applies there. This limitation must remain visible.
Use raw visibility, NOT the measurement mask with eye/brow/mouth/nostril holes.

Recompute inward smoothstep alpha on the revised support with the SAME face
width and demonstration parameters .85/1.05/.95. Pass the hard veto to blending;
never fill the protected holes. Save veto reasons, new masks, exact alpha,
old/new overlays and fixed demonstration. Keep the measurement mask/features
unchanged. Verify new support is a subset, zero protected alpha, unchanged
protected/outside image bytes and exact neutral identity. Tests should include
enclosed objects, misclassified skin occlusion, facial-feature retention and
face-only visibility not erasing neck. Independently replay saved arithmetic.

Inspect all12 boards; specifically inspect glasses/hand29617, head covering29863,
hair48879 and microphone59807. Record missed objects and skin loss rather than
claiming complete protection or selecting good cases. No manual object polygons,
ground-truth claim or new human annotation workload. No skin/MST admission,
variants, target/tree/calibration fitting, model adoption, publication or contacts.
Record this user-requested correction-policy change in the panel register.
