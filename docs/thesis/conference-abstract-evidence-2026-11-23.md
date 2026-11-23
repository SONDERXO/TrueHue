# Conference abstract evidence and claim limits

The Android prototype uses one depth-four regression tree to predict five exposure and colour controls from 314 image-derived features. It applies the adjustments within an automatically generated skin region, which may include adjacent neck, and exports an original-size PNG. It processes the photo on the device. The fitted tree uses neither the supplied Individual Typology Angle (ITA) field nor the estimated Monk Skin Tone (MST) field in its splits. [Method and model](../wb314-completion-blockers-and-two-round-plan-2026-11-19.md#cross-check-against-the-proposal)

## Controlled test on the frozen manuscript build

On the OPPO A94, Soft Edge Test `1.0-wb314-soft-edge-test.5` completed all 24 cases from four Face Research Lab London Set v5 studio portraits. The four people were outside the earlier London pilot. Identity overlap with other datasets was unverified. Each portrait contributed its original and five controlled variants. Exposure changes were ±½ stop. The raw and corrected images were compared with the corresponding unaltered portrait on the same fixed skin region, defined using the app's mask on that unaltered portrait. The table gives mean CIEDE2000 error across the four cases in each condition. Lower values indicate closer agreement with the reference. [Full evaluation record](../wb314-final-evaluation-preflight-2026-11-22.md#completed-correction-only-test)

| Condition | Cases | Input error | Output error | Observed result |
| --- | ---: | ---: | ---: | --- |
| Original | 4 | 0.00 | 1.39 | Three unchanged. One was edited and gained clipping at 19 pixels. |
| Colour cast only | 4 | 5.67 | 5.67 | All unchanged. |
| Underexposure | 4 | 7.41 | 2.43 | All improved. |
| Overexposure | 4 | 7.60 | 7.60 | All unchanged. |
| Underexposure with colour cast | 4 | 10.11 | 2.92 | All improved. |
| Overexposure with colour cast | 4 | 8.55 | 8.55 | All unchanged. |

All 24 outputs kept the original resolution and preserved every pixel outside their saved correction masks. The results support improvement under the tested underexposure conditions. The reference is each original studio photograph. [Dataset release](https://doi.org/10.6084/m9.figshare.5047666.v5)

## Separate exploratory check on everyday portraits

The same frozen build completed 17 of 21 user-supplied everyday portraits. Four stopped at facial analysis. A single reviewer identified two as needing correction before running the app. The result on one naturally backlit portrait showed a modest lift. The other photo stopped at facial analysis. This check used visual judgments without clean target images. [Everyday-portrait evidence](../wb314-final-evaluation-preflight-2026-11-22.md#evidence-on-unedited-everyday-portraits)

## Newer Highlight Test build

The later local build checks the rendered skin region for new RGB clipping or strong brightening near white. It retries a weaker edit and preserves the input if the retry triggers the check again. The WB314 tree remains the same. Its face-analysis logs record both attempted analysis sizes and the mask measurements reached before a failure.

- In a repeat of the 21 everyday portraits, the Highlight Test completed 17; the same four stopped at face analysis. Of the 17 exports, 14 matched the frozen build, two unwanted edits were skipped, and one was made milder. The useful backlit output was among the 14 exact matches. All 28 JVM tests passed.
- In a separate check on the OPPO with six new-to-correction UT Austin portraits, three completed unchanged and three stopped at face analysis. The single portrait judged to need correction stayed unchanged. Its saved report showed an unchanged tree decision. These six images had been viewed during intake. [UT Austin dataset](https://live.ece.utexas.edu/research/ChallengeDB/) · [Image quality study](https://doi.org/10.1109/TIP.2015.2500021)
- The latest `1.0-wb314-highlight-test.3` APK adds the simplified interface. The installed OPPO APK matched the local build. The Android emulator checks showed the selected-photo screen, percentage progress, glasses prompt, comparison, unchanged and error states, and save confirmation. The corrected example saved at the input's 1350 × 1350 dimensions. In the emulator examples, the build reduced a proposed edit on an underexposed input and applied no correction to a colour-only input.

## Claims for an abstract

Use the controlled London Set underexposure results to state what the prototype demonstrated and include the unchanged conditions as a limitation. The small studio sample and exploratory everyday checks leave reliability on typical smartphone portraits, especially the decision to make an edit, unverified. Skin-tone estimation accuracy and performance across independently labelled skin-tone groups remain unverified. The original expert development feedback applies to its fixed model and image set. Final expert appraisal remains pending. [Study scope](../wb314-final-evaluation-preflight-2026-11-22.md#23-november-scope-decision)
