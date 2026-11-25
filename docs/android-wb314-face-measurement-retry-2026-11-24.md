# Android face measurement retry on everyday portraits

This emulator development check reused the six cases from the second intake of the UT Austin LIVE In the Wild collection. The first pass was Highlight Test .6. Original-only visual screening identified two apparent colour casts and four portraits with natural-looking colour. Both cast cases stopped before correction. Two natural-colour cases completed with exactly their input pixels, and the other two stopped at face analysis.

## Change tested

The Android app normally requires 1,000 facial measurement pixels on the 256 × 256 analysis grid, including on its 512-pixel vision retry. The opt-in test uses 30% of the detected face-box area on the measurement grid, rounded up and constrained to 750–1,000 pixels, only on the existing retry. The first pass keeps the usual minimum. The retry still requires landmarks and applies the same skin, anatomical and occlusion checks. It keeps the existing application mask and clipping protections. The pinned model and the feature calculations are unchanged.

In the first implementation, Highlight Test .7 found 859 facial pixels and 771 visible measurement pixels on the target retry. Mask generation completed with its test minimum of 750. The feature extractor independently required 1,000 and ended the run before model prediction. Highlight Test .8 passes the same minimum through both steps. The standalone feature API and normal builds retain their existing 1,000-pixel minimum.

## Six-photo check

| Photos | Highlight Test .6 | Highlight Test .8 |
| --- | --- | --- |
| Cast photo with a smaller detected face | Stopped at skin measurement | Completed with a pixel-identical export. All five correction controls were 1. |
| Cast photo with the face turned sideways | Stopped at landmark detection | Stopped at landmark detection |
| Two natural-colour photos that completed | Two pixel-identical exports | Same decoded inputs, exports and masks |
| Two natural-colour photos that stopped | Stopped at skin measurement | Both still stopped at skin measurement |

The local test recovered one analysis path and added no corrected outputs. The smaller face's cast persisted because the tree selected leaf 14 and returned identity. Every completed output retained its dimensions and every pixel outside support. All 31 Android unit tests passed. Eight provisioned model files had the same SHA-256 digests before and after the in-place emulator update. Reused photos show what happened to these cases. General reliability on naturally cast portraits remains unverified.

Build the separate picker test using `-Pwb314PickerTest=true -Pwb314SoftEdgeTest=true -Pwb314HighlightTest=true -Pwb314FaceMeasurementTest=true`. This is development evidence for the emulator picker. The manuscript freeze and the expert development round retain their recorded versions.

## OPPO A94 check

The OPPO A94 updated in place from Highlight Test .3 to .8 on Android 13. The application ID stayed the same. The installed APK matched the verified local build and all eight provisioned model files matched the emulator check.

Three reused development fixtures ran through the normal picker repository. The severely backlit portrait changed on 25,189 pixels, matching the previous OPPO input, mask and export bytes. A well-balanced portrait stayed pixel-for-pixel unchanged. The smaller-face cast portrait reproduced the emulator's 771 visible pixels on its larger retry and exported pixel-for-pixel unchanged. All three files retained their 500 × 500 dimensions. No output introduced clipping or changed a pixel outside support. Colour correction for the smaller-face portrait remains unresolved. These three checks describe the test build on one device.

The on-screen photo picker, glasses prompt, results view and Save action were also exercised with the backlit photo. The PNG saved to Downloads matched the instrumented correction byte for byte. The first automation attempt expected a seconds field in the picker timestamp. The OPPO picker displays minutes and requires a Done tap after selection, and the completed check used that flow.

## Full-resolution camera capture on OPPO

The user reported that the in-app camera photos were too large to correct. Both saved camera JPEGs were 4896 × 6528 with normal EXIF orientation. Their hashes matched the earlier decode-stage reports that recorded insufficient memory before face analysis. The app had budgeted 16 bytes per pixel for full-size buffers. Decoding and orientation, analysis conversion, and rendering run in sequence. Each can have two full-size RGBA buffers live at its peak.

Highlight Test .9 budgets for two full-size buffers and 48 MiB of additional working memory. It records source dimensions before the memory check and retains full-resolution decoding, face analysis, mask protection, rendering and PNG creation. The original encoded-file size guard and out-of-memory handling remain active. The update used the existing OPPO app ID. All 33 Android unit tests passed and the eight provisioned model files matched .8.

Both previously rejected camera JPEGs completed through the camera's FileProvider URI on the OPPO. The decoded input and generated PNG were 4896 × 6528 in both cases, with a sampling factor of one. The capture bytes matched their earlier hashes afterward. The model selected identity on one photo. The other received a colour adjustment, backed off by the existing highlight protection. The first instrumentation connection dropped over USB, and its completed report and PNGs were recovered from the phone. The second instrumentation command exited successfully. This verifies full-size handling for these camera captures. The manuscript build and expert round keep their original versions.

An independent comparison of the saved PNGs found exact decoded RGB equality for the identity case. The corrected case changed 3,339,321 pixels inside application support and zero pixels outside it.

## Missed lift under indoor lighting

