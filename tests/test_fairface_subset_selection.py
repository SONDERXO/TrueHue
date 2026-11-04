"""Tests for scripts/12_select_fairface_candidates.py.

All tests use synthetic metadata and temporary dummy image files only.
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
select = importlib.import_module("12_select_fairface_candidates")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RACES = ["White", "Black", "Asian", "Indian", "Others"]
GENDERS = ["Male", "Female"]
AGES = ["0-2", "3-9", "20-29", "40-49", "70+"]


def write_metadata(
    path: Path,
    rows: list[dict],
) -> Path:
    """Write a FairFace-style metadata CSV."""
    pd.DataFrame(
        [
            {
                "file": row["file"],
                "age": row.get("age", "20-29"),
                "gender": row.get("gender", "Male"),
                "race": row.get("race", "White"),
                "service_test": row.get("service_test", "FALSE"),
            }
            for row in rows
        ]
    ).to_csv(path, index=False)
    return path


def make_image(root: Path, relative: str) -> Path:
    """Create a dummy image file and return its path."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"not a real image")
    return path


def pool_frame(rows: list[tuple[str, str, str, str, str]]) -> pd.DataFrame:
    """Build a candidate-pool frame from (id, split, race, gender, age) rows."""
    return pd.DataFrame(
        [
            {
                "image_id": image_id,
                "image_path": f"C:/x/{image_id}.jpg",
                "source_split": split,
                select.RACE_FIELD: race,
                select.GENDER_FIELD: gender,
                select.AGE_FIELD: age,
            }
            for image_id, split, race, gender, age in rows
        ]
    )


# ---------------------------------------------------------------------------
# Column / split detection
# ---------------------------------------------------------------------------


def test_detect_column_aliases():
    columns = ["file", "age", "gender", "race"]
    assert select.detect_column(columns, select.FILE_COLUMN_CANDIDATES) == "file"
    assert select.detect_column(columns, select.RACE_COLUMN_CANDIDATES) == "race"
    assert select.detect_column(["img"], select.FILE_COLUMN_CANDIDATES) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("train", "train"),
        ("training", "train"),
        ("val", "validation"),
        ("valid", "validation"),
        ("validation", "validation"),
        ("", "validation"),
    ],
)
def test_normalize_split(value, expected):
    assert select.normalize_split(value) == expected


# ---------------------------------------------------------------------------
# Image path resolution
# ---------------------------------------------------------------------------


def test_resolve_image_path_variants(tmp_path):
    root = tmp_path / "fairface"
    direct = make_image(root, "train/1.jpg")
    flat = make_image(root, "2.jpg")
    split_named = make_image(root, "train/3.jpg")

    assert select.resolve_image_path(root, "train", "train/1.jpg") == direct
    assert select.resolve_image_path(root, "train", "2.jpg") == flat
    assert select.resolve_image_path(root, "train", "3.jpg") == split_named
    assert select.resolve_image_path(root, "train", "missing.jpg") is None


def test_resolve_image_path_blank_returns_none(tmp_path):
    assert select.resolve_image_path(tmp_path, "train", "") is None
    assert select.resolve_image_path(tmp_path, "train", None) is None


# ---------------------------------------------------------------------------
# Metadata loading
# ---------------------------------------------------------------------------


def test_load_split_metadata_reads_and_drops_missing(tmp_path):
    root = tmp_path / "fairface"
    make_image(root, "train/1.jpg")
    make_image(root, "train/2.jpg")
    csv_path = write_metadata(
        tmp_path / "train.csv",
        [
            {"file": "train/1.jpg", "race": "White", "gender": "Male", "age": "20-29"},
            {"file": "train/2.jpg", "race": "Black", "gender": "Female", "age": "30-39"},
            {"file": "train/999.jpg", "race": "Asian"},  # missing on disk
        ],
    )

    frame, total, missing = select.load_split_metadata(csv_path, "train", root)

    assert total == 3
    assert missing == 1
    assert len(frame) == 2
    assert list(frame["image_id"]) == [
        "fairface__train/1.jpg",
        "fairface__train/2.jpg",
    ]
    assert list(frame["source_split"]) == ["train", "train"]
    assert list(frame[select.RACE_FIELD]) == ["White", "Black"]
    assert set(frame.columns) == {
        "image_id",
        "image_path",
        "source_split",
        select.RACE_FIELD,
        select.GENDER_FIELD,
        select.AGE_FIELD,
    }


def test_load_split_metadata_missing_file_raises(tmp_path):
    with pytest.raises(select.MetadataError):
        select.load_split_metadata(tmp_path / "nope.csv", "train", tmp_path)


def test_load_split_metadata_missing_file_column_raises(tmp_path):
    csv_path = tmp_path / "bad.csv"
    pd.DataFrame([{"a": 1, "b": 2}]).to_csv(csv_path, index=False)
    with pytest.raises(select.MetadataError):
        select.load_split_metadata(csv_path, "train", tmp_path)


