# WB314 in the Android photo picker

The picker passes the selected photo and glasses choice to WB314. The app decodes the photo at full size, applies EXIF orientation and makes one 256 × 256 area-resized analysis image. That image feeds both automatic mask generation and feature extraction for the frozen WB314 tree. The renderer maps the selected support to the upright original and exports a PNG at its original dimensions. Protected and outside-support pixels receive no correction. The mask preview shows the analysis-resolution application support.

Choose clear or opaque lenses when appropriate. If the parser detects glasses and the selection is unsure, the app asks for a choice before applying correction. When WB314 selects identity controls, Results opens with **Photo kept unchanged** and explains that TrueHue kept the original brightness and colour. It shows one full-photo preview and offers **Try another photo**. **Save photo** is available on corrected results. The message reports the model’s decision on that photo.

In the initial 21 November unchanged-message build, the API 35 emulator showed the explanation and full photo for a known identity case. All 18 JVM tests passed. The build installed and opened on the Huawei with all eight model assets verified. The later button change was checked on both unchanged and corrected emulator results, including opening the save dialog for a corrected photo. The updated build installed and opened on the Huawei.

## Local research build

For the Huawei picker test build, run `gradlew.bat -Pwb314PickerTest=true :app:assembleDebug` from `android-app/`. It appears as **TrueHue Picker Test** and installs alongside the usual app under `com.example.skintonecorrection.pickertest`. Provision its pinned local assets with `scripts/install_android_wb314_research_assets.ps1 -Serial <adb-serial> -PickerTest` from the repository root.

The test build enables the [widespread-brightness limit](wb314-widespread-exposure-2026-11-21.md) and [FaceOcc application visibility margin](android-wb314-huawei-boundary-protection-2026-11-21.md) in the normal picker. The build flag defaults to off for regular debug builds and is off in release builds.

On 21 November the separate APK installed on the Huawei, and all eight provisioned assets matched their pinned hashes. The usual APK also matched its pre-install checksum. All 18 JVM tests passed. One Huawei instrumentation test opened all three saved fixtures as local URIs through the same repository used by the picker. It ran the normal decoder and correction pipeline, wrote results and invoked the app's export method for both corrected photos. The check exercised the processing and export code directly.

| Saved fixture | Output dimensions | Result | Pixels changed outside saved support | Newly clipped pixels |
| --- | --- | --- | ---: | ---: |
| Previous boundary failure | 3072 × 4096 | Corrected and exported | 0 | 126,756 |
| Identity | 512 × 768 | Exact pixel match and unchanged result state | 0 | 0 |
| Bright portrait | 3000 × 4000 | Corrected and exported | 0 | 213 |

All three retained the expected raw tree controls. The boundary fixture also activated the facial luminance limit with both fixes enabled, reducing newly clipped pixels from 470,669 in the earlier boundary-only preview to 126,756. The bright portrait used the facial RGB limit and reproduced the earlier 213-pixel clipping count. Exact agreement between Huawei and Python masks remains open. The expert development round remains bound to its original WB314 release.

### RGB check on the luminance limit

A later 3000 × 4000 phone photo remained too bright in the picker test build. The same raw WB314 exposure gain of 1.414× that had been limited to 1.005× on the approved portrait was limited to 1.350× on the later shot. The latter used the luminance limit, which could leave individual RGB channels clipped.

Picker test version `1.0-wb314-picker-test.2` checks the proposed luminance gain against the same original-resolution pixels that triggered the widespread-clipping rule. If any of those pixels would still clip in an RGB channel, the existing RGB search finds a lower exposure gain. The one-quarter trigger, raw tree controls, colour controls, and FaceOcc boundary margin are retained. The research preview keeps its recorded rule and the expert development release keeps its frozen outputs.

On the Huawei, the standard processing and export path reproduced the reported photo's decoded input, saved application mask and raw controls. The new limit selected **1.005×** exposure. Newly clipped pixels over the full frame fell from **425,471 to 46,380**. The PNG remained 3000 × 4000, with zero edits outside the saved support. The researcher subsequently approved the appearance of this one photo in picker test v2.

All 18 JVM tests and both Huawei instrumentation checks passed. The three saved fixtures retained their dimensions, raw controls and zero edits outside saved support. The approved bright portrait and identity fixture produced byte-identical correction PNGs to picker test v1. The previous boundary failure used the lower RGB limit and newly clipped pixels fell from 126,756 to 33,193. The Huawei's installed test APK matched the local build checksum, and the usual APK matched its earlier checksum. Only aggregate results are recorded here.

