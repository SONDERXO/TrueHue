"""
08_analyze_ita_by_mst.py

Purpose:
    Describe the distribution of computed ITA per official Monk Skin Tone
    (MST) label using only the clean, trusted MST-E calibration rows written by
    scripts/07_build_clean_mst_e_calibration.py.

    The input is filtered to ``calibration_included is True`` (Skin Mask V2,
    successful, good/acceptable manual review, no V1 fallback). For each
    official ``source_mst_label`` from 1 to 10 this script reports:

        count, mean_ita, median_ita, standard_deviation_ita, minimum_ita,
        q1_ita, q3_ita, maximum_ita, mean_skin_ratio_percent,
        median_skin_ratio_percent

    When a ``source_lighting`` column is available it also reports ITA
    summaries per label and lighting condition.

    This script is descriptive only. It does not derive ITA-to-MST thresholds,
    does not map ITA to MST categories, and does not train or evaluate any
    correction model. The charts it saves show distributions; they are not
    proof of perfect category separation and must not be read as thresholds.

Input:
    data/manifests/mst_e_ita_calibration_clean.csv

Outputs:
    data/manifests/mst_e_ita_by_label_summary.csv
    data/manifests/mst_e_ita_by_label_and_lighting_summary.csv
    outputs/figures/mst_e_ita_distribution_by_label.png
    outputs/figures/mst_e_ita_distribution_by_label_and_lighting.png

Run from the project root:
    python scripts/08_analyze_ita_by_mst.py
    python scripts/08_analyze_ita_by_mst.py --input <clean.csv>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: render straight to PNG, no display needed

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Make the project root importable when this file is run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# -------------------------------------------------------------------
# Paths and constants
# -------------------------------------------------------------------

DEFAULT_INPUT = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_calibration_clean.csv"
)
DEFAULT_LABEL_SUMMARY = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_by_label_summary.csv"
)
DEFAULT_LIGHTING_SUMMARY = (
    PROJECT_ROOT / "data" / "manifests"
    / "mst_e_ita_by_label_and_lighting_summary.csv"
)
DEFAULT_LABEL_FIGURE = (
    PROJECT_ROOT / "outputs" / "figures"
    / "mst_e_ita_distribution_by_label.png"
)
DEFAULT_LIGHTING_FIGURE = (
    PROJECT_ROOT / "outputs" / "figures"
    / "mst_e_ita_distribution_by_label_and_lighting.png"
)

#: Official MST labels 1-10 used by MST-E ground truth.
MST_LABELS: tuple[int, ...] = tuple(range(1, 11))

LABEL_SUMMARY_COLUMNS: tuple[str, ...] = (
    "source_mst_label",
    "count",
    "mean_ita",
    "median_ita",
    "standard_deviation_ita",
    "minimum_ita",
    "q1_ita",
    "q3_ita",
    "maximum_ita",
    "mean_skin_ratio_percent",
    "median_skin_ratio_percent",
)

LIGHTING_SUMMARY_COLUMNS: tuple[str, ...] = (
    "source_mst_label",
    "source_lighting",
    "count",
    "mean_ita",
    "median_ita",
    "q1_ita",
    "q3_ita",
)

#: Fixed, colour-blind-friendly palette for lighting conditions.
LIGHTING_COLOURS: tuple[str, ...] = (
    "#4C72B0",
    "#DD8452",
    "#55A868",
    "#C44E52",
    "#8172B3",
    "#937860",
)

SEPARATION_NOTE = (
    "Descriptive distribution of computed ITA for the trusted V2 calibration "
    "subset.\nNot a threshold decision and does not assert perfect category "
    "separation."
)


# -------------------------------------------------------------------
# IO helpers
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


def to_bool(value: object) -> bool:
    """Parse a boolean-ish cell written by script 07 (``True``/``False``)."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return read_text(value).lower() in {"true", "1", "yes"}


def read_csv_flexible(path: Path) -> pd.DataFrame:
    """Read a CSV exported by pandas or Excel (UTF-8 or Windows-1252)."""
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as error:  # pragma: no cover - encoding
            last_error = error
    if last_error is not None:  # pragma: no cover - defensive
        raise last_error
    raise ValueError(f"could not read {path}")  # pragma: no cover


def load_included_rows(path: Path) -> pd.DataFrame:
    """Load the clean table and keep only ``calibration_included`` rows.

    ITA and skin-ratio columns are coerced to floats so a partially filled or
    partially numeric column cannot break the statistics.
    """
    frame = read_csv_flexible(path)
    if "calibration_included" not in frame.columns:
        raise ValueError(
            "the clean calibration CSV is missing the calibration_included "
            "column; run scripts/07_build_clean_mst_e_calibration.py first"
        )
    if "source_mst_label" not in frame.columns or "ita_degrees" not in frame.columns:
        raise ValueError(
            "the clean calibration CSV must contain source_mst_label and "
            "ita_degrees"
        )

    included = frame[frame["calibration_included"].map(to_bool)].copy()
    included["source_mst_label"] = pd.to_numeric(
        included["source_mst_label"], errors="coerce"
    )
    included = included[included["source_mst_label"].isin(MST_LABELS)]
    included["source_mst_label"] = included["source_mst_label"].astype(int)
    included["ita_degrees"] = pd.to_numeric(
        included["ita_degrees"], errors="coerce"
    )
    if "skin_ratio_percent" in included.columns:
        included["skin_ratio_percent"] = pd.to_numeric(
            included["skin_ratio_percent"], errors="coerce"
        )
    return included


# -------------------------------------------------------------------
# Summaries
# -------------------------------------------------------------------


def summarize_by_label(included: pd.DataFrame) -> pd.DataFrame:
    """Return the per-MST-label ITA and skin-ratio summary (labels 1-10)."""
    records: list[dict[str, object]] = []
    for label in MST_LABELS:
        subset = included[included["source_mst_label"] == label]
        ita = subset["ita_degrees"].dropna()
        ratio = (
            subset["skin_ratio_percent"].dropna()
            if "skin_ratio_percent" in subset.columns
            else pd.Series(dtype=float)
        )
        records.append(
            {
                "source_mst_label": label,
                "count": int(ita.shape[0]),
                "mean_ita": ita.mean() if not ita.empty else np.nan,
                "median_ita": ita.median() if not ita.empty else np.nan,
                "standard_deviation_ita": ita.std() if ita.shape[0] > 1 else np.nan,
                "minimum_ita": ita.min() if not ita.empty else np.nan,
                "q1_ita": ita.quantile(0.25) if not ita.empty else np.nan,
                "q3_ita": ita.quantile(0.75) if not ita.empty else np.nan,
                "maximum_ita": ita.max() if not ita.empty else np.nan,
                "mean_skin_ratio_percent": ratio.mean() if not ratio.empty else np.nan,
                "median_skin_ratio_percent": (
                    ratio.median() if not ratio.empty else np.nan
                ),
            }
        )
    return pd.DataFrame(records, columns=list(LABEL_SUMMARY_COLUMNS))


def summarize_by_label_and_lighting(included: pd.DataFrame) -> pd.DataFrame:
    """Return the per-label, per-lighting ITA summary (empty when unavailable)."""
    if "source_lighting" not in included.columns:
        return pd.DataFrame(columns=list(LIGHTING_SUMMARY_COLUMNS))

    frame = included.copy()
    frame["source_lighting"] = frame["source_lighting"].map(read_text)
    frame = frame[frame["source_lighting"] != ""]
    if frame.empty:
        return pd.DataFrame(columns=list(LIGHTING_SUMMARY_COLUMNS))

    records: list[dict[str, object]] = []
    grouped = frame.groupby(["source_mst_label", "source_lighting"], dropna=False)
    for (label, lighting), subset in grouped:
        ita = subset["ita_degrees"].dropna()
        records.append(
            {
                "source_mst_label": int(label),
                "source_lighting": lighting,
                "count": int(ita.shape[0]),
                "mean_ita": ita.mean() if not ita.empty else np.nan,
                "median_ita": ita.median() if not ita.empty else np.nan,
                "q1_ita": ita.quantile(0.25) if not ita.empty else np.nan,
                "q3_ita": ita.quantile(0.75) if not ita.empty else np.nan,
            }
        )

    summary = pd.DataFrame(records, columns=list(LIGHTING_SUMMARY_COLUMNS))
    return summary.sort_values(
        ["source_mst_label", "source_lighting"], ignore_index=True
    )


