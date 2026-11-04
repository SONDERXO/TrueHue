"""Tests for scripts/14_prepare_fairface_candidate_pool.py.

Only the pure helpers are exercised here; the frozen pipeline itself (YuNet +
Skin Mask V2 + ITA) is already covered by the scripts/11, /12, and /13 tests and
requires the real local models. Dummy image files are used so nothing is
downloaded or processed.
"""

from __future__ import annotations

import argparse
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
pool = importlib.import_module("14_prepare_fairface_candidate_pool")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_metadata(path: Path, rows: list[dict]) -> Path:
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


def build_dataset(tmp_path: Path, count: int = 6) -> tuple[Path, Path, Path]:
    """Create a tiny train/val FairFace-style dataset and return its paths."""
    root = tmp_path / "FairFace"
    train_rows = []
    for index in range(1, count + 1):
        make_image(root, f"train/{index}.jpg")
        train_rows.append(
            {
                "file": f"train/{index}.jpg",
                "race": ["White", "Black", "Asian"][index % 3],
                "gender": ["Male", "Female"][index % 2],
                "age": ["20-29", "40-49", "70+"][index % 3],
            }
        )
    make_image(root, "val/1.jpg")
    train_csv = write_metadata(tmp_path / "train_labels.csv", train_rows)
    val_csv = write_metadata(
        tmp_path / "val_labels.csv",
        [{"file": "val/1.jpg", "race": "Indian", "gender": "Female", "age": "30-39"}],
    )
    return root, train_csv, val_csv


def pool_args(root: Path, train_csv: Path, val_csv: Path, limit: int = 3):
    """Build the argparse namespace build_selection_frame expects."""
    return argparse.Namespace(
        image_root=root,
        train_csv=train_csv,
        val_csv=val_csv,
        seed=42,
        limit=limit,
    )


def processed_frame(rows: list[dict]) -> pd.DataFrame:
    """Build a minimal processed-like frame with the columns the helpers use."""
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Selection and record building
# ---------------------------------------------------------------------------


def test_build_selection_frame_marks_training_candidate(tmp_path):
    root, train_csv, val_csv = build_dataset(tmp_path)
    selection = pool.build_selection_frame(pool_args(root, train_csv, val_csv))

    assert len(selection) == 3
    assert (selection["source_mst_label"].astype(str) == "").all()
    assert (selection["source_broad_mst_group"].astype(str) == "").all()
    assert (
        selection["estimated_broad_ita_group"] == "pending_ita_processing"
    ).all()
    assert (selection["group_assignment_source"] == "not_available_until_ita").all()
    assert (selection["selection_reason"] == "stratified_source_diversity").all()
    assert selection["intended_use"].eq("training_candidate").all()


def test_build_selection_frame_is_reproducible(tmp_path):
    root, train_csv, val_csv = build_dataset(tmp_path)
    first = pool.build_selection_frame(pool_args(root, train_csv, val_csv))
    second = pool.build_selection_frame(pool_args(root, train_csv, val_csv))
    assert list(first["image_id"]) == list(second["image_id"])


def test_build_pipeline_records_preserves_split_ids_and_training_use(tmp_path):
    root, train_csv, val_csv = build_dataset(tmp_path)
    selection = pool.build_selection_frame(pool_args(root, train_csv, val_csv))
    records = pool.build_pipeline_records(selection, root)

    assert len(records) == len(selection)
    assert set(records["image_id"]) == set(selection["image_id"])
    assert records["dataset_name"].eq("FairFace").all()
    assert records["intended_use"].eq("training_candidate").all()
    for image_id, relative in zip(records["image_id"], records["relative_path"]):
        assert image_id == f"fairface__{relative}"
        assert relative.startswith(("train/", "val/"))


# ---------------------------------------------------------------------------
# Smoke-test overlap
# ---------------------------------------------------------------------------


