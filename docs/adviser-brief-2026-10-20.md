# TrueHue: progress update and questions for our adviser

**21 October 2026**

We have built the parts that find a face, select its skin areas, and calculate an image-based skin-tone measurement called ITA. We have also tested creating altered photos and the correction settings needed to restore them. We have not yet trained the decision-tree model or completed the Android app.

Before continuing with the main experiments, we would appreciate your guidance on three points:

1. **Using skin-tone measurements:** Our tests found that different Monk Skin Tone (MST) categories can have similar ITA values. We cannot yet reliably turn an ITA value into one of the ten MST categories. May we use the measured ITA value directly to guide correction, and use images with existing MST labels to compare results across skin tones?

2. **Choosing suitable photos:** Only one of the 184 SCIN photos we selected showed a visible face. May we use FairFace as our main source of training photos, or should we find another suitable collection of facial photos?

3. **Choosing how much to alter photos:** The proposal applies stronger artificial exposure and color errors to darker skin-tone groups. However, FairFace does not provide MST labels, and we do not yet have a reliable way to assign them. May we apply the same range of artificial changes across all photos, then compare correction results using evaluation images with existing MST labels?

These are suggestions for your approval, not changes to the approved method. The goal remains an Android app that corrects facial photos directly on the phone. We would also like to confirm how photos should be divided for training and evaluation, what image size to use, and how to keep the final evaluation separate from development.
