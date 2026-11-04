"""Tests for scripts/13_fairface_smoke_test.py.

Only the pure selection / record-building helpers are exercised here; the
frozen pipeline itself (YuNet + Skin Mask V2 + ITA) is already covered by the
scripts/11 and scripts/12 tests and requires the real local models. Dummy
image files are used so nothing is downloaded or processed.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
for _path in (str(PROJECT_ROOT), str(SCRIPTS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Script modules start with a digit, so import them through importlib.
smoke = importlib.import_module("13_fairface_smoke_test")
select = importlib.import_module("12_select_fairface_candidates")


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
    root = tmp_path / "fairface"
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


def smoke_args(root: Path, train_csv: Path, val_csv: Path, limit: int = 3):
    """Build the argparse namespace select_candidates_frame expects."""
    return argparse.Namespace(
        image_root=root,
        train_csv=train_csv,
        val_csv=val_csv,
        seed=42,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Selection (reused from scripts/12)
# ---------------------------------------------------------------------------


def test_select_candidates_frame_blanks_official_labels(tmp_path):
    root, train_csv, val_csv = build_dataset(tmp_path)
    selection = smoke.select_candidates_frame(smoke_args(root, train_csv, val_csv))

    assert len(selection) == 3
    assert (selection["source_mst_label"].astype(str) == "").all()
    assert (selection["source_broad_mst_group"].astype(str) == "").all()
    assert (
        selection["estimated_broad_ita_group"] == "pending_ita_processing"
    ).all()
    assert (selection["group_assignment_source"] == "not_available_until_ita").all()
    assert (
        selection["selection_reason"] == "smoke_test_stratified_source_diversity"
    ).all()
    assert selection["dataset_name"].eq("FairFace").all()


def test_select_candidates_frame_is_reproducible(tmp_path):
    root, train_csv, val_csv = build_dataset(tmp_path)
    first = smoke.select_candidates_frame(smoke_args(root, train_csv, val_csv))
    second = smoke.select_candidates_frame(smoke_args(root, train_csv, val_csv))
    assert list(first["image_id"]) == list(second["image_id"])


# ---------------------------------------------------------------------------
# Pipeline record building
# ---------------------------------------------------------------------------


def test_build_pipeline_records_preserves_split_ids_and_marks_smoke_test(tmp_path):
    root, train_csv, val_csv = build_dataset(tmp_path)
    selection = smoke.select_candidates_frame(smoke_args(root, train_csv, val_csv))
    records = smoke.build_pipeline_records(selection, root)

    assert len(records) == len(selection)
    assert set(records["image_id"]) == set(selection["image_id"])
    assert records["dataset_name"].eq("FairFace").all()
    assert records["intended_use"].eq(smoke.INTENDED_USE_SMOKE_TEST).all()

    # Relative paths preserve the original split folder.
    for image_id, relative in zip(records["image_id"], records["relative_path"]):
        assert image_id == f"fairface__{relative}"
        assert relative.startswith(("train/", "val/"))
        assert Path(relative).parent.name in {"train", "val"}
