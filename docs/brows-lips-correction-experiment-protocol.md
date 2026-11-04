# Correction-only eyebrows and lips experiment

31October2026. User explicitly requested including eyebrows and lips during
correction while excluding them from ITA/MST assessment. This is an authorized
correction-region experiment, not a measurement/calibration change.

Keep the current facial binary mask and all Lab/ITA/endpoint measurement pixels
exactly unchanged. Preserve existing neck support. Add only parser classes2/3
(brows) and12/13(lips) inside the selected facial-mask bounding rectangle to
correction support. Do not fill the full mouth polygon, add mouth-interior11,
eye4/5, glasses6 or hair17 classes. Honor explicit protected pixels. Predicted
class exclusions are not a guarantee about real eyes/teeth or other objects.
No new model, beard-specific work, training or MST lookup is introduced.

Reuse exactly the21saved face/neck cases, masks, class maps and illustrative
direct-gamma/red/blue settings (.85,1.05,.95). No inference or tuning sweep is
needed. Compare existing face+neck correction support with the optional brows/
lips addition using identical settings. Label outputs operator demonstrations,
not learned correction or evidence of improved color. Pigmented lips and brow
hair need not benefit from skin-derived settings; inspect that tradeoff.

Save measurement masks, feature additions and changed outputs separately.
Check unchanged ITA statistics, unchanged output outside additions relative to
the baseline, excluded classes, identity and original-file immutability. Test
protected pixels and other-face features outside the selected face bounds.
The ordinary preview stays unchanged; provide an explicitly opt-in preview.
No current demo or calibration artifact is switched. Save actual results and
limitations without declaring adoption from visual preference alone.
