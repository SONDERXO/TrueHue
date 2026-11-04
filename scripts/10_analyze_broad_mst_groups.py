"""
10_analyze_broad_mst_groups.py

Purpose:
    The MST-E ITA diagnostics showed that adjacent official MST labels overlap
    substantially, so a precise ten-level ITA-to-MST threshold table must NOT be
    created. Instead, this script pools the ten official labels into three broad
    official-MST groups and describes them:

        light   : MST 1, 2, 3
        medium  : MST 4, 5, 6, 7
        dark    : MST 8, 9, 10

    For each broad group it reports count, mean/median ITA, standard deviation,
    minimum, Q1, Q3, maximum, mean/median skin ratio, and (when subject identity
    is available) the count of distinct subjects. The same summary is produced
    per lighting condition when ``source_lighting`` is present.

    The grouping uses the *official* MST-E ground-truth labels. It never uses a
    predicted group label, never derives an automatic ITA threshold, never
    trains a model, and never modifies Skin Mask V2, ITA, face detection, CIELAB
    conversion, or any raw dataset. MST-E is evaluation/calibration data only
    and must never enter model training.

Input:
    data/manifests/mst_e_ita_conservative_subset.csv

Outputs:
    data/manifests/mst_e_ita_broad_group_summary.csv
    data/manifests/mst_e_ita_broad_group_by_lighting_summary.csv
    outputs/figures/mst_e_ita_broad_groups.png
    outputs/figures/mst_e_ita_broad_groups_by_lighting.png

Run from the project root:
    python scripts/10_analyze_broad_mst_groups.py
    python scripts/10_analyze_broad_mst_groups.py --min-group-count 20
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
# -----------------------------------------------------------

DEFAULT_INPUT = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_conservative_subset.csv"
)
DEFAULT_GROUP_SUMMARY = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_broad_group_summary.csv"
)
DEFAULT_LIGHTING_SUMMARY = (
    PROJECT_ROOT / "data" / "manifests"
    / "mst_e_ita_broad_group_by_lighting_summary.csv"
)
DEFAULT_GROUP_FIGURE = (
    PROJECT_ROOT / "outputs" / "figures" / "mst_e_ita_broad_groups.png"
)
DEFAULT_LIGHTING_FIGURE = (
    PROJECT_ROOT / "outputs" / "figures" / "mst_e_ita_broad_groups_by_lighting.png"
)

#: Official MST label -> broad official group.
BROAD_GROUPS: dict[str, tuple[int, ...]] = {
    "light": (1, 2, 3),
    "medium": (4, 5, 6, 7),
    "dark": (8, 9, 10),
}

#: Display order of the broad groups (bright -> dark).
GROUP_ORDER: tuple[str, ...] = ("light", "medium", "dark")

#: Reverse lookup: official label -> broad group.
LABEL_TO_GROUP: dict[int, str] = {
    label: group for group, labels in BROAD_GROUPS.items() for label in labels
}

#: Manual quality labels accepted as calibration input.
QUALITY_ELIGIBLE: frozenset[str] = frozenset({"good", "acceptable"})

#: A broad group with fewer images than this triggers a warning.
DEFAULT_MIN_GROUP_COUNT = 20

#: Summary column layouts.
BROAD_GROUP_SUMMARY_COLUMNS: tuple[str, ...] = (
    "broad_group",
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
    "distinct_subjects",
)
BROAD_GROUP_LIGHTING_SUMMARY_COLUMNS: tuple[str, ...] = (
    "broad_group",
    "source_lighting",
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
    "distinct_subjects",
)

#: Colour-blind-friendly palette for the three groups.
GROUP_COLOURS: dict[str, str] = {
    "light": "#F0C571",
    "medium": "#B98A5E",
    "dark": "#5A3A24",
}

DISCLAIMER = (
    "Official MST-E ground-truth group analysis (light = MST 1-3, "
    "medium = MST 4-7, dark = MST 8-10).\nGroups are official labels, NOT "
    "predicted labels. Descriptive only: no ITA threshold is derived and no "
    "model is trained here."
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


def extract_subject(image_id: object, relative_path: object = "") -> str | None:
    """Extract the dataset's own subject folder (``subject_0``) if present."""
    for text in (read_text(image_id), read_text(relative_path)):
        match = re.search(r"subject[\s_\-]?(\d+)", text, re.IGNORECASE)
        if match:
            return f"subject_{int(match.group(1))}"
    return None


