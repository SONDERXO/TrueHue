# Open the TrueHue demo

## Optional manual mask refinement — 9 November

After a successful **current** masking run, click **Refine mask**. Remove
hair/beard spill or add missed visible skin; switch between correction and facial
measurement areas, undo or reset, then apply. Protected regions require the
explicit unlock checkbox before adding skin there. Measurement is face-only;
correction can include visible neck. Cancel leaves the existing result intact.

Saved results preserve the original automatic evidence and your edit strokes.
The edited mask's ITA is for display; the older MST estimate and correction
controls are retained. This is a human-assisted experimental demo, not a newly
validated model. Failed detection/measurement runs cannot yet be rescued by this
editor. See [workflow and verification](manual-mask-refinement-route-2026-11-09.md).

## Adviser meeting: 7 November, 11:00 PM

Open the [progress briefing](adviser-progress-brief-2026-11-07.md) separately
for meeting notes. The Try example and Research progress buttons were removed
at the user's request.

The live photo pipeline now defaults to **current masking**: existing face parser,
FaceOcc visibility, separate facial measurement, face/neck correction, object
protection and inward blending. Correction controls still come from the older
baseline5/fold1 model using its original measurement and MST lookup. The new
mask's ITA is displayed separately; it is not fed into the old lookup. This
combination is an unvalidated demo adaptation, not a newly accepted model.

Choose **Glasses: clear** for transparent prescription lenses, **opaque** for
sunglasses or **uncertain** to keep glasses protected. Rims are approximate.
Switch **Green overlay** between **Correction area** and **Facial measurement**.
**Masking: legacy** retains the historical demo for comparison. Changing masking
or glasses clears the result and requires another run. Failed current masks do
not silently fall back to the old output. The latest research gates remain absent.
Use your own or an otherwise permitted photo for the meeting; avoid displaying
restricted dataset photos or private research review boards.

Rehearse photo selection, processing, mask/result comparison and export on this
computer before the meeting. A failed photo is a real result to explain.

The launcher detects the missing Tcl library in this computer's Python 3.14
installation and uses the existing Python 3.13 Tk window as a compatibility
frontend. It keeps all photo inference in `venv\Scripts\python.exe` and uses
the project demo service. Local runs and the copied existing Tk scripts stay
under ignored `outputs/`; there are no new package downloads or model fits.

## Run a photo

1. In the TrueHue folder, double-click **run_truehue_demo.cmd**.
2. Click **Choose photo** to use your own picture.
3. Click **Run demo**.
4. Choose the glasses setting; compare the photo, green correction/measurement area and trial result.
5. Click **Save result / report** if you want to keep the files.

Use a clear photo with one face. If the photo cannot be processed, the app
explains why. It does not change your original photo or upload it.

**The app works, but the correction model is still a trial model.** Its results
can be wrong. This is not the finished thesis model.

If double-click does not work, open PowerShell in the TrueHue folder and run:

```powershell
.\venv\Scripts\python.exe scripts/246_run_python_demo.py
```

Current masks require the existing local parser/FaceOcc assets and isolated
FaceOcc environment. No assets are downloaded automatically. Export includes
separate measurement/correction/protected masks, blending alpha and provenance.