# -------------------------------------------------------------------
# Figures
# -------------------------------------------------------------------


def _ita_values_by_label(included: pd.DataFrame) -> list[np.ndarray]:
    """Return one 1-D ITA array per MST label 1-10."""
    return [
        included.loc[
            included["source_mst_label"] == label, "ita_degrees"
        ].dropna().to_numpy()
        for label in MST_LABELS
    ]


def plot_distribution_by_label(
    included: pd.DataFrame, output_path: Path
) -> None:
    """Save a boxplot of ITA across official MST labels 1-10."""
    values = _ita_values_by_label(included)
    counts = [int(array.shape[0]) for array in values]
    non_empty = [array for array in values if array.shape[0] > 0]

    figure, axis = plt.subplots(figsize=(11, 6.5))
    if non_empty:
        axis.boxplot(
            values,
            positions=list(MST_LABELS),
            widths=0.6,
            showfliers=True,
            patch_artist=True,
            boxprops={"facecolor": "#8FB8DE", "edgecolor": "#2F5D8A"},
            medianprops={"color": "#B22222", "linewidth": 2},
        )

    axis.set_xticks(list(MST_LABELS))
    axis.set_xticklabels(
        [f"MST {label}\n(n={count})" for label, count in zip(MST_LABELS, counts)]
    )
    axis.set_xlabel("Official Monk Skin Tone Label")
    axis.set_ylabel("Computed ITA (degrees)")
    axis.set_title(
        "Computed ITA distribution by official Monk Skin Tone label "
        "(trusted V2 MST-E calibration subset)"
    )
    axis.grid(axis="y", linestyle=":", alpha=0.5)
    figure.text(0.01, 0.01, SEPARATION_NOTE, fontsize=8, color="#555555")
    figure.tight_layout(rect=(0, 0.04, 1, 1))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def plot_distribution_by_label_and_lighting(
    included: pd.DataFrame, output_path: Path
) -> None:
    """Save a grouped boxplot of ITA per official MST label and lighting."""
    figure, axis = plt.subplots(figsize=(12, 6.5))

    if "source_lighting" in included.columns:
        frame = included.copy()
        frame["source_lighting"] = frame["source_lighting"].map(read_text)
        frame = frame[frame["source_lighting"] != ""]
    else:
        frame = included.iloc[0:0]

    lighting_names = sorted(frame["source_lighting"].unique().tolist())
    if lighting_names:
        width = 0.8 / len(lighting_names)
        for index, lighting in enumerate(lighting_names):
            offset = (index - (len(lighting_names) - 1) / 2) * width
            values = [
                frame.loc[
                    (frame["source_mst_label"] == label)
                    & (frame["source_lighting"] == lighting),
                    "ita_degrees",
                ].dropna().to_numpy()
                for label in MST_LABELS
            ]
            positions = [label + offset for label in MST_LABELS]
            axis.boxplot(
                values,
                positions=positions,
                widths=width * 0.9,
                showfliers=False,
                patch_artist=True,
                boxprops={
                    "facecolor": LIGHTING_COLOURS[index % len(LIGHTING_COLOURS)],
                    "edgecolor": "#333333",
                },
                medianprops={"color": "#111111", "linewidth": 1.5},
            )
        axis.legend(
            handles=[
                plt.Rectangle(
                    (0, 0),
                    1,
                    1,
                    facecolor=LIGHTING_COLOURS[index % len(LIGHTING_COLOURS)],
                    edgecolor="#333333",
                )
                for index, _ in enumerate(lighting_names)
            ],
            labels=lighting_names,
            title="Source lighting",
            loc="best",
        )
    else:
        axis.text(
            0.5,
            0.5,
            "source_lighting is not available in the clean calibration table",
            ha="center",
            va="center",
            transform=axis.transAxes,
        )

    axis.set_xticks(list(MST_LABELS))
    axis.set_xticklabels([f"MST {label}" for label in MST_LABELS])
    axis.set_xlabel("Official Monk Skin Tone Label")
    axis.set_ylabel("Computed ITA (degrees)")
    axis.set_title(
        "Computed ITA by official Monk Skin Tone label and lighting "
        "(trusted V2 MST-E calibration subset)"
    )
    axis.grid(axis="y", linestyle=":", alpha=0.5)
    figure.text(0.01, 0.01, SEPARATION_NOTE, fontsize=8, color="#555555")
    figure.tight_layout(rect=(0, 0.04, 1, 1))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


# -------------------------------------------------------------------
# Command-line entry point
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description=(
            "Summarise and plot computed ITA per official MST label for the "
            "clean MST-E V2 calibration subset. Descriptive only."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Clean calibration CSV to read (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--label-summary",
        type=Path,
        default=DEFAULT_LABEL_SUMMARY,
        help=f"Per-label summary CSV to write (default: {DEFAULT_LABEL_SUMMARY})",
    )
    parser.add_argument(
        "--lighting-summary",
        type=Path,
        default=DEFAULT_LIGHTING_SUMMARY,
        help=(
            "Per-label-and-lighting summary CSV to write "
            f"(default: {DEFAULT_LIGHTING_SUMMARY})"
        ),
    )
    parser.add_argument(
        "--label-figure",
        type=Path,
        default=DEFAULT_LABEL_FIGURE,
        help=f"Per-label boxplot PNG to write (default: {DEFAULT_LABEL_FIGURE})",
    )
    parser.add_argument(
        "--lighting-figure",
        type=Path,
        default=DEFAULT_LIGHTING_FIGURE,
        help=(
            "Per-label-and-lighting boxplot PNG to write "
            f"(default: {DEFAULT_LIGHTING_FIGURE})"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Summarise and plot ITA per MST label from the clean calibration table."""
    args = parse_arguments()

    if not args.input.is_file():
        print(f"ERROR: the clean calibration file was not found: {args.input}")
        print("Run scripts/07_build_clean_mst_e_calibration.py first.")
        sys.exit(1)

    try:
        included = load_included_rows(args.input)
    except ValueError as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    label_summary = summarize_by_label(included)
    lighting_summary = summarize_by_label_and_lighting(included)

    args.label_summary.parent.mkdir(parents=True, exist_ok=True)
    label_summary.to_csv(args.label_summary, index=False)
    args.lighting_summary.parent.mkdir(parents=True, exist_ok=True)
    lighting_summary.to_csv(args.lighting_summary, index=False)

    plot_distribution_by_label(included, args.label_figure)
    plot_distribution_by_label_and_lighting(included, args.lighting_figure)

    print("=" * 65)
    print("MST-E ITA distribution by official MST label")
    print("=" * 65)
    print(f"Input (included rows only): {args.input}")
    print(f"Included rows             : {len(included)}")
    print()
    print("Per-label summary:")
    display = label_summary.copy()
    for column in display.columns:
        if column != "source_mst_label":
            display[column] = display[column].map(
                lambda value: f"{value:.2f}" if pd.notna(value) else "-"
            )
    print(display.to_string(index=False))
    print()
    print(f"Label summary CSV    : {args.label_summary}")
    print(f"Lighting summary CSV : {args.lighting_summary}")
    print(f"Label figure PNG     : {args.label_figure}")
    print(f"Lighting figure PNG  : {args.lighting_figure}")
    print()
    print("Remember: descriptive analysis only. No ITA-to-MST thresholds are")
    print("decided here and the charts do not prove perfect category separation.")


if __name__ == "__main__":
    main()