def test_verify_smoke_overlap_counts_each_image_once():
    selection = pd.DataFrame(
        {"image_id": ["a", "b", "c", "d"]}
    )
    smoke = pd.DataFrame({"image_id": ["a", "c"]})
    overlap = pool.verify_smoke_overlap(selection, smoke)

    assert overlap["selection_rows"] == 4
    assert overlap["selection_unique"] is True
    assert overlap["smoke_rows"] == 2
    assert overlap["smoke_images_in_selection"] == 2
    assert overlap["smoke_images_missing"] == 0


def test_verify_smoke_overlap_flags_missing_and_duplicates():
    selection = pd.DataFrame({"image_id": ["a", "a", "b"]})
    smoke = pd.DataFrame({"image_id": ["a", "z"]})
    overlap = pool.verify_smoke_overlap(selection, smoke)

    assert overlap["selection_unique"] is False
    assert overlap["smoke_images_in_selection"] == 1
    assert overlap["smoke_images_missing"] == 1


# ---------------------------------------------------------------------------
# Unassigned-group count and ITA summary
# ---------------------------------------------------------------------------


def test_count_unassigned_broad_groups():
    frame = processed_frame(
        [
            {"source_broad_mst_group": "", "estimated_broad_mst_group": ""},
            {"source_broad_mst_group": "", "estimated_broad_mst_group": "light"},
            {"source_broad_mst_group": "dark", "estimated_broad_mst_group": ""},
        ]
    )
    assert pool.count_unassigned_broad_groups(frame) == 1
    assert pool.count_unassigned_broad_groups(pd.DataFrame()) == 0


def test_ita_continuous_summary_reports_quartiles():
    successful = pd.DataFrame({"ita_degrees": [10.0, 20.0, 30.0, 40.0]})
    stats = pool.ita_continuous_summary(successful)

    assert stats["count"] == 4
    assert stats["minimum_ita"] == 10.0
    assert stats["q1_ita"] == pytest.approx(17.5)
    assert stats["median_ita"] == pytest.approx(25.0)
    assert stats["q3_ita"] == pytest.approx(32.5)
    assert stats["maximum_ita"] == 40.0


# ---------------------------------------------------------------------------
# Reproducible debug-visualization selection
# ---------------------------------------------------------------------------


def test_select_visualization_rows_is_reproducible_and_deduped():
    frame = processed_frame(
        [
            {
                "image_id": f"fairface__train/{index}.jpg",
                "image_path": f"/x/train/{index}.jpg",
                "skin_ratio_percent": float(index),
                "ita_degrees": float(index),
                "landmarks_available": True,
            }
            for index in range(1, 21)
        ]
    )
    first = pool.select_visualization_rows(
        frame, seed=42, random_count=5, extreme_count=2
    )
    second = pool.select_visualization_rows(
        frame, seed=42, random_count=5, extreme_count=2
    )

    assert list(first["image_id"]) == list(second["image_id"])
    assert first["image_id"].is_unique
    reasons = set(first["visualization_reason"])
    assert "lowest_mask_coverage" in reasons
    assert "highest_mask_coverage" in reasons
    assert any(reason.startswith("random_example_seed") for reason in reasons)


def test_select_visualization_rows_excludes_v1_fallback():
    frame = processed_frame(
        [
            {
                "image_id": "v2",
                "image_path": "/x/v2.jpg",
                "skin_ratio_percent": 5.0,
                "ita_degrees": -10.0,
                "landmarks_available": True,
            },
            {
                "image_id": "v1_fallback",
                "image_path": "/x/v1.jpg",
                "skin_ratio_percent": 5.0,
                "ita_degrees": 3.0,
                "landmarks_available": False,
            },
        ]
    )
    selected = pool.select_visualization_rows(
        frame, seed=42, random_count=10, extreme_count=10
    )
    assert set(selected["image_id"]) == {"v2"}


def test_select_visualization_rows_empty_when_no_v2_rows():
    frame = processed_frame(
        [
            {
                "image_id": "v1",
                "image_path": "/x/v1.jpg",
                "skin_ratio_percent": 5.0,
                "ita_degrees": 3.0,
                "landmarks_available": False,
            }
        ]
    )
    selected = pool.select_visualization_rows(
        frame, seed=42, random_count=5, extreme_count=5
    )
    assert selected.empty
