"""Tests for src/data_preparation/training_manifest.py and the pure helpers of
scripts/11_prepare_training_manifests.py.

All tests use synthetic rows and temporary files only: no real FairFace/SCIN
images, models, or metadata are required.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
for _path in (str(PROJECT_ROOT), str(SCRIPTS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from src.data_preparation import training_manifest as tm  # noqa: E402

# Script modules start with a digit, so import them through importlib.
script11 = importlib.import_module("11_prepare_training_manifests")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_rule(tmp_path: Path, payload: dict, name: str = "rule.json") -> Path:
    """Write a JSON rule file and return its path."""
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def valid_rule_payload() -> dict:
    """A well-formed rule: dark < -30 <= medium < 10 <= light."""
    return {
        "name": "documented_broad_group_rule_v1",
        "source": "docs/training-data-preparation-protocol.md",
        "intervals": [
            {"broad_group": "dark", "min_ita": None, "max_ita": -30.0},
            {"broad_group": "medium", "min_ita": -30.0, "max_ita": 10.0},
            {"broad_group": "light", "min_ita": 10.0, "max_ita": None},
        ],
    }


def sample_row(
    image_id: str,
    *,
    dataset_name: str = "FairFace",
    source_mst_label=None,
    estimated_group=None,
    ita=None,
    status: str = tm.STATUS_SUCCESS,
    exclusion: str = "",
    assignment_source=None,
) -> dict:
    """Build a synthetic manifest row for summary/cap tests."""
    if assignment_source is None:
        if source_mst_label is not None:
            assignment_source = tm.GROUP_SOURCE_OFFICIAL
        elif estimated_group is not None:
            assignment_source = tm.GROUP_SOURCE_ESTIMATED
        else:
            assignment_source = tm.GROUP_SOURCE_NONE
    return {
        "dataset_name": dataset_name,
        "image_id": image_id,
        "image_path": image_id,
        "source_label": "",
        "source_mst_label": source_mst_label,
        "source_broad_mst_group": (
            tm.broad_group_for_label(source_mst_label)
            if source_mst_label is not None
            else None
        ),
        "estimated_broad_mst_group": estimated_group,
        "group_assignment_source": assignment_source,
        "face_detected": True,
        "landmarks_available": True,
        "skin_pixels": 5000,
        "skin_ratio_percent": 40.0,
        "mean_l_star": 60.0,
        "mean_a_star": 10.0,
        "mean_b_star": 18.0,
        "ita_degrees": ita,
        "processing_status": status,
        "exclusion_reason": exclusion,
        "intended_use": tm.INTENDED_USE_TRAINING,
    }


# ---------------------------------------------------------------------------
# Broad groups and dataset roles
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
        ("07", "medium"),
        (3.0, "light"),
    ],
)
def test_broad_group_for_label_maps_official_labels(label, expected):
    assert tm.broad_group_for_label(label) == expected


@pytest.mark.parametrize("label", [0, 11, -1, None, "", "abc", 2.5, True])
def test_broad_group_for_label_rejects_invalid(label):
    assert tm.broad_group_for_label(label) is None


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("MST-E", True),
        ("mst_e", True),
        ("mste", True),
        ("MST E", True),
        ("FairFace", False),
        ("SCIN", False),
    ],
)
def test_is_mst_e_name(name, expected):
    assert tm.is_mst_e_name(name) is expected


def test_validate_training_dataset_names_allows_training_sets():
    tm.validate_training_dataset_names(["FairFace", "SCIN"])


def test_validate_training_dataset_names_rejects_mst_e():
    with pytest.raises(ValueError):
        tm.validate_training_dataset_names(["FairFace", "MST-E"])


# ---------------------------------------------------------------------------
# Small cell helpers
# ---------------------------------------------------------------------------


def test_read_text_and_read_label():
    assert tm.read_text(None) == ""
    assert tm.read_text("  hi ") == "hi"
    assert tm.read_text(float("nan")) == ""
    assert tm.read_label("03") == 3
    assert tm.read_label("3.0") == 3
    assert tm.read_label(None) is None
    assert tm.read_label("abc") is None
    assert tm.read_label("2.5") is None


# ---------------------------------------------------------------------------
# Estimated-group rule loading
# ---------------------------------------------------------------------------


def test_load_estimated_group_rule_valid(tmp_path):
    path = write_rule(tmp_path, valid_rule_payload())
    rule = tm.load_estimated_group_rule(path)
    assert rule["name"] == "documented_broad_group_rule_v1"
    assert len(rule["intervals"]) == 3


def test_load_estimated_group_rule_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        tm.load_estimated_group_rule(tmp_path / "nope.json")


def test_load_estimated_group_rule_bad_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        tm.load_estimated_group_rule(path)


def test_load_estimated_group_rule_missing_keys(tmp_path):
    path = write_rule(tmp_path, {"name": "x"})
    with pytest.raises(ValueError):
        tm.load_estimated_group_rule(path)


def test_load_estimated_group_rule_unknown_group(tmp_path):
    payload = valid_rule_payload()
    payload["intervals"][0]["broad_group"] = "ultra"
    with pytest.raises(ValueError):
        tm.load_estimated_group_rule(write_rule(tmp_path, payload))


def test_load_estimated_group_rule_duplicate_group(tmp_path):
    payload = {
        "name": "x",
        "intervals": [
            {"broad_group": "dark", "min_ita": None, "max_ita": -30.0},
            {"broad_group": "dark", "min_ita": -30.0, "max_ita": None},
        ],
    }
    with pytest.raises(ValueError):
        tm.load_estimated_group_rule(write_rule(tmp_path, payload))


def test_load_estimated_group_rule_min_ge_max(tmp_path):
    payload = {
        "name": "x",
        "intervals": [
            {"broad_group": "medium", "min_ita": 20.0, "max_ita": 10.0},
        ],
    }
    with pytest.raises(ValueError):
        tm.load_estimated_group_rule(write_rule(tmp_path, payload))


def test_load_estimated_group_rule_overlapping_intervals(tmp_path):
    payload = {
        "name": "x",
        "intervals": [
            {"broad_group": "dark", "min_ita": None, "max_ita": 0.0},
            {"broad_group": "medium", "min_ita": -10.0, "max_ita": 20.0},
        ],
    }
    with pytest.raises(ValueError):
        tm.load_estimated_group_rule(write_rule(tmp_path, payload))


def test_load_estimated_group_rule_boolean_rejected(tmp_path):
    payload = {
        "name": "x",
        "intervals": [
            {"broad_group": "dark", "min_ita": True, "max_ita": 0.0},
        ],
    }
    with pytest.raises(ValueError):
        tm.load_estimated_group_rule(write_rule(tmp_path, payload))


# ---------------------------------------------------------------------------
# Estimated-group assignment
# ---------------------------------------------------------------------------


def test_assign_estimated_group_without_rule_is_none():
    assert tm.assign_estimated_broad_group(-50.0, None) is None


@pytest.mark.parametrize(
    ("ita", "expected"),
    [
        (-100.0, "dark"),
        (-30.0, "medium"),  # boundary: dark max is exclusive
        (-30.001, "dark"),
        (0.0, "medium"),
        (9.999, "medium"),
        (10.0, "light"),  # boundary: light min is inclusive
        (80.0, "light"),
    ],
)
def test_assign_estimated_group_boundaries(tmp_path, ita, expected):
    rule = tm.load_estimated_group_rule(write_rule(tmp_path, valid_rule_payload()))
    assert tm.assign_estimated_broad_group(ita, rule) == expected


@pytest.mark.parametrize("ita", [None, "", "abc", float("nan"), float("inf")])
def test_assign_estimated_group_invalid_ita(tmp_path, ita):
    rule = tm.load_estimated_group_rule(write_rule(tmp_path, valid_rule_payload()))
    assert tm.assign_estimated_broad_group(ita, rule) is None


# ---------------------------------------------------------------------------
# Exclusion classification
# ---------------------------------------------------------------------------


def test_classify_exclusion_ok():
    reason = tm.classify_exclusion(
        image_loaded=True,
        face_count=1,
        mask_created=True,
        landmarks_available=True,
        skin_pixels=5000,
        ita_valid=True,
        minimum_skin_pixels=1000,
    )
    assert reason == ""


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"image_loaded": False}, tm.EXCLUSION_CORRUPT_IMAGE),
        ({"face_count": 0}, tm.EXCLUSION_NO_FACE),
        ({"face_count": 2}, tm.EXCLUSION_MULTI_FACE),
        ({"mask_created": False}, tm.EXCLUSION_NO_MASK),
        ({"landmarks_available": False}, tm.EXCLUSION_MASK_FALLBACK),
        ({"skin_pixels": 10}, tm.EXCLUSION_INSUFFICIENT_SKIN),
        ({"skin_pixels": None}, tm.EXCLUSION_INSUFFICIENT_SKIN),
        ({"ita_valid": False}, tm.EXCLUSION_ITA_FAILED),
    ],
)
def test_classify_exclusion_branches(kwargs, expected):
    base = {
        "image_loaded": True,
        "face_count": 1,
        "mask_created": True,
        "landmarks_available": True,
        "skin_pixels": 5000,
        "ita_valid": True,
        "minimum_skin_pixels": 1000,
    }
    base.update(kwargs)
    assert tm.classify_exclusion(**base) == expected


def test_classify_exclusion_order_corrupt_wins():
    reason = tm.classify_exclusion(
        image_loaded=False,
        face_count=0,
        mask_created=False,
        landmarks_available=False,
        skin_pixels=None,
        ita_valid=False,
        minimum_skin_pixels=1000,
    )
    assert reason == tm.EXCLUSION_CORRUPT_IMAGE


def test_describe_exclusion_known_and_unknown():
    assert tm.describe_exclusion(tm.EXCLUSION_NO_FACE)
    assert tm.describe_exclusion("custom_reason") == "custom_reason"


# ---------------------------------------------------------------------------
# Row building
# ---------------------------------------------------------------------------


def test_build_processed_row_official_label_wins(tmp_path):
    rule = tm.load_estimated_group_rule(write_rule(tmp_path, valid_rule_payload()))
    row = tm.build_processed_row(
        dataset_name="SCIN",
        image_id="scin__a.jpg",
        image_path="a.jpg",
        source_mst_label=9,
        estimated_rule=rule,
        ita_degrees=50.0,
    )
    assert row["source_broad_mst_group"] == "dark"
    assert row["estimated_broad_mst_group"] is None
    assert row["group_assignment_source"] == tm.GROUP_SOURCE_OFFICIAL
    assert row["processing_status"] == tm.STATUS_SUCCESS


def test_build_processed_row_estimates_when_no_official(tmp_path):
    rule = tm.load_estimated_group_rule(write_rule(tmp_path, valid_rule_payload()))
    row = tm.build_processed_row(
        dataset_name="FairFace",
        image_id="fairface__a.jpg",
        image_path="a.jpg",
        source_mst_label=None,
        estimated_rule=rule,
        ita_degrees=-50.0,
    )
    assert row["source_broad_mst_group"] is None
    assert row["estimated_broad_mst_group"] == "dark"
    assert row["group_assignment_source"] == tm.GROUP_SOURCE_ESTIMATED


def test_build_processed_row_no_rule_no_group():
    row = tm.build_processed_row(
        dataset_name="FairFace",
        image_id="fairface__a.jpg",
        image_path="a.jpg",
        ita_degrees=-50.0,
    )
    assert row["estimated_broad_mst_group"] is None
    assert row["group_assignment_source"] == tm.GROUP_SOURCE_NONE


def test_build_processed_row_exclusion_status():
    row = tm.build_processed_row(
        dataset_name="FairFace",
        image_id="fairface__a.jpg",
        image_path="a.jpg",
        exclusion_reason=tm.EXCLUSION_NO_FACE,
    )
    assert row["processing_status"] == tm.STATUS_EXCLUDED
    assert row["exclusion_reason"] == tm.EXCLUSION_NO_FACE


def test_build_processed_manifest_columns_and_dtype():
    rows = [sample_row("fairface__a.jpg"), sample_row("scin__b.jpg")]
    frame = tm.build_processed_manifest(rows)
    assert list(frame.columns) == list(tm.MANIFEST_COLUMNS)
    assert str(frame["source_mst_label"].dtype) == "Int64"


# ---------------------------------------------------------------------------
# Effective group and stratified cap
# ---------------------------------------------------------------------------


def test_effective_broad_group_prefers_official():
    row = sample_row("x", source_mst_label=2, estimated_group="dark")
    assert tm.effective_broad_group(row) == "light"


def test_effective_broad_group_falls_back_to_estimate():
    row = sample_row("x", estimated_group="dark")
    assert tm.effective_broad_group(row) == "dark"


def test_effective_broad_group_unassigned():
    assert (
        tm.effective_broad_group(sample_row("x")) == tm.UNASSIGNED_GROUP
    )


def test_apply_stratified_cap_without_cap_orders_by_image_id():
    frame = tm.build_processed_manifest(
        [
            sample_row("fairface__c.jpg", source_mst_label=1),
            sample_row("fairface__a.jpg", source_mst_label=2),
            sample_row("fairface__b.jpg", source_mst_label=9),
        ]
    )
    capped = tm.apply_stratified_cap(frame, cap_per_group=0)
    # Output is ordered by broad group (light before dark), then image_id.
    assert list(capped["image_id"]) == [
        "fairface__a.jpg",
        "fairface__c.jpg",
        "fairface__b.jpg",
    ]


def test_apply_stratified_cap_limits_each_group():
    rows = [
        sample_row("fairface__a1.jpg", source_mst_label=1),
        sample_row("fairface__a2.jpg", source_mst_label=2),
        sample_row("fairface__a3.jpg", source_mst_label=3),
        sample_row("fairface__b1.jpg", source_mst_label=8),
        sample_row("fairface__b2.jpg", source_mst_label=9),
    ]
    frame = tm.build_processed_manifest(rows)
    capped = tm.apply_stratified_cap(frame, cap_per_group=2)
    assert len(capped) == 4
    light = capped[capped["source_broad_mst_group"] == "light"]
    dark = capped[capped["source_broad_mst_group"] == "dark"]
    assert len(light) == 2
    assert len(dark) == 2
    # Deterministic: earliest image_ids are kept.
    assert list(light["image_id"]) == ["fairface__a1.jpg", "fairface__a2.jpg"]


def test_apply_stratified_cap_empty_frame():
    frame = tm.build_processed_manifest([])
    capped = tm.apply_stratified_cap(frame, cap_per_group=5)
    assert capped.empty


def test_apply_stratified_cap_is_per_dataset_and_group():
    rows = [
        sample_row("fairface__a1.jpg", source_mst_label=1),
        sample_row("fairface__a2.jpg", source_mst_label=2),
        sample_row("scin__b1.jpg", dataset_name="SCIN", source_mst_label=1),
        sample_row("scin__b2.jpg", dataset_name="SCIN", source_mst_label=2),
    ]
    frame = tm.build_processed_manifest(rows)
    capped = tm.apply_stratified_cap(frame, cap_per_group=1)
    # One light row per dataset is kept, not one across both.
    assert len(capped) == 2
    assert set(capped["dataset_name"]) == {"FairFace", "SCIN"}


def test_select_training_candidates_drops_excluded():
    rows = [
        sample_row("fairface__a.jpg", source_mst_label=1),
        sample_row(
            "fairface__b.jpg",
            status=tm.STATUS_EXCLUDED,
            exclusion=tm.EXCLUSION_NO_FACE,
        ),
    ]
    frame = tm.build_processed_manifest(rows)
    candidates = tm.select_training_candidates(frame)
    assert list(candidates["image_id"]) == ["fairface__a.jpg"]
    assert list(candidates.columns) == list(tm.MANIFEST_COLUMNS)


# ---------------------------------------------------------------------------
# Summaries
# ---------------------------------------------------------------------------


def summarize_frame() -> pd.DataFrame:
    return tm.build_processed_manifest(
        [
            sample_row("fairface__a.jpg", source_mst_label=1),
            sample_row(
                "fairface__b.jpg",
                status=tm.STATUS_EXCLUDED,
                exclusion=tm.EXCLUSION_NO_FACE,
            ),
            sample_row("scin__c.jpg", source_mst_label=9, dataset_name="SCIN"),
        ]
    )


def test_summarize_processed():
    summary = tm.summarize_processed(summarize_frame())
    assert set(summary.columns) == {"dataset_name", "processing_status", "count"}
    assert int(summary["count"].sum()) == 3


def test_summarize_by_exclusion_only_excluded():
    summary = tm.summarize_by_exclusion(summarize_frame())
    assert list(summary["exclusion_reason"]) == [tm.EXCLUSION_NO_FACE]
    assert int(summary["count"].sum()) == 1


def test_summarize_by_exclusion_empty_when_no_exclusions():
    frame = tm.build_processed_manifest([sample_row("fairface__a.jpg")])
    assert tm.summarize_by_exclusion(frame).empty


def test_summarize_by_group_uses_source_then_estimate():
    frame = tm.build_processed_manifest(
        [
            sample_row(
                "scin__a.jpg",
                dataset_name="SCIN",
                source_mst_label=9,
                ita=-60.0,
            ),
            sample_row(
                "fairface__b.jpg",
                ita=-60.0,
                estimated_group="dark",
                assignment_source=tm.GROUP_SOURCE_ESTIMATED,
            ),
        ]
    )
    summary = tm.summarize_by_group(frame)
    assert set(summary["broad_group"]) == {"dark"}
    assert set(summary["group_assignment_source"]) == {
        tm.GROUP_SOURCE_OFFICIAL,
        tm.GROUP_SOURCE_ESTIMATED,
    }


# ---------------------------------------------------------------------------
# Script 11 pure helpers
# ---------------------------------------------------------------------------


def test_script11_resolve_image_path_prefers_stored(tmp_path):
    stored = tmp_path / "stored.jpg"
    stored.write_bytes(b"x")
    resolved = script11.resolve_image_path(
        str(stored), "relative.jpg", tmp_path / "root"
    )
    assert resolved == stored


def test_script11_resolve_image_path_falls_back_to_root(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    fallback = root / "relative.jpg"
    fallback.write_bytes(b"x")
    resolved = script11.resolve_image_path(
        str(tmp_path / "missing.jpg"), "relative.jpg", root
    )
    assert resolved == fallback


def test_script11_process_record_marks_corrupt_image(tmp_path):
    row = script11.process_record(
        {
            "relative_path": "nope.jpg",
            "image_path": str(tmp_path / "nope.jpg"),
            "image_id": "fairface__nope.jpg",
            "intended_use": "training",
        },
        dataset_name="FairFace",
        source_mst_label=None,
        source_label="",
        dataset_root=tmp_path,
        yunet_model=tmp_path / "yunet.onnx",
        landmarker_model=tmp_path / "landmarker.task",
        minimum_skin_pixels=1000,
        score_threshold=0.85,
        estimated_rule=None,
    )
    assert row["processing_status"] == tm.STATUS_EXCLUDED
    assert row["exclusion_reason"] == tm.EXCLUSION_CORRUPT_IMAGE
    assert list(row.keys()) == list(tm.MANIFEST_COLUMNS)
