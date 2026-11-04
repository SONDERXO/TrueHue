# MST-E ITA Calibration Diagnostic Protocol

## Purpose

The cleaned MST-E calibration table (`mst_e_ita_calibration_clean.csv`) contains
trusted Skin Mask V2 measurements with official MST-E ground-truth labels 1-10.
When the labels are ordered by their median computed ITA, they do **not** form a
clean monotonic sequence.

This document describes the diagnostic, sensitivity-style analysis performed by
`scripts/09_diagnose_mst_e_ita_calibration.py` **before** any ITA-to-MST mapping
thresholds are chosen. The goal is to understand *why* the labels do not order
cleanly, not to force them to.

**This analysis does not create final thresholds and does not train the
correction model.** No change is made to face detection, Skin Mask V2, CIELAB
conversion, or ITA computation.

## Input and row filter

Input:

```
data/manifests/mst_e_ita_calibration_clean.csv
```

A row enters the diagnostic set only when **all** of the following hold:

- `calibration_included` is `True`
- `quality_review` is `good` or `acceptable`
- `ita_use` is `include`
- `landmarks_available` is `True`
- `ita_degrees` is not null
- `source_mst_label` is an integer from 1 to 10

This is the same trusted V2 subset used by
`scripts/08_analyze_ita_by_mst.py`: 419 rows.

## Analyses

### A. Full included data

Group all trusted rows by official MST label and report, per label 1-10:

`count, median_ita, q1_ita, q3_ita, minimum_ita, maximum_ita`

This is the baseline view. It is the table the other analyses are compared
against, and the one used if a subset turns out to be misleading.

### B. Lighting-stratified data

Group by official MST label **and** `source_lighting`, and report the same ITA
statistics. Boxplots separated by lighting condition are saved to
`outputs/figures/mst_e_ita_by_label_lighting.png`.

This is the most important diagnostic: the manually recorded `source_lighting`
(`well_lit`, `poorly_lit`) changes computed ITA as strongly as, or more strongly
than, the MST label itself.

### C. Conservative well-lit subset

Keep rows where:

- `source_lighting == well_lit`, **and**
- `skin_ratio_percent` is between **40 and 95 inclusive**.

Report the same ITA statistics per label, and write the retained rows to
`data/manifests/mst_e_ita_conservative_subset.csv`.

**This 40-95% band and the well-lit restriction are diagnostic choices for a
sensitivity analysis. They are not permanent thresholds, are not validated, and
must not be treated as final. A different band may be relabelled later; the point
of this subset is to see how much of the messy ordering is explained by exposure
and mask coverage.**

### Per-subject breakdown

The dataset's own subject folder (`subject_N`) is extracted from `image_id` /
`relative_path`, and the per-subject median ITA is computed, grouped by official
MST label. The subject identifier is only the dataset folder name: it carries no
personal information and the analysis never classifies a person.

A scatter of per-subject medians is saved to
`outputs/figures/mst_e_ita_by_label_subject.png`. It exists to check whether a
label is dominated by one or two subjects rather than by the tone range.

### ITA vs skin-mask ratio

A scatter of computed ITA against `skin_ratio_percent`, coloured by MST label,
is saved to `outputs/figures/mst_e_ita_vs_skin_ratio.png`. The 40% and 95% guide
lines mark the conservative band.

## Outputs

| Output | Path |
|--------|------|
| Stacked diagnostic summary (A, B, C, per-subject) | `data/manifests/mst_e_ita_diagnostic_summary.csv` |
| Conservative well-lit subset rows | `data/manifests/mst_e_ita_conservative_subset.csv` |
| ITA by label and lighting boxplots | `outputs/figures/mst_e_ita_by_label_lighting.png` |
| Per-subject median ITA scatter | `outputs/figures/mst_e_ita_by_label_subject.png` |
| ITA vs skin ratio scatter | `outputs/figures/mst_e_ita_vs_skin_ratio.png` |

The diagnostic summary is one long table with this shape:

```
analysis, source_mst_label, source_lighting, subject_id,
count, median_ita, q1_ita, q3_ita, minimum_ita, maximum_ita
```

`analysis` is one of `full_included`, `by_lighting`, `conservative_well_lit`,
`per_subject`.

### Why filtering is not hiding unfavourable results

Every filtered view is reported **next to** the full included data, never instead
of it. The full-data column is always written first, the lighting breakdown keeps
the poorly-lit rows in view, and the console output prints the sample count per
label after every filter together with a warning for any label with fewer than 10
images. The purpose is to explain a diagnostic pattern, not to make an
unfavourable label disappear.

## Small-sample warnings

Any label with fewer than 10 rows in a given subset triggers a printed warning.
In the current data this fires for:

- **Poorly-lit** MST 6 (9) and MST 10 (6).
- **Well-lit** MST 10 (9), and therefore the conservative subset MST 10 (9).

Small counts are reported, not removed.

## What the current run shows (illustrative, not a decision)

Full included set (419 rows): median ITA is **not** monotonic in MST label.
MST 1 has the highest median, but labels 2, 3 and 7 have lower medians than
labels 4, 5 and 6.

Lighting explains much of the disorder:

- Under `poorly_lit`, every label's median ITA is negative and clustered roughly
  between -63 and -72 degrees; label differences largely collapse.
- Under `well_lit`, the medians recover and are more spread out, but the
  ordering is still noisy.

This is consistent with ITA being a camera/lighting-dependent quantity rather
than a measurement of a person's true or permanent skin tone. It is the reason
thresholds must not be derived from a single pooled pass.

## Explicit non-goals

- No ITA-to-MST thresholds are produced here. That is a later, separate decision.
- The correction model is not trained, validated, or evaluated here.
- The conservative subset is not a permanent rule and is not a claim that
  non-well-lit or unusual-coverage images are invalid.
- No person is classified, described, or assessed. Only mask measurements and
  lighting metadata are grouped.

## How to run

From the project root:

```
python scripts/09_diagnose_mst_e_ita_calibration.py
python scripts/09_diagnose_mst_e_ita_calibration.py --min-per-label 10
```

Tests:

```
pytest tests/test_diagnose_mst_e_ita_calibration.py -q
```
