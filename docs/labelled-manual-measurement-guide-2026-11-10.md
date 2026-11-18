# Review the labelled facial measurements

Double-click `review_labelled_measurements.cmd` in the TrueHue repository.
Alternatively, from the repository directory:

```powershell
venv\Scripts\python.exe -B scripts/725_review_labelled_measurements.py
```

This opens a separate research editor, not the correction demo. It uses cached
development images and does not run detection, masking, MST prediction or the
correction tree. No brightness correction is displayed or adjusted here.

The header shows the number of distinct saved reviews and whether the current
case is saved. The editor opens at the first case without a saved review.
**Go to first unsaved review** finds the remaining cases. Pressing **Next** alone
does not save: use a save action even when the existing mask needs no changes.

1. Compare the photograph on the left with the green measurement selection on
   the right. Select **visible facial skin only**. Remove hair, beard/moustache,
   eyebrows, eyes, lips, mouth interior, objects and neck.
2. Use **Remove** and **Add skin** with the brush-radius control. **Undo** removes
   the last stroke; **Reset edits** returns to the initial selection. **Restore
   initial selection** restores only the painted area to the original seed.
3. Five cases start empty because no automatic measurement mask was saved. Paint
   only skin you can actually identify. Do not fill uncertain areas merely to
   reach the pixel threshold.
4. Add an optional note, then click **Save reviewed selection**. If the image
   cannot support a credible selection, choose **Save as unjudgeable** instead.
   This is a valid outcome and keeps the case in the denominator.
5. Read the save status, then click **Next**. Review all30 cases in their existing
   order. A saved selection below1,000 selected normalized pixels or with invalid
   ITA remains unavailable. It is preserved, not admitted by lowering the guard.

An unchanged mask still needs **Save reviewed selection** to record your review.
Saving does not advance automatically. Reopening a case resumes its latest saved
strokes and note; subsequent saves create separate revisions. Notes and unsaved
strokes prompt before navigation/closing. Keep all three conditions of each
subject; reference MST scores are hidden while you annotate.

Real annotations go to `outputs/labelled_measurement_annotations_v1`; worker jobs
go to `outputs/labelled_measurement_jobs_v1`. Generated GUI checks stay in a
separate directory and are not annotations for these photos.

When the reviews are saved, tell Codex they are ready. The next read-only audit
will check actual exports, failures, support and labelled/group coverage before
deciding whether a compatible calibration design is ready. No automatic training
or scientific admission occurs when you save.

Your approved FFHQ29863 desktop measurement is preserved separately. These native
crop measurements have a different method identity and are not pooled with it.
