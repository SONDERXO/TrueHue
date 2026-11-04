"""
06_prepare_mst_e_review.py

Purpose:
    Prepare a manual mask-quality review workbook for the MST-E ITA
    calibration results produced by scripts/05_run_mst_e_ita_calibration.py.

    It reads data/manifests/mst_e_ita_calibration_results.csv (the calibration
    table is NEVER modified), classifies every row on the *automatic* criteria
    below, writes data/manifests/mst_e_mask_quality_review.csv, and generates
    the 2x2 mask-review PNGs for every valid V2 row that is still pending
    review.

    The resulting review CSV is the file a human edits by hand: set
    ``quality_review`` to ``good``, ``acceptable``, or ``poor`` (see
    docs/mask-quality-review.md). Because the script reuses the previous run's
    manual labels, re-running it never clobbers choices a reviewer already
    made.

Automatic classification (no thresholds are decided here):
    1. A row is an automatic failure when its calibration status is not
       ``success``, or the ground-truth MST label is missing, or
       ``ita_degrees`` is empty, or ``landmarks_available`` is False:
       ``quality_review = automatic_failure``, ``ita_use = exclude``, and
       ``review_reason`` explains why.
    2. A successful row that used the V1 fallback mask is also an automatic
       failure (``review_reason = "V1 fallback mask used; exclude from V2
       calibration."``).
    3. Every remaining valid V2 row starts as ``quality_review = pending``,
       ``ita_use = pending``.

Visualization generation:
    For each pending V2 row, the face crop stored in the calibration results
    (face_x/face_y/face_width/face_height) is re-masked with the exact same
    frozen pipeline that produced the calibration row (Skin Mask V2 plus the
    padded-crop landmark cascade), and saved as a 2x2 grid with
    ``save_mask_visualization`` into:

        outputs/mst_e_review_visualizations/mst_01/.../mst_10/

    No algorithm, detector, skin mask, threshold, or ITA calculation is
    changed or re-parameterised.

Run from the project root:
    python scripts/06_prepare_mst_e_review.py
    python scripts/06_prepare_mst_e_review.py --skip-visualizations
    python scripts/06_prepare_mst_e_review.py --force
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

# Make the project root importable when this file is run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.skin_masking.skin_mask import save_mask_visualization
from src.utilities.config import get_config

# -------------------------------------------------------------------
# Paths and constants
# -------------------------------------------------------------------

DEFAULT_RESULTS = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_calibration_results.csv"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_mask_quality_review.csv"
)
DEFAULT_VIS_ROOT = PROJECT_ROOT / "outputs" / "mst_e_review_visualizations"
DEFAULT_MST_E_ROOT = PROJECT_ROOT / "data" / "raw" / "mst-e_data"
DEFAULT_LANDMARKER_MODEL = (
    PROJECT_ROOT / get_config().FACE_LANDMARKER_MODEL_PATH
)

#: Review labels the reviewer may assign by hand (docs/mask-quality-review.md).
MANUAL_REVIEW_LABELS: frozenset[str] = frozenset({"good", "acceptable", "poor"})

#: Derived use decision for manual labels.
MANUAL_USE: dict[str, str] = {
    "good": "use",
    "acceptable": "use",
    "poor": "exclude",
}

#: Column order of the review CSV.
REVIEW_COLUMNS: tuple[str, ...] = (
    "image_id",
    "image_path",
    "source_mst_label",
    "ita_degrees",
    "skin_pixels",
    "skin_ratio_percent",
    "landmarks_available",
    "mask_status",
    "quality_review",
    "ita_use",
    "review_reason",
    "reviewer",
    "date_reviewed",
)

#: Values written for automatic failures.
AUTOMATIC_FAILURE = "automatic_failure"
ITA_USE_EXCLUDE = "exclude"
ITA_USE_PENDING = "pending"

#: Reasons (exact wording required by the review workflow).
REASON_V1_FALLBACK = "V1 fallback mask used; exclude from V2 calibration."
REASON_NO_LABEL = (
    "source_mst_label missing in the calibration results; "
    "exclude from V2 calibration."
)
REASON_NO_ITA = (
    "ita_degrees empty in the calibration results; "
    "exclude from V2 calibration."
)
REASON_NO_LANDMARKS = (
    "landmarks_available is False; V2 feature exclusion did not run; "
    "exclude from V2 calibration."
)


# -------------------------------------------------------------------
# Small helpers
# -------------------------------------------------------------------


def read_text(value: object) -> str:
    """Return a stripped string, or ``""`` when the cell is missing."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):  # pragma: no cover - defensive
        pass
    return str(value).strip()


def is_missing(value: object) -> bool:
    """Return True when a cell holds no usable value."""
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return True
    return str(value).strip() == ""