The researcher reported that a recent correction looked darker. The newest saved camera run on Highlight Test .9 showed the unchanged-results screen and had exact decoded input/output equality. An earlier colour adjustment used a different capture. It raised mean encoded luminance within the application area by 0.43 of 255 code levels while increasing the red channel and reducing the blue channel. The newest photo had a visibly shaded face and a broad bright wall. A screening calculation on the saved application mask found that 3.2% of its outside area reached luma 224, below the existing near-white scene requirement.

Highlight Test .10 adds one opt-in branch of the existing low-light rule. The tree must choose identity. The three-stop separation between facial upper luminance and scene highlight luminance remains required. The alternate branch requires at least a quarter of the unaffected scene at encoded luminance 192 or above, and the face's 75th-percentile luminance must be at least one stop above its 25th percentile. It uses the existing 3/8-stop lift, render headroom check, highlight protection and skin mask. The learned controls, colour policy and frozen model remain the same.

With the same source hash and clear-glasses choice, the latest OPPO portrait retained its 4896 × 6528 dimensions. Its mean encoded luminance within support increased by 5.90 of 255 code levels. Exactly 4,589,438 pixels brightened. Zero darkened, newly saturated or changed outside the mask. The source, decoded input and mask matched the earlier run. All 34 Android unit tests passed.

Four OPPO regression photos retained their earlier output and mask bytes. The original severe-backlight lift, an acceptable-lighting portrait, and both earlier full-resolution camera outputs all matched. The existing app was updated in place, and all eight model assets matched .9. This local test is limited to one reported miss and four reused regression photos. The frozen manuscript build and expert round retain their recorded versions. The .10 build adds `-Pwb314DiffuseBacklightTest=true` to the earlier picker-test flags.

### Stronger indoor lift

The researcher found the 3/8-stop result too subtle. Highlight Test .11 adds a quarter stop to this branch for a 5/8-stop proposal. The eligibility rule and the original near-white backlight lift remain as tested. The stronger proposal must pass the highlight and clipping checks before the edge fade. If it fails, the app checks the original 3/8-stop proposal. The standard output highlight check still runs on the final blend.

On the same OPPO capture at 4896 × 6528, the average luminance lift within the mask increased from 5.90 to 10.19 encoded code levels. The output brightened 4,715,105 pixels, with zero darkened or newly saturated pixels and zero changes outside the unchanged mask. The known near-white backlight and acceptable-lighting fixtures retained their previous output and mask bytes. All 34 Android unit tests passed. The in-place OPPO test build uses the same eight model files. The evidence covers one strength change on a reported indoor case and two regression checks.

### Automatic indoor lift strength

Highlight Test .12 adjusts strength for portraits that meet the existing indoor lighting rule. It retains the 5/8-stop lift when the difference between the 75th and 25th percentiles of facial luminance is at most two stops. Above that, it adds one quarter stop of lift for each additional stop of contrast within the measured face, capped at one stop. If the stronger lift fails the highlight check, the app can use the earlier 5/8-stop or 3/8-stop lift, subject to the same safety checks. The eligibility conditions and the near-white backlight path retain their earlier behaviour.

On 25 November 2026, the OPPO A94 updated in place and verified all eight model files. The approved 4896 × 6528 photo, a near-white backlight fixture, and a well-lit portrait retained their exact input, mask and output bytes. All 35 Android unit tests passed, including tests for deeper generated shadows and the one-stop cap. The higher strengths were exercised on generated measurements. General reliability on naturally underexposed phone photos remains open.

### Decision check on a new indoor portrait

On 25 November 2026, a new OPPO camera capture that the researcher flagged as needing correction completed face analysis with 5,153 visible facial pixels at the 256-pixel analysis scale. Highlight Test .12 kept all five controls at identity. The decoded 4896 × 6528 output matched the input exactly. The indoor lift did not run.

One local candidate, .13, tested whether near-white and moderately bright background areas could jointly supply evidence of backlighting. On the unaffected scene, the candidate weighted the fraction at luma 224 or above by 16 and the fraction from luma 192 through 223 by 4, requiring their sum to reach one for the alternate backlight branch. The face-shadow requirements and existing headroom checks stayed in place. All 36 unit tests passed. For the same captured file and glasses choice, both builds reported identity controls and matching input, mask and output file hashes. The target check failed, so the planned follow-up comparisons did not run. The .13 trial was rejected, and the OPPO was restored to .12 in place.

This case shows a missed decision on a full-resolution camera input after successful face analysis. The next development check records decisions on originals before showing candidate outputs. It counts missed corrections, unnecessary edits and analysis stops separately and checks whether outputs improve portraits judged to need a change. The frozen manuscript build and development expert materials retain their recorded versions.

### Six-portrait decision baseline and colour screen

The researcher marked six original phone photos for correction before the .12 comparison. The OPPO brightened one, returned four unchanged at the established comparison precision, and stopped at facial measurement on one. Three of the completed portraits called for a colour correction and all three retained neutral colour controls. The labels identify the desired edit types. They give no quality judgment on the one brightened output. All six called for some edit, so this baseline does not estimate the frequency of unnecessary edits.

