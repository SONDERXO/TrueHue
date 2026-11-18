# Review the11 accepted FFHQ reference selections

Run `review_ffhq_support.cmd` from the TrueHue folder.
This is a separate queue; the earlier labelled, brightness and PPR reviews need
no redo. FFHQ29863 is excluded because you rejected its underexposed original.
Your earlier measurement approval and too-bright correction report stay recorded.

For each of the11 originals:

1. Click **Open mask editor / save both reviews**.
2. Inspect **measurement**: facial skin only; remove beard/hair, glasses or other
   unwanted material where selected. Inspect **correction** separately: the
   intended face/visible-neck area, without spill onto coverings/background.
3. Paint only where needed. If both selections are acceptable, leave them unchanged.
4. Confirm both review boxes, then click **Save reviewed masks** at the top.
   Wait for the editor to close and the saved counter to increase.
5. If the image/detail makes a usable selection impossible, use **unjudgeable**.
   Do not force a selection merely to complete the queue.

The queue should finish at **11/11 saved**. Opening, viewing or pressing Next does
not save. Drafts preserve edits but do not count as finished reviews; restart the
same launcher to resume. Both top save controls and worker/save/resume have been
checked with a generated fixture. No real review has been fabricated.

These are the existing256px working images, not new high-resolution segmentation.
Small boundaries remain uncertain. This review prepares correction-training data;
it does not tune brightness or run the correction model. The original appearance
choices are already recorded, so no new aesthetic decisions or MST labels are
requested. After you finish, report done and the actual saved exports will be
audited before any data generation or model fitting.