def to_bool(value: object) -> bool:
    """Parse a boolean-ish cell."""
    if is_missing(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    return text in {"true", "1", "yes"}


def sanitise_filename(value: str) -> str:
    """Turn an image ID into a safe filename fragment."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return cleaned or "image"


def label_folder(source_mst_label: object) -> str | None:
    """Return the ``mst_NN`` folder name for a label, or None when missing."""
    if is_missing(source_mst_label):
        return None
    try:
        label = int(float(source_mst_label))
    except (TypeError, ValueError):
        return None
    return f"mst_{label:02d}"


def resolve_image_path(stored_path: str, relative_path: str) -> Path:
    """Turn the stored image path into a usable local path (same fallback
    rule as scripts/05_run_mst_e_ita_calibration.py)."""
    candidate = Path(stored_path) if stored_path else Path(relative_path)
    if candidate.is_file():
        return candidate
    fallback = DEFAULT_MST_E_ROOT / relative_path if relative_path else candidate
    if fallback.is_file():
        return fallback
    return candidate


# -------------------------------------------------------------------
# Load the calibration harness (frozen pipeline reuse only)
# -------------------------------------------------------------------

# The padded-crop landmark cascade lives in the 05 calibration script. We
# reuse it rather than copy it, so the visualizations are produced by the
# exact same masking call that wrote the calibration rows. This imports the
# script module only for its functions; no algorithm is changed.
def _load_calibration_harness():
    scripts_dir = PROJECT_ROOT / "scripts"
    sys.path.insert(0, str(scripts_dir))
    module = importlib.import_module("05_run_mst_e_ita_calibration")
    return module


# -------------------------------------------------------------------
# Classification
# -------------------------------------------------------------------


def classify_row(row: pd.Series) -> dict[str, str]:
    """Return the automatic review columns for one calibration row.

    Returns a dict with ``quality_review``, ``ita_use`` and ``review_reason``
    using the rules in the module docstring. This is the *automatic* pass
    only; a human later upgrades ``pending`` to ``good``/``acceptable``/
    ``poor`` in the review CSV.
    """
    mask_status = read_text(row.get("mask_status"))
    status = read_text(row.get("status"))
    reason = read_text(row.get("reason"))

    is_v1_fallback = "fallback" in mask_status.lower()

    if is_v1_fallback:
        return {
            "quality_review": AUTOMATIC_FAILURE,
            "ita_use": ITA_USE_EXCLUDE,
            "review_reason": REASON_V1_FALLBACK,
        }

    if status != "success":
        fallback_reason = reason or "Calibration row is not marked success"
        return {
            "quality_review": AUTOMATIC_FAILURE,
            "ita_use": ITA_USE_EXCLUDE,
            "review_reason": fallback_reason,
        }

    if is_missing(row.get("source_mst_label")):
        return {
            "quality_review": AUTOMATIC_FAILURE,
            "ita_use": ITA_USE_EXCLUDE,
            "review_reason": REASON_NO_LABEL,
        }

    if is_missing(row.get("ita_degrees")):
        return {
            "quality_review": AUTOMATIC_FAILURE,
            "ita_use": ITA_USE_EXCLUDE,
            "review_reason": REASON_NO_ITA,
        }

    if not to_bool(row.get("landmarks_available")):
        return {
            "quality_review": AUTOMATIC_FAILURE,
            "ita_use": ITA_USE_EXCLUDE,
            "review_reason": REASON_NO_LANDMARKS,
        }

    return {
        "quality_review": "pending",
        "ita_use": ITA_USE_PENDING,
        "review_reason": "",
    }


def is_manually_reviewed(record: pd.Series) -> bool:
    """True when a previous review-CSV row was touched by a human."""
    if read_text(record.get("quality_review")).lower() in MANUAL_REVIEW_LABELS:
        return True
    if read_text(record.get("reviewer")):
        return True
    if read_text(record.get("date_reviewed")):
        return True
    return False


def load_previous_review(path: Path) -> dict[str, pd.Series]:
    """Read the previous review CSV, keyed by image_id, if it exists."""
    if not path.is_file():
        return {}
    previous = pd.read_csv(path, dtype=str)
    keyed: dict[str, pd.Series] = {}
    for _, record in previous.iterrows():
        image_id = read_text(record.get("image_id"))
        if image_id and is_manually_reviewed(record):
            keyed[image_id] = record
    return keyed


# -------------------------------------------------------------------
# Visualization generation
# -------------------------------------------------------------------


def generate_visualization(
    row: pd.Series,
    vis_root: Path,
    landmarker_model: Path,
    harness,
    force: bool = False,
) -> bool:
    """Re-mask one pending row and write its 2x2 review grid.

    Returns True when the PNG exists (newly written or already present).
    """
    relative_path = read_text(row.get("relative_path"))
    image_path = resolve_image_path(read_text(row.get("image_path")), relative_path)
    label_name = label_folder(row.get("source_mst_label"))
    if label_name is None:
        return False

    image_id = read_text(row.get("image_id"))
    safe_id = sanitise_filename(image_id)
    dest_dir = vis_root / label_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    destination = dest_dir / f"{safe_id}_visualization.png"
    if destination.is_file() and not force:
        return True

    try:
        face_x = int(float(row.get("face_x")))
        face_y = int(float(row.get("face_y")))
        face_w = int(float(row.get("face_width")))
        face_h = int(float(row.get("face_height")))
    except (TypeError, ValueError):
        return False

    image_bgr = cv2.imread(str(image_path))
    if image_bgr is None:
        return False

    face_crop_bgr = image_bgr[
        face_y : face_y + face_h, face_x : face_x + face_w
    ].copy()
    if face_crop_bgr.size == 0:
        return False

    mask_result = harness.compute_v2_skin_mask_with_margin(
        face_crop_bgr=face_crop_bgr,
        image_bgr=image_bgr,
        face_box=(face_x, face_y, face_w, face_h),
        landmarker_model=landmarker_model,
    )
    if mask_result.mask is None or mask_result.mask.size == 0:
        return False

    save_mask_visualization(
        face_bgr=face_crop_bgr,
        candidate_mask=mask_result.candidate_mask,
        exclusion_mask=mask_result.exclusion_mask,
        final_mask=mask_result.mask,
        save_path=str(destination),
        landmarks_available=mask_result.landmarks_available,
    )
    return True


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description=(
            "Build the manual mask-quality review workbook from the MST-E "
            "calibration results and generate per-label review visualizations."
        )
    )
    parser.add_argument(
        "--calibration-results",
        type=Path,
        default=DEFAULT_RESULTS,
        help=f"Calibration results CSV (default: {DEFAULT_RESULTS})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Review CSV to write (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--visualizations-root",
        type=Path,
        default=DEFAULT_VIS_ROOT,
        help=(
            "Folder that receives the mst_01..mst_10 review-grid subfolders "
            f"(default: {DEFAULT_VIS_ROOT})"
        ),
    )
    parser.add_argument(
        "--landmarker-model",
        type=Path,
        default=DEFAULT_LANDMARKER_MODEL,
        help=(
            "Local MediaPipe face_landmarker.task used to re-mask pending "
            f"rows (default: {DEFAULT_LANDMARKER_MODEL})"
        ),
    )
    parser.add_argument(
        "--skip-visualizations",
        action="store_true",
        help="Only write the review CSV; do not generate any PNGs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate review PNGs even when they already exist.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only generate visualizations for the first N pending rows "
        "(0 = all). For a quick trial.",
    )
    return parser.parse_args()


def main() -> None:
    """Classify rows, reuse manual labels, generate grids, print summary."""
    args = parse_arguments()

    if not args.calibration_results.is_file():
        print(f"ERROR: calibration results were not found: {args.calibration_results}")
        sys.exit(1)

    results = pd.read_csv(args.calibration_results)
    if results.empty:
        print(f"ERROR: no rows in {args.calibration_results}")
        sys.exit(1)

    required = {"image_id", "image_path", "status", "source_mst_label",
                "ita_degrees"}
    missing_cols = sorted(required - set(results.columns))
    if missing_cols:
        print(f"ERROR: missing required columns: {', '.join(missing_cols)}")
        sys.exit(1)

    previous = load_previous_review(args.output)
    harness = _load_calibration_harness()

    rows: list[dict[str, object]] = []
    pending_records: list[pd.Series] = []

    for _, record in results.iterrows():
        image_id = read_text(record.get("image_id"))
        auto = classify_row(record)

        manual: dict[str, object] = {}
        if image_id in previous:
            manual_row = previous[image_id]
            manual = {
                "quality_review": read_text(manual_row.get("quality_review")),
                "ita_use": read_text(manual_row.get("ita_use")),
                "review_reason": read_text(manual_row.get("review_reason")),
                "reviewer": read_text(manual_row.get("reviewer")),
                "date_reviewed": read_text(manual_row.get("date_reviewed")),
            }
            if (
                manual["quality_review"].lower() in MANUAL_USE
                and not manual["ita_use"]
            ):
                manual["ita_use"] = MANUAL_USE[manual["quality_review"].lower()]

        quality_review = manual.get("quality_review", "") or auto["quality_review"]
        ita_use = manual.get("ita_use", "") or auto["ita_use"]
        review_reason = manual.get("review_reason", "") or auto["review_reason"]
        reviewer = manual.get("reviewer", "") or ""
        date_reviewed = manual.get("date_reviewed", "") or ""

        rows.append(
            {
                "image_id": image_id,
                "image_path": read_text(record.get("image_path")),
                "source_mst_label": record.get("source_mst_label"),
                "ita_degrees": record.get("ita_degrees"),
                "skin_pixels": record.get("skin_pixels"),
                "skin_ratio_percent": record.get("skin_ratio_percent"),
                "landmarks_available": to_bool(record.get("landmarks_available")),
                "mask_status": read_text(record.get("mask_status")),
                "quality_review": quality_review,
                "ita_use": ita_use,
                "review_reason": review_reason,
                "reviewer": reviewer,
                "date_reviewed": date_reviewed,
            }
        )

        if quality_review == "pending" and ita_use == ITA_USE_PENDING:
            pending_records.append(record)

    review_df = pd.DataFrame(rows, columns=list(REVIEW_COLUMNS))
    review_df["source_mst_label"] = (
        pd.to_numeric(review_df["source_mst_label"], errors="coerce").astype("Int64")
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    review_df.to_csv(args.output, index=False)

    # ------------------------------------------------------------------
    # Visualization generation for the pending rows
    # ------------------------------------------------------------------
    written = 0
    skipped = 0
    failed = 0
    if not args.skip_visualizations:
        if not args.landmarker_model.is_file():
            print(
                f"WARNING: landmarker model not found: {args.landmarker_model}\n"
                "  Bypassing landmark cascade on reruns would diverge from the "
                "calibration run, so visualizations are skipped."
            )
        else:
            vis_root: Path = args.visualizations_root
            if args.limit and args.limit > 0:
                pending_records = pending_records[: args.limit]
            for index, record in enumerate(pending_records, start=1):
                already = False
                relative_path = read_text(record.get("relative_path"))
                image_path = resolve_image_path(
                    read_text(record.get("image_path")), relative_path
                )
                safe_id = sanitise_filename(read_text(record.get("image_id")))
                label_name = label_folder(record.get("source_mst_label"))
                destination = (
                    vis_root / label_name / f"{safe_id}_visualization.png"
                )
                if destination.is_file() and not args.force:
                    already = True
                    skipped += 1
                else:
                    ok = generate_visualization(
                        row=record,
                        vis_root=vis_root,
                        landmarker_model=args.landmarker_model,
                        harness=harness,
                        force=args.force,
                    )
                    if ok:
                        written += 1
                    else:
                        failed += 1
                        print(
                            f"  WARNING: could not visualize: "
                            f"{read_text(record.get('image_id'))}"
                        )
                if index % 250 == 0:
                    print(f"[{index}/{len(pending_records)}] visualizations...")
            print(f"Visualizations written: {written}, already present: {skipped}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    automatic = review_df[review_df["quality_review"] == AUTOMATIC_FAILURE]
    pending = review_df[review_df["quality_review"] == "pending"]
    manually_reviewed = review_df[
        review_df["quality_review"].str.lower().isin(MANUAL_REVIEW_LABELS)
    ]

    print("=" * 65)
    print("MST-E mask-quality review workbook")
    print("=" * 65)
    print(f"Review CSV        : {args.output}")
    print(f"Calibration rows  : {len(review_df)}")
    print(f"Automatic failures: {len(automatic)} (ita_use = exclude)")
    print(f"Pending visual    : {len(pending)} (ita_use = pending)")
    print(f"Manually reviewed : {len(manually_reviewed)} (preserved)")
    print(f"Failed visualise  : {failed}")
    if not args.skip_visualizations:
        print(f"Visualization dir : {args.visualizations_root}")

    print()
    print("Pending rows per MST label:")
    if pending.empty:
        print("  (none)")
    else:
        by_label = (
            pending["source_mst_label"]
            .map(lambda value: f"mst_{int(value):02d}")
            .value_counts()
            .sort_index()
        )
        for label, count in by_label.items():
            print(f"  {label:<8}: {count}")

    if len(automatic):
        print()
        print("Automatic failure reasons:")
        for reason, count in automatic["review_reason"].value_counts().items():
            print(f"  {count:>5}  {reason}")

    print()
    print("Next steps (manual, not done here):")
    print("  1. Open the review PNGs under outputs/mst_e_review_visualizations/")
    print("     and label each pending row per docs/mask-quality-review.md.")
    print("  2. Edit data/manifests/mst_e_mask_quality_review.csv, set")
    print("     quality_review to good/acceptable/poor, reviewer and date.")
    print("  3. Re-run this script anytime: manual labels are preserved.")
    print("  4. Only then decide ITA-to-MST calibration thresholds.")


if __name__ == "__main__":
    main()