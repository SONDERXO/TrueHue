# Review the photographic correction references

Open `review_photographic_references.cmd` in the repository.

The viewer shows **original source on the left** and **editor-A reference on the
right**, at the same display scale. These are existing photographic pairs, not
outputs from the TrueHue model. No image is independently brightened for display.

For each of the eight pairs, choose whether the reference's skin appearance is
a suitable goal: **Suitable target**, **Too bright**, **Too dark**, **Other
concern**, or **Uncertain**. Add an optional note and click **Save choice and
next**. The count shows distinct pairs saved, and reopening resumes the first
missing choice. Earlier decisions remain preserved when you revise a choice.

Judge the appearance you would want the app to aim for. Do not choose Suitable
merely because a professional editor produced the image. Uncertain is appropriate
when the small native face detail prevents a reliable judgement.

Known person-selection and support problems remain visible. In904 the historical
pipeline selected the child instead of the intended adult man. Accepting the
editor's appearance does not repair that failure. The1188profile has sparse
source support; a larger display cannot create missing photographic detail.

This step records **reference appearance preference only**. It does not approve
masks, verify source/target registration, create MST labels, fit the tree or
change the demo's brightness. Your completed30calibration-mask reviews remain
preserved; there is no request to redo them here.

Decisions are saved locally in `outputs/photographic_reference_decisions_v1`.
When all eight choices are saved, tell Codex they are ready. The next step will
check which photographic references are suitable before preparing any further
support annotation or matched correction-target work.
