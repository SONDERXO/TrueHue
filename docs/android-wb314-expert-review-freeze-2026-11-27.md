# Android .25 freeze for expert feedback

On 27 November 2026, the researcher froze Highlight Test .25 for the current expert feedback packet. The app runs the WB314 correction, tries a bounded exposure lift if that path keeps the original, and checks the proposed result for excessive change or brightened highlights. If the check rejects the result, the app preserves the original and displays **Photo kept unchanged**. The .25 jaw taper reduces the contrast introduced by the edit around protected face-to-neck seams. The tested application masks and protected areas remain fixed.

The freeze binds the signed Android APK, fitted brightness file, and eight Android research assets. The private archive and upload PNGs are stored with the local research project. Both archives and each of the 20 upload PNGs passed hash verification.

The .25 build extends the [opt-in .22 profile](android-wb314-learned-brightness-2026-11-26.md) with `wb314DarkFaceStrengthTest`, `wb314DefaultCorrectionTest`, and `wb314JawSeamTest` enabled. These options default to off. Restore the exact signed build with its matching local assets for version-specific comparisons.

## Verification

- The .25 build passed 46 JVM tests. The Android emulator reproduced the jaw taper through the normal photo picker. In four traced portraits, the mean adjustment beside the seam decreased by about 45% relative to .24. Across six checked photographs, zero additional pixels changed outside the existing masks and zero new clipped pixels appeared relative to .24. A narrow jaw gap remains visible on one portrait.
- The guarded default exposure test on .24 accepted eight smaller lifts and restored the original on two bright portraits that .23 had left alone. The normal picker displayed **Photo kept unchanged** on a rejected candidate and the saved before and after bytes matched.
- The .25 Form packet has 20 supplied MST-E photos of 13 previously seen people, with two photos per publisher MST category. It retains the section order and uses aligned face crops from full-resolution Android outputs. Eighteen pairs show changes at presentation precision and two show preserved originals.

These results cover local development and emulator checks. An independent analysis of correction consistency by reference skin-tone category remains open.

## Expert feedback and defense

Use a copy of the earlier questionnaire for the .25 packet. Retain the consent, overall quality rating, preference question and comments. Keep earlier responses attached to their original image and version.

Add the same adjustment-necessity question to every pair. Where practical, ask it after showing the original and before showing the app output.

> Looking only at the original photo, would you recommend adjusting the brightness or color of the face?
>
> - Yes, an adjustment would help.
> - No, the original looks acceptable.
> - Unsure or unable to judge.

Report these judgments with reviewer counts in a separate table from the quality and preference responses. Preserve disagreements and unsure responses. The export check establishes pixel preservation. Expert judgments address whether that decision was appropriate for the reviewed photographs.
