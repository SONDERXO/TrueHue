# Android demonstration script — 31 October 2026

Open `outputs/android_demonstration_20261031_v1/index.html` locally. These are
screenshots from separate emulator runs, arranged as a walkthrough, not a video.
Allow about 90 seconds. Keep dataset photos local; nothing has been sent or
published. The demonstration does not change the app or research model.

**Home and photo selection:** “TrueHue can now select a photo and run the
pipeline locally on an Android emulator. The warning is intentional: the
current model is experimental and failed our quality checks.”

**Mask:** “The app detects one face, selects skin pixels using the original
rules, measures ITA and the experimental MST estimate, and applies the existing
decision tree. This mask shows which pixels are used. The newer parser preview
and beard/mustache changes are not adopted here.”

**Result:** “Here is an actual output. You can see uneven color and hard mask
boundaries. This confirms that the implementation runs, but it also shows why
we cannot call the correction model finished. We kept the existing baseline
rather than switching to another failed candidate.”

**Save:** “The app can save the trial image and a separate processing report
through Android’s file picker. The original photo stays unchanged.”

**Failure:** “A plain gray image contains no face. The app explains the failure
and offers a report, without showing a correction result.”

**Close:** “The next model and masking decisions still need to address quality
and the adviser’s feedback. Physical-phone checks, final MST validation and neck
coverage remain unfinished. Professional review and refinement will follow a
good initial correction model.”

Evidence: `docs/android-emulator-check-2026-10-31.md` and
`docs/android-reliability-check-2026-10-31.md`. Previous verification passed six
native emulator tests and eighteen JVM tests; this walkthrough adds no new
training or repeated model comparison. The gray-image screen is a demonstration
capture, not an additional scientific evaluation cohort.