def subject_values(frame: pd.DataFrame) -> pd.Series:
    """Return a subject identifier per row.

    Prefers an existing ``subject_id`` column; otherwise derives the identifier
    from ``image_id`` / ``relative_path``. The identifier is only the dataset's
    own folder name and never carries personal information.
    """
    if "subject_id" in frame.columns:
        return frame["subject_id"].map(read_text)

    empty = pd.Series([""] * len(frame), index=frame.index)
    ids = frame["image_id"] if "image_id" in frame.columns else empty
    paths = (
        frame["relative_path"] if "relative_path" in frame.columns else empty
    )
    return pd.Series(
        [extract_subject(image_id, path) or "" for image_id, path in zip(ids, paths)],
        index=frame.index,
    )


# -------------------------------------------------------------------
# Filtering and group assignment
# -------------------------------------------------------------------


def select_included_rows(frame: pd.DataFrame) -> pd.DataFrame:
    """Keep only valid included rows (same rule as scripts 07-09)."""
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
        & labels.isin(list(LABEL_TO_GROUP))
    )

    selected = work.loc[mask].copy()
    selected["source_mst_label"] = labels[mask].astype(int)
    selected["ita_degrees"] = ita[mask]
    if "skin_ratio_percent" in selected.columns:
        selected["skin_ratio_percent"] = pd.to_numeric(
            selected["skin_ratio_percent"], errors="coerce"
        )
    return selected


def assign_broad_group(label: object) -> str | None:
    """Map one official MST label to its broad group, or ``None``.

    The label must be an integer value (``3`` and ``3.0`` are accepted, but
    ``2.5`` and non-numeric text are not).
    """
    if label is None:
        return None
    try:
        numeric = float(str(label).strip())
    except (TypeError, ValueError):
        return None
    if not numeric.is_integer():
        return None
    return LABEL_TO_GROUP.get(int(numeric))


