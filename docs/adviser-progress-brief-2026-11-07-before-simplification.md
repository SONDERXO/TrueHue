# TrueHue: short adviser update

7 November 2026 | 11:00 PM meeting

## Changes compared with the thesis proposal

- **Finding skin:** We now use a trained model to help find facial skin instead of relying only on colour rules.
- **Area corrected:** We expanded from the face alone to the face and visible neck, with softer edges.
- **Protecting objects:** We added protection for glasses and other objects so they are not unnecessarily changed.
- **Clear glasses:** We allow correction through clear lenses while trying to protect the frames. This still needs improvement.
- **Photos used:** We explored additional datasets, including FFHQ and Stellenbosch.
- **Estimating skin tone:** We tested using both brightness and colour to improve the estimate.
- **Deciding to correct:** We tested a step that decides whether to correct the photo or leave it unchanged.
- **Testing:** We added unchanged photos and different lighting changes to check both improvements and mistakes.

The newer model changes are still experimental. The Android goal and three correction controls remain. These changes are not yet formally approved by the panel.

## What we are building

- An Android app that improves exposure and colour in a photo of one person.
- It finds the face, estimates skin tone and predicts brightness and colour adjustments.
- It should leave a photo unchanged when correction would not help.

## What we have done

- Built working Python and Android prototypes that process photos locally.
- Added photo selection, face detection, skin-tone measurement and before/after comparison.
- Developed face and neck correction, softer edges and experimental protection for glasses and other objects.
- Prepared research datasets and tools for checking results and tracing mistakes.
- Obtained the Stellenbosch dataset directly from its researcher: 21,375 photos across 285 publisher groups. Only small subsets have been evaluated.
- Completed manual checks of six photos to identify missed skin and unwanted selections.
- Improved experimental skin-tone estimation by combining brightness and colour measurements with ITA, our image-based skin-tone measurement.
- Tested several correction models and ways to decide whether correction is needed.
- Tested difficult inputs, including lighting changes and face-detection failures, and kept unsuccessful results.

## What we learned

- Combining ITA with colour measurements worked better than ITA alone in our small experiment.
- Correction can reduce errors in artificially darkened or colour-shifted photos.
- Our main problem is that some models also change photos that did not need an added correction.
- The latest attempt reduced unwanted edits from 23 to 3 out of 23 later clean photos, but still failed our requirement to leave all of them unchanged. An older research comparison changed only 1.
- The model is still unfinished. The live demos use an older experimental model.

## Current limitations

- Skin selection can miss areas or include beard, hair, glasses and other objects.
- Artificial lighting changes do not cover every real-world situation.
- Evaluation groups are small and have been used repeatedly during development.
- Lower numerical error does not always mean a more natural-looking photo.
- We have not established reliable performance across all skin tones.
- Dataset photos and private review outputs cannot be redistributed without consent.

## What we still need to do

- Understand why the model changes unseen clean photos, then agree on one justified improvement.
- Improve consistency of skin selection and correction boundaries.
- Evaluate a suitable model on a properly separated test set.
- Obtain photographer feedback once we have a good initial model, then refine and review it again.
- Integrate an accepted model into Android and complete phone testing and documentation.
- Confirm conference requirements and discuss what the current evidence can support.

## Timeline

- **November 8-12:** target the next development decision and reassess model readiness. Further experiments need a separately agreed plan.
- **November 13:** target a conference draft based on results actually available.
- **November 14:** conference submission deadline.
- **November 28:** provisional project-completion planning target, depending on model results, integration and reviewer availability. Reassess on November 12; a validated model cannot yet be promised by a fixed date.

## What to show tonight

- Select a permitted photo, run the Python demo and compare the input, selected skin and trial correction.
- Switch the green overlay between correction area and facial measurement. MST and correction controls still use the older model's separate measurements.
- Use this briefing separately to explain the latest findings.
- Explain that the prototype works, but correction quality still needs improvement.
