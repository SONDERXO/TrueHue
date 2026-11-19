# Frozen WB314 single-photo research runner

**Current original-size output:** the runner now applies predicted controls to original decoded pixels and saves the main PNG at original dimensions/aspect ratio. Internal model analysis remains256x256; low-resolution analysis outputs are separately named. Read [original-resolution implementation and proof](wb314-original-resolution-output-2026-11-19.md). This supersedes the256-output limitation and filenames described in the historical implementation checkpoint below. The two existing user-photo predictions were reused to export original-size files without new model inference or fitting; real nonidentity original-resolution appearance and mask quality remain unqualified.

**Later execution checkpoint:** the runner has now completed two full native runs on explicitly user-selected photos. Both outputs exactly preserve the normalized inputs because the existing tree selects identity controls. Read [two-photo native check](wb314-two-photo-native-check-2026-11-19.md). This supersedes the earlier “not yet executed” stopping point below; it does not establish correction benefit or final quality qualification. The runner itself is unchanged.

`scripts/run_wb314_photo.py` connects one explicitly selected local photo to the existing masking service and frozen WB314 correction. Previously, the research predictor required already prepared arrays/masks while the desktop demo used older baseline controls. This new command supplies the missing research entry point without changing that demo or replacing the model under expert review.

## Actual processing path

1. Decode the selected local image using the existing reader. Save its source hash and normalize the whole frame to 256x256 with `INTER_AREA`.
2. Use the existing pinned single-photo service for detection, landmarks, parsing, FaceOcc visibility and facial measurement. Confirm its image exactly matches the normalized input. Build correction support using the existing glasses handling, associated-ear support, protection and blending code.
3. Require valid separate measurement, application alpha and protection arrays before constructing WB314. Unknown glasses remain protected; if glasses are detected and the caller's choice is uncertain, stop before prediction and request an explicit clear/opaque choice. There is no automatic glasses-type classifier.
4. Convert BGR to RGB explicitly and call the unchanged `WB314WithHeadroomAdvisory`. Export the unchanged primary result and a separately named candidate when available. Check input immutability, protected/outside pixels, primary-policy identity and source immutability before exporting.
5. Save masks, alpha, controls, 314 features, the report and an artifact-hash manifest. Failed stages record a failure and raise; they never fall back to historical controls. Existing output folders cannot be overwritten.

No new mask rule, model fit, threshold, source allocation, source cohort, app mode or dependency was added. Official MST category labels are not inputs. The existing predictor's development MST feature remains unvalidated. This is a software connection, not a quality improvement established by new photographs.

## Use

Run from the project root with the existing local virtual environment and already installed model assets:

```powershell
.\venv\Scripts\python.exe scripts/run_wb314_photo.py --source "C:\path\to\permitted-photo.jpg" --output "outputs\wb314-my-photo-001" --glasses opaque
```

Choose `clear` for known transparent glasses, `opaque` for known sunglasses/protection, or `uncertain` when unknown. Use only a permitted photo you explicitly select. The command does not scan datasets, choose an example, download assets or change the source. The output directory must be new. It contains local photo material and reports and must not be published to the public repository.

`primary_correction.png` is the main result. `separate_headroom_candidate.png` is an explicitly separate alternative, not an automatic replacement or an independently accepted improvement. Both remain 256x256; there is no original-resolution mask/render adapter or new HD detail. Check `report.json` and `manifest.json` before using a successful export. A folder with a failed report is not a valid correction result, even if intermediate diagnostic files exist.

## Completed verification

- **15 generated integration tests passed in 10.30s**, with one pre-existing NumPy import deprecation warning. These cover area normalization and channel order, distinct primary/alternative files, hash-bound export, output-folder preservation, mask failure before model construction, invalid inputs, source/mask service consistency, uncertain-glasses refusal, unavailable advisories and rejection of changed protection, mutated inputs or changed primary policy.
- The first attempt had 14 setup errors because the default Windows temporary directory was inaccessible. No application tests ran in that attempt. The rerun used a new workspace-local temporary directory; production code did not change in response to the permission failure.
- CLI help/import succeeds. All **34 existing mask dependency hashes** and the existing isolated FaceOcc executable are present and verified without inference.
- Seven existing predictor/masking/demo modules match their committed source after normalizing line endings. Every artifact in the released expert upload package retains its recorded hash.
- Frozen model SHA remains `7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f`, with no new fit. No trained correction calls, mask inference or new photographic inputs were used for this implementation check.

Local receipts: `outputs/wb314_photo_runner_integration_v1/`, including the initial setup failure, captured test output, final summary and source bindings. Tests substitute generated mask-service and predictor outputs; checking installed dependencies does not mean the native photo pipeline was executed.

## Stopping point and limits

The research file-to-mask-to-correction entry point is implemented and its glue is tested. **The complete native path has not yet been executed on a newly selected photograph.** Automatic mask accuracy, correction necessity/preservation on normal photos, independent final MST evaluation, actual expert appraisal and device qualification remain incomplete. Neither a finished model nor a completed real-photo integration qualification is claimed.

Keep the expert round's images, model and questionnaire fixed during collection. No new photographic study, guard variant, retraining or closed-study restart is selected by this implementation. The desktop and Android defaults are unchanged. Both earlier headroom parity screens remain failed, and retaining the primary result retains its earlier highlight behaviour. Future refinements must identify their actual trigger and be tracked as a different model/image version.
