"""Tests for scripts/10_analyze_broad_mst_groups.py.

All tests build small synthetic DataFrames; no real MST-E images, models, or
CSVs are required.
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
broad = importlib.import_module("10_analyze_broad_mst_groups")


# ---------------------------------------------------------------------------
# Synthetic row builder
# ---------------------------------------------------------------------------


def group_row(
    image_id: str,
    label: object,
    ita: object,
    *,
    included: object = True,
    quality: str = "good",
    use: str = "include",
    landmarks: object = True,
    lighting: object = "well_lit",
    ratio: object = 80.0,
    subject_id: object = None,
) -> dict:
    """Build one synthetic conservative-subset row."""
    row = {
        "image_id": image_id,
        "relative_path": image_id.split("__")[-1],
        "calibration_included": included,
        "quality_review": quality,
        "ita_use": use,
        "landmarks_available": landmarks,
        "source_mst_label": label,
        "ita_degrees": ita,
        "source_lighting": lighting,
        "skin_ratio_percent": ratio,
    }
    if subject_id is not None:
        row["subject_id"] = subject_id
    return row


def frame_with_labels(labels_to_ita: dict[int, float], per_label: int = 3) -> pd.DataFrame:
    """Build a frame with `per_label` identical-ITA rows per MST label."""
    rows = []
    for label, ita in labels_to_ita.items():
        for index in range(per_label):
            rows.append(
                group_row(
                    f"mst_e__subject_{label}/img_{index}.jpg",
                    label,
                    ita,
                    ratio=70.0 + label,
                )
            )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Group assignment
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        (1, "light"),
        (2, "light"),
        (3, "light"),
        (4, "medium"),
        (5, "medium"),
        (6, "medium"),
        (7, "medium"),
        (8, "dark"),
        (9, "dark"),
        (10, "dark"),
    ],
)
def test_assign_broad_group_maps_official_labels(label, expected):
    assert broad.assign_broad_group(label) == expected


@pytest.mark.parametrize("label", [0, 11, -1, None, "", "abc", 2.5])
def test_assign_broad_group_returns_none_for_invalid(label):
    assert broad.assign_broad_group(label) is None


def test_add_broad_group_adds_column():
    frame = frame_with_labels({1: 40.0, 5: 0.0, 9: -50.0}, per_label=1)

    with_group = broad.add_broad_group(frame)

    assert "broad_group" in with_group.columns
    assert set(with_group["broad_group"]) == {"light", "medium", "dark"}


# ---------------------------------------------------------------------------
# Filtering behaviour
# ---------------------------------------------------------------------------


def test_select_included_rows_keeps_only_valid_rows():
    frame = pd.DataFrame(
        [
            group_row("ok.jpg", 3, -10.0),
            group_row("not_included.jpg", 3, -10.0, included=False),
            group_row("poor.jpg", 3, -10.0, quality="poor"),
            group_row("excluded.jpg", 3, -10.0, use="exclude"),
            group_row("no_landmarks.jpg", 3, -10.0, landmarks=False),
            group_row("bad_label.jpg", 0, -10.0),
            group_row("no_ita.jpg", 3, np.nan),
        ]
    )

    selected = broad.select_included_rows(frame)

    assert list(selected["image_id"]) == ["ok.jpg"]


def test_select_included_rows_rejects_missing_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        broad.select_included_rows(pd.DataFrame([{"image_id": "x.jpg"}]))


# ---------------------------------------------------------------------------
# Summary columns and contents
# ---------------------------------------------------------------------------


def test_summary_columns_and_group_order():
    frame = broad.add_broad_group(
        frame_with_labels({1: 40.0, 4: 0.0, 8: -40.0}, per_label=3)
    )

    summary = broad.summarize_broad_groups(frame)

    assert list(summary.columns) == list(broad.BROAD_GROUP_SUMMARY_COLUMNS)
    assert summary["broad_group"].tolist() == ["light", "medium", "dark"]
    assert summary["count"].tolist() == [3, 3, 3]


def test_summary_values_and_skin_ratio_and_distinct_subjects():
    rows = [
        group_row("mst_e__subject_1/a.jpg", 2, 10.0, ratio=80.0),
        group_row("mst_e__subject_1/b.jpg", 2, 20.0, ratio=90.0),
        group_row("mst_e__subject_2/c.jpg", 2, 30.0, ratio=85.0),
    ]
    frame = broad.add_broad_group(pd.DataFrame(rows))

    summary = broad.summarize_broad_groups(frame)
    light = summary[summary["broad_group"] == "light"].iloc[0]

    assert light["count"] == 3
    assert light["mean_ita"] == pytest.approx(20.0)
    assert light["median_ita"] == pytest.approx(20.0)
    assert light["q1_ita"] == pytest.approx(15.0)
    assert light["q3_ita"] == pytest.approx(25.0)
    assert light["minimum_ita"] == pytest.approx(10.0)
    assert light["maximum_ita"] == pytest.approx(30.0)
    assert light["mean_skin_ratio_percent"] == pytest.approx(85.0)
    assert light["median_skin_ratio_percent"] == pytest.approx(85.0)
    assert light["distinct_subjects"] == 2


def test_distinct_subjects_prefers_subject_id_column():
    rows = [
        group_row("mst_e__subject_9/a.jpg", 9, -50.0, subject_id="subject_alpha"),
        group_row("mst_e__subject_9/b.jpg", 9, -51.0, subject_id="subject_beta"),
    ]
    frame = broad.add_broad_group(pd.DataFrame(rows))

    summary = broad.summarize_broad_groups(frame)
    dark = summary[summary["broad_group"] == "dark"].iloc[0]

    assert dark["distinct_subjects"] == 2


# ---------------------------------------------------------------------------
# Lighting breakdown
# ---------------------------------------------------------------------------


def test_lighting_summary_columns():
    frame = broad.add_broad_group(
        pd.DataFrame(
            [
                group_row("a.jpg", 1, 40.0, lighting="well_lit"),
                group_row("b.jpg", 5, 0.0, lighting="poorly_lit"),
                group_row("c.jpg", 9, -50.0, lighting="well_lit"),
            ]
        )
    )

    summary = broad.summarize_broad_groups_by_lighting(frame)

    assert list(summary.columns) == list(
        broad.BROAD_GROUP_LIGHTING_SUMMARY_COLUMNS
    )
    assert len(summary) == 3


def test_lighting_summary_missing_source_lighting_is_empty():
    frame = broad.add_broad_group(
        pd.DataFrame([group_row("a.jpg", 1, 40.0)]).drop(columns=["source_lighting"])
    )

    summary = broad.summarize_broad_groups_by_lighting(frame)

    assert summary.empty
    assert list(summary.columns) == list(
        broad.BROAD_GROUP_LIGHTING_SUMMARY_COLUMNS
    )


# ---------------------------------------------------------------------------
# Small-sample warnings
# ---------------------------------------------------------------------------


def test_low_count_groups_flags_small_groups():
    frame = broad.add_broad_group(
        frame_with_labels({1: 40.0, 4: 0.0, 8: -40.0}, per_label=3)
    )

    summary = broad.summarize_broad_groups(frame)

    assert broad.low_count_groups(summary, 20) == ["light", "medium", "dark"]
    assert broad.low_count_groups(summary, 3) == []


# ---------------------------------------------------------------------------
# Separability diagnostic
# ---------------------------------------------------------------------------


def test_adjacent_separability_prefers_broad_groups_when_labels_overlap():
    # Within each broad group all labels share the same ITA (complete local
    # overlap); the broad groups are far apart.
    frame = frame_with_labels(
        {
            1: 50.0,
            2: 50.0,
            3: 50.0,
            4: 0.0,
            5: 0.0,
            6: 0.0,
            7: 0.0,
            8: -50.0,
            9: -50.0,
            10: -50.0,
        },
        per_label=3,
    )

    result = broad.adjacent_separability(frame)

    assert result["broad_mean"] == pytest.approx(1.0)
    assert result["label_mean"] < result["broad_mean"]


def test_adjacent_separability_perfect_individual_labels():
    frame = frame_with_labels(
        {label: 100.0 - label * 9 for label in range(1, 11)}, per_label=3
    )

    result = broad.adjacent_separability(frame)

    assert result["label_mean"] == pytest.approx(1.0)
    assert result["broad_mean"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Figures are written
# ---------------------------------------------------------------------------


def test_plot_functions_write_png_files(tmp_path):
    frame = broad.add_broad_group(
        frame_with_labels({1: 40.0, 4: 0.0, 8: -40.0}, per_label=3)
    )
    group_path = tmp_path / "groups.png"
    lighting_path = tmp_path / "groups_lighting.png"

    broad.plot_broad_groups(frame, group_path)
    broad.plot_broad_groups_by_lighting(frame, lighting_path)

    assert group_path.is_file() and group_path.stat().st_size > 0
    assert lighting_path.is_file() and lighting_path.stat().st_size > 0


def test_plot_handles_missing_lighting(tmp_path):
    frame = broad.add_broad_group(
        pd.DataFrame([group_row("a.jpg", 1, 40.0)]).drop(columns=["source_lighting"])
    )
    lighting_path = tmp_path / "groups_lighting.png"

    broad.plot_broad_groups_by_lighting(frame, lighting_path)

    assert lighting_path.is_file()
