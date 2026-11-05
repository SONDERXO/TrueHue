# Reusable correction preview with an explicit glasses choice

5November2026. The object-protected and clear-lens candidates now share one
reusable preview API and command-line tool. They no longer require hard-coded
FFHQ IDs to choose clear lenses. **Glasses type is selected explicitly, not
automatically classified.** This is a development tool, not a new final-app
interaction requirement or a trained correction system.

[Open the twelve-case regression gallery](../outputs/reusable_correction_preview_v1/review.html).

## Use it on a selected photo

From the project root, with the existing local models and environments:

```powershell
.\run_object_protected_preview.cmd "C:\path\photo.jpg" clear
```

Choose `clear` for visibly transparent lenses, `opaque` for sunglasses, or
`uncertain` when unsure. Dragging a photo onto the new launcher defaults to
`uncertain`. It prints the saved gallery path; open that HTML file to inspect
the result. The launcher does not automatically open another application.
Clear lenses retain the current approximate rim/bridge protection. Opaque and
uncertain handling keep the whole predicted glasses region protected.

The equivalent command is:

```powershell
venv\Scripts\python.exe -B scripts/419_preview_object_protected_face.py --image "C:\path\photo.jpg" --glasses clear
```

If glasses are predicted and the choice is uncertain, the report/gallery says
`needs_glasses_choice`. This prevents an unresolved glasses mask being mistaken
for a finished selection. If the parser misses glasses, that flag cannot detect
the error; absence of its glasses class is not validated absence of glasses.
Missing required FaceOcc visibility fails explicitly, with no all-visible fallback.

Each run uses a new ignored output folder. Plans, source/dependency hashes and
failure reports are retained. The raw-photo path uses the existing detector,
landmark helper and parser, then one CPU FaceOcc pass in the existing isolated
environment. No downloads/installs occur; unavailable dependencies fail visibly.
The main environment does not import PyTorch. Inference requests are bound to
input hashes and refuse a repeat forward after a partial or completed attempt.

For a saved example with zero new inference:

```powershell
venv\Scripts\python.exe -B scripts/419_preview_object_protected_face.py --saved-case 16061 --glasses clear
```

## What was verified

Under the [recorded protocol](reusable-correction-preview-protocol-2026-11-05.md),
script421 exercised the shared API on all12 saved FFHQ cases. All12 correction
masks, float alpha arrays and RGB8 demonstrations exactly match script418.
Glasses uncertainty was also exercised on29617/16061/59807: each flags a required
choice and produces the same protected mask as opaque handling. Prior clear
designations are retained as assistant observations, not new user answers or
automatic classifications.

The real CLI was exercised with saved16061/clear and29617/default-uncertain;
both generated reports/galleries with the expected status. The clear case's
saved board was visually inspected.51 focused tests passed in2.43seconds,
including mode validation, missing visibility, explicit protections, clear lens
restoration, uncertainty, measurement independence and the existing mask/service
checks. This is not a full-suite run. The Windows launcher and the raw-photo
model-inference branch were not executed in this validation; their new-photo
behaviour is not claimed experimentally verified. No new photo or model pass
was needed for the saved-input regression.

Evidence is under `outputs/reusable_correction_preview_v1/`, with artifact hashes
and a dependency ledger preserving all previous packages, originals and pinned
historical sources/manifests. CLI smoke outputs are
`outputs/object_protected_preview_e3d0d1437afa/` and
`outputs/object_protected_preview_e948b3bf685b/`. No actual browser-render test
is claimed. No photographs or models were published.

## Remaining mask decisions

The per-case [remaining-issue ledger](../outputs/reusable_correction_preview_v1/results.json)
retains the earlier observations rather than inventing new annotations or
passing thresholds. Correction object protection does not fix the beard/hair
pixels still selected for measurement. Missing/fragmentary neck support,
reflections, approximate rims and possible loss of skin remain. In particular:

- 54632/29863: beard/moustache measurement contamination remains unresolved.
- 48879: possible hair selection in measurement remains unresolved.
- 52445: no associated neck;32685/46795: small uncertain neck fragments.
- 16061/59807: clear-lens correction is supported by explicit choice, but exact
  frame segmentation and measurement through lenses remain unverified.

These are retained concerns, not a new automatic rejection/admission scheme.
All12 remain unadmitted. Next resolve source/measurement/neck eligibility before
creating photographic training examples. No new tuning, admission or training
batch is activated here. Automatic glasses classification remains unresolved;
this explicit development choice must not be reported as solving that research
problem. ITA-to-MST remains deferred and retained in the eventual method.

The new API is `src/skin_masking/correction_preview.py`; CLI419 and isolated
runner420 compose unchanged pinned masks. Historical350 launchers, desktop and
Android defaults are unchanged. No MST/target/tree fitting, variants, human
annotation task, contacts or submitted/working thesis edits. The development
workflow is recorded in the [panel register](panel-change-register.md), without
claiming panel approval.
