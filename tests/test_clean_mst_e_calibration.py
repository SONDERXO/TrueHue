"""Tests for scripts/07_build_clean_mst_e_calibration.py.

These tests are pure pandas tests: every input is a small synthetic
DataFrame (or a temporary CSV), so they never need real MST-E images, YuNet,
MediaPipe, ONNX models, or any network access.
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
clean_calibration = importlib.import_module("07_build_clean_mst_e_calibration")
analyze_ita = importlib.import_module("08_analyze_ita_by_mst")


# ---------------------------------------------------------------------------
# Synthetic row builders
# ---------------------------------------------------------------------------


def calibration_row(
    image_id: str,
    *,
    status: str = "success",
    label: object = 3,
    ita: object = -10.0,
    landmarks: object = True,
    mask_status: str = "skin mask computed with feature exclusion",
    reason: str = "ITA computed successfully",
    skin_ratio: object = 80.0,
) -> dict:
    """Build one synthetic calibration-result row with all original columns."""
    return {
        "dataset_name": "MST-E",
        "image_id": image_id,
        "image_path": f"/tmp/mst-e_data/{image_id}",
        "source_mst_label": label,
        "intended_use": "evaluation_only",
        "status": status,
        "reason": reason,
        "face_detected": True,
        "skin_pixels": 100000.0,
        "skin_ratio_percent": skin_ratio,
        "passes_minimum_skin_pixel_rule": True,
        "mean_l_star": 40.0,
        "mean_a_star": 20.0,
        "mean_b_star": 18.0,
        "ita_degrees": ita,
        "quality_review": "pending",
        "exclusion_reason": "",
        "relative_path": image_id,
        "source_pose": "facing_camera",
        "source_lighting": "well_lit",
        "source_wearing_mask": 0.0,
        "face_x": 1.0,
        "face_y": 1.0,
        "face_width": 100.0,
        "face_height": 100.0,
        "face_area_pixels": 10000.0,
        "landmarks_available": landmarks,
        "mask_status": mask_status,
    }


def review_row(
    image_id: str,
    *,
    quality: str = "good",
    use: str = "include",
    reason: str = "",
    reviewer: str = "tester",
    date: str = "2026-01-01",
) -> dict:
    """Build one synthetic manual-review row."""
    return {
        "image_id": image_id,
        "quality_review": quality,
        "ita_use": use,
        "review_reason": reason,
        "reviewer": reviewer,
        "date_reviewed": date,
    }


def clean_one(cal_row: dict, review: dict) -> pd.Series:
    """Run the join/clean pipeline over a single row and return the result."""
    clean = clean_calibration.build_clean_calibration(
        pd.DataFrame([cal_row]), pd.DataFrame([review])
    )
    assert len(clean) == 1
    return clean.iloc[0]


# ---------------------------------------------------------------------------
# 1 & 2: good / acceptable V2 rows are included
# ---------------------------------------------------------------------------


def test_good_include_valid_v2_row_is_included():
    row = clean_one(
        calibration_row("good.jpg"),
        review_row("good.jpg", quality="good", use="include"),
    )

    assert bool(row["calibration_included"]) is True
    assert row["calibration_inclusion_reason"] == clean_calibration.INCLUDED_GOOD_MASK
    assert row["quality_review"] == "good"
    assert row["ita_use"] == "include"


def test_acceptable_include_valid_v2_row_is_included():
    row = clean_one(
        calibration_row("acceptable.jpg"),
        review_row("acceptable.jpg", quality="acceptable", use="include"),
    )

    assert bool(row["calibration_included"]) is True
    assert (
        row["calibration_inclusion_reason"]
        == clean_calibration.INCLUDED_ACCEPTABLE_MASK
    )


# ---------------------------------------------------------------------------
# 3: poor mask rows are excluded
# ---------------------------------------------------------------------------


def test_poor_mask_row_is_excluded():
    row = clean_one(
        calibration_row("poor.jpg"),
        review_row("poor.jpg", quality="poor", use="exclude"),
    )

    assert bool(row["calibration_included"]) is False
    assert row["calibration_inclusion_reason"] == clean_calibration.EXCLUDED_POOR_MASK


# ---------------------------------------------------------------------------
# 4: V1 fallback rows are excluded (mask status and reason signals)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mask_status", "reason"),
    [
        ("V1 FALLBACK mask used (no landmarks)", "ITA computed successfully"),
        ("skin mask computed", "V1 fallback mask was produced instead"),
    ],
)
def test_v1_fallback_row_is_excluded(mask_status, reason):
    row = clean_one(
        calibration_row(
            "fallback.jpg",
            mask_status=mask_status,
            reason=reason,
        ),
        review_row("fallback.jpg", quality="good", use="include"),
    )

    assert bool(row["calibration_included"]) is False
    assert (
        row["calibration_inclusion_reason"] == clean_calibration.EXCLUDED_V1_FALLBACK
    )


# ---------------------------------------------------------------------------
# 5: rows without landmarks are excluded
# ---------------------------------------------------------------------------


def test_landmarks_unavailable_row_is_excluded():
    row = clean_one(
        calibration_row("no_landmarks.jpg", landmarks=False),
        review_row("no_landmarks.jpg", quality="acceptable", use="include"),
    )

    assert bool(row["calibration_included"]) is False
    assert (
        row["calibration_inclusion_reason"] == clean_calibration.EXCLUDED_V1_FALLBACK
    )


# ---------------------------------------------------------------------------
# 6: missing MST label rows are excluded
# ---------------------------------------------------------------------------


def test_missing_mst_label_row_is_excluded():
    row = clean_one(
        calibration_row("no_label.jpg", label=None),
        review_row("no_label.jpg", quality="good", use="include"),
    )

    assert bool(row["calibration_included"]) is False
    assert (
        row["calibration_inclusion_reason"]
        == clean_calibration.EXCLUDED_MISSING_MST_LABEL
    )


# ---------------------------------------------------------------------------
# 7: missing ITA rows are excluded
# ---------------------------------------------------------------------------


def test_missing_ita_row_is_excluded():
    row = clean_one(
        calibration_row("no_ita.jpg", ita=None),
        review_row("no_ita.jpg", quality="good", use="include"),
    )

    assert bool(row["calibration_included"]) is False
    assert (
        row["calibration_inclusion_reason"] == clean_calibration.EXCLUDED_MISSING_ITA
    )


# ---------------------------------------------------------------------------
# Extra: automatic failures and incomplete reviews are excluded
# ---------------------------------------------------------------------------


def test_automatic_failure_row_is_excluded():
    row = clean_one(
        calibration_row("failed.jpg", status="excluded", reason="No face detected"),
        review_row("failed.jpg", quality="automatic_failure", use="exclude"),
    )

    assert bool(row["calibration_included"]) is False
    assert (
        row["calibration_inclusion_reason"]
        == clean_calibration.EXCLUDED_AUTOMATIC_FAILURE
    )


def test_review_automatic_failure_beats_success_status():
    """A review row flagged automatic_failure is excluded even if status=success."""
    row = clean_one(
        calibration_row("stale.jpg", status="success"),
        review_row("stale.jpg", quality="automatic_failure", use="exclude"),
    )

    assert bool(row["calibration_included"]) is False
    assert (
        row["calibration_inclusion_reason"]
        == clean_calibration.EXCLUDED_AUTOMATIC_FAILURE
    )


def test_review_not_complete_is_excluded():
    row = clean_one(
        calibration_row("pending.jpg"),
        review_row("pending.jpg", quality="pending", use="pending"),
    )

    assert bool(row["calibration_included"]) is False
    assert (
        row["calibration_inclusion_reason"]
        == clean_calibration.EXCLUDED_MANUAL_REVIEW_NOT_COMPLETE
    )


def test_trailing_whitespace_and_excluded_variant_are_normalised():
    included = clean_one(
        calibration_row("space.jpg"),
        review_row("space.jpg", quality="good", use="include "),
    )
    assert bool(included["calibration_included"]) is True

    excluded = clean_one(
        calibration_row("variant.jpg"),
        review_row("variant.jpg", quality="acceptable", use="excluded"),
    )
    assert bool(excluded["calibration_included"]) is False
    assert (
        excluded["calibration_inclusion_reason"]
        == clean_calibration.EXCLUDED_MANUAL_DECISION
    )


# ---------------------------------------------------------------------------
# 8: duplicate review image_id produces a clear error
# ---------------------------------------------------------------------------


def test_duplicate_review_image_id_raises_clear_error():
    calibration = pd.DataFrame(
        [
            calibration_row("dup.jpg"),
            calibration_row("other.jpg"),
        ]
    )
    review = pd.DataFrame(
        [
            review_row("dup.jpg", quality="good", use="include"),
            review_row("dup.jpg", quality="poor", use="exclude"),
        ]
    )

    with pytest.raises(ValueError, match="duplicate image_id"):
        clean_calibration.build_clean_calibration(calibration, review)


def test_duplicate_calibration_image_id_raises_clear_error():
    calibration = pd.DataFrame(
        [
            calibration_row("dup.jpg"),
            calibration_row("dup.jpg"),
        ]
    )
    review = pd.DataFrame([review_row("dup.jpg")])

    with pytest.raises(ValueError, match="duplicate image_id"):
        clean_calibration.build_clean_calibration(calibration, review)


# ---------------------------------------------------------------------------
# 9: the summary contains MST labels 1-10 and the required summary columns
# ---------------------------------------------------------------------------


def test_summary_contains_all_mst_labels_and_required_columns():
    calibration = pd.DataFrame(
        [
            calibration_row(f"l{label}_{index}.jpg", label=label, ita=-20.0 + label)
            for label in range(1, 11)
            for index in range(2)
        ]
    )
    review = pd.DataFrame(
        [
            review_row(f"l{label}_{index}.jpg", quality="good", use="include")
            for label in range(1, 11)
            for index in range(2)
        ]
    )

    clean = clean_calibration.build_clean_calibration(calibration, review)
    counts = clean_calibration.included_counts_by_label(clean)

    assert list(counts.columns) == ["source_mst_label", "included_count"]
    assert sorted(counts["source_mst_label"].tolist()) == list(range(1, 11))
    assert (counts["included_count"] == 2).all()

    by_quality = clean_calibration.included_counts_by_quality(clean)
    assert by_quality.get("good", 0) == 20


def test_ita_summary_has_required_columns_and_labels():
    included = pd.DataFrame(
        [
            {
                "source_mst_label": label,
                "ita_degrees": -30.0 + label,
                "skin_ratio_percent": 75.0,
                "calibration_included": True,
            }
            for label in range(1, 11)
            for _ in range(3)
        ]
    )

    summary = analyze_ita.summarize_by_label(included)

    assert list(summary.columns) == list(analyze_ita.LABEL_SUMMARY_COLUMNS)
    assert sorted(summary["source_mst_label"].tolist()) == list(range(1, 11))
    assert (summary["count"] == 3).all()
    assert summary["mean_ita"].notna().all()
    assert summary["standard_deviation_ita"].notna().all()
