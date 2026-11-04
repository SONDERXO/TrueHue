"""Tests for scripts/09_diagnose_mst_e_ita_calibration.py.

Every test builds small synthetic DataFrames, so no real MST-E images, models,
or CSVs are required.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
for _path in (str(PROJECT_ROOT), str(SCRIPTS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Script modules start with a digit, so import them through importlib.
diagnose = importlib.import_module("09_diagnose_mst_e_ita_calibration")


# ---------------------------------------------------------------------------
# Synthetic row builder
# ---------------------------------------------------------------------------


def diagnostic_row(
    image_id: str = "mst_e__subject_0/img.jpg",
    *,
    included: object = True,
    quality: str = "good",
    use: str = "include",
    landmarks: object = True,
    label: object = 3,
    ita: object = -10.0,
    lighting: object = "well_lit",
    ratio: object = 80.0,
    relative_path: str = "subject_0/img.jpg",
) -> dict:
    """Build one synthetic clean-calibration row."""
    return {
        "image_id": image_id,
        "relative_path": relative_path,
        "calibration_included": included,
        "quality_review": quality,
        "ita_use": use,
        "landmarks_available": landmarks,
        "source_mst_label": label,
        "ita_degrees": ita,
        "source_lighting": lighting,
        "skin_ratio_percent": ratio,
    }


def summarize_labels(frame: pd.DataFrame) -> pd.DataFrame:
    return diagnose.summarize_ita_by_label(frame)


# ---------------------------------------------------------------------------
# Filtering behaviour
# ---------------------------------------------------------------------------


def test_select_diagnostic_rows_keeps_only_eligible_rows():
    frame = pd.DataFrame(
        [
            diagnostic_row("valid.jpg"),
            diagnostic_row("not_included.jpg", included=False),
            diagnostic_row("poor.jpg", quality="poor"),
            diagnostic_row("excluded_use.jpg", use="exclude"),
            diagnostic_row("no_landmarks.jpg", landmarks=False),
            diagnostic_row("bad_label.jpg", label=0),
            diagnostic_row("missing_ita.jpg", ita=np.nan),
        ]
    )

    selected = diagnose.select_diagnostic_rows(frame)

    assert list(selected["image_id"]) == ["valid.jpg"]
    assert selected["source_mst_label"].tolist() == [3]


def test_select_diagnostic_rows_normalises_types():
    frame = pd.DataFrame(
        [
            diagnostic_row(
                "space.jpg",
                quality="Acceptable",
                use=" include ",
                landmarks="TRUE",
                label="4",
            )
        ]
    )

    selected = diagnose.select_diagnostic_rows(frame)

    assert len(selected) == 1
    assert selected["source_mst_label"].iloc[0] == 4
    assert selected["ita_degrees"].iloc[0] == -10.0


def test_select_diagnostic_rows_rejects_missing_required_columns():
    frame = pd.DataFrame([{"image_id": "x.jpg"}])

    with pytest.raises(ValueError, match="missing required columns"):
        diagnose.select_diagnostic_rows(frame)


# ---------------------------------------------------------------------------
# Required output columns
# ---------------------------------------------------------------------------


def test_label_summary_columns_and_labels_1_to_10():
    frame = diagnose.select_diagnostic_rows(
        pd.DataFrame([diagnostic_row(f"l{label}.jpg", label=label) for label in range(1, 11)])
    )

    summary = summarize_labels(frame)

    assert list(summary.columns) == list(diagnose.LABEL_SUMMARY_COLUMNS)
    assert summary["source_mst_label"].tolist() == list(range(1, 11))
    assert (summary["count"] == 1).all()


def test_lighting_summary_columns():
    frame = diagnose.select_diagnostic_rows(
        pd.DataFrame(
            [
                diagnostic_row("a.jpg", lighting="well_lit", label=1),
                diagnostic_row("b.jpg", lighting="poorly_lit", label=1),
                diagnostic_row("c.jpg", lighting="well_lit", label=2),
            ]
        )
    )

    summary = diagnose.summarize_ita_by_label_and_lighting(frame)

    assert list(summary.columns) == list(diagnose.LIGHTING_LABEL_SUMMARY_COLUMNS)
    assert len(summary) == 3
    assert set(summary["source_lighting"]) == {"well_lit", "poorly_lit"}


def test_diagnostic_summary_has_required_columns_and_analysis_tags():
    frame = diagnose.select_diagnostic_rows(
        pd.DataFrame(
            [
                diagnostic_row("a.jpg", label=1, lighting="well_lit", ratio=70.0),
                diagnostic_row("b.jpg", label=1, lighting="poorly_lit", ratio=60.0),
            ]
        )
    )
    conservative = diagnose.build_conservative_subset(frame)

    diagnostic = diagnose.build_diagnostic_summary(frame, conservative)

    assert list(diagnostic.columns) == list(diagnose.DIAGNOSTIC_COLUMNS)
    assert set(diagnostic["analysis"]) == {
        diagnose.ANALYSIS_FULL,
        diagnose.ANALYSIS_LIGHTING,
        diagnose.ANALYSIS_CONSERVATIVE,
        diagnose.ANALYSIS_SUBJECT,
    }


def test_subject_summary_columns_and_extraction():
    frame = diagnose.select_diagnostic_rows(
        pd.DataFrame(
            [
                diagnostic_row(
                    "mst_e__subject_5/a.jpg", relative_path="subject_5/a.jpg"
                ),
                diagnostic_row(
                    "mst_e__subject_5/b.jpg", relative_path="subject_5/b.jpg"
                ),
            ]
        )
    )

    summary = diagnose.per_subject_median_by_label(frame)

    assert list(summary.columns) == list(diagnose.SUBJECT_SUMMARY_COLUMNS)
    assert summary["subject_id"].tolist() == ["subject_5"]
    assert summary["count"].tolist() == [2]


# ---------------------------------------------------------------------------
# Missing source_lighting
# ---------------------------------------------------------------------------


def test_missing_source_lighting_does_not_break_lighting_summary():
    frame = pd.DataFrame([diagnostic_row("a.jpg")]).drop(
        columns=["source_lighting"]
    )
    selected = diagnose.select_diagnostic_rows(frame)

    summary = diagnose.summarize_ita_by_label_and_lighting(selected)

    assert summary.empty
    assert list(summary.columns) == list(diagnose.LIGHTING_LABEL_SUMMARY_COLUMNS)


def test_missing_source_lighting_makes_conservative_subset_empty():
    frame = pd.DataFrame([diagnostic_row("a.jpg")]).drop(
        columns=["source_lighting"]
    )
    selected = diagnose.select_diagnostic_rows(frame)

    conservative = diagnose.build_conservative_subset(selected)

    assert conservative.empty


def test_missing_skin_ratio_makes_conservative_subset_empty():
    frame = pd.DataFrame([diagnostic_row("a.jpg")]).drop(
        columns=["skin_ratio_percent"]
    )
    selected = diagnose.select_diagnostic_rows(frame)

    conservative = diagnose.build_conservative_subset(selected)

    assert conservative.empty


# ---------------------------------------------------------------------------
# Skin-ratio filter boundaries (40 and 95 inclusive)
# ---------------------------------------------------------------------------


def test_conservative_subset_skin_ratio_boundaries_are_inclusive():
    frame = diagnose.select_diagnostic_rows(
        pd.DataFrame(
            [
                diagnostic_row("below.jpg", ratio=39.99),
                diagnostic_row("low_edge.jpg", ratio=40.0),
                diagnostic_row("high_edge.jpg", ratio=95.0),
                diagnostic_row("above.jpg", ratio=95.01),
            ]
        )
    )

    conservative = diagnose.build_conservative_subset(frame)

    kept = sorted(conservative["skin_ratio_percent"].tolist())
    assert kept == [40.0, 95.0]


def test_conservative_subset_requires_well_lit():
    frame = diagnose.select_diagnostic_rows(
        pd.DataFrame(
            [
                diagnostic_row("well.jpg", lighting="well_lit", ratio=70.0),
                diagnostic_row("poor.jpg", lighting="poorly_lit", ratio=70.0),
                diagnostic_row("video.jpg", lighting="video", ratio=70.0),
            ]
        )
    )

    conservative = diagnose.build_conservative_subset(frame)

    assert conservative["image_id"].tolist() == ["well.jpg"]


def test_conservative_subset_handles_well_lit_spelling_variants():
    assert diagnose.normalize_lighting("Well-Lit") == diagnose.LIGHTING_WELL
    assert diagnose.normalize_lighting("well_lit") == diagnose.LIGHTING_WELL
    assert (
        diagnose.normalize_lighting("Poorly Lit") == diagnose.LIGHTING_POORLY
    )


# ---------------------------------------------------------------------------
# Counts / warnings helpers
# ---------------------------------------------------------------------------


def test_label_counts_and_low_count_warnings():
    frame = diagnose.select_diagnostic_rows(
        pd.DataFrame(
            [diagnostic_row(f"l1_{index}.jpg", label=1) for index in range(3)]
            + [diagnostic_row("l2.jpg", label=2)]
        )
    )
    summary = summarize_labels(frame)

    counts = diagnose.label_counts(frame)
    assert counts[1] == 3
    assert counts[2] == 1
    assert counts[10] == 0

    assert diagnose.low_count_labels(summary, 10) == list(range(1, 11))
