# Visible-neck support: fixed implementation and checks

The user explicitly retained visible-neck correction and authorized proceeding
on31October2026. This is a scope expansion from the facial-only proposal, not
an already completed requirement. No adviser-request gate applies. Beard-specific
models remain held. Neither existing demo changes during this candidate work.

Facial binary masks remain exact ITA/MST measurement support. A separate neck
mask joins them only for correction. Reuse the existing local19-class parser;
only its neck class14 can supply new pixels. Associate neck components with the
selected lower face using a fixed geometry rule: a10%-facial-width attachment
radius, x bounds equal to the face-mask bounds, y from facial midpoint through
one face-mask height below its bottom. Keep only class14 components intersecting
the attachment band. These are engineering association rules, not validated
anatomy or identity. No post-result geometry search is planned.

Never fill holes or add generic skin, torso, shoulders, clothing, hair, necklace,
ears or background classes as neck. Preserve explicitly protected pixels. If
no neck component qualifies, keep face-only correction and record unavailable
neck; do not infer that this proves the person has no visible neck. Exactly-one-
face is required upstream. Parser mistakes, touching people and occluders can
still defeat the association; predicted-class exclusions are not ground truth.

Use21 already exposed frames: six accepted semantic reference masks (training
role) and the15 fixed per-subject MST diagnostics (mapping-development role).
No new source selection, reserved evaluation images, labels or training fits.
Existing category maps are reused when available. Save independent face, neck,
combined masks, source/code/model hashes, status and read-only previews.

Show a fixed illustrative direct-gamma/gain setting (.85,1.05,.95) on face-only
and face+neck support, labelled as an operator demonstration, not a learned
prediction or quality improvement. Use identical settings in both comparisons;
identity settings must reproduce input exactly, and pixels outside combined
support must stay exact. Natural face/neck lighting/color differences remain.
Do not score these real photos as aligned neutral-reference reconstruction.

Check facial-mask bytes and Lab/ITA statistics remain exact. Keep parser/mask
failure and neck-unavailable counts. Synthetic boundary tests cover exclusions,
no-neck, disconnected unrelated regions, explicit veto, multiple faces and
outside-pixel preservation. Inspect all saved contact sheets. Do not tune on
this cohort or claim complete neck coverage from a working preview.
