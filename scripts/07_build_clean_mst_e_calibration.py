"""
07_build_clean_mst_e_calibration.py

Purpose:
    Build the *clean* MST-E ITA calibration table used for ITA-to-MST analysis.

    This script joins two files on ``image_id``:

      * data/manifests/mst_e_ita_calibration_results.csv
            The original automatic calibration output from
            scripts/05_run_mst_e_ita_calibration.py. This file is READ ONLY
            and is never modified.
      * data/manifests/mst_e_mask_quality_review.csv
            The completed manual mask-quality review exported from Excel.

    Skin Mask V2 is the selected mask version, so a row is only eligible for
    calibration when it is a successful V2 mask that a human reviewer judged
    trustworthy. V1 fallback masks are never eligible. This script does not
    change face detection, Skin Mask V2, CIELAB conversion, ITA computation,
    any raw dataset, or Android code. It also does not decide any ITA-to-MST
    threshold and does not train a model.

A row is INCLUDED only when every rule below holds:
    1. Calibration ``status`` is ``success``.
    2. ``source_mst_label`` is present and an integer from 1 to 10.
    3. ``ita_degrees`` is present.
    4. ``landmarks_available`` is True.
    5. The row did NOT use a V1 fallback mask. A fallback is detected when any
       of these is true:
           - ``landmarks_available`` is False,
           - ``mask_status`` contains "FALLBACK" (case-insensitive), or
           - ``reason`` contains "fallback" (case-insensitive).
    6. Manual ``quality_review`` is ``good`` or ``acceptable``.
    7. Manual ``ita_use`` is ``include``.

Everything else is excluded with a machine-readable
``calibration_inclusion_reason`` such as ``excluded_v1_fallback`` or
``excluded_manual_review_not_complete``.

Output:
    data/manifests/mst_e_ita_calibration_clean.csv

    The clean table preserves every original calibration field and adds:
        quality_review               (the manual label, replacing the placeholder)
        ita_use                      (the manual include/exclude decision)
        review_reason                (the reviewer's free-text reason)
        reviewer                     (who reviewed the row)
        date_reviewed                (when the row was reviewed)
        calibration_included         (True/False)
        calibration_inclusion_reason (why the row was kept or dropped)

Run from the project root:
    python scripts/07_build_clean_mst_e_calibration.py
    python scripts/07_build_clean_mst_e_calibration.py --min-included-per-label 10
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# Make the project root importable when this file is run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# -------------------------------------------------------------------
# Paths and constants
# -------------------------------------------------------------------

DEFAULT_RESULTS = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_calibration_results.csv"
)
DEFAULT_REVIEW = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_mask_quality_review.csv"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_calibration_clean.csv"
)

#: Official MST labels 1-10 used by MST-E ground truth.
MST_LABELS: tuple[int, ...] = tuple(range(1, 11))

#: A label with fewer included images than this triggers a warning.
DEFAULT_MIN_INCLUDED_PER_LABEL = 10

#: Manual quality labels a reviewer may assign.
MANUAL_QUALITY_ELIGIBLE: frozenset[str] = frozenset({"good", "acceptable"})
MANUAL_QUALITY_KNOWN: frozenset[str] = frozenset(
    {"good", "acceptable", "poor"}
)

#: Machine-readable inclusion / exclusion reasons.
INCLUDED_GOOD_MASK = "included_good_mask"
INCLUDED_ACCEPTABLE_MASK = "included_acceptable_mask"
EXCLUDED_AUTOMATIC_FAILURE = "excluded_automatic_failure"
EXCLUDED_V1_FALLBACK = "excluded_v1_fallback"
EXCLUDED_MISSING_MST_LABEL = "excluded_missing_mst_label"
EXCLUDED_MISSING_ITA = "excluded_missing_ita"
EXCLUDED_POOR_MASK = "excluded_poor_mask"
EXCLUDED_MANUAL_REVIEW_NOT_COMPLETE = "excluded_manual_review_not_complete"
EXCLUDED_MANUAL_DECISION = "excluded_manual_decision"

#: Manual review columns carried over from the review CSV.
MANUAL_REVIEW_COLUMNS: tuple[str, ...] = (
    "quality_review",
    "ita_use",
    "review_reason",
    "reviewer",
    "date_reviewed",
)

#: New columns appended to the preserved calibration fields.
ADDED_COLUMNS: tuple[str, ...] = (
    "ita_use",
    "review_reason",
    "reviewer",
    "date_reviewed",
    "calibration_included",
    "calibration_inclusion_reason",
)

#: Columns that must exist in each input file.
REQUIRED_CALIBRATION_COLUMNS: tuple[str, ...] = (
    "image_id",
    "status",
    "source_mst_label",
    "ita_degrees",
    "landmarks_available",
    "mask_status",
    "reason",
)
REQUIRED_REVIEW_COLUMNS: tuple[str, ...] = (
    "image_id",
    "quality_review",
    "ita_use",
)


# -------------------------------------------------------------------
# Cell helpers
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
    """Parse a boolean-ish cell (``True``/``False``/``TRUE``/``1``/``yes``)."""
    if is_missing(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_label(value: object) -> int | None:
    """Return an integer MST label in 1-10, or ``None`` when absent/invalid."""
    if is_missing(value):
        return None
    try:
        label = int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None
    if 1 <= label <= 10:
        return label
    return None


def read_csv_flexible(path: Path) -> pd.DataFrame:
    """Read a CSV exported by pandas or Excel.

    The manual review CSV is exported from Excel, so it is often encoded in
    Windows-1252 rather than UTF-8. Try UTF-8 first, then the common Windows
    code pages, so the same script works on either export.
    """
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as error:  # pragma: no cover - encoding
            last_error = error
    if last_error is not None:  # pragma: no cover - defensive
        raise last_error
    raise ValueError(f"could not read {path}")  # pragma: no cover


# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------


def validate_unique_image_ids(frame: pd.DataFrame, source_name: str) -> None:
    """Raise a clear error when ``image_id`` is duplicated or missing."""
    if "image_id" not in frame.columns:
        raise ValueError(f"{source_name} is missing the image_id column")
    ids = frame["image_id"].map(read_text)
    duplicated = ids[ids.duplicated(keep=False)]
    if not duplicated.empty:
        examples = sorted(set(duplicated.tolist()))[:5]
        raise ValueError(
            f"{source_name} has duplicate image_id values "
            f"({len(duplicated)} rows, e.g. {examples}); image_id must be "
            "unique or the join would silently multiply rows"
        )
    if (ids == "").any():
        raise ValueError(
            f"{source_name} has {int((ids == '').sum())} empty image_id values"
        )


def validate_columns(
    frame: pd.DataFrame, required: tuple[str, ...], source_name: str
) -> None:
    """Raise a clear error when a required column is missing."""
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(
            f"{source_name} is missing required columns: {', '.join(missing)}"
        )


# -------------------------------------------------------------------
# Inclusion decision
# -------------------------------------------------------------------


def is_v1_fallback(
    landmarks_available: object, mask_status: object, reason: object
) -> bool:
    """Detect a V1 fallback mask row from the three documented signals."""
    if not to_bool(landmarks_available):
        return True
    if "fallback" in read_text(mask_status).lower():
        return True
    if "fallback" in read_text(reason).lower():
        return True
    return False


def classify_calibration_row(
    *,
    status: object,
    source_mst_label: object,
    ita_degrees: object,
    landmarks_available: object,
    mask_status: object,
    reason: object,
    quality_review: object,
    ita_use: object,
) -> tuple[bool, str]:
    """Return ``(calibration_included, calibration_inclusion_reason)``.

    The checks run in the documented order so the first failing rule is the
    reason recorded for a row. Manual ``quality_review`` / ``ita_use`` are the
    values from the review CSV (empty when the row was never reviewed).
    """
    if read_text(status) != "success":
        return False, EXCLUDED_AUTOMATIC_FAILURE

    # The review's own automatic pass may flag a formerly successful row
    # (e.g. a stale calibration run); such a row is still an automatic failure.
    if read_text(quality_review).lower() == "automatic_failure":
        return False, EXCLUDED_AUTOMATIC_FAILURE

    if read_label(source_mst_label) is None:
        return False, EXCLUDED_MISSING_MST_LABEL

    if is_missing(ita_degrees):
        return False, EXCLUDED_MISSING_ITA

    if is_v1_fallback(landmarks_available, mask_status, reason):
        return False, EXCLUDED_V1_FALLBACK

    quality = read_text(quality_review).lower()
    use = read_text(ita_use).lower()

    if quality == "poor":
        return False, EXCLUDED_POOR_MASK

    if use in {"exclude", "excluded"}:
        return False, EXCLUDED_MANUAL_DECISION

    if quality in MANUAL_QUALITY_ELIGIBLE and use == "include":
        if quality == "good":
            return True, INCLUDED_GOOD_MASK
        return True, INCLUDED_ACCEPTABLE_MASK

    return False, EXCLUDED_MANUAL_REVIEW_NOT_COMPLETE


# -------------------------------------------------------------------
# Build the clean table
# -------------------------------------------------------------------


def build_clean_calibration(
    calibration: pd.DataFrame, review: pd.DataFrame
) -> pd.DataFrame:
    """Join calibration results with the manual review and clean the rows.

    Parameters
    ----------
    calibration : pandas.DataFrame
        The unmodified automatic calibration output.
    review : pandas.DataFrame
        The manual mask-quality review export.

    Returns
    -------
    pandas.DataFrame
        The original calibration fields plus the manual review decision and
        the ``calibration_included`` / ``calibration_inclusion_reason`` columns.
    """
    validate_columns(calibration, REQUIRED_CALIBRATION_COLUMNS, "calibration results")
    validate_columns(review, REQUIRED_REVIEW_COLUMNS, "review")
    validate_unique_image_ids(calibration, "calibration results")
    validate_unique_image_ids(review, "review")

    # Rename the review columns that also exist in the calibration table so the
    # merge cannot create ambiguous ``_x`` / ``_y`` columns.
    rename_map = {
        "quality_review": "review_quality_review",
        "ita_use": "review_ita_use",
        "mask_status": "review_mask_status",
        "landmarks_available": "review_landmarks_available",
        "source_mst_label": "review_source_mst_label",
        "ita_degrees": "review_ita_degrees",
        "reason": "review_reason_source",
    }
    review_renamed = review.rename(
        columns={key: value for key, value in rename_map.items() if key in review.columns}
    )
    manual_columns = ["image_id", "review_quality_review", "review_ita_use"]
    manual_columns += [
        column
        for column in ("review_reason", "reviewer", "date_reviewed",
                       "review_mask_status", "review_landmarks_available",
                       "review_source_mst_label", "review_ita_degrees")
        if column in review_renamed.columns
    ]
    manual_columns = list(dict.fromkeys(manual_columns))

    merged = calibration.merge(
        review_renamed[manual_columns], on="image_id", how="left"
    )

    original_columns = list(calibration.columns)
    rows: list[dict[str, object]] = []

    for _, row in merged.iterrows():
        # A review cannot run the mask, so the calibration columns stay
        # authoritative; the review columns only fill a gap when calibration
        # left one empty.
        source_label = row.get("source_mst_label")
        if is_missing(source_label):
            source_label = row.get("review_source_mst_label")
        ita_value = row.get("ita_degrees")
        if is_missing(ita_value):
            ita_value = row.get("review_ita_degrees")
        landmarks = row.get("landmarks_available")
        if is_missing(landmarks):
            landmarks = row.get("review_landmarks_available")
        mask_status = row.get("mask_status")
        if is_missing(mask_status):
            mask_status = row.get("review_mask_status")

        quality_review = read_text(row.get("review_quality_review"))
        ita_use = read_text(row.get("review_ita_use"))

        included, reason = classify_calibration_row(
            status=row.get("status"),
            source_mst_label=source_label,
            ita_degrees=ita_value,
            landmarks_available=landmarks,
            mask_status=mask_status,
            reason=row.get("reason"),
            quality_review=quality_review,
            ita_use=ita_use,
        )

        output: dict[str, object] = {c: row[c] for c in original_columns}
        output["quality_review"] = quality_review
        output["ita_use"] = ita_use
        output["review_reason"] = read_text(row.get("review_reason"))
        output["reviewer"] = read_text(row.get("reviewer"))
        output["date_reviewed"] = read_text(row.get("date_reviewed"))
        output["calibration_included"] = bool(included)
        output["calibration_inclusion_reason"] = reason
        rows.append(output)

    clean = pd.DataFrame(rows, columns=original_columns + list(ADDED_COLUMNS))
    clean["source_mst_label"] = pd.to_numeric(
        clean["source_mst_label"], errors="coerce"
    ).astype("Int64")
    clean["calibration_included"] = clean["calibration_included"].astype(bool)
    return clean


# -------------------------------------------------------------------
# Summary helpers (also used by the test-suite)
# -------------------------------------------------------------------


def exclusion_counts_by_reason(clean: pd.DataFrame) -> pd.Series:
    """Count excluded rows by ``calibration_inclusion_reason``."""
    excluded = clean[~clean["calibration_included"].astype(bool)]
    return excluded["calibration_inclusion_reason"].value_counts()


def included_counts_by_label(clean: pd.DataFrame) -> pd.DataFrame:
    """Return included counts for every official MST label 1-10."""
    included = clean[clean["calibration_included"].astype(bool)]
    counts = included["source_mst_label"].value_counts()
    return pd.DataFrame(
        {
            "source_mst_label": list(MST_LABELS),
            "included_count": [int(counts.get(label, 0)) for label in MST_LABELS],
        }
    )


def included_counts_by_quality(clean: pd.DataFrame) -> pd.Series:
    """Count included rows by manual ``quality_review``."""
    included = clean[clean["calibration_included"].astype(bool)]
    return included["quality_review"].str.lower().value_counts()


def labels_below_minimum(
    counts: pd.DataFrame, minimum: int
) -> list[int]:
    """Return the MST labels whose included count is below ``minimum``."""
    return [
        int(row.source_mst_label)
        for row in counts.itertuples(index=False)
        if int(row.included_count) < minimum
    ]


def print_summary(
    total_original: int,
    total_reviewed: int,
    clean: pd.DataFrame,
    minimum: int,
) -> None:
    """Print the required console summary."""
    included_mask = clean["calibration_included"].astype(bool)
    included = int(included_mask.sum())
    excluded = int((~included_mask).sum())

    print("=" * 65)
    print("MST-E clean calibration table")
    print("=" * 65)
    print(f"Total original rows : {total_original}")
    print(f"Total reviewed rows : {total_reviewed}")
    print(f"Included rows       : {included}")
    print(f"Excluded rows       : {excluded}")

    print()
    print("Exclusion counts by reason:")
    exclusions = exclusion_counts_by_reason(clean)
    if exclusions.empty:
        print("  (none)")
    else:
        for reason, count in exclusions.items():
            print(f"  {int(count):>5}  {reason}")

    print()
    print("Included counts by official source_mst_label (1-10):")
    counts = included_counts_by_label(clean)
    for row in counts.itertuples(index=False):
        print(f"  MST {int(row.source_mst_label):>2}: {int(row.included_count)}")

    print()
    print("Included counts by quality_review:")
    by_quality = included_counts_by_quality(clean)
    if by_quality.empty:
        print("  (none)")
    else:
        for quality, count in by_quality.items():
            print(f"  {quality:<12}: {int(count)}")

    under = labels_below_minimum(counts, minimum)
    if under:
        print()
        print(
            f"WARNING: MST label(s) with fewer than {minimum} included images: "
            + ", ".join(f"MST {label}" for label in under)
        )


# -------------------------------------------------------------------
# Command-line entry point
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description=(
            "Join the MST-E calibration results with the manual mask-quality "
            "review and write the clean V2 calibration table."
        )
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=DEFAULT_RESULTS,
        help=f"Original calibration results CSV (default: {DEFAULT_RESULTS})",
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=DEFAULT_REVIEW,
        help=f"Manual mask-quality review CSV (default: {DEFAULT_REVIEW})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Clean calibration CSV to write (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--min-included-per-label",
        type=int,
        default=DEFAULT_MIN_INCLUDED_PER_LABEL,
        help=(
            "Warn when an MST label has fewer included images than this "
            f"(default: {DEFAULT_MIN_INCLUDED_PER_LABEL})"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Build the clean calibration table and print the summary."""
    args = parse_arguments()

    for label, path in (("calibration results", args.results), ("review", args.review)):
        if not path.is_file():
            print(f"ERROR: the {label} file was not found: {path}")
            sys.exit(1)

    try:
        calibration = read_csv_flexible(args.results)
        review = read_csv_flexible(args.review)
        clean = build_clean_calibration(calibration, review)
    except ValueError as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(args.output, index=False)

    total_reviewed = int(
        clean["ita_use"].map(lambda value: read_text(value) != "").sum()
    )
    print_summary(
        total_original=len(calibration),
        total_reviewed=total_reviewed,
        clean=clean,
        minimum=args.min_included_per_label,
    )

    print()
    print(f"Clean calibration CSV: {args.output}")
    print()
    print("Next steps (not done here):")
    print("  1. Inspect the ITA distribution with")
    print("     python scripts/08_analyze_ita_by_mst.py")
    print("  2. Do NOT derive ITA-to-MST thresholds yet.")
    print("  3. Do NOT train the decision-tree model yet.")


if __name__ == "__main__":
    main()
