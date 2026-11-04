"""Tests for scripts/11b_select_scin_subset.py.

All tests use synthetic pandas DataFrames only: no real SCIN metadata, no
images, and no network access are required.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
for _path in (str(PROJECT_ROOT), str(SCRIPTS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Script modules start with a digit, so import them through importlib.
subset = importlib.import_module("11b_select_scin_subset")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

IMAGE_PATH_COLUMNS = ["image_1_path", "image_2_path", "image_3_path"]


def make_cases(rows: list[dict]) -> pd.DataFrame:
    """Build a synthetic cases frame with the three image path slots."""
    records = []
    for row in rows:
        record = {"case_id": row["case_id"]}
        for column in IMAGE_PATH_COLUMNS:
            record[column] = row.get(column)
        records.append(record)
    return pd.DataFrame(records)


def make_labels(rows: list[dict], india: bool = True) -> pd.DataFrame:
    """Build a synthetic labels frame with a single eMST column."""
    column = (
        subset.EMST_INDIA_COLUMN if india else subset.EMST_US_COLUMN
    )
    return pd.DataFrame(
        [{"case_id": row["case_id"], column: row.get("emst")} for row in rows]
    )


def valid_frame(label_case_pairs: list[tuple[int, str]]) -> pd.DataFrame:
    """Build a valid-rows frame: one image per (label, case) pair."""
    rows = [
        {
            "case_id": case_id,
            "image_slot": 1,
            "image_path": f"{case_id}.png",
            "source_mst_label": label,
            "source_broad_mst_group": subset.broad_group_for_label(label),
        }
        for label, case_id in label_case_pairs
    ]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 1. Valid MST 1-10 -> broad group mapping
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
def test_valid_mst_maps_to_broad_group(label, expected):
    assert subset.broad_group_for_label(label) == expected


@pytest.mark.parametrize("label", [0, 11, -1, None, "", "abc", 2.5])
def test_invalid_mst_has_no_broad_group(label):
    assert subset.broad_group_for_label(label) is None


# ---------------------------------------------------------------------------
# 2. Invalid / missing MST removal
# ---------------------------------------------------------------------------


def test_attach_official_emst_drops_invalid_and_missing():
    cases = make_cases(
        [
            {"case_id": "a", "image_1_path": "a.png"},
            {"case_id": "b", "image_1_path": "b.png"},
            {"case_id": "c", "image_1_path": "c.png"},
            {"case_id": "d", "image_1_path": "d.png"},
            {"case_id": "e", "image_1_path": "e.png"},
        ]
    )
    labels = make_labels(
        [
            {"case_id": "a", "emst": 3.0},   # valid
            {"case_id": "b", "emst": 11.0},  # out of range
            {"case_id": "c", "emst": 0.0},   # out of range
            {"case_id": "d", "emst": None},  # missing
            # case "e" has no label row at all
        ]
    )
    image_rows = subset.expand_cases_to_image_rows(
        cases, "case_id", IMAGE_PATH_COLUMNS
    )
    valid = subset.attach_official_emst(image_rows, labels, "case_id", subset.EMST_INDIA_COLUMN)

    assert list(valid["case_id"]) == ["a"]
    assert list(valid["source_mst_label"]) == [3]
    assert list(valid["source_broad_mst_group"]) == ["light"]


def test_expand_cases_drops_empty_image_paths():
    cases = make_cases(
        [
            {
                "case_id": "a",
                "image_1_path": "a1.png",
                "image_2_path": None,
                "image_3_path": "a3.png",
            }
        ]
    )
    rows = subset.expand_cases_to_image_rows(cases, "case_id", IMAGE_PATH_COLUMNS)
    assert list(rows["image_slot"]) == [1, 3]
    assert list(rows["image_path"]) == ["a1.png", "a3.png"]


# ---------------------------------------------------------------------------
# 3. One-image-per-case preference
# ---------------------------------------------------------------------------


def test_one_image_per_case_is_preferred():
    rows = []
    for case_index in range(10):
        for slot in (1, 2, 3):
            rows.append(
                {
                    "case_id": f"case_{case_index}",
                    "image_slot": slot,
                    "image_path": f"case_{case_index}_{slot}.png",
                    "source_mst_label": 1,
                    "source_broad_mst_group": "light",
                }
            )
    frame = pd.DataFrame(rows)

    selected = subset.select_group_candidates(frame, per_group=5, seed=42)

    assert len(selected) == 5
    assert selected["case_id"].nunique() == 5
    assert selected["multiple_images_from_same_case"].tolist() == [False] * 5
    # Every selected row is image slot 1: the first image of its case.
    assert set(selected["image_slot"]) == {1}


# ---------------------------------------------------------------------------
# 4. Reproducible sampling with seed 42
# ---------------------------------------------------------------------------


def test_sampling_is_reproducible_with_seed_42():
    pairs = [(1, f"case_{index:03d}") for index in range(200)]
    frame = valid_frame(pairs)

    first = subset.select_group_candidates(frame, per_group=40, seed=42)
    second = subset.select_group_candidates(frame, per_group=40, seed=42)

    assert list(first["case_id"]) == list(second["case_id"])


def test_different_seed_can_change_selection():
    pairs = [(1, f"case_{index:03d}") for index in range(200)]
    frame = valid_frame(pairs)

    seed_42 = subset.select_group_candidates(frame, per_group=40, seed=42)
    seed_7 = subset.select_group_candidates(frame, per_group=40, seed=7)

    assert list(seed_42["case_id"]) != list(seed_7["case_id"])


# ---------------------------------------------------------------------------
# 5. Correct per-group selection when enough input exists
# ---------------------------------------------------------------------------


def test_select_candidates_returns_per_group_when_enough_input():
    pairs = []
    # 80 unique cases in each broad group (more than the requested 75).
    for index in range(80):
        pairs.append((2, f"light_{index:03d}"))
        pairs.append((5, f"medium_{index:03d}"))
        pairs.append((9, f"dark_{index:03d}"))
    frame = valid_frame(pairs)

    selected, warnings = subset.select_candidates(frame, per_group=75, seed=42)

    assert warnings == []
    counts = selected["source_broad_mst_group"].value_counts().to_dict()
    assert counts == {"light": 75, "medium": 75, "dark": 75}
    assert len(selected) == 225
    # One image per case everywhere, so nothing is marked as repeated.
    assert not selected["multiple_images_from_same_case"].any()

    output = subset.build_selection_output(
        selected, subset.GROUP_SOURCE_EMST_INDIA, 42
    )
    assert list(output.columns) == list(subset.OUTPUT_COLUMNS)
    assert len(output) == 225
    assert output["intended_use"].unique().tolist() == ["training_candidate"]
    assert output["group_assignment_source"].unique().tolist() == [
        "official_scin_emst_india"
    ]


# ---------------------------------------------------------------------------
# 6. Graceful warning when a group has fewer rows than requested
# ---------------------------------------------------------------------------


def test_short_group_produces_warning_and_does_not_raise():
    pairs = []
    for index in range(80):
        pairs.append((2, f"light_{index:03d}"))
    for index in range(3):  # dark only has 3 unique cases
        pairs.append((9, f"dark_{index:03d}"))
    frame = valid_frame(pairs)

    selected, warnings = subset.select_candidates(frame, per_group=75, seed=42)

    dark_count = int((selected["source_broad_mst_group"] == "dark").sum())
    assert dark_count == 3
    assert any("dark" in warning for warning in warnings)
    # No medium rows existed at all, so that group warns too but returns none.
    assert any("medium" in warning for warning in warnings)


def test_short_group_reuses_images_and_marks_them():
    rows = []
    for case_index in range(2):
        for slot in (1, 2, 3):
            rows.append(
                {
                    "case_id": f"dark_{case_index}",
                    "image_slot": slot,
                    "image_path": f"dark_{case_index}_{slot}.png",
                    "source_mst_label": 9,
                    "source_broad_mst_group": "dark",
                }
            )
    frame = pd.DataFrame(rows)

    selected = subset.select_group_candidates(frame, per_group=5, seed=42)

    assert len(selected) == 5
    # The first image of each case is a primary row, the rest are extras.
    assert int(selected["multiple_images_from_same_case"].sum()) == 3
    assert selected["case_id"].nunique() == 2


# ---------------------------------------------------------------------------
# File detection and column detection
# ---------------------------------------------------------------------------


def test_detect_metadata_files_handles_dataset_prefix(tmp_path):
    cases = tmp_path / "dataset_scin_cases.csv"
    labels = tmp_path / "dataset_scin_labels.csv"
    questions = tmp_path / "dataset_scin_label_questions.csv"
    for path in (cases, labels, questions):
        path.write_text("x", encoding="utf-8")

    detected_cases, detected_labels = subset.detect_metadata_files(tmp_path)

    assert detected_cases == cases
    assert detected_labels == labels


def test_detect_metadata_files_reports_ambiguity(tmp_path):
    for name in (
        "dataset_scin_cases.csv",
        "other_cases.csv",
        "dataset_scin_labels.csv",
    ):
        (tmp_path / name).write_text("x", encoding="utf-8")

    with pytest.raises(subset.MetadataFileError):
        subset.detect_metadata_files(tmp_path)


def test_detect_emst_column_prefers_india_and_falls_back_to_us():
    india = ["case_id", subset.EMST_INDIA_COLUMN, subset.EMST_US_COLUMN]
    assert subset.detect_emst_column(india) == (
        subset.EMST_INDIA_COLUMN,
        subset.GROUP_SOURCE_EMST_INDIA,
    )

    us_only = ["case_id", subset.EMST_US_COLUMN]
    assert subset.detect_emst_column(us_only) == (
        subset.EMST_US_COLUMN,
        subset.GROUP_SOURCE_EMST_US,
    )


def test_detect_emst_column_missing_raises():
    with pytest.raises(subset.MetadataFileError):
        subset.detect_emst_column(["case_id", "something_else"])
