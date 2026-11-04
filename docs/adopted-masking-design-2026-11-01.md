# Adopted masking design

1November2026. User accepted whole-face support with inward edge blending and
explicitly asked to retain strict ITA/MST exclusions. This adopts the method
for continued development, not scientific reliability or a finished model.

**Correction:** filled selected face shape plus retained facial support and
associated visible neck. Hair, features and objects within that face shape are
included, as requested. Explicit protections override correction. Blend only
inward across the union's outer edge, using fixed smoothstep width
max(2,ceil(3%facewidth)). No independent jaw/neck fade or outward spill.

**Measurement:** selected semantic facial skin/nose, with predicted non-skin
classes and hard anatomical eye/brow/mouth regions removed, plus the conservative
nasal-base guard. Neck and correction alpha never supply Lab/ITA/MST features.
The nasal guard excludes nearby nose skin as well; parser/landmark mistakes can
still select occluders or miss actual skin. Exclusion construction checks are
not ground-truth mask approval or proof of reference-lighting quality.

Measurement contract:
`1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7`.
Older lookups/features and prior facial-mask approvals do not automatically
apply. The current calibrated-MST evidence is being rebuilt in one fixed cycle
under the [frozen protocol](nostril-mst-single-cycle-protocol-2026-11-01.md).
No tiny recipe/radius/model-setting trials follow the result.

Face/neck correction previews use illustrative settings, not a reliable learned
model. Current desktop/Android correction models stay unchanged. No final
ten-category MST, independent held-out performance or completed thesis claim
follows from adopting the masks. Beard-specific model work remains on hold.
