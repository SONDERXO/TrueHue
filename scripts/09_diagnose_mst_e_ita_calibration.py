"""
09_diagnose_mst_e_ita_calibration.py

Purpose:
    Diagnostic sensitivity analysis of the clean MST-E ITA calibration table
    BEFORE any ITA-to-MST mapping thresholds are chosen.

    The 10-class MST labels do not currently order cleanly by median ITA. This
    script does three *descriptive* analyses, plus a subject-level breakdown
    and a skin-ratio scatter, so the reasons can be inspected rather than
    hidden:

        A. Full included data      - ITA summary per official MST label.
        B. Lighting-stratified     - ITA summary per MST label and lighting.
        C. Conservative well-lit   - ITA summary per MST label on well-lit
                                     images whose skin ratio is 40-95%.

    This script deliberately does NOT derive ITA-to-MST thresholds, does NOT
    train or evaluate the correction model, and does NOT change face
    detection, Skin Mask V2, CIELAB conversion, or ITA code. It reads the clean
    calibration table only.

Input:
    data/manifests/mst_e_ita_calibration_clean.csv

Outputs:
    data/manifests/mst_e_ita_diagnostic_summary.csv
    data/manifests/mst_e_ita_conservative_subset.csv
    outputs/figures/mst_e_ita_by_label_lighting.png
    outputs/figures/mst_e_ita_by_label_subject.png
    outputs/figures/mst_e_ita_vs_skin_ratio.png

Rows used (all must hold):
    calibration_included is True
    quality_review is good or acceptable
    ita_use is include
    landmarks_available is True
    ita_degrees is not null
    source_mst_label is an integer from 1 to 10

Run from the project root:
    python scripts/09_diagnose_mst_e_ita_calibration.py
    python scripts/09_diagnose_mst_e_ita_calibration.py --min-per-label 10
"""

from __future__ import annotations

import argparse
import re
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
DEFAULT_DIAGNOSTIC_SUMMARY = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_diagnostic_summary.csv"
)
DEFAULT_CONSERVATIVE_SUBSET = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_conservative_subset.csv"
)
DEFAULT_LIGHTING_FIGURE = (
    PROJECT_ROOT / "outputs" / "figures" / "mst_e_ita_by_label_lighting.png"
)
DEFAULT_SUBJECT_FIGURE = (
    PROJECT_ROOT / "outputs" / "figures" / "mst_e_ita_by_label_subject.png"
)
DEFAULT_SKIN_RATIO_FIGURE = (
    PROJECT_ROOT / "outputs" / "figures" / "mst_e_ita_vs_skin_ratio.png"
)

#: Official MST labels 1-10 used by MST-E ground truth.
MST_LABELS: tuple[int, ...] = tuple(range(1, 11))

#: Manual quality labels accepted as calibration input.
QUALITY_ELIGIBLE: frozenset[str] = frozenset({"good", "acceptable"})

#: Conservative skin-ratio band (inclusive), in percent.
SKIN_RATIO_MIN = 40.0
SKIN_RATIO_MAX = 95.0

#: A subset with fewer images than this for a label triggers a warning.
DEFAULT_MIN_PER_LABEL = 10

#: Canonical lighting tokens (underscores/spaces/case normalised away).
LIGHTING_WELL = "welllit"
LIGHTING_POORLY = "poorlylit"

#: Required summary columns.
LABEL_SUMMARY_COLUMNS: tuple[str, ...] = (
    "source_mst_label",
    "count",
    "median_ita",
    "q1_ita",
    "q3_ita",
    "minimum_ita",
    "maximum_ita",
)
LIGHTING_LABEL_SUMMARY_COLUMNS: tuple[str, ...] = (
    "source_mst_label",
    "source_lighting",
    "count",
    "median_ita",
    "q1_ita",
    "q3_ita",
    "minimum_ita",
    "maximum_ita",
)
SUBJECT_SUMMARY_COLUMNS: tuple[str, ...] = (
    "source_mst_label",
    "subject_id",
    "count",
    "median_ita",
    "q1_ita",
    "q3_ita",
    "minimum_ita",
    "maximum_ita",
)
#: Columns of the single stacked diagnostic summary CSV.
DIAGNOSTIC_COLUMNS: tuple[str, ...] = (
    "analysis",
    "source_mst_label",
    "source_lighting",
    "subject_id",
    "count",
    "median_ita",
    "q1_ita",
    "q3_ita",
    "minimum_ita",
    "maximum_ita",
)

