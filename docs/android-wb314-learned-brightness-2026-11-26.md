# Android learned brightness development test

Highlight Test .22 uses the existing Android photo picker. It adds a bounded brightness step after the WB314 result has passed its existing checks. The researcher approved the appearance of six development previews, including a lower-strength daylight edit. One local fit uses six positive examples and six no-additional-lift controls. Its four measurements are face luminance, nearby luminance relative to the face, spread of facial luminance, and the brightness gain already delivered. The learned materials and photographs are local.

The extra adjustment multiplies linear RGB channels uniformly and fades inward from the saved mask boundary. It tapers off on brighter skin and keeps the accepted output wherever the proposal would reduce luminance or lose highlights. An accepted backlight lift, local shadow lift, cooling adjustment, or darkening decision takes precedence. The correction model and its masks, ITA and estimated skin-tone fields retain their existing path.

The separate orientation retry only runs after both normal analysis sizes return zero faces on a landscape image. The retry requires one consistent single detection across two sizes in only one of the two quarter-turns. The normal processing stages then run on the recovered orientation. The app restores original width and height and reapplies the restored mask to preserve pixels outside it.

The opt-in build takes the SHA-256 of the provisioned local fit through `wb314PhoneBrightnessFitSha`. It verifies the matching file `files/wb314_phone_brightness.json` at runtime. The orientation retry is controlled by `wb314QuarterTurnTest`. Both settings default to off. The manuscript APK and expert-review evidence retain their prior versions.

## Local verification

The development comparison ran on the Android emulator using the existing .20 inputs. Five upright portraits received average extra lifts of approximately 5.33, 6.09, 3.10, 10.06 and 11.00 RGB luminance code levels within their saved masks. The normal picker recovered the reclining portrait at 3088 × 2316. The no-face control was rejected. A previously accepted backlight edit, cooling edit and unchanged outputs matched the baseline.

The approved strengths and earlier examples belong to development. A separate backlit portrait still stayed unchanged. These findings describe the recorded checks and leave new-photo decision reliability and field-device performance unqualified.
