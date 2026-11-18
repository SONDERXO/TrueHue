# Plan for better skin and object separation — 8 November 2026

The existing annotations can check whether a change recovers skin while protecting
hair and objects. They do not yet justify training or claiming a dedicated beard
or transparent-glasses model. No training, model search or new review is started.

## What we actually have

| Completed reference | Available information | Important limit |
| --- | --- | --- |
| Six-photo point review | 129 skin, 101 hair-or-beard, 8 object-or-other points | Hair and beard share a label; objects are not separated by type |
| Same six-photo patch review | 36 polygons, 3,156 original-image pixels | Selected positive patches, some neck; no complete skin/non-skin outlines |
| Source grouping | Six photos from five publisher groups | Groups are not verified identities; all six photos have been exposed during development |

All eight object points are in one photo. There are no explicit labels separating
frames, rims, clear lenses and opaque lenses. There are no dense negative masks.
Three hair/beard points fall inside skin-patch polygons: two in review_02 and one
in review_04. The original annotations remain unchanged. These conflicts do not
invalidate the entire review, but must not become contradictory training targets.

The earlier semantic-mask acceptance file contains six accept/reject decisions,
not six new dense human segmentations. The broader FaceOcc polygon import is not
present at its expected existing output location; it is not counted as completed
training evidence. No older package is assumed to be compatible ground truth
without checking its label meaning, provenance and source coordinates.

## Development decision

Keep the six reviewed photos as a fixed development regression reference. Do not
fine-tune a large parser on them and then report their scores as validation. Do
not train a beard or glasses classifier by renaming the combined labels. Do not
treat unmarked pixels as background or augmentations as additional people.

The target behavior remains:

- Recover visible facial skin that the current parser misses.
- Exclude hair, beard and objects from skin-colour measurement.
- For correction through explicitly designated transparent prescription glasses,
  retain visible face through the lenses while protecting frames and rims.
- Leave uncertain or failed measurements unchanged, and report the failure.

The last two tasks need separate evidence: skin measurement excludes eyes and
other facial features, while correction has a broader face/neck support. One
binary mask cannot be assumed to validate both behaviors.

## One focused implementation route

Use a material-aware segmentation candidate only when a complete checkpoint,
its actual label definitions, preprocessing, reuse terms and local execution are
verified. The needed distinction is visible skin versus facial hair and objects;
a generic larger parser with the same labels is not a demonstrated solution.

This is a dependency check, not authorisation for another dataset/checkpoint
search. The existing 6 November material-model suitability decision already
records that no suitable accessible complete explicit-beard checkpoint was
established. Do not repeat its failed auxiliary models or access attempts without
a changed dependency. No currently verified candidate is selected by this plan.

When a suitable candidate is available, prepare one fixed comparison before
execution. Use the same actual-input framing, original measurement pixels,
source groups and fixed protections. Retain all failures. Do not change correction
controls, fit MST, lower the measurement threshold or tune candidate parameters
on these six examples during that comparison.

## Concrete acceptance criteria for that comparison

1. Recover additional reviewed skin points and marked skin-patch pixels on the
   same available photos, while showing per-photo gains and losses separately.
2. Introduce **zero newly included definite hair/beard or object points** compared
   with the current raw baseline. A lower pooled count does not excuse newly
   including a previously protected point.
3. Preserve all previously usable measurements; a missing prediction must not be
   counted as successful protection. Report all six attempts and paired results.
4. Keep original-pixel statistics, correct coordinates and explicit protection
   invariants reproducible. Show all fixed comparison boards.
5. Report conflicting annotations separately. Keep original point and patch
   totals for continuity, plus a clearly identified conflict-aware diagnostic;
   do not silently delete or relabel the three conflicting pixels.
6. Make no automatic clear-lens/rim accuracy claim: the existing eight generic
   object points cannot certify it. Preserve the explicit clear/opaque/uncertain
   glasses choice and existing protection checks.

Passing these is a development screening result, not general mask validation or
permission to integrate. Independent evidence would still be needed for final
accuracy claims. No new annotation round is requested by this plan.

## Correction model remains a separate acceptance step

Better masks will change Lab/ITA and possibly MST, so the current learned models
must not silently consume a different measurement contract. Only after a mask
candidate passes the fixed checks should a matching, separately approved learning
cycle be considered. That cycle must preserve unseen clean photos and retain
distortion recovery. The present four clean-photo edits remain unresolved, and
this label inventory does not show that a material model will fix them.

There is no evidence-based completion date yet. The next executable inference
depends on a verified suitable candidate; another fit using the same insufficient
labels would not remove that dependency.

## Work completed for this plan

Script583 inventories the completed exports, checks source/image bindings and
counts label overlaps. Private results: `outputs/material_label_inventory_v1`.
It confirms six photos/five publisher groups, 238 points, 36 polygons and 3,156
pixels. Original labels, artifacts, research-only permissions and scientific
admission flags remain unchanged. No fits, forwards, downloads or app changes.
