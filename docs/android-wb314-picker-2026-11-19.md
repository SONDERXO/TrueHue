# WB314 in the Android photo picker

The picker passes the selected photo and glasses choice to WB314. The app decodes the photo at full size, applies EXIF orientation and makes one 256 × 256 area-resized analysis image. That image feeds both automatic mask generation and feature extraction for the frozen WB314 tree. The renderer maps the selected support to the upright original and exports a PNG at its original dimensions. Protected and outside-support pixels receive no correction. The mask preview shows the analysis-resolution application support.

Choose clear or opaque lenses when appropriate. If the parser detects glasses and the selection is unsure, the app asks for a choice before applying correction. When WB314 selects identity controls, Results opens with **Photo kept unchanged** and explains that TrueHue kept the original brightness and colour. It shows one full-photo preview and offers **Try another photo**. **Save photo** is available on corrected results. The message reports the model’s decision on that photo.

In the initial 21 November unchanged-message build, the API 35 emulator showed the explanation and full photo for a known identity case. All 18 JVM tests passed. The build installed and opened on the Huawei with all eight model assets verified. The later button change was checked on both unchanged and corrected emulator results, including opening the save dialog for a corrected photo. The updated build installed and opened on the Huawei.

## Local research build

Install the debug APK and run `scripts/install_android_wb314_research_assets.ps1 -Serial <adb-serial>`. The script checks the eight pinned local files before copying them, then verifies each copy in the app's private directory. It installs no photo fixtures. A debug install without the local assets reports that they are missing. There is no fallback to the older model in the picker.

The APK contains the app code. The WB314 model, mapping, white-balance bank, parser, FaceOcc graph and test photos remain local. This is a research build. Physical-phone latency, memory and broader correction quality remain unqualified.

A later Huawei nova 7i check completed 3072 × 4096 export but failed exact Python parity and protection. [Physical-phone evidence](android-wb314-huawei-check-2026-11-19.md)

## Figma-inspired layout, 20 November 2026

The Android interface follows the researcher-supplied Home, Select, Process and Results screenshots. The selected-photo screen presents the actual image, encoded dimensions and file format. Results show the entire upright image at its original aspect ratio, with a draggable split and accessible slider. **Save photo** exports an original-size PNG through the Android document picker. The Results page omits file details and diagnostic controls.

The 21 November update adds a teal native launch screen and makes Home's photo picker a single large tappable card. During correction, the displayed estimate moves from 1% through values below 100%, with status text tied to the actual processing stage. It reaches 100% after a successful result is ready and then opens Results. On the API 35 emulator, a cold launch showed the branded screen, the card opened the gallery, and a selected photo showed moving percentages followed by 100% and Results. Eighteen JVM and seven emulator tests passed.

The compact API 35 emulator displayed the four screens, accepted the existing protected-glasses choice, moved the comparison divider and saved a PNG through Android's system UI. For the saved adjusted fixture, the resulting 512 × 768 PNG matched the existing Python reference pixel for pixel, including 40,902 pixels changed from the uncorrected input. The updated build passed 18 JVM tests and five emulator tests. This is interface evidence for the frozen research pipeline. Physical-device preservation qualification remains open.

After the full-photo layout revision, the emulator showed the processing percentage and status text, fit the 512 × 768 portrait into a 205 × 308 comparison frame and saved it through **Save photo**. The saved PNG again matched the Python reference at 512 × 768. Eighteen JVM tests and five emulator tests passed, including stage checks on the glasses pause and successful correction paths.

## Glasses prompt, 20 November 2026

The photo picker starts processing with glasses type unknown. Only a parser glasses label inside the detected face can trigger the question. The screen offers **No glasses**, **Clear glasses**, and **Tinted glasses or unsure**. Each choice resumes the selected photo. **No glasses** dismisses the question and retains the conservative protection for any disputed pixels. A false label inside the face may still prompt.

The processing screen shows plain-language guidance for cases such as unclear facial features, insufficient visible skin and an unreadable photo. **Choose another photo** opens the system picker directly. Technical error details remain in the private run record.

The updated build passed 18 JVM and seven emulator tests. Focused tests checked that a background label does not prompt, both **Clear glasses** and **No glasses** resume the same photo at its original dimensions, and technical exception text is restricted to the private report.

The initial API 35 emulator check exercised the Android system photo picker, displayed the glasses prompt and reached the result screen after choosing clear lenses. The focused `Wb314GlassesFlowTest` used two saved inputs. It verified that the paused run saved no corrected image, the clear-lenses retry used the identical source digest and original dimensions, and the input with no parser glasses flag completed directly at its original dimensions. Both APKs built, with 18 JVM tests and five emulator tests passing. The test fixtures stayed local.

## Verification on 19 November 2026

The API 35 x86-64 emulator exercised the same URI processing and export methods used by the picker and save screens. It used the two saved 512 × 768 fixtures from the earlier renderer check. Both fixtures were made by integer replication of saved normalized development photos. The masks were generated automatically in this run.

Both cases matched Python on the leaf, the five controls, correction support and all 786,432 exported pixels across the two PNGs. The nonidentity case changed 40,902 pixels and preserved all protected and outside-support pixels exactly. The identity case preserved every input pixel. Both debug APKs built. All 18 JVM tests and five emulator tests passed, including four existing regressions. No physical phone was connected.

To reproduce the focused check, privately stage `adjusted_input.png`, `adjusted_output.png`, `adjusted.bin` and the three equivalent `preserved` files from the earlier parity fixture under `files/wb314_picker_test`. Run `Wb314PickerParityTest` with `wb314PickerFixture=true`. The test uses file URIs through the app repository, so its comparison does not depend on navigating the Android system picker UI. [Reference fixture and renderer check](../android-app/README.md)
