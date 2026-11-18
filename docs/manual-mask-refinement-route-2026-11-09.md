# User-assisted mask refinement route — 9 November 2026

## User decision and implementation

The user chose: “lets just do the manual refinement route”. This explicitly
supersedes the prior fully automatic masking requirement for this optional
review/edit step. The decision-tree and ITA/MST requirements remain. No adviser
or panel approval is inferred and the submitted proposal is unchanged.

The Python desktop demo now offers **Refine mask** in both the normal frontend
and the Python3.13 compatibility frontend used on this machine. The automatic
mask remains the starting point. The user may remove hair/beard/object spill,
add missed skin, or restore the pre-edit selection, with undo and reset.
Correction and facial measurement can be edited separately or together.

This first version opens after a **successful current-mask demo run**. Failed
face/landmark/measurement runs cannot yet be rescued by this editor; legacy mode
is not supported. Do not describe this as a complete pre-inference manual-mask
pipeline, Android delivery or a finished correction model.

## How to use

1. Launch `run_truehue_demo.cmd`, choose a permitted single-face photo and run
   the demo with **Masking: current**.
2. Click **Refine mask**. Green shows the selected area. Start with **Remove**
   and **Both masks** for hair/beard spill; choose the correction or measurement
   view when their intended areas differ.
3. Use **Add skin** for missed visible skin. Protected regions remain locked
   unless the user checks **Allow additions in protected areas**. That is an
   explicit decision to permit changes in those painted pixels; retain eyes,
   hair, frames, objects and clothing unless intentionally correcting an error.
4. Measurement skin is facial skin only; correction may include visible neck.
   Undo reverses the latest stroke. Reset clears this editing session. Restore
   paints back the selection present when this session opened. Cancel keeps
   the existing result. Reopening a refined result starts a new editing session.
5. Click **Apply refinement**, compare the new overlay/result, and save the
   result/report. The original photograph and automatic evidence remain intact.

If the edited measurement has fewer than the existing1000normalized selected
pixels or invalid ITA, application is refused and the editor stays available for
undo/restoration. No stale correction is exported as a successful refinement.
Adding skin in a protected region without the unlock checkbox leaves it unchanged.

## Scientific and model boundary

The edited correction support is blended using the same captured historical
gamma/red/blue controls. No model is rerun or retrained. The edited facial mask
gets newly computed display Lab/ITA statistics and a distinct measurement-contract
identity; those values are **not fed to the historical MST lookup/tree**. The old
model features, MST estimate and control values remain identified as historical.

Thus edits can fix where the trial correction is applied and improve the user's
selected measurement region. They cannot by themselves fix a wrong predicted
correction direction, qualify MST calibration, recover clipped colour or validate
the correction tree. All quality/scientific/admission flags remain false. This
human-assisted workflow must be evaluated as such, separately from all earlier
automatic-mask benchmarks. Do not substitute manual edits into those results.

Future calibration/training on user-refined masks requires actual user edits,
compatible measurement/control contracts, grouped roles and a declared validation
design. Generated tests are not training annotations. No earlier points/patches
are converted into app edits, and no private dataset/final-holdout image is opened
for this implementation.

## Evidence preserved in each edited export

- Original automatic photo, masks, report, correction and alpha retained with
  `automatic_` filenames through subsequent editing revisions.
- Immediate preceding report, explicit brush strokes and base-manifest hash.
- Added/removed measurement/correction counts and explicitly unprotected pixels.
- New measurement/correction/protection masks, alpha, overlays and output, all
  bound in the normal export manifest under a new run identity.

No original export is overwritten. Export membership/hash checks reject stale or
modified inputs, including injected unbound automatic-evidence files. Protected
pixels remain unchanged unless explicitly unlocked by a painted addition;
outside the final alpha the output equals the original image exactly. Manual
edits never silently become an automatically generated mask.

## Verification

New code: shared stdlib brush geometry, worker-side refinement and a shared Tk
editor; both existing frontends are integrated. The older standalone exclusion
prototype stays unchanged. Android and active model assets stay unchanged.

Focused command:

```powershell
venv\Scripts\python.exe -B -m pytest tests/test_manual_refinement.py tests/test_demo_service.py tests/test_demo_current_masking.py tests/test_mask_editor.py tests/test_seamless_blend.py -q -p no:cacheprovider --basetemp=tmp/manual_refinement_checks_v3 --tb=short
```

**33tests pass in5.61seconds.** They exercise immutable originals, added/removed
support, explicit protection unlock, existing controls/MST provenance, stale
payload/tampered export rejection, repeated revisions, brush restore/reset,
measurement failure, generic service re-export history and output/protected-pixel invariants. This is not a full
suite, Android test or photographic quality result.

The actual Python3.13 compatibility window was exercised with a generated256px
fixture: real canvas events, undo/reset, project-Python subprocess application,
new-result display and saved export all passed. No image-model calls were made.
Evidence: `outputs/manual_refinement_gui_check_v2/verification.json`; generated
fixtures and edited output stay under ignored outputs. The initial GUI check
stopped at screenshot capture; its folder is preserved. The completed check
records `ImageGrab: screen grab failed`, so **no window screenshot or visual layout
inspection is claimed**. Runtime interaction/display checks still completed.
No screen-capture bypass or new installation was attempted.

No private-photo inference, dataset acquisition, MST/correction fit, final-holdout
read, contact, upload, commit or push occurred. Existing research artifacts are
preserved. Final8group/24photos remain byte-unread.