# ---------------------------------------------------------------------------
# Candidate pool
# ---------------------------------------------------------------------------


def test_stack_candidate_pool_dedups_and_sorts():
    first = pool_frame(
        [
            ("fairface__b.jpg", "train", "White", "Male", "20-29"),
            ("fairface__a.jpg", "train", "Black", "Female", "30-39"),
        ]
    )
    second = pool_frame(
        [
            ("fairface__a.jpg", "validation", "White", "Male", "40-49"),
            ("fairface__c.jpg", "validation", "Asian", "Male", "20-29"),
        ]
    )
    pool = select.stack_candidate_pool([first, second])
    assert list(pool["image_id"]) == [
        "fairface__a.jpg",
        "fairface__b.jpg",
        "fairface__c.jpg",
    ]
    # The first occurrence of a duplicate id wins.
    assert pool.loc[pool["image_id"] == "fairface__a.jpg", "source_split"].iloc[0] == "train"


# ---------------------------------------------------------------------------
# Stratified sampling
# ---------------------------------------------------------------------------


def big_pool() -> pd.DataFrame:
    """A pool with many rows in every race/gender/age combination."""
    rows = []
    for race in RACES:
        for gender in GENDERS:
            for age in AGES:
                for index in range(20):
                    rows.append(
                        (
                            f"fairface__{race}_{gender}_{age}_{index}.jpg",
                            "train",
                            race,
                            gender,
                            age,
                        )
                    )
    return pool_frame(rows)


def test_stratified_sample_is_reproducible_with_seed_42():
    pool = big_pool()
    first = select.stratified_sample(pool, limit=200, seed=42)
    second = select.stratified_sample(pool, limit=200, seed=42)
    assert list(first["image_id"]) == list(second["image_id"])


def test_stratified_sample_different_seed_changes_selection():
    pool = big_pool()
    seed_42 = select.stratified_sample(pool, limit=200, seed=42)
    seed_7 = select.stratified_sample(pool, limit=200, seed=7)
    assert list(seed_42["image_id"]) != list(seed_7["image_id"])


def test_stratified_sample_respects_limit_and_spreads_across_races():
    pool = big_pool()
    selected = select.stratified_sample(pool, limit=100, seed=42)
    assert len(selected) == 100
    # Every race must be represented (diversity, not one dominant group).
    assert set(selected[select.RACE_FIELD]) == set(RACES)


def test_stratified_sample_selects_650_when_enough_input():
    pool = big_pool()  # 5 races * 2 genders * 5 ages * 20 = 1000 rows
    assert len(pool) == 1000
    selected = select.stratified_sample(pool, limit=select.DEFAULT_LIMIT, seed=42)
    assert len(selected) == 650
    assert list(selected.columns) == list(pool.columns)


def test_stratified_sample_limit_larger_than_pool_returns_all():
    pool = pool_frame(
        [
            ("a", "train", "White", "Male", "20-29"),
            ("b", "train", "Black", "Female", "30-39"),
        ]
    )
    selected = select.stratified_sample(pool, limit=100, seed=42)
    assert len(selected) == 2


# ---------------------------------------------------------------------------
# Limit resolution and smoke test
# ---------------------------------------------------------------------------


def test_resolve_limit_smoke_test_forces_20():
    assert select.resolve_limit(None, True) == select.SMOKE_TEST_LIMIT
    assert select.resolve_limit(500, True) == select.SMOKE_TEST_LIMIT


def test_resolve_limit_default_and_explicit():
    assert select.resolve_limit(None, False) == select.DEFAULT_LIMIT
    assert select.resolve_limit(123, False) == 123


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def test_build_output_sets_fixed_fields_and_columns():
    selected = select.stratified_sample(big_pool(), limit=10, seed=42)
    output = select.build_output(selected, seed=42, smoke_test=False)

    assert list(output.columns) == list(select.OUTPUT_COLUMNS)
    assert len(output) == 10
    assert set(output["dataset_name"]) == {"FairFace"}
    assert set(output["source_mst_label"]) == {""}
    assert set(output["source_broad_mst_group"]) == {""}
    assert set(output["estimated_broad_ita_group"]) == {"pending_ita_processing"}
    assert set(output["group_assignment_source"]) == {"not_available_until_ita"}
    assert set(output["intended_use"]) == {"training_candidate"}
    assert set(output["selection_seed"]) == {42}


def test_build_output_marks_smoke_test_reason():
    selected = select.stratified_sample(big_pool(), limit=5, seed=42)
    output = select.build_output(selected, seed=42, smoke_test=True)
    assert set(output["selection_reason"]) == {
        "smoke_test_stratified_source_diversity"
    }


def test_build_output_empty_frame_has_columns():
    output = select.build_output(pd.DataFrame(), seed=42, smoke_test=False)
    assert list(output.columns) == list(select.OUTPUT_COLUMNS)
    assert output.empty