An offline screen tested whether bright background samples could establish a common colour bias across three or more spatial tiles. The screen excluded saved correction support and abstained when a tile appeared neutral. The fixed gate required a proposal on at least two of the three completed colour misses and no proposal on either brightness-only portrait or one preserved comparison portrait. It proposed colour on one of the three misses and one brightness-only portrait. Four generated checks passed, including tests of a known cast and abstention under mixed lighting. The natural-photo screen failed. No candidate correction was rendered or installed. Highlight Test .12 remained on the OPPO.

### Reducing a confirmed warm cast

The researcher confirmed that the three completed colour misses all needed less yellow or orange. A fixed offline ridge candidate used three red-to-blue cues from the corrected region and the surrounding scene. The three warm portraits and a brightness-only portrait of the same person stayed together for the held prediction. The other brightness-only portrait and the leave-as-is portrait supplied the remaining groups. Six generated warm inputs stayed with their original scenes. This small development check used three fits and no locked allocations.

The candidate missed all three original warm portraits, proposed unwanted colour changes on two of the three colour controls, and detected a generated cast on at least one variant for two of the three original scenes. It failed the decision check. No final fit or Android integration followed.

A separate offline render used the researcher's labels to apply a mild cooling proposal to each of the three warm portraits. All retained their original dimensions, with zero changes outside the saved correction support and zero newly clipped channels relative to the colour-managed inputs. The mean encoded luminance change within support was 0.16 to 0.42 code levels out of 255. These are draft colour references with no researcher approval of strength. The two combined cases still require separate exposure work. The installed build and frozen study versions retain their recorded settings.

### Paired cooling training

A later local trial fitted a shared cooling strength with the existing renderer directly to the three provisional drafts. The two photos from the same scene stayed together, yielding two capture-group fits. All three held checks reduced mean RGB error against the drafts from 1.396–2.058 to 0.006–0.007 of 255 code levels, with no new clipped channels or changes outside the saved support at native resolution. These are reconstruction checks against authored drafts of the same person. They supply no appearance approval or cross-person performance estimate.

A separate estimator learned from colour differences within each pair and used three subject-held fits for the decision screen. It missed all three requested warm edits and preserved the three colour controls. The highest held control score was above every warm-case score, so a common relaxation of the threshold would colour-shift a control before recovering a miss. No final fit or deployment followed. The OPPO stays on .12, and the frozen manuscript and development expert versions retain their recorded settings.

### Local warm-cast test build

The researcher identified two additional warm portraits and four portraits whose colour should stay as captured. The local ridge model used three usable labelled UT Austin originals, two warm and one keep-colour. One planned training control stopped at facial measurement. A new user-supplied warm portrait and two keep-colour controls were held back. All three completed unchanged on the .12 OPPO baseline. The frozen candidate proposed cooling only the warm portrait. The earlier personal portraits were excluded from fitting.

The opt-in Android path computes the three fitted colour cues from usable pixels in the existing support. It proposes the bounded cooling edit only when the baseline would make no edit. The first port, .14, matched the decision screen but abandoned the entire edit after both proposals failed the highlight check. Build .15 keeps the input at any pixel that triggers the existing highlight protection during the cooling render. Other edit paths use their existing behaviour. The feature is enabled only with `-Pwb314WarmCastTest=true`. The frozen thesis build and expert development round retain their recorded versions.

All 37 Android unit tests passed. In the emulator, .15 cooled the held 828 × 1104 portrait with 345,610 changed pixels, zero changes outside its saved mask and zero new clipping. The existing highlight checks preserved 15,418 pixels at their input values. Mean encoded luminance within support rose by 0.37 of 255 code levels. Both colour controls stayed pixel-for-pixel unchanged. The .12 baseline used the OPPO, and the .15 audit compared the emulator output with its own saved input. The two devices differed in some decoded input and mask pixels for the warm portrait. This check establishes the edit on the emulator and does not establish device parity or generalisation. The OPPO remained on .12 at the researcher's request to continue on the emulator.

### Stronger warm-cast edit

After the researcher found the .15 cooling too subtle, .16 increased the cooling strength from 0.8048 to 1.35 on the existing gain scale. The fitted decision, masks and highlight protection kept the same implementation. The cooling edit still compensates for the colour gains using the bright-face luminance estimate.

On the same Android emulator, the reduction in mean encoded red minus blue within support increased from 5.43 to 8.77 code levels out of 255. Mean encoded luminance rose by 0.46 code levels from the input. The 828 × 1104 output had zero new clipping and zero changes outside the mask. The input, mask and decision scores matched .15 on all three photos. Both the keep-colour outputs matched .15 pixel for pixel. All 37 Android unit tests passed. The warm photo now serves as a development example for strength because the researcher commented on its earlier edit. The OPPO and frozen thesis build were not updated.

Photo credit. D. Ghadiyaram and A. C. Bovik. [LIVE In the Wild Image Quality Challenge Database](https://live.ece.utexas.edu/research/ChallengeDB/) (2015) and [Massive Online Crowdsourced Study of Subjective and Objective Picture Quality](https://doi.org/10.1109/TIP.2015.2500021) (2016).
