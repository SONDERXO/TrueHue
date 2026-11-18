# Review source and target supports

Open `review_photographic_support.cmd` in the repository.

**Restart the whole reviewer after the10November layout fix.** Save buttons and
both review checkboxes are now at the top of the editor. New painted edits and
notes are automatically checkpointed as drafts; reopening offers restoration.
Drafts do not count as saved reviews until you explicitly confirm and save.

There are **14 editable roles: source and target for each of seven pairs**.
The904source/target roles remain separately recorded as blocked because their
cached pipeline selects the wrong person. They are not counted as approved or
silently removed. Your30labelled calibration-mask reviews remain complete.

For each role:

1. Click **Open mask editor / save both reviews**. The editor starts in **Measurement**.
   Select facial skin only; exclude hair/beard, brows, eyes, lips, mouth interior,
   neck and objects. Remove/add/restore, radius, undo and reset are available.
2. Switch to **Correction** and inspect the intended face/visible-neck support
   separately. Keep clothing, background and retained protected objects excluded.
   Correction is a separate area from facial measurement. Do not copy one mask
   into the other just to make them agree.
3. Protected additions remain locked. Explicitly unlock only when you have
   checked that the pixels you are adding were incorrectly protected. This is
   not permission to include actual objects in measurement.
4. Confirm both review boxes, add an optional note, and click **Save reviewed
   masks**. An unchanged mask still needs your explicit review. If the face or
   detail cannot support a credible selection, use **Save as unjudgeable**.
5. The editor closes and the queue shows the saved status. Click **First unsaved
   review** or **Next** to continue. Counts refer to roles reviewed, not mask
   strokes or revisions. Reopening a saved role starts from its latest revision;
   earlier masks, reports and strokes remain preserved.

The1188profile remains small and sparse in the source photograph. Do not paint
uncertain areas merely to reach the minimum count. A large normalized mask does
not create native detail. Fewer than1,000measurement pixels or invalid ITA stays
unavailable even when saved; unjudgeable always remains unavailable.

This editor prepares supports only. It does not apply a learned correction,
predict MST, fit controls or adjust the demo's brightness. The source and target
may have different native crop bounds; reviewing them separately does not prove
pixel correspondence or registration.

Saves go to `outputs/photographic_support_annotations_v1`; jobs go to
`outputs/photographic_support_jobs_v1`. Generated test records are isolated
elsewhere. When all14roles have a saved review, tell Codex they are ready for
the support/coverage/contract audit. Scientific/training admission is not
automatic when the counter reaches14.
