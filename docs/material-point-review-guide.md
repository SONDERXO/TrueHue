# Small material review

Completed: [human review results](material-point-review-results.md). The saved
labels are now a development regression set; do not overwrite them for tuning.

Open [the review page](../outputs/material_point_review_v1/review.html) in your
browser. There are **24 points on six photos**, not another full-image review.
If your editor displays HTML source, open the file with your usual browser.

1. Enter your initials or a reviewer name.
2. For each card, label the tiny center square: **Skin, Hair, Paint, Other,
   or Unsure**. The full photo is on the left; a magnified view is on the right.
   Label the center point only, even when the surrounding patch is mixed.
3. Click **Save labels** and save `material_review_labels.json` in
   `data/manifests/material_review_v1/`. If it downloads elsewhere, tell Codex
   the location. **Save draft** and **Load saved labels** support breaks.

Skin means visible, unpainted facial skin, including darker or shaded skin.
Hair includes eyebrows and facial hair. Paint means a visible coating. Eyes,
lips, teeth, clothing and background are Other. Use Unsure for ambiguous points.
No answers are suggested or prefilled. Nothing is uploaded. Saving downloads a
file; it does not automatically submit labels to the project. Browser progress
storage is a convenience only; keep an exported draft when pausing.

Once the completed labels are available, run from the project root:

```text
venv/Scripts/python.exe scripts/34_score_material_point_review.py
```

For another location, add `--labels "C:/path/to/material_review_labels.json"`.
The scorer checks reviewer identity, manifest hash, complete unique point IDs,
allowed labels and prediction coverage. Drafts are rejected. It refuses to
overwrite existing results. Output will be
`outputs/material_point_review_v1/human_labeled_results.json`.

## What this review can tell us

The sources include the familiar patch example, known hair and paint cases,
an ordinary face whose skin recovery was blocked, and darker/shaded facial
examples. These descriptions are developer selection reasons, not human labels
or demographic/MST assignments. They are not shown as expected answers on cards.

Six previously exposed development sources were deliberately selected; rejected
29962 stays rejected for training. None is reserved final-test data. The labels
will be independent of mask overlays during review, but the point selection is
developer-biased and **not an independent or representative test sample**.

Material labels apply to decoded original-image coordinates. The same labels
can score the fixed color-only synthetic shift, which does not move image
content. This is a material task, not a rating of how skin-colored a pixel looks.
The label policy must remain fixed during review; no labels enter model fitting.

Cached observations cover original, guarded and material-checked masks for clean
and shifted inputs: 24 points × two variants × three methods = 144 observations.
All were available in this build. Future unavailable observations are reported
explicitly, not converted into negative predictions. Unsure points do not enter
confusion counts, precision or recall. A denominator of zero produces no score.

The scorer reports retained skin points, selected non-skin points, and counts
for hair/paint/other separately. These are selected-point diagnostics, not
image-area segmentation accuracy, fairness evidence or final thesis results.
There are no measured material-accuracy results until the human review is done.

## Reproducibility and verification

Builder: `scripts/33_prepare_material_point_review.py`; it refuses to replace an
existing review. The JSON manifest, source hashes and cached predictions are in
`data/manifests/material_review_v1/`; point images, blank form and build summary
are in `outputs/material_point_review_v1/`. Raw images remain local and ignored.

425 tests passed, including complete/unique label validation, manifest matching,
draft rejection, per-material counts, unavailable/unsure handling and empty
denominators. The generated form passed JavaScript syntax checking; manifest
coordinates, card count and cached-observation coverage were checked. Generated
card images were visually inspected. Live browser interaction could not be
tested because no browser connection was available.

The review awaits human labels. Current masks, model, earlier human decisions
and thesis scope remain unchanged.
