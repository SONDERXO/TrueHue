# WB314 in the Android photo picker

The picker passes the selected photo and glasses choice to WB314. The app decodes the photo at full size, applies EXIF orientation and makes one 256 × 256 area-resized analysis image. That image feeds both automatic mask generation and feature extraction for the frozen WB314 tree. The renderer maps the selected support to the upright original and exports a PNG at its original dimensions. Protected and outside-support pixels receive no correction. The mask preview shows the analysis-resolution application support.

Choose clear or opaque lenses when appropriate. If the parser detects glasses and the selection is unsure, the app asks for a choice before applying correction. When WB314 selects identity controls, the result says the photo was left unchanged. This describes the controls selected by the model. It does not establish that the input needed no correction.

## Local research build

Install the debug APK and run `scripts/install_android_wb314_research_assets.ps1 -Serial <adb-serial>`. The script checks the eight pinned local files before copying them, then verifies each copy in the app's private directory. It installs no photo fixtures. A debug install without the local assets reports that they are missing. There is no fallback to the older model in the picker.

The APK contains the app code. The WB314 model, mapping, white-balance bank, parser, FaceOcc graph and test photos remain local. This is a research build. Physical-phone latency, memory and broader correction quality remain unqualified.

## Verification on 19 November 2026

The API 35 x86-64 emulator exercised the same URI processing and export methods used by the picker and save screens. It used the two saved 512 × 768 fixtures from the earlier renderer check. Both fixtures were made by integer replication of saved normalized development photos. The masks were generated automatically in this run.

Both cases matched Python on the leaf, the five controls, correction support and all 786,432 exported pixels across the two PNGs. The nonidentity case changed 40,902 pixels and preserved all protected and outside-support pixels exactly. The identity case preserved every input pixel. Both debug APKs built. All 18 JVM tests and five emulator tests passed, including four existing regressions. No physical phone was connected.

To reproduce the focused check, privately stage `adjusted_input.png`, `adjusted_output.png`, `adjusted.bin` and the three equivalent `preserved` files from the earlier parity fixture under `files/wb314_picker_test`. Run `Wb314PickerParityTest` with `wb314PickerFixture=true`. The test uses file URIs through the app repository, so its comparison does not depend on navigating the Android system picker UI. [Reference fixture and renderer check](../android-app/README.md)