def add_broad_group(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a ``broad_group`` column (official labels only)."""
    work = frame.copy()
    work["broad_group"] = work["source_mst_label"].map(assign_broad_group)
    return work


# -------------------------------------------------------------------
# Summaries
# -------------------------------------------------------------------


def _group_stats(subset: pd.DataFrame) -> dict[str, object]:
    """Return the descriptive statistics for one broad-group subset."""
    ita = pd.to_numeric(subset["ita_degrees"], errors="coerce").dropna()
    if "skin_ratio_percent" in subset.columns:
        ratio = pd.to_numeric(subset["skin_ratio_percent"], errors="coerce").dropna()
    else:
        ratio = pd.Series(dtype=float)

    if ita.empty:
        record: dict[str, object] = {
            "count": 0,
            "mean_ita": np.nan,
            "median_ita": np.nan,
            "standard_deviation_ita": np.nan,
            "minimum_ita": np.nan,
            "q1_ita": np.nan,
            "q3_ita": np.nan,
            "maximum_ita": np.nan,
        }
    else:
        record = {
            "count": int(ita.shape[0]),
            "mean_ita": float(ita.mean()),
            "median_ita": float(ita.median()),
            "standard_deviation_ita": (
                float(ita.std()) if ita.shape[0] > 1 else np.nan
            ),
            "minimum_ita": float(ita.min()),
            "q1_ita": float(ita.quantile(0.25)),
            "q3_ita": float(ita.quantile(0.75)),
            "maximum_ita": float(ita.max()),
        }

    record["mean_skin_ratio_percent"] = (
        float(ratio.mean()) if not ratio.empty else np.nan
    )
    record["median_skin_ratio_percent"] = (
        float(ratio.median()) if not ratio.empty else np.nan
    )
    subjects = subject_values(subset)
    record["distinct_subjects"] = int(subjects[subjects != ""].nunique())
    return record


def summarize_broad_groups(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the per-broad-group ITA summary (light, medium, dark)."""
    work = frame if "broad_group" in frame.columns else add_broad_group(frame)
    records: list[dict[str, object]] = []
    for group in GROUP_ORDER:
        subset = work[work["broad_group"] == group]
        record = {"broad_group": group}
        record.update(_group_stats(subset))
        records.append(record)
    return pd.DataFrame(records, columns=list(BROAD_GROUP_SUMMARY_COLUMNS))


def summarize_broad_groups_by_lighting(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the per-broad-group, per-lighting ITA summary.

    Returns an empty, correctly-shaped frame when ``source_lighting`` is absent
    or blank for every row.
    """
    if "source_lighting" not in frame.columns:
        return pd.DataFrame(
            columns=list(BROAD_GROUP_LIGHTING_SUMMARY_COLUMNS)
        )

    work = frame if "broad_group" in frame.columns else add_broad_group(frame)
    work = work[work["broad_group"].notna()].copy()
    work["source_lighting"] = work["source_lighting"].map(read_text)
    work = work[work["source_lighting"] != ""]
    if work.empty:
        return pd.DataFrame(
            columns=list(BROAD_GROUP_LIGHTING_SUMMARY_COLUMNS)
        )

    records: list[dict[str, object]] = []
    for (group, lighting), subset in work.groupby(
        ["broad_group", "source_lighting"], dropna=False
    ):
        record = {"broad_group": group, "source_lighting": lighting}
        record.update(_group_stats(subset))
        records.append(record)

    summary = pd.DataFrame(
        records, columns=list(BROAD_GROUP_LIGHTING_SUMMARY_COLUMNS)
    )
    order = {group: index for index, group in enumerate(GROUP_ORDER)}
    summary["_order"] = summary["broad_group"].map(order).fillna(len(order))
    summary = summary.sort_values(
        ["_order", "source_lighting"], ignore_index=True
    ).drop(columns="_order")
    return summary


def low_count_groups(summary: pd.DataFrame, minimum: int) -> list[str]:
    """Return broad groups whose ``count`` is below ``minimum``."""
    return [
        str(row.broad_group)
        for row in summary.itertuples(index=False)
        if int(row.count) < minimum
    ]


# -------------------------------------------------------------------
# Separability diagnostic
# -------------------------------------------------------------------


def _common_language_effect(brighter: pd.Series, darker: pd.Series) -> float:
    """Return P(brighter > darker) + 0.5 * P(brighter == darker).

    0.5 means complete overlap; 1.0 means the brighter set is always larger.
    Higher ITA means lighter skin, so a brighter group should score above 0.5.
    """
    a = pd.to_numeric(brighter, errors="coerce").dropna().to_numpy()
    b = pd.to_numeric(darker, errors="coerce").dropna().to_numpy()
    if a.size == 0 or b.size == 0:
        return np.nan
    greater = (a[:, None] > b[None, :]).sum()
    equal = (a[:, None] == b[None, :]).sum()
    total = a.size * b.size
    return float((greater + 0.5 * equal) / total)


def adjacent_separability(frame: pd.DataFrame) -> dict[str, float]:
    """Compare adjacent broad groups vs adjacent individual labels.

    Uses the average common-language effect size across adjacent ordered pairs.
    A value near 0.5 means the two distributions overlap almost completely.
    """
    work = frame if "source_mst_label" in frame.columns else frame.copy()

    broad_pairs = [
        ("light", "medium"),
        ("medium", "dark"),
    ]
    broad_scores: list[float] = []
    for brighter, darker in broad_pairs:
        bright_labels = BROAD_GROUPS[brighter]
        dark_labels = BROAD_GROUPS[darker]
        bright = work.loc[
            work["source_mst_label"].isin(bright_labels), "ita_degrees"
        ]
        dark = work.loc[
            work["source_mst_label"].isin(dark_labels), "ita_degrees"
        ]
        score = _common_language_effect(bright, dark)
        if not np.isnan(score):
            broad_scores.append(score)

    label_scores: list[float] = []
    labels = sorted(LABEL_TO_GROUP)
    for brighter, darker in zip(labels, labels[1:]):
        bright = work.loc[work["source_mst_label"] == brighter, "ita_degrees"]
        dark = work.loc[work["source_mst_label"] == darker, "ita_degrees"]
        score = _common_language_effect(bright, dark)
        if not np.isnan(score):
            label_scores.append(score)

    return {
        "broad_mean": float(np.mean(broad_scores)) if broad_scores else np.nan,
        "broad_pairs": len(broad_scores),
        "label_mean": float(np.mean(label_scores)) if label_scores else np.nan,
        "label_pairs": len(label_scores),
    }


# -------------------------------------------------------------------
# Figures
# -------------------------------------------------------------------


def plot_broad_groups(frame: pd.DataFrame, output_path: Path) -> None:
    """Boxplots of ITA across the light, medium, and dark official groups."""
    work = frame if "broad_group" in frame.columns else add_broad_group(frame)

    values: list[np.ndarray] = []
    labels: list[str] = []
    for group in GROUP_ORDER:
        subset = work.loc[work["broad_group"] == group, "ita_degrees"]
        values.append(
            pd.to_numeric(subset, errors="coerce").dropna().to_numpy()
        )
        labels.append(f"{group}\n(n={values[-1].size})")

    figure, axis = plt.subplots(figsize=(9, 6.5))
    if any(array.size for array in values):
        axis.boxplot(
            values,
            positions=range(1, len(GROUP_ORDER) + 1),
            widths=0.6,
            showfliers=True,
            patch_artist=True,
            boxprops={"edgecolor": "#333333"},
            medianprops={"color": "#B22222", "linewidth": 2},
        )
        for patch, group in zip(axis.patches, GROUP_ORDER):
            patch.set_facecolor(GROUP_COLOURS[group])

    axis.set_xticks(range(1, len(GROUP_ORDER) + 1))
    axis.set_xticklabels(labels)
    axis.set_xlabel("Official MST Broad Group")
    axis.set_ylabel("Computed ITA (degrees)")
    axis.set_title(
        "Computed ITA by official broad MST group "
        "(light = MST 1-3, medium = MST 4-7, dark = MST 8-10)"
    )
    axis.grid(axis="y", linestyle=":", alpha=0.5)
    figure.text(0.01, 0.01, DISCLAIMER, fontsize=7.5, color="#555555")
    figure.tight_layout(rect=(0, 0.06, 1, 1))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def plot_broad_groups_by_lighting(frame: pd.DataFrame, output_path: Path) -> None:
    """Grouped boxplots of ITA across broad groups and lighting conditions."""
    work = frame if "broad_group" in frame.columns else add_broad_group(frame)
    figure, axis = plt.subplots(figsize=(10, 6.5))

    if "source_lighting" in work.columns:
        lighting_frame = work.copy()
        lighting_frame["source_lighting"] = lighting_frame["source_lighting"].map(
            read_text
        )
        lighting_frame = lighting_frame[lighting_frame["source_lighting"] != ""]
    else:
        lighting_frame = work.iloc[0:0]

    if "source_lighting" in lighting_frame.columns:
        lighting_names = sorted(lighting_frame["source_lighting"].unique().tolist())
    else:
        lighting_names = []
    if lighting_names:
        width = 0.8 / len(lighting_names)
        positions = range(1, len(GROUP_ORDER) + 1)
        for index, lighting in enumerate(lighting_names):
            offset = (index - (len(lighting_names) - 1) / 2) * width
            values = [
                pd.to_numeric(
                    lighting_frame.loc[
                        (lighting_frame["broad_group"] == group)
                        & (lighting_frame["source_lighting"] == lighting),
                        "ita_degrees",
                    ],
                    errors="coerce",
                )
                .dropna()
                .to_numpy()
                for group in GROUP_ORDER
            ]
            axis.boxplot(
                values,
                positions=[position + offset for position in positions],
                widths=width * 0.9,
                showfliers=True,
                patch_artist=True,
                boxprops={
                    "facecolor": "#4C72B0" if index == 0 else "#DD8452",
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
                    facecolor="#4C72B0" if index == 0 else "#DD8452",
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
            "source_lighting is not available in this table",
            ha="center",
            va="center",
            transform=axis.transAxes,
        )

    axis.set_xticks(list(range(1, len(GROUP_ORDER) + 1)))
    axis.set_xticklabels([group for group in GROUP_ORDER])
    axis.set_xlabel("Official MST Broad Group")
    axis.set_ylabel("Computed ITA (degrees)")
    axis.set_title(
        "Computed ITA by official broad MST group and lighting "
        "(light = MST 1-3, medium = MST 4-7, dark = MST 8-10)"
    )
    axis.grid(axis="y", linestyle=":", alpha=0.5)
    figure.text(0.01, 0.01, DISCLAIMER, fontsize=7.5, color="#555555")
    figure.tight_layout(rect=(0, 0.06, 1, 1))
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
            "Describe ITA across three broad official MST groups "
            "(light/medium/dark). No thresholds, no model training."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Conservative subset CSV to read (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--group-summary",
        type=Path,
        default=DEFAULT_GROUP_SUMMARY,
        help=f"Broad-group summary CSV to write (default: {DEFAULT_GROUP_SUMMARY})",
    )
    parser.add_argument(
        "--lighting-summary",
        type=Path,
        default=DEFAULT_LIGHTING_SUMMARY,
        help=(
            "Broad-group-by-lighting summary CSV to write "
            f"(default: {DEFAULT_LIGHTING_SUMMARY})"
        ),
    )
    parser.add_argument(
        "--group-figure",
        type=Path,
        default=DEFAULT_GROUP_FIGURE,
        help=f"Broad-group boxplot PNG (default: {DEFAULT_GROUP_FIGURE})",
    )
    parser.add_argument(
        "--lighting-figure",
        type=Path,
        default=DEFAULT_LIGHTING_FIGURE,
        help=(
            "Broad-group-by-lighting boxplot PNG "
            f"(default: {DEFAULT_LIGHTING_FIGURE})"
        ),
    )
    parser.add_argument(
        "--min-group-count",
        type=int,
        default=DEFAULT_MIN_GROUP_COUNT,
        help=(
            "Warn when a broad group has fewer rows than this "
            f"(default: {DEFAULT_MIN_GROUP_COUNT})"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Summarise ITA across broad official MST groups and print a conclusion."""
    args = parse_arguments()

    if not args.input.is_file():
        print(f"ERROR: the input file was not found: {args.input}")
        print("Run scripts/09_diagnose_mst_e_ita_calibration.py first.")
        sys.exit(1)

    try:
        raw = read_csv_flexible(args.input)
        frame = add_broad_group(select_included_rows(raw))
    except ValueError as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    group_summary = summarize_broad_groups(frame)
    lighting_summary = summarize_broad_groups_by_lighting(frame)

    args.group_summary.parent.mkdir(parents=True, exist_ok=True)
    group_summary.to_csv(args.group_summary, index=False)
    args.lighting_summary.parent.mkdir(parents=True, exist_ok=True)
    lighting_summary.to_csv(args.lighting_summary, index=False)

    plot_broad_groups(frame, args.group_figure)
    plot_broad_groups_by_lighting(frame, args.lighting_figure)

    # ------------------------------------------------------------------
    # Console report
    # ------------------------------------------------------------------
    print("=" * 72)
    print("MST-E broad official-group ITA analysis (no thresholds, no model)")
    print("=" * 72)
    print(f"Input                    : {args.input}")
    print(f"Valid included rows      : {len(frame)}")
    print()
    print("Broad group assignment (official MST-E ground-truth labels):")
    for group in GROUP_ORDER:
        members = ", ".join(str(label) for label in BROAD_GROUPS[group])
        print(f"  {group:<7}: MST {members}")
    print()
    print("Per-group ITA summary:")
    display = group_summary.copy()
    for column in display.columns:
        if column in {"broad_group", "count", "distinct_subjects"}:
            continue
        display[column] = display[column].map(
            lambda value: f"{value:.2f}" if pd.notna(value) else "-"
        )
    print(display.to_string(index=False))

    print()
    print("Small-sample checks:")
    low = low_count_groups(group_summary, args.min_group_count)
    if low:
        for group in low:
            row = group_summary[group_summary["broad_group"] == group].iloc[0]
            print(
                f"  WARNING: broad group '{group}' has only {int(row['count'])} "
                f"image(s) (< {args.min_group_count}); treat its ITA statistics "
                "as indicative only."
            )
    else:
        print(
            f"  OK: every broad group has at least {args.min_group_count} images."
        )

    if lighting_summary.empty:
        print()
        print("Lighting breakdown: source_lighting not available.")
    else:
        print()
        print("Lighting breakdown rows written:")
        for row in lighting_summary.itertuples(index=False):
            print(
                f"  {row.broad_group:<7} {row.source_lighting:<12} "
                f"n={int(row.count):<4} median_ita={row.median_ita:.2f}"
            )

    separability = adjacent_separability(frame)
    print()
    print("-" * 72)
    print("Conclusion: are the three broad groups more separable than the ten")
    print("individual labels?")
    print("-" * 72)
    print(
        "  Metric: average adjacent-pair common-language effect size (AUC); "
        "0.5 = full overlap, 1.0 = perfect separation."
    )
    print(
        f"  Three broad groups : {separability['broad_mean']:.3f} "
        f"({int(separability['broad_pairs'])} adjacent pairs)"
    )
    print(
        f"  Ten individual labels: {separability['label_mean']:.3f} "
        f"({int(separability['label_pairs'])} adjacent pairs)"
    )
    if (
        not np.isnan(separability["broad_mean"])
        and not np.isnan(separability["label_mean"])
        and separability["broad_mean"] > separability["label_mean"]
    ):
        print(
            "  RESULT: YES - pooling the overlaps into light/medium/dark gives "
            "more separation than\n          adjacent individual labels, so a "
            "broad three-group mapping is more defensible\n          than a "
            "precise ten-level ITA-to-MST threshold table."
        )
    else:
        print(
            "  RESULT: NO clear improvement - broad groups do not separate "
            "better than adjacent\n          individual labels on this subset. "
            "Do not create a precise threshold table."
        )
    print()
    print("Even where broad groups separate better, adjacent labels within a")
    print("group still overlap. Do NOT create a ten-level ITA-to-MST threshold")
    print("table, and do NOT train the correction model yet. MST-E remains")
    print("evaluation/calibration data only.")

    print()
    print("Outputs:")
    print(f"  Broad-group summary CSV      : {args.group_summary}")
    print(f"  Broad-group lighting CSV     : {args.lighting_summary}")
    print(f"  Broad-group figure PNG       : {args.group_figure}")
    print(f"  Broad-group lighting PNG     : {args.lighting_figure}")


if __name__ == "__main__":
    main()
