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

Photo credit. D. Ghadiyaram and A. C. Bovik. [LIVE In the Wild Image Quality Challenge Database](https://live.ece.utexas.edu/research/ChallengeDB/) (2015) and [Massive Online Crowdsourced Study of Subjective and Objective Picture Quality](https://doi.org/10.1109/TIP.2015.2500021) (2016).