The installed and local v2 APKs were reverified at SHA-256 `fdb6bca7b46582d9771aae995ab3b6fdce8b838e368910c00e1460a082f956fd`. All eight provisioned assets matched their pins, including the original WB314 tree (`7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f`). This build is the candidate to carry into final evaluation preparation. The appearance approval supplies one development observation. The final cohort, protocol, mapping validation and app qualification remain open under the [two-round completion plan](wb314-completion-blockers-and-two-round-plan-2026-11-19.md).

### Jawline gap diagnosis

The Huawei trace reproduced both saved correction masks exactly. A diagnostic five-pixel closing kernel identified 127 and 40 analysis-resolution pixels in small holes or notches across the two masks. These counts include the whole mask. The earlier visibility cutoff recovered zero and one of those pixels. The parser indicated skin or neck at 78 and 33 gap pixels, of which the earlier FaceOcc cutoff already rejected 78 and 31. The parser indicated background, hair or clothing at the other 49 and seven gap pixels. This explains why a blanket expansion or reversal of the newer visibility margin would be poorly targeted.

A candidate repair can look for short gaps between corrected facial and neck skin near the jaw. It would need independent evidence that the current visibility rejection is wrong before restoring those pixels, using parser labels as one cue. Keep the collar, hair and other protected regions excluded. Check the two reported cases and an occlusion control before selecting a new mask policy. This trace tested the existing mask logic and the two visibility cutoffs. The installed v2 APK matched its previous hash and the production mask rules were unchanged.

### Bounded ear and neck coverage test

The separate TrueHue Edge Test build enables a small parser-constrained expansion around existing ear and neck coverage and closes short gaps beside accepted face and neck areas. The installed v2 candidate and the expert development release retain their original mask policy. Build the separate experiment with `-Pwb314PickerTest=true -Pwb314EdgeTest=true` and provision with `-EdgeTest`.

All 18 JVM tests passed. Huawei processing and export succeeded for seven saved cases with the same tree controls, effective controls and dimensions as v2. Two unchanged inputs stayed pixel-identical. The reported repeat added 29 analysis pixels, comprising 2 face, 4 ear and 23 neck pixels. It added 18 newly clipped output pixels relative to v2. The earlier jawline examples also gained localized coverage.

**Preservation regression.** The expansion changed 12,096 pixels outside the saved reference support on the earlier boundary fixture and 2,405 on the approved brightness fixture. Both counts were zero with picker v2. The experiment remains a separate test build and is unsuitable as the default. The checks used saved URIs and the same app export code. They leave future-photo generalization and the reported ear boundary open.

A separate offline preview strengthened partial correction only on parser-labelled skin, ear and neck pixels within the saved support. On the three saved reported cases it preserved all outside-support and protected pixels, with original exposure and colour controls. The boundary remained visible on the latest photo, and two photos gained 9 and 46 newly clipped pixels. This preview did not resolve the issue and was not adopted. For this failure, a future repair needs better evidence of the actual skin boundary where visibility and parser labels disagree.

One follow-up offline preview required a candidate skin pixel to lie between accepted skin pixels of a compatible class and similar Lab colour on both sides. The three reported photos gained 36, 57 and 37 analysis pixels respectively. On the repeat photo, four pixels were labelled ear and 18 neck. Each preview preserved output outside its candidate region and the remaining vetoes, and retained the previous pixel values where the preview introduced clipping. The remaining visible outer-ear boundary on the repeat photo fell outside this interior-gap rule. The preview stopped at the reported cases and did not advance to the preservation regression fixtures or the Android picker.

The researcher reported that the jaw concern was resolved in the preview, with the latest photo still requiring work. Its trace showed that only four excluded ear-labelled cells were within three analysis pixels of the accepted ear. A disjoint ear-labelled patch appeared on the background, and the cells immediately outside the real ear were mostly labelled hair. A separate original-resolution ear-rim preview extended at most one analysis cell from matching connected ear skin. It changed 10,802 pixels, including 9,830 classified as hair at analysis resolution, and introduced no clipping or edits outside its ear band. The candidate was inspected locally and remains a case-specific preview pending appearance and protection checks.

The researcher then reported that the ear-only preview looked similar and that the missed coverage affected the correction outline more generally. A 768-pixel image-guided segmentation preview tested a narrow band around the full outline. Visual inspection of its added-support overlay showed coverage spilling across the forehead hairline and onto the door next to the cheek. The candidate was rejected for the picker. It preserved the original dimensions and did not add clipping, but those checks cannot establish correct support. The installed v2 and approved local jaw preview were left intact.

