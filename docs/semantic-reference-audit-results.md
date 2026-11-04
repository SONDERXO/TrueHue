# Semantic classes versus skin-only reference regions

26 October 2026. Script94 audited the55 cached category maps from the framing
comparison without running a model or changing masks. Nine maps share exact
coordinates with the three completed polygon frames;48 prior native point
observations were also read. These repeat known development sources and are
not an independent evaluation set.

[Local gallery](../outputs/semantic_reference_audit_v1/review.html) |
[Counts and provenance](../outputs/semantic_reference_audit_v1/summary.json) |
[Verification](../outputs/semantic_reference_audit_v1/verification.json) |
[Fixed protocol](semantic-reference-audit-protocol.md).

## Finding: model classes do not match the required exclusions

The model's face-skin class is broad. It includes the eyes, brows, mouth and
most painted regions in these references. This is evidence of a mismatch
between its semantic categories and TrueHue's desired measurement/correction
mask, not proof that it is malfunctioning at its own classification task.

| Reference/input | Labeled skin predicted face skin | Feature exclusion pixels predicted face skin |
| --- | ---: | ---: |
| 40048 source and unchanged | 100.00% | 3458/3458 |
| 40048 dark | 99.60% | 3425/3458 |
| 40048 mild | 100.00% | 3458/3458 |
| 60162 source | 99.86% | 3739/3739 |
| 60162 dark | 99.69% | 3650/3739 |
| 60162 color | 99.90% | 3739/3739 |
| 16798 clean | 99.55% | 3187/3187 |
| 16798 shifted | 99.55% | 3187/3187 |

On16798, the painted reference regions total6003pixels. Face-skin selects
5659(94.27%) clean and5784(96.35%) shifted. Including body-skin adds just two
shifted paint pixels, yielding5786. Thus changing from face/body to face-only
does not provide useful paint/feature separation on these frames.

All12 labeled skin points per variant are predicted face-skin, but so are all3
paint points per variant. Two of4 clean hair points and one of4 shifted hair
points are also predicted face-skin. Among five other/non-skin points, two are
predicted face-skin per variant. These are sparse diagnostic labels, not an
overall segmentation error rate.

These are **semantic predictions alone**, not the final combined pipeline mask.
Earlier combined masks excluded the three paint points using other constraints;
that does not demonstrate that the learned semantic model recognized paint.
The paint-area disagreements also preserve the distinction between passing a
few points and excluding a whole painted region.

## Reference handling and inspection

Original polygon coordinates/notes/labels remain unchanged. For the descriptive
audit only, Codex inspected numbered existing exclusions:16798polygons1-6 are
paint;7-13 are features/nostrils/mouth. All40048/60162 exclusion polygons are
features. This grouping is not an additional reviewer annotation or a new
training label. Paint takes priority at overlaps; each group's union is checked
against the exact original excluded raster. Per-polygon class histograms are
saved, so conclusions do not depend on this descriptive grouping alone.

Full and one-pixel-interior scoring are retained. Outside polygons and uncertain
pixels remain unscored; no uncertain polygons were supplied, which does not
prove boundary certainty. Unmarked neck is not a negative region.

All nine original/category/disagreement boards and three numbered-polygon
overlays were inspected. Face boundaries are broadly localized while feature
and paint areas remain green in the categorical maps and red in disagreement
panels. Occasional others/clothes predictions inside paint do not form a reliable
paint veto. Predicted body skin around the neck does not establish same-person
neck localization or neck-correction quality.

## Decision and next design checkpoint

Retain the semantic model only as experimental coarse face/hair/background
evidence in the current development pipeline. Do not promote its face-skin
class to the final skin-only mask or relax geometric/color gates on the basis
of its high labeled-skin coverage. No existing runtime policy is changed.

The next design checkpoint must separate three requirements: actual face
contour coverage, explicit anatomical-feature exclusion, and paint/non-skin
protection. A replacement or combined approach needs evidence for each on the
fixed references and broader existing regression set. Further crop/margin
tuning alone cannot establish paint recognition. Define and predeclare that
comparison before implementing another rule or downloading a new model;
preserve the proposal's user workflow and on-device constraints.

No input regeneration, eligibility change or model fitting is justified by this
audit. Previous reviewer decisions, technical holds, fold limitations and all
failed experiments remain part of the record.

## Verification and thesis distinctions

All55 native category maps are uint8 with known classes and unchanged dimensions.
Reference raster reconstruction matches all three saved label images. Class
histograms sum to exact region sizes. Independent boolean selection counts
reproduce full/interior scores on all nine reference maps; disjoint region
totals cover every reference pixel. All recorded input, model, label, prior
decision and exposure-ledger hashes remain unchanged. Zero new inference calls,
zero model fits. All471 tests pass in11.74s using a workspace-local temporary
directory.

The learned semantic model remains an addition to the proposal's rule-based
skin selection, with these limitations explicitly recorded. Three exposed
mixed224/256 manual references are development diagnostics, not final
segmentation evaluation or calibrated color truth; annotation is not an added
application-user requirement. Neck support, validated MST mapping, final data/
split/evaluation, expert MOS and Android remain unfinished. No proposal
amendment or adviser approval is implied.
