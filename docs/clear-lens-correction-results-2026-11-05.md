# Clear lenses receive correction; approximate rims remain protected

5November2026. User clarified that transparent prescription lenses should not
leave uncorrected patches over the eyes. Correction should pass through the
lenses while avoiding frames/rims. Sunglasses remain opaque objects.

**[Open the comparison gallery](../outputs/ffhq_clear_lens_correction_v1/review.html).**
Panels: original; previous whole-glasses exclusion; revised correction green;
lens interiors green/approximate rims pink; fixed illustrative correction.

## Implementation and limits

The parser has one glasses class, not separate lens/frame masks. The new
`src/skin_masking/clear_lens_correction.py` requires an explicit transparent-glasses
designation. It fills enclosed holes in the glasses envelope, retains a fixed
two-pixel inner boundary band as approximate rims/bridge/arms on the existing
256px frame, and restores correction through the remaining lens interior.
Visible eyes are included. The override is confined to original face/correction
support and facial skin/feature/glasses labels. Other object classes and explicit
protections retain precedence. Measurement masks/features are unchanged.

This is **an approximation, not exact frame segmentation**. Thin wires inside
lenses and reflections can be missed; some skin can be protected by the band.
There is no automatic glasses-type classifier or prescription verification.
Opaque/unknown glasses keep whole-glasses protection. The
[protocol](clear-lens-correction-protocol-2026-11-05.md) fixed the rule before
processing; no width/threshold sweep, manual frame tracing or new model was used.

## Bounded results

All same12 cases were retained. From the previously inspected originals, the
assistant explicitly designated16061 and59807 as clear-lens examples;29617 stays
sunglasses. These designations are not training labels. All other10 correction
masks remain byte-for-byte unchanged.

Both revised clear-lens boards were inspected. Correction now covers the visible
eye/lens interiors while approximate rims and bridges stay protected. No dense
frame annotations or pixel accuracy claim follows.

| Case | Restored pixels | Lens pixels with positive alpha | At full alpha |
|---|---:|---:|---:|
| 16061 | 2109 | 2109 | 1147 |
| 59807 | 2196 | 2196 | 1426 |

Remaining lens-interior pixels blend inward near protected rims. These are mask
counts, not optical calibration or correct-colour scores. Bright reflections
remain. Demonstration parameters .85/1.05/.95 are illustrative, not predictions.

All12 passed original-support subset, lens-only restoration, unchanged measurement,
zero protected/rim alpha, unchanged protected/outside pixels, exact neutral
identity, and independent alpha/RGB8 checks. **18 focused tests passed in0.57s**,
covering visible eye correction, rims/bridge, opaque glasses, unavailable lens
interiors and explicit protection precedence; not a full-suite run.

Script418 saves masks, lens/rim regions, veto, float alpha, boards, reports and
hashes in `outputs/ffhq_clear_lens_correction_v1/`. Its input ledger verifies the
previous FFHQ/object-protection packages, original photos and pinned historical
sources/manifests unchanged. Inherited semantic/visibility removal counters in
reports describe the baseline veto before lens restoration; restored/total
correction counts describe the revised mask. Attribution remains in the gallery.

No new inference/photos, variants, target/tree/MST fits, admissions, publication,
contacts or runtime switch. Historical350 launchers and desktop/Android defaults
are unchanged. Measurement through lenses is not newly admitted. The submitted
proposal and working thesis drafts are untouched; the user-requested refinement
is recorded in the [panel register](panel-change-register.md), not panel-approved.
