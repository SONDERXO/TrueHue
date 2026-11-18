# TrueHue: Adviser Update

**Meeting:** 7 November 2026, 11:00 PM

## What we have done

- Built working Python and Android demo apps.
- Added photo selection, face detection and before-and-after comparison.
- Improved how the Python demo selects the face and neck for correction.
- Added softer edges and protection for glasses and other objects.
- Tested ways to estimate skin tone and decide whether a photo needs correction.
- Checked six photos by hand to identify missed skin and unwanted selections.

## What changed from the proposal

- **Finding skin:** We now use a trained model, rather than colour rules alone.
- **Correction area:** We added the visible neck and softened the edges.
- **Glasses:** We allow correction through clear lenses while trying to protect the frames.
- **Photos:** We explored more datasets, including FFHQ and Stellenbosch.
- **Skin-tone estimate:** We tested brightness and colour together.
- **Correction decision:** We tested whether to change a photo or leave it alone.
- **Testing:** We check unchanged photos as well as photos with added lighting and colour problems.

The newer models are still experimental. Panel approval of these changes has not been assumed.

## What the results mean

- Our newer skin-tone estimate performed better in a small study.
- Correction helped many photos with added brightness or colour problems.
- Some versions also changed photos that should have stayed unchanged.
- In one later check, the latest version changed 3 of 23 unchanged photos. The older research version changed 1, so the latest version was not adopted.
- The model is not finished. The Python demo uses the new masks with older correction controls; Android still uses the older pipeline.

## What still needs work

- Leave acceptable photos unchanged.
- Reduce missed skin, unwanted selections and visible correction edges.
- Test on photos kept separate from model development.
- Get photographer feedback once we have a good initial model.
- Integrate an accepted model into Android and finish phone testing.

Our tests are small, simulated lighting does not cover every real situation, and lower numerical error does not always mean a better-looking photo. We cannot yet claim reliable performance across all skin tones. Restricted dataset photos cannot be shared without consent.

## Proposed dates

- **8-12 November:** Choose the next improvement and reassess progress.
- **13 November:** Aim to prepare the conference draft using available results.
- **14 November:** Conference submission deadline.
- **28 November:** Tentative project target, depending on results and review. Reassess on 12 November; this is not a promised completion date.

## Demo for the meeting

- Choose a permitted photo and run the demo.
- Show the original, selected area and trial result.
- Switch between the correction area and the skin-measurement view.
- Explain that the app works, but its correction model still needs improvement.