A closer-crop diagnostic ran the same pinned parser on a 512-pixel crop located automatically from the saved application support. It allowed nearby connected skin proposals on a finer grid while retaining the saved WB314 controls. The three reported photos produced local previews. On the latest photo the added-support overlay still followed part of the door beside the cheek and crossed the hairline. A separate proposal-only check seeded with the two earlier saved reference masks proposed 1,120 and 640 cells beyond those masks. These counts describe proposed support, without a new on-device render. The crop alone did not resolve the protection conflict and was not integrated.

A separate screening pass required agreement with the existing MediaPipe selfie material model before accepting closer-crop additions. On the repeat photo the proposal shrank from 1,349 to 801 cells on the 512-square grid, but the overlay still showed suspected hairline and cheek-background edits and incomplete visible neck coverage. The earlier saved-reference checks still proposed 771 and 388 cells beyond the permitted areas. The candidate failed this offline screen. No app code, expert material or tree was changed for this pass.

On 22 November an offline preview used a wider inward fade, blending the saved correction toward the original near the existing support boundary. Across the three reported photos, the mean adjacent-pixel step in the correction's luminance contribution dropped by approximately 17–23% in the boundary neighbourhood. Pixels outside the saved support, protected pixels and the core correction stayed identical. The preview retained original dimensions and introduced no clipping in previously non-clipped pixels. This is an appearance mitigation that leaves the same skin outside support. It has not been selected for the Android picker.

The researcher approved the softer appearance and reported that Photo 3 still showed jaw gaps because the soft preview used the original picker support. Its local comparison now combines the prior 37-cell jaw repair with one continuous original-resolution fade. Any remaining veto and pixels outside the revised support stayed unchanged. This jaw combination remains local to Photo 3.

The separate TrueHue Soft Edge Test APK implements the softer inward fade through the normal picker. It blends the existing renderer output toward the input after calculating frozen WB314 controls, so it cannot expand support. Build with `-Pwb314PickerTest=true -Pwb314SoftEdgeTest=true` and provision with `-SoftEdgeTest`. The scope is deliberately separate from the failed coverage expansion. All 20 JVM tests passed.

On 22 November the APK was installed on the Huawei alongside Picker Test v2. The installed APK and all eight assets passed checksum verification. One instrumented test exercised the picker repository's processing and export methods on five saved inputs: two reported cases, the previous boundary failure, the approved brightness portrait, and the identity fixture. All five retained their dimensions, raw and effective controls, and protected-pixel counts. Neither reported photo changed its saved support. All five stayed within the permitted boundaries, the identity fixture was pixel-identical, and no case increased newly clipped pixels. The regular picker and expert development release remain fixed. The phone check covers processing and export from photo URIs. Photo 3's coverage repair remains a separate local preview.

### Automatic jaw-gap test

The separate Jaw Test APK required nearby face and neck pixels on opposite sides of each proposed gap and similar Lab colour on both sides. It retained the soft fade and used the base mask for measurements and the exposure check. Five Huawei runs completed processing and export successfully. Photo 3 gained 32 analysis pixels of support, including 27 labelled neck. All five kept original dimensions, raw and effective controls, and clipping counts. The identity fixture stayed pixel-identical.

**The protection gate failed.** The boundary fixture had 12,074 changed pixels outside its saved permitted support and the brightness fixture had 1,591. Both previous Soft Edge Test counts were zero. The narrower bridge is not selected for the normal picker. Its APK remains separate from the verified Soft Edge Test build and the frozen expert release. No final validation or general jaw correction is claimed.

### Single app for Huawei updates

Use the verified Soft Edge Test installation as the active TrueHue app on this Huawei. Build future accepted updates with the same application ID, `com.example.skintonecorrection.pickertest.soft`, and signing key so they can replace that installation in place and retain its data. Preserve the current APK locally for rollback before applying an update. Exercise new candidate code through tests before replacing the phone build. The earlier test packages remain historical examples of isolated development builds.

### Milder positive exposure

The 22 November Soft Edge Test update retains three quarters of the predicted positive exposure in stops and uses the existing highlight limit whenever it is stricter. Negative exposure, identity, the other four controls, and mask generation retain their existing behaviour. The fold and tree remain frozen. The app reports both the highlight-limited gain and the gain actually applied.

The update used the existing Huawei app ID and installed in place. On the reported photo, compared against the previous Soft Edge build using the same decoded image, the gain fell from 1.414× to 1.297× and newly clipped pixels fell from 337,089 to 162,472. The mask matched exactly and pixels outside it remained unchanged. Both earlier adjusted and brightness fixtures retained their stricter gains and exact preservation checks. The identity fixture stayed pixel-identical. All four instrumented photo cases retained dimensions and raw controls. The mask coverage limitation and expert development release remain unchanged.

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
