# Complete-mouth exclusion experiment v1 (2026-10-19)

## Isolated change

`src/skin_masking/mouth_exclusion_experiment.py` defines the complete ordered
20-vertex outer-lip contour. It fills the mouth interior and removes that
region from V2's final mask, retaining all existing baseline exclusions.
It never adds skin pixels. Vertex clipping/truncation matches the existing
exclusion convention; no dilation, face-outline restriction, threshold,
resolution, detector, eye/brow mask, or measurement change was introduced.

Run from the project root:

```text
venv/Scripts/python.exe scripts/19_compare_complete_mouth.py
```

The command refuses to overwrite an existing experiment. Local outputs are
`outputs/complete_mouth_experiment_v1/comparison.csv`, `summary.json`, and
80 before/after grids under `grids/`. Baseline code, input manifests, manual
decisions, and model hashes are checked unchanged. The same 80 reviewed
development images are used, including 45 baseline accepts and 35 rejects.
This is not held-out evaluation or evidence of population-level improvement.

## Numerical findings

- 80 compared, zero blocked; baseline regeneration checks passed.
- 68 masks changed; the other 12 had no additional selected pixels removed.
- No previously valid ITA calculation became invalid under the 1,000-pixel
  condition, including all 45 baseline accepts.
- Median nonempty-mask retention: 98.55% of V2's selected pixels.
- Largest removal among baseline accepts: 5.27% in train/7712.
- Largest absolute ITA shift among numerically valid before/after pairs:
  approximately 2.11 degrees in train/17096.

Retained pixels and ITA shifts are descriptive effects, not accuracy metrics.
The final masks remain subsets of V2, so useful skin missed by V2 is not restored.

## Targeted visual findings

Inspected all 12 incomplete-mouth cases from the accepted-image audit:
train/124, 17773, 21241, 26799, 30603, 47374, 62331, 6236, 67854,
7712, val/10480 and val/1728. The completed mouth region visibly covers
the upper/lower mouth more fully and removes previously selected mouth
pixels in these examples. Image blur, occlusion and raster boundaries limit
claims about exact lip-edge accuracy. In 124, the mouth is partly occluded
by fabric, so the polygon should not be interpreted as a verified lip boundary.

Also inspected train/12947 (one of the larger accepted removals), train/48136
(baseline accepted, facial-hair concern), and train/83184 (known bad mesh).
The latter still places a mouth region on the forehead. A correct polygon
definition cannot repair unreliable detected landmarks.

These 15 inspections are Codex development observations, not a full visual
re-review of all 80 or new human acceptance labels. Experimental visual-review
fields in the comparison CSV remain pending.

## Decision

The experiment supports correcting the incomplete mouth polygon as a narrowly
defined candidate change. Keep it experimental for now: the frozen V2 default
and existing extracted features remain unchanged, and the face-outline
restriction remains rejected. Landmark misplacement, hair/background leakage,
glasses, and lighting-sensitive missing skin are not solved.

Next, freeze the candidate definition and assess both V2 and this variant on
a fresh deterministic sample not among these 80 development images. Compare
mouth coverage and regressions without using ITA values to select examples.
Do not automatically request full review of all 510 images. Before adopting
the change, record the version decision and consistently regenerate features
for whichever sources are subsequently used; do not mix V2 and variant
statistics in one supposedly frozen run.

## Verification

362 tests passed. New tests check that the ordered outer contour follows the
installed MediaPipe lip-topology edges, removes upper and lower mouth interior,
preserves unrelated pixels and baseline holes, does not mutate inputs or add
skin pixels, and rejects invalid/degenerate geometry.

## Fresh-image check (2026-10-20)

Command: `venv/Scripts/python.exe scripts/19_compare_complete_mouth.py --fresh-sample 30 --seed 42`.
The stable sorted sampling pool consists of 460 automated successes outside
all 80 development IDs; no group, ITA value or demographic field determines
selection. This is a new comparison sample, not an untouched thesis test set.
Its images are now part of pipeline assessment and must be disclosed as such.

Local results: `outputs/complete_mouth_fresh30_seed42/` contains comparison
records, per-image grids, five contact sheets and a summary recording the
sample seed, excluded IDs and input/model/candidate hashes.

- 30 comparisons completed; zero blocked or mismatched baselines.
- 29 masks changed; no loss of numerical ITA validity.
- All 30 comparisons were inspected through five contact sheets by Codex.
  No obvious gross removal of facial skin from this change was observed.
  Mouth removal looks more complete in open-mouth examples. Blur and
  occlusion limit exact boundary judgments, and numerical validity does
  not establish suitability of the entire mask.
- Other defects remain visible, including missing skin and glasses/background
  contamination. The mouth change does not make all 30 images acceptable.
- No human review labels were assigned or changed. This is qualitative
  pipeline assessment, not measured segmentation accuracy or independent
  human agreement. No candidate tuning was performed using these 30 images.

The narrow change is supported for a versioned candidate named
`v2_complete_mouth_v1`. Keep its current contour and exclusion conventions
fixed for subsequent feature preparation; do not add the rejected oval.
The existing V2 default is still unchanged. Integration must explicitly
select and record the version, preserve old outputs, and regenerate affected
measurements consistently. No further review batch is planned for this mouth
polygon fix. Landmark-quality failures remain a separate limitation.

The next implementation milestone is version-aware candidate feature
preparation, followed by a documented source-image split and explicit
synthetic-transform/correction-target definitions. Group-conditioned severity
must not be invented while the ITA-to-group policy is unresolved. Do not call
the source photographs calibrated true-color ground truth.

## Integration completed (2026-10-20)

The reviewed change is now available through the explicit
`v2_complete_mouth_v1` version in script 11's `process_record` and
`compute_versioned_skin_mask`. Historical calls still default to `v2`.
The implementation lives in `src/skin_masking/mouth_exclusion.py`; the old
experimental import path re-exports it for compatibility. Unknown versions
and inconsistent repeated landmark geometry fail explicitly. Unavailable V2
landmarks retain the existing exclusion path; there is no silent V1 rescue.

`venv/Scripts/python.exe scripts/20_regenerate_mouth_fixed_features.py`
regenerated all 650 existing FairFace candidates into the separate directory
`data/manifests/v2_complete_mouth_v1/`, without processing SCIN or MST-E.
It refuses overwrite and records version, input/code/model hashes, and
screening/landmark caveats. Original manifests and reviews remain unchanged.

Results: 533 automated successes and 117 exclusions, with no status changes.
Exclusions remain 68 unavailable-V2-landmark fallbacks, 34 insufficient pixel
counts, 13 no-face cases and 2 multiple-face cases. Pixel counts changed
numerically in 507 rows; ITA changed in 505 rows. All 110 previously compared
examples reproduced their experimental pixel counts and ITA at saved precision.
All rows are marked not visually revalidated for this version; 83184 has an
explicit known-misplaced-geometry flag. These are feature candidates, not an
automatically approved training subset.

366 tests passed after integration. Next steps and the proposed transform
contract are recorded in `docs/correction-training-next-steps.md`.
