# ITA-to-MST mapping feasibility audit (21 October 2026)

Follow-up: the current-mask comparison is complete. See
`docs/mst-mask-version-comparison.md` for the detector-scale reproducibility
issue, paired 394-image results and limitations. The original 418-image
historical results below are retained unchanged.

## Question and boundary

Can a simple mapping from ITA to the proposal's ten MST categories generalize
to a different subject? This audit investigates that question before changing
the proposal or exporting FairFace groups. No correction model, production
thresholds, dataset labels, source images, or approved methodology are changed.

This is a feasibility study on already inspected development data, not an
untouched final test. Subject-separated folds prevent direct same-subject
photo overlap in each fit, but do not undo past development use or review bias.

## Recovered evidence and provenance

The old cleaned calibration table is absent from the project. The completed
review was recovered at the user's indicated Desktop location:
`C:/Users/NYTHAN/OneDrive/Desktop/mst_e_mask_quality_review.csv`.
The earlier Documents copy had pending reviews; it is not the completed file.
The completed file is Windows-1252 encoded; the reader accepts that encoding
without altering the original. A byte-identical local snapshot is retained
under `data/manifests/mst_mapping_feasibility_v1/review_source_original.csv`.

The recovered file has 1,489 measurement rows:

| Human review status | Rows |
| --- | ---: |
| good | 177 |
| acceptable | 242 |
| poor | 246 |
| pending | 643 |
| automatic_failure | 181 |

All 419 good/acceptable rows are marked include after whitespace normalization.
One included image, `subject_18/PXL_20220922_183142438.jpg`, has no exact
image/subject match in the official metadata. It is held from the mapping
test pending resolution, not automatically declared a bad image. Thus the
primary fit/evaluation uses **418 reviewed, included images from 15 subjects**.
Poor, pending and automatic-failure rows never enter the fit.

Official `mst-e_image_details.csv` contains 1,546 rows, 19 subjects and three
duplicate image/subject keys. Those duplicates agree on MST and lighting;
two disagree on pose. They are joined once per reviewed image and never counted
as multiple measurements. Four measurement rows lack an exact metadata match;
only one of those was included by the reviewer. No matched row disagrees on
the official MST label. Raw measurement/metadata availability and exclusions
are retained in the audit; no label is guessed from a filename variant.

These are historical V2 measurements, not regenerated complete-mouth-version
features. The historical run has no available model/code hash. Results cannot
be silently transferred to the newer mask version. The review is also a
selected subset, not a random sample of all available MST-E images.

## Fixed test design

Implemented in `src/ita_estimation/mapping_feasibility.py` and script 26:

1. Hold out all images of one subject, fit using only other subjects, and
   repeat for all 15 reviewed subjects. Subject IDs are dataset folder IDs.
2. Give each training subject equal total weight so subjects with more photos
   do not dominate the monotone mapping.
3. Compare three predeclared simple rules, without tuning on held-out results:
   a training-subject median-label baseline; a decreasing isotonic ITA-to-label
   mapping rounded to 1-10; and nearest class-median ITA prototypes, formed
   from subject medians. Ties use deterministic rules.
4. Record exact category accuracy, accuracy within one category, and ordinal
   mean absolute error (MAE, in category steps). Report image-weighted and
   equal-subject summaries, label coverage and lighting breakdowns.

Higher ITA is constrained toward a lower/lighter label in the monotone rule.
This is a defensible exploratory candidate for an ordered lookup, not proof
that every classifier should be monotone or that all possible mappings fail.
There is no image-random train/test split, final fitted lookup export, or
FairFace assignment. The nearest-prototype rule need not be monotone.

## Subject-support limitation

MST 7 and 10 each have one subject in the official metadata. After review,
MST 4, 5, 7, 9 and 10 each have only one represented subject. When that subject
is held out, its exact category has no training-subject examples. Predictions
can still interpolate ordinal values, but that does not supply evidence from
an independent training subject in the category.

This means neither a conventional subject-separated holdout nor this cross-
validation can provide well-supported training and test subjects for every
one of the ten labels using the reviewed subset. Report that limitation;
do not solve it by splitting one person's photos across training and test.

## Exploratory results

All three rules below use the same 418 images and 15 held-out-subject folds.

| Rule | Exact accuracy | Within one category | Ordinal MAE |
| --- | ---: | ---: | ---: |
| Training-subject median label | 13.9% | 22.0% | 2.84 |
| Monotone ITA lookup | 12.4% | 28.5% | 2.42 |
| Nearest class-median ITA | 16.5% | 34.0% | 3.03 |

The monotone rule reduces mean category error relative to the constant baseline
but does not improve exact accuracy. Nearest prototypes improve exact accuracy
slightly but have worse category MAE. Neither is supported as a reliable
ten-category mapping by this test. No acceptance threshold was selected after
seeing these numbers, and no uncertainty/generalization claim is made from
15 selected subjects.

Equal-subject exact accuracies are 6.7% for the baseline, 7.5% for the monotone
rule and 12.9% for prototypes. Equal-subject MAEs are 3.00, 2.71 and 3.46.
Image-weighted scores should therefore not be the only result presented.

Reviewed inputs include 162 poorly-lit, 255 well-lit and one metadata `video`
row. Lighting summaries reuse the out-of-subject predictions from the full
fit, rather than selecting a better-looking subset and hiding the rest. They
are descriptive: subjects and label mixtures differ between lighting groups.
Full metrics and per-image predictions are saved, including whether each
held-out image's label was represented among training subjects.

## Interpretation and next action within the proposed method

We now have a measured feasibility result instead of concluding that overlap
alone rules out mapping. The result is currently weak and subject support is
limited. It does not establish that every possible mapping approach fails,
and it does not justify silently replacing the proposal.

Before adopting a lookup:

- Resolve the unmatched included metadata row and preserve the review decisions.
- Evaluate the same reviewed sources under the current frozen mask version
  before choosing operational thresholds; keep historical and new runs separate.
- Establish what mapping error is tolerable for the intended downstream use,
  and how insufficient independent subjects will be handled. Do not claim
  precise category estimation on unsupported evidence.
- If further development is justified, keep it separate from a genuinely
  reserved final evaluation. Earlier MST-E diagnostic use must be disclosed.

No changes to FairFace groups, tone-dependent severity, SCIN's role or final
thesis objectives are made by this audit. The adviser can review these concrete
results when deciding whether more mapping work or a formal revision is needed.

## Reproduction and checks

```text
venv/Scripts/python.exe scripts/26_audit_mst_mapping_feasibility.py --review "C:/Users/NYTHAN/OneDrive/Desktop/mst_e_mask_quality_review.csv"
```

Outputs under `data/manifests/mst_mapping_feasibility_v1/`: recovered input
snapshot, metadata audit, reviewed included rows, subject/label coverage,
held-out predictions, overall/per-label/per-lighting metrics and JSON summary.
Existing outputs are protected. Original files remain unchanged; input hashes
are recorded. Tests cover fold separation, equal-subject weights, monotone
direction/bounds and inconsistent subject labels. All reported counts and
metrics are recomputed from the recovered file, not copied from historical logs.
