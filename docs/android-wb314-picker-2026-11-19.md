# WB314 in the Android photo picker

The picker passes the selected photo and glasses choice to WB314. The app decodes the photo at full size, applies EXIF orientation and makes one 256 × 256 area-resized analysis image. That image feeds both automatic mask generation and feature extraction for the frozen WB314 tree. The renderer maps the selected support to the upright original and exports a PNG at its original dimensions. Protected and outside-support pixels receive no correction. The mask preview shows the analysis-resolution application support.

Choose clear or opaque lenses when appropriate. If the parser detects glasses and the selection is unsure, the app asks for a choice before applying correction. When WB314 selects identity controls, the result says the photo was left unchanged. This describes the controls selected by the model. It does not establish that the input needed no correction.

## Local research build

Install the debug APK and run `scripts/install_android_wb314_research_assets.ps1 -Serial <adb-serial>`. The script checks the eight pinned local files before copying them, then verifies each copy in the app's private directory. It installs no photo fixtures. A debug install without the local assets reports that they are missing. There is no fallback to the older model in the picker.

The APK contains the app code. The WB314 model, mapping, white-balance bank, parser, FaceOcc graph and test photos remain local. This is a research build. Physical-phone latency, memory and broader correction quality remain unqualified.

A later Huawei nova 7i check completed 3072 × 4096 export but failed exact Python parity and protection. [Physical-phone evidence](android-wb314-huawei-check-2026-11-19.md)

## Figma-inspired layout, 20 November 2026

The Android interface follows the researcher-supplied Home, Select, Process and Results screenshots. Home explains local processing and opens the Android photo picker. The selected-photo screen presents the actual image, encoded dimensions and file format. Processing uses an indeterminate progress ring and retains the existing glasses choice. Results show a draggable split and accessible slider, output status, saved dimensions and original-size PNG export through the Android document picker. The split can crop the preview to fit compact displays. The export uses the full image.

The compact API 35 emulator displayed the four screens, accepted the existing protected-glasses choice, moved the comparison divider and saved a PNG through Android's system UI. For the saved adjusted fixture, the resulting 512 × 768 PNG matched the existing Python reference pixel for pixel, including 40,902 pixels changed from the uncorrected input. The updated build passed 18 JVM tests and five emulator tests. This is interface evidence for the frozen research pipeline. Physical-device preservation qualification remains open.

## Glasses prompt, 20 November 2026

The photo picker starts processing with glasses type unknown. When the parser flags possible glasses, the processing screen offers clear lenses or keeping the detected area protected. A choice resumes processing on the selected photo. Images with no glasses flag go directly to the result. The existing clear and protected mask rules are used after the choice.

The API 35 emulator exercised the Android system photo picker, displayed the glasses prompt and reached the result screen after choosing clear lenses. The focused `Wb314GlassesFlowTest` used two saved inputs. It verified that the paused run saved no corrected image, the clear-lenses retry used the identical source digest and original dimensions, and the input with no parser glasses flag completed directly at its original dimensions. Both APKs built, with 18 JVM tests and five emulator tests passing. The test fixtures stayed local.

## Verification on 19 November 2026

The API 35 x86-64 emulator exercised the same URI processing and export methods used by the picker and save screens. It used the two saved 512 × 768 fixtures from the earlier renderer check. Both fixtures were made by integer replication of saved normalized development photos. The masks were generated automatically in this run.

Both cases matched Python on the leaf, the five controls, correction support and all 786,432 exported pixels across the two PNGs. The nonidentity case changed 40,902 pixels and preserved all protected and outside-support pixels exactly. The identity case preserved every input pixel. Both debug APKs built. All 18 JVM tests and five emulator tests passed, including four existing regressions. No physical phone was connected.

To reproduce the focused check, privately stage `adjusted_input.png`, `adjusted_output.png`, `adjusted.bin` and the three equivalent `preserved` files from the earlier parity fixture under `files/wb314_picker_test`. Run `Wb314PickerParityTest` with `wb314PickerFixture=true`. The test uses file URIs through the app repository, so its comparison does not depend on navigating the Android system picker UI. [Reference fixture and renderer check](../android-app/README.md)