#: Analysis tags used in the ``analysis`` column.
ANALYSIS_FULL = "full_included"
ANALYSIS_LIGHTING = "by_lighting"
ANALYSIS_CONSERVATIVE = "conservative_well_lit"
ANALYSIS_SUBJECT = "per_subject"

#: Colour-blind-friendly palette (used for the 10 MST labels).
LABEL_COLOURS: tuple[str, ...] = (
    "#4C72B0",
    "#DD8452",
    "#55A868",
    "#C44E52",
    "#8172B3",
    "#937860",
    "#DA8BC3",
    "#8C8C8C",
    "#CCB974",
    "#64B5CD",
)

#: Palette for lighting conditions in the lighting figure.
LIGHTING_COLOURS: dict[str, str] = {
    "well_lit": "#4C72B0",
    "poorly_lit": "#DD8452",
    "video": "#55A868",
}

DISCLAIMER = (
    "Diagnostic sensitivity analysis only. Filtering exposes how ITA varies "
    "with lighting and mask coverage; it is not an attempt to hide "
    "unfavourable results, and none of these groupings are final thresholds."
)


# -------------------------------------------------------------------
# Cell / IO helpers
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
    """Parse a boolean-ish cell (``True``/``False``/``1``/``yes``)."""
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
            return pd.read_csv(path, encoding=encoding, low_memory=False)
        except UnicodeDecodeError as error:  # pragma: no cover - encoding
            last_error = error
    if last_error is not None:  # pragma: no cover - defensive
        raise last_error
    raise ValueError(f"could not read {path}")  # pragma: no cover


def normalize_lighting(value: object) -> str:
    """Return a canonical lighting token: ``welllit``, ``poorlylit``, etc.

    ``well_lit``, ``Well-Lit``, and ``welllit`` all map to ``welllit`` so the
    conservative filter is robust to the spelling used in the manifest.
    """
    text = read_text(value).lower()
    text = re.sub(r"[\s_\-]+", "", text)
    return text


def extract_subject(image_id: object, relative_path: object = "") -> str | None:
    """Extract a subject identifier (``subject_0``) from an image identifier.

    Returns ``None`` when no subject token is present. The identifier never
    carries any personal information: it is only the dataset's own folder name,
    used to check whether a few subjects dominate a label.
    """
    for text in (read_text(image_id), read_text(relative_path)):
        match = re.search(r"subject[\s_\-]?(\d+)", text, re.IGNORECASE)
        if match:
            return f"subject_{int(match.group(1))}"
    return None


# -------------------------------------------------------------------
# Filtering
# -------------------------------------------------------------------


def select_diagnostic_rows(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply the documented row filter and return the analysable subset.

    Every rule is applied together: the result is the *full included* set.
    ``source_lighting`` and ``skin_ratio_percent`` are optional here; they are
    only needed for the lighting and conservative analyses.
    """
    required = {
        "calibration_included",
        "quality_review",
        "ita_use",
        "landmarks_available",
        "ita_degrees",
        "source_mst_label",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(
            "the input is missing required columns: " + ", ".join(missing)
        )

    work = frame.copy()
    included = work["calibration_included"].map(to_bool)
    quality = work["quality_review"].map(lambda value: read_text(value).lower())
    use = work["ita_use"].map(lambda value: read_text(value).lower())
    landmarks = work["landmarks_available"].map(to_bool)
    labels = pd.to_numeric(work["source_mst_label"], errors="coerce")
    ita = pd.to_numeric(work["ita_degrees"], errors="coerce")

    mask = (
        included
        & quality.isin(QUALITY_ELIGIBLE)
        & (use == "include")
        & landmarks
        & ita.notna()
        & labels.isin(MST_LABELS)
    )

    selected = work.loc[mask].copy()
    selected["source_mst_label"] = labels[mask].astype(int)
    selected["ita_degrees"] = ita[mask]
    if "skin_ratio_percent" in selected.columns:
        selected["skin_ratio_percent"] = pd.to_numeric(
            selected["skin_ratio_percent"], errors="coerce"
        )
    return selected


def build_conservative_subset(frame: pd.DataFrame) -> pd.DataFrame:
    """Well-lit rows with a skin ratio in the inclusive 40-95% band.

    This is a *diagnostic* subset. It is not a permanent threshold and it is
    not a way to hide unfavourable rows: every exploration is reported next to
    the full included data.
    """
    if frame.empty:
        return frame.copy()
    if "source_lighting" not in frame.columns or "skin_ratio_percent" not in frame.columns:
        return frame.iloc[0:0].copy()

    lighting = frame["source_lighting"].map(normalize_lighting)
    ratio = pd.to_numeric(frame["skin_ratio_percent"], errors="coerce")
    mask = (lighting == LIGHTING_WELL) & ratio.between(
        SKIN_RATIO_MIN, SKIN_RATIO_MAX, inclusive="both"
    )
    return frame.loc[mask].copy()


# -------------------------------------------------------------------
# Summaries
# -------------------------------------------------------------------


def _ita_stats(ita: pd.Series) -> dict[str, object]:
    """Return count/median/Q1/Q3/min/max for one ITA series."""
    cleaned = ita.dropna()
    if cleaned.empty:
        return {
            "count": 0,
            "median_ita": np.nan,
            "q1_ita": np.nan,
            "q3_ita": np.nan,
            "minimum_ita": np.nan,
            "maximum_ita": np.nan,
        }
    return {
        "count": int(cleaned.shape[0]),
        "median_ita": float(cleaned.median()),
        "q1_ita": float(cleaned.quantile(0.25)),
        "q3_ita": float(cleaned.quantile(0.75)),
        "minimum_ita": float(cleaned.min()),
        "maximum_ita": float(cleaned.max()),
    }


def summarize_ita_by_label(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the per-MST-label ITA summary for labels 1-10."""
    records: list[dict[str, object]] = []
    for label in MST_LABELS:
        subset = frame.loc[frame["source_mst_label"] == label, "ita_degrees"]
        record = {"source_mst_label": label}
        record.update(_ita_stats(subset))
        records.append(record)
    return pd.DataFrame(records, columns=list(LABEL_SUMMARY_COLUMNS))


def summarize_ita_by_label_and_lighting(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the per-MST-label, per-lighting ITA summary.

    When ``source_lighting`` is absent (or empty for every row) an empty frame
    with the correct columns is returned instead of raising.
    """
    if "source_lighting" not in frame.columns:
        return pd.DataFrame(columns=list(LIGHTING_LABEL_SUMMARY_COLUMNS))

    work = frame.copy()
    work["source_lighting"] = work["source_lighting"].map(read_text)
    work = work[work["source_lighting"] != ""]
    if work.empty:
        return pd.DataFrame(columns=list(LIGHTING_LABEL_SUMMARY_COLUMNS))

    records: list[dict[str, object]] = []
    for (label, lighting), subset in work.groupby(
        ["source_mst_label", "source_lighting"], dropna=False
    ):
        record = {
            "source_mst_label": int(label),
            "source_lighting": lighting,
        }
        record.update(_ita_stats(subset["ita_degrees"]))
        records.append(record)

    summary = pd.DataFrame(records, columns=list(LIGHTING_LABEL_SUMMARY_COLUMNS))
    return summary.sort_values(
        ["source_mst_label", "source_lighting"], ignore_index=True
    )


def per_subject_median_by_label(frame: pd.DataFrame) -> pd.DataFrame:
    """Return per-subject ITA medians, grouped by official MST label."""
    if frame.empty:
        return pd.DataFrame(columns=list(SUBJECT_SUMMARY_COLUMNS))

    ids = (
        frame["image_id"]
        if "image_id" in frame.columns
        else pd.Series([""] * len(frame), index=frame.index)
    )
    paths = (
        frame["relative_path"]
        if "relative_path" in frame.columns
        else pd.Series([""] * len(frame), index=frame.index)
    )

    work = frame.copy()
    work["subject_id"] = [
        extract_subject(image_id, path) for image_id, path in zip(ids, paths)
    ]
    work = work[work["subject_id"].notna()]
    if work.empty:
        return pd.DataFrame(columns=list(SUBJECT_SUMMARY_COLUMNS))

    records: list[dict[str, object]] = []
    for (label, subject), subset in work.groupby(
        ["source_mst_label", "subject_id"], dropna=False
    ):
        record = {
            "source_mst_label": int(label),
            "subject_id": subject,
        }
        record.update(_ita_stats(subset["ita_degrees"]))
        records.append(record)

    summary = pd.DataFrame(records, columns=list(SUBJECT_SUMMARY_COLUMNS))
    return summary.sort_values(
        ["source_mst_label", "subject_id"], ignore_index=True
    )


def build_diagnostic_summary(
    full: pd.DataFrame,
    conservative: pd.DataFrame,
) -> pd.DataFrame:
    """Stack analyses A, B, C and the per-subject breakdown into one table."""
    blocks: list[pd.DataFrame] = []

    full_summary = summarize_ita_by_label(full).copy()
    full_summary.insert(0, "analysis", ANALYSIS_FULL)
    full_summary["source_lighting"] = ""
    full_summary["subject_id"] = ""
    blocks.append(full_summary)

    lighting_summary = summarize_ita_by_label_and_lighting(full).copy()
    lighting_summary.insert(0, "analysis", ANALYSIS_LIGHTING)
    lighting_summary["subject_id"] = ""
    blocks.append(lighting_summary)

    conservative_summary = summarize_ita_by_label(conservative).copy()
    conservative_summary.insert(0, "analysis", ANALYSIS_CONSERVATIVE)
    conservative_summary["source_lighting"] = "well_lit"
    conservative_summary["subject_id"] = ""
    blocks.append(conservative_summary)

    subject_summary = per_subject_median_by_label(full).copy()
    subject_summary.insert(0, "analysis", ANALYSIS_SUBJECT)
    subject_summary["source_lighting"] = ""
    blocks.append(subject_summary)

    combined = pd.concat(blocks, ignore_index=True)
    return combined[list(DIAGNOSTIC_COLUMNS)]


# -------------------------------------------------------------------
# Counts and warnings
# -------------------------------------------------------------------


def label_counts(frame: pd.DataFrame) -> dict[int, int]:
    """Return the number of rows per official MST label (0 when absent)."""
    if frame.empty or "source_mst_label" not in frame.columns:
        return {label: 0 for label in MST_LABELS}
    counts = frame["source_mst_label"].value_counts()
    return {label: int(counts.get(label, 0)) for label in MST_LABELS}


def format_label_counts(frame: pd.DataFrame) -> str:
    """Return a compact ``MST 1: n, MST 2: n, ...`` string."""
    counts = label_counts(frame)
    return ", ".join(f"MST {label}: {counts[label]}" for label in MST_LABELS)


def low_count_labels(summary: pd.DataFrame, minimum: int) -> list[int]:
    """Return labels whose ``count`` is below ``minimum``."""
    return [
        int(row.source_mst_label)
        for row in summary.itertuples(index=False)
        if int(row.count) < minimum
    ]


def print_count_warnings(
    summary: pd.DataFrame, minimum: int, context: str
) -> None:
    """Print a warning for every label below ``minimum`` in a subset."""
    low = low_count_labels(summary, minimum)
    for label in low:
        row = summary[summary["source_mst_label"] == label].iloc[0]
        print(
            f"  WARNING: {context}: MST {label} has only "
            f"{int(row['count'])} image(s) (< {minimum}); treat its ITA "
            "statistics as indicative only."
        )


# -------------------------------------------------------------------
# Figures
# -------------------------------------------------------------------


def plot_ita_by_label_lighting(frame: pd.DataFrame, output_path: Path) -> None:
    """Boxplots of ITA per MST label, separated by lighting condition."""
    figure, axis = plt.subplots(figsize=(12, 6.5))

    if "source_lighting" in frame.columns:
        work = frame.copy()
        work["source_lighting"] = work["source_lighting"].map(read_text)
        work = work[work["source_lighting"] != ""]
    else:
        work = frame.iloc[0:0]

    lighting_names = sorted(work["source_lighting"].unique().tolist())
    if lighting_names:
        width = 0.8 / len(lighting_names)
        for index, lighting in enumerate(lighting_names):
            offset = (index - (len(lighting_names) - 1) / 2) * width
            values = [
                work.loc[
                    (work["source_mst_label"] == label)
                    & (work["source_lighting"] == lighting),
                    "ita_degrees",
                ]
                .dropna()
                .to_numpy()
                for label in MST_LABELS
            ]
            axis.boxplot(
                values,
                positions=[label + offset for label in MST_LABELS],
                widths=width * 0.9,
                showfliers=True,
                patch_artist=True,
                boxprops={
                    "facecolor": LIGHTING_COLOURS.get(
                        lighting, LABEL_COLOURS[index % len(LABEL_COLOURS)]
                    ),
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
                    facecolor=LIGHTING_COLOURS.get(
                        lighting, LABEL_COLOURS[index % len(LABEL_COLOURS)]
                    ),
                    edgecolor="#333333",
                )
                for index, lighting in enumerate(lighting_names)
            ],
            labels=lighting_names,
            title="Source lighting",
            loc="best",
        )
    else:
        axis.text(
            0.5,
            0.5,
            "source_lighting is not available in this table",
            ha="center",
            va="center",
            transform=axis.transAxes,
        )

    axis.set_xticks(list(MST_LABELS))
    axis.set_xticklabels([f"MST {label}" for label in MST_LABELS])
    axis.set_xlabel("Official Monk Skin Tone Label")
    axis.set_ylabel("Computed ITA (degrees)")
    axis.set_title(
        "Computed ITA by official MST label and lighting "
        "(clean MST-E calibration subset, n={})".format(len(frame))
    )
    axis.grid(axis="y", linestyle=":", alpha=0.5)
    figure.text(0.01, 0.01, DISCLAIMER, fontsize=8, color="#555555")
    figure.tight_layout(rect=(0, 0.05, 1, 1))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def plot_ita_by_label_subject(
    subject_summary: pd.DataFrame,
    label_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """Scatter of per-subject median ITA per MST label, with label medians."""
    figure, axis = plt.subplots(figsize=(12, 6.5))
    rng = np.random.default_rng(0)

    if subject_summary.empty:
        axis.text(
            0.5,
            0.5,
            "No subject identifiers could be extracted from image_id/relative_path",
            ha="center",
            va="center",
            transform=axis.transAxes,
        )
    else:
        for label in MST_LABELS:
            subset = subject_summary[subject_summary["source_mst_label"] == label]
            if subset.empty:
                continue
            jitter = rng.uniform(-0.18, 0.18, size=len(subset))
            axis.scatter(
                np.full(len(subset), label) + jitter,
                subset["median_ita"],
                s=28,
                alpha=0.75,
                color=LABEL_COLOURS[(label - 1) % len(LABEL_COLOURS)],
                edgecolors="none",
                label=f"MST {label}",
            )
        medians = label_summary.dropna(subset=["median_ita"])
        axis.plot(
            medians["source_mst_label"],
            medians["median_ita"],
            color="#111111",
            marker="D",
            markersize=6,
            linewidth=1.4,
            label="Label median",
            zorder=5,
        )
        axis.legend(
            loc="center left",
            bbox_to_anchor=(1.01, 0.5),
            fontsize=8,
            title="MST label",
        )

    axis.set_xticks(list(MST_LABELS))
    axis.set_xticklabels([f"MST {label}" for label in MST_LABELS])
    axis.set_xlabel("Official Monk Skin Tone Label")
    axis.set_ylabel("Per-subject median ITA (degrees)")
    axis.set_title(
        "Per-subject median ITA by official MST label "
        "(clean MST-E calibration subset)"
    )
    axis.grid(axis="y", linestyle=":", alpha=0.5)
    figure.text(0.01, 0.01, DISCLAIMER, fontsize=8, color="#555555")
    figure.tight_layout(rect=(0, 0.05, 0.94, 1))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def plot_ita_vs_skin_ratio(frame: pd.DataFrame, output_path: Path) -> None:
    """Scatter of ITA against skin ratio, coloured by MST label."""
    figure, axis = plt.subplots(figsize=(12, 6.5))

    if frame.empty or "skin_ratio_percent" not in frame.columns:
        axis.text(
            0.5,
            0.5,
            "skin_ratio_percent is not available in this table",
            ha="center",
            va="center",
            transform=axis.transAxes,
        )
    else:
        for label in MST_LABELS:
            subset = frame[frame["source_mst_label"] == label]
            axis.scatter(
                subset["skin_ratio_percent"],
                subset["ita_degrees"],
                s=22,
                alpha=0.7,
                color=LABEL_COLOURS[(label - 1) % len(LABEL_COLOURS)],
                edgecolors="none",
                label=f"MST {label}",
            )
        axis.axvline(
            SKIN_RATIO_MIN,
            color="#888888",
            linestyle="--",
            linewidth=1,
        )
        axis.axvline(
            SKIN_RATIO_MAX,
            color="#888888",
            linestyle="--",
            linewidth=1,
        )
        axis.text(
            SKIN_RATIO_MIN,
            axis.get_ylim()[0],
            f" {int(SKIN_RATIO_MIN)}%",
            va="bottom",
            ha="left",
            fontsize=8,
            color="#555555",
        )
        axis.text(
            SKIN_RATIO_MAX,
            axis.get_ylim()[0],
            f" {int(SKIN_RATIO_MAX)}% ",
            va="bottom",
            ha="right",
            fontsize=8,
            color="#555555",
        )
        axis.legend(
            loc="center left",
            bbox_to_anchor=(1.01, 0.5),
            fontsize=8,
            title="MST label",
        )

    axis.set_xlabel("Skin mask ratio (% of face box)")
    axis.set_ylabel("Computed ITA (degrees)")
    axis.set_title(
        "Computed ITA vs skin-mask ratio by official MST label "
        "(clean MST-E calibration subset)"
    )
    axis.grid(linestyle=":", alpha=0.5)
    figure.text(0.01, 0.01, DISCLAIMER, fontsize=8, color="#555555")
    figure.tight_layout(rect=(0, 0.05, 0.94, 1))
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
            "Diagnostic (non-threshold) analysis of the clean MST-E ITA "
            "calibration table: full, lighting-stratified, conservative "
            "well-lit, and per-subject views."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Clean calibration CSV to read (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--diagnostic-summary",
        type=Path,
        default=DEFAULT_DIAGNOSTIC_SUMMARY,
        help=(
            "Stacked diagnostic summary CSV to write "
            f"(default: {DEFAULT_DIAGNOSTIC_SUMMARY})"
        ),
    )
    parser.add_argument(
        "--conservative-subset",
        type=Path,
        default=DEFAULT_CONSERVATIVE_SUBSET,
        help=(
            "Conservative well-lit subset rows CSV to write "
            f"(default: {DEFAULT_CONSERVATIVE_SUBSET})"
        ),
    )
    parser.add_argument(
        "--lighting-figure",
        type=Path,
        default=DEFAULT_LIGHTING_FIGURE,
        help=f"Lighting boxplot PNG (default: {DEFAULT_LIGHTING_FIGURE})",
    )
    parser.add_argument(
        "--subject-figure",
        type=Path,
        default=DEFAULT_SUBJECT_FIGURE,
        help=f"Per-subject scatter PNG (default: {DEFAULT_SUBJECT_FIGURE})",
    )
    parser.add_argument(
        "--skin-ratio-figure",
        type=Path,
        default=DEFAULT_SKIN_RATIO_FIGURE,
        help=f"ITA vs skin-ratio scatter PNG (default: {DEFAULT_SKIN_RATIO_FIGURE})",
    )
    parser.add_argument(
        "--min-per-label",
        type=int,
        default=DEFAULT_MIN_PER_LABEL,
        help=(
            "Warn when a label has fewer rows than this in a subset "
            f"(default: {DEFAULT_MIN_PER_LABEL})"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Run the diagnostic analysis and write every output."""
    args = parse_arguments()

    if not args.input.is_file():
        print(f"ERROR: the clean calibration file was not found: {args.input}")
        print("Run scripts/07_build_clean_mst_e_calibration.py first.")
        sys.exit(1)

    try:
        clean = read_csv_flexible(args.input)
        full = select_diagnostic_rows(clean)
    except ValueError as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    conservative = build_conservative_subset(full)
    label_summary = summarize_ita_by_label(full)
    lighting_summary = summarize_ita_by_label_and_lighting(full)
    subject_summary = per_subject_median_by_label(full)
    diagnostic = build_diagnostic_summary(full, conservative)

    args.diagnostic_summary.parent.mkdir(parents=True, exist_ok=True)
    diagnostic.to_csv(args.diagnostic_summary, index=False)
    args.conservative_subset.parent.mkdir(parents=True, exist_ok=True)
    conservative.to_csv(args.conservative_subset, index=False)

    plot_ita_by_label_lighting(full, args.lighting_figure)
    plot_ita_by_label_subject(subject_summary, label_summary, args.subject_figure)
    plot_ita_vs_skin_ratio(full, args.skin_ratio_figure)

    # ------------------------------------------------------------------
    # Console report
    # ------------------------------------------------------------------
    print("=" * 72)
    print("MST-E ITA calibration diagnostic (no thresholds decided here)")
    print("=" * 72)
    print(f"Input (clean table)      : {args.input}")
    print(f"Total clean rows read    : {len(clean)}")
    print(f"Full included rows (A)   : {len(full)}")
    print(f"  Sample count per label : {format_label_counts(full)}")
    print_count_warnings(label_summary, args.min_per_label, "Analysis A (full)")

    print()
    print("Analysis B - lighting-stratified:")
    if lighting_summary.empty:
        print("  (source_lighting unavailable; no lighting breakdown)")
    else:
        for lighting in sorted(lighting_summary["source_lighting"].unique()):
            subset = lighting_summary[
                lighting_summary["source_lighting"] == lighting
            ]
            lighting_rows = full[
                full["source_lighting"].map(read_text) == lighting
            ]
            print(f"  {lighting}:")
            print(
                f"    sample count per label : "
                f"{format_label_counts(lighting_rows)}"
            )
            print_count_warnings(
                subset, args.min_per_label, f"Analysis B ({lighting})"
            )

    print()
    print("Analysis C - conservative well-lit subset:")
    print(
        f"  Filters: source_lighting == well_lit AND "
        f"{SKIN_RATIO_MIN:.0f} <= skin_ratio_percent <= {SKIN_RATIO_MAX:.0f}"
    )
    print(f"  Rows kept              : {len(conservative)}")
    print(f"  Sample count per label : {format_label_counts(conservative)}")
    conservative_summary = summarize_ita_by_label(conservative)
    print_count_warnings(
        conservative_summary, args.min_per_label, "Analysis C (conservative)"
    )

    print()
    print("Per-subject breakdown:")
    if subject_summary.empty:
        print("  (no subject identifiers found)")
    else:
        print(
            f"  Subjects with data     : "
            f"{subject_summary['subject_id'].nunique()}"
        )

    print()
    print("Outputs:")
    print(f"  Diagnostic summary CSV : {args.diagnostic_summary}")
    print(f"  Conservative subset CSV : {args.conservative_subset}")
    print(f"  Lighting figure PNG    : {args.lighting_figure}")
    print(f"  Subject figure PNG     : {args.subject_figure}")
    print(f"  Skin-ratio figure PNG  : {args.skin_ratio_figure}")

    print()
    print("Reminder: this is a diagnostic sensitivity analysis, not an attempt")
    print("to hide unfavourable results. The conservative subset is NOT a final")
    print("permanent threshold. Do NOT derive ITA-to-MST thresholds or train the")
    print("correction model yet.")


if __name__ == "__main__":
    main()
