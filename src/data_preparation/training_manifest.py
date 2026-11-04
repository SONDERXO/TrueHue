"""
Training-data preparation for FairFace and SCIN.

Purpose
-------
This module turns the results of running the frozen TrueHue pipeline over the
training datasets (FairFace and SCIN) into three auditable manifests:

1. ``fairface_processed_manifest.csv``
2. ``scin_processed_manifest.csv``
3. ``training_candidates_manifest.csv``

The first two list *every* processed image with its measurement, processing
status, and (when it is not usable) the reason it was excluded. The third is
the clean, excluded-free, optionally capped subset that a later stage may use
to train the correction model.

What is deliberately fixed here
-------------------------------
- Skin Mask V2 (HSV/YCrCb + morphology + largest component + landmark
  eye/eyebrow/lip exclusion) is the selected segmentation method. This module
  never changes the detector, the skin mask, or the ITA math; it only records
  their outcome.
- ITA stays a *continuous* feature. No ten-level ITA-to-MST threshold table is
  derived here.
- The only broad groups are the three documented pools
  ``light = MST 1-3``, ``medium = MST 4-7``, ``dark = MST 8-10``.
- SCIN MST labels come from SCIN's *official* metadata when available and are
  recorded as ground truth. FairFace has no official MST label, so its
  ``source_mst_label`` stays empty and any broad group for FairFace can only be
  an ITA-based *estimate*, never ground truth.
- MST-E never appears in a training manifest. It is evaluation/calibration
  data only; :func:`validate_training_dataset_names` rejects it.

Official vs estimated group labels
----------------------------------
``group_assignment_source`` records where a row's broad group came from:

- ``official_scin_mst``   the group was derived from SCIN's official MST label
- ``estimated_from_ita``  the group is an estimate from ITA using a *documented,
                          externally supplied* rule (never derived here)
- ``none``                no group could be assigned

An ITA estimate is **not** ground truth and is marked as such everywhere.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Broad groups (the only documented grouping)
# ---------------------------------------------------------------------------

#: Documented broad groups over the official 1-10 MST labels.
BROAD_GROUPS: dict[str, tuple[int, ...]] = {
    "light": (1, 2, 3),
    "medium": (4, 5, 6, 7),
    "dark": (8, 9, 10),
}

#: Display order (bright -> dark).
GROUP_ORDER: tuple[str, ...] = ("light", "medium", "dark")

#: Reverse lookup: official MST label -> broad group.
LABEL_TO_GROUP: dict[int, str] = {
    label: group for group, labels in BROAD_GROUPS.items() for label in labels
}

#: Label used when a row cannot be assigned to any broad group.
UNASSIGNED_GROUP = "unassigned"


# ---------------------------------------------------------------------------
# Dataset roles
# ---------------------------------------------------------------------------

FAIRFACE_DATASET_NAME = "FairFace"
SCIN_DATASET_NAME = "SCIN"

#: Datasets this module may prepare. MST-E is intentionally absent.
TRAINING_DATASET_NAMES: tuple[str, ...] = (
    FAIRFACE_DATASET_NAME,
    SCIN_DATASET_NAME,
)

#: Dataset keys (lowercased, alphanumerics only) that must never be trained on.
_MST_E_KEYS: frozenset[str] = frozenset({"mste"})


def is_mst_e_name(dataset_name: object) -> bool:
    """Return True when ``dataset_name`` refers to MST-E (any spelling)."""
    text = read_text(dataset_name).lower()
    key = "".join(character for character in text if character.isalnum())
    return key in _MST_E_KEYS


def validate_training_dataset_names(names: Iterable[object]) -> None:
    """Raise ``ValueError`` if any name is MST-E.

    Training manifests must never contain MST-E rows. This is checked in code
    rather than left to documentation so a later script cannot silently pick
    MST-E up.

    Parameters
    ----------
    names : Iterable[object]
        Dataset names about to be written into a training manifest.

    Raises
    ------
    ValueError
        If any name refers to MST-E.
    """
    offending = sorted(
        {str(name) for name in names if is_mst_e_name(name)}
    )
    if offending:
        raise ValueError(
            "MST-E must never appear in a training manifest; it is "
            f"evaluation/calibration data only. Offending dataset name(s): "
            f"{offending}."
        )


# ---------------------------------------------------------------------------
# Processing status and exclusion reasons
# ---------------------------------------------------------------------------

#: ``processing_status`` values.
STATUS_SUCCESS = "success"
STATUS_EXCLUDED = "excluded"

#: Stable, machine-readable exclusion reasons.
EXCLUSION_CORRUPT_IMAGE = "corrupt_or_unreadable_image"
EXCLUSION_NO_FACE = "no_face_detected"
EXCLUSION_MULTI_FACE = "multiple_faces_detected"
EXCLUSION_NO_MASK = "skin_mask_unavailable"
EXCLUSION_MASK_FALLBACK = "skin_mask_v1_fallback_landmarks_unavailable"
EXCLUSION_INSUFFICIENT_SKIN = "insufficient_skin_pixels"
EXCLUSION_ITA_FAILED = "ita_estimation_failed"

#: All exclusion reasons, in the order they are checked.
EXCLUSION_REASONS: tuple[str, ...] = (
    EXCLUSION_CORRUPT_IMAGE,
    EXCLUSION_NO_FACE,
    EXCLUSION_MULTI_FACE,
    EXCLUSION_NO_MASK,
    EXCLUSION_MASK_FALLBACK,
    EXCLUSION_INSUFFICIENT_SKIN,
    EXCLUSION_ITA_FAILED,
)

#: Human-readable explanation for each exclusion reason.
EXCLUSION_DESCRIPTIONS: dict[str, str] = {
    EXCLUSION_CORRUPT_IMAGE: "OpenCV could not read the image file.",
    EXCLUSION_NO_FACE: "No face was detected by the YuNet detector.",
    EXCLUSION_MULTI_FACE: (
        "More than one face was detected; the system supports a single face."
    ),
    EXCLUSION_NO_MASK: "The skin mask could not be created.",
    EXCLUSION_MASK_FALLBACK: (
        "Landmark feature exclusion was unavailable, so the V1 fallback mask "
        "would have been produced instead of Skin Mask V2."
    ),
    EXCLUSION_INSUFFICIENT_SKIN: (
        "Fewer than the minimum number of valid skin pixels were selected."
    ),
    EXCLUSION_ITA_FAILED: "ITA could not be computed for the selected skin.",
}


# ---------------------------------------------------------------------------
# Group assignment sources
# ---------------------------------------------------------------------------

GROUP_SOURCE_OFFICIAL = "official_scin_mst"
GROUP_SOURCE_ESTIMATED = "estimated_from_ita"
GROUP_SOURCE_NONE = "none"


# ---------------------------------------------------------------------------
# Column layout
# ---------------------------------------------------------------------------

#: Columns of every processed/candidates manifest, in order.
MANIFEST_COLUMNS: tuple[str, ...] = (
    "dataset_name",
    "image_id",
    "image_path",
    "source_label",
    "source_mst_label",
    "source_broad_mst_group",
    "estimated_broad_mst_group",
    "group_assignment_source",
    "face_detected",
    "landmarks_available",
    "skin_pixels",
    "skin_ratio_percent",
    "mean_l_star",
    "mean_a_star",
    "mean_b_star",
    "ita_degrees",
    "processing_status",
    "exclusion_reason",
    "intended_use",
)

#: ``intended_use`` written for training-dataset rows.
INTENDED_USE_TRAINING = "training"


# ---------------------------------------------------------------------------
# Small cell helpers
# ---------------------------------------------------------------------------


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


def read_label(value: object) -> int | None:
    """Return an integer MST label, or ``None`` when the cell is empty/invalid."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):  # pragma: no cover - defensive
        pass
    text = str(value).strip()
    if not text:
        return None
    try:
        numeric = float(text)
    except ValueError:
        return None
    if not numeric.is_integer():
        return None
    return int(numeric)


# ---------------------------------------------------------------------------
# Official broad-group assignment
# ---------------------------------------------------------------------------


def broad_group_for_label(label: object) -> str | None:
    """Map one official MST label to its documented broad group, or ``None``.

    ``3`` and ``3.0`` are accepted; ``2.5`` and non-numeric text are not.
    """
    integer = read_label(label)
    if integer is None:
        return None
    return LABEL_TO_GROUP.get(integer)


# ---------------------------------------------------------------------------
# ITA-based estimated broad groups (external, documented rule)
# ---------------------------------------------------------------------------

#: Required top-level keys of an estimated-group rule file.
_RULE_REQUIRED_KEYS: tuple[str, ...] = ("name", "intervals")


def load_estimated_group_rule(path: str | Path) -> dict:
    """Load and validate a documented ITA-to-broad-group rule from JSON.

    The rule is supplied *externally* by a human; nothing in this module
    derives or guesses thresholds. The JSON format is::

        {
          "name": "documented_broad_group_rule_v1",
          "source": "docs/training-data-preparation-protocol.md",
          "notes": "optional free text",
          "intervals": [
            {"broad_group": "dark",   "min_ita": null,  "max_ita": -30.0},
            {"broad_group": "medium", "min_ita": -30.0, "max_ita": 10.0},
            {"broad_group": "light",  "min_ita": 10.0,  "max_ita": null}
          ]
        }

    Each interval is half-open ``[min_ita, max_ita)``; ``null`` means
    unbounded on that side. Intervals must not overlap and each broad group
    may appear at most once.

    Parameters
    ----------
    path : str | Path
        Path to the JSON rule file.

    Returns
    -------
    dict
        Normalised rule with keys ``name``, ``source``, ``notes`` and
        ``intervals`` (a list of ``(broad_group, min_ita, max_ita)`` tuples).

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the JSON is malformed or the intervals overlap / are invalid.
    """
    rule_path = Path(path)
    if not rule_path.is_file():
        raise FileNotFoundError(
            f"Estimated broad-group rule file was not found: {rule_path}. "
            "Provide a documented JSON rule, or omit --estimated-group-rule to "
            "leave estimated groups blank."
        )

    try:
        raw = json.loads(rule_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Estimated broad-group rule {rule_path} is not valid JSON: {error}"
        ) from error

    if not isinstance(raw, dict):
        raise ValueError(
            f"Estimated broad-group rule {rule_path} must be a JSON object."
        )

    missing = [key for key in _RULE_REQUIRED_KEYS if key not in raw]
    if missing:
        raise ValueError(
            f"Estimated broad-group rule {rule_path} is missing key(s): "
            f"{missing}. Expected at least {list(_RULE_REQUIRED_KEYS)}."
        )

    raw_intervals = raw["intervals"]
    if not isinstance(raw_intervals, list) or not raw_intervals:
        raise ValueError(
            f"Estimated broad-group rule {rule_path} must list at least one "
            "interval."
        )

    intervals: list[tuple[str, float | None, float | None]] = []
    seen_groups: set[str] = set()
    for index, entry in enumerate(raw_intervals):
        if not isinstance(entry, dict):
            raise ValueError(
                f"Interval {index} in {rule_path} must be a JSON object."
            )
        group = read_text(entry.get("broad_group"))
        if group not in GROUP_ORDER:
            raise ValueError(
                f"Interval {index} in {rule_path} names unknown broad group "
                f"{group!r}; allowed: {list(GROUP_ORDER)}."
            )
        if group in seen_groups:
            raise ValueError(
                f"Broad group {group!r} appears more than once in {rule_path}."
            )
        seen_groups.add(group)

        minimum = _as_optional_float(entry.get("min_ita"), rule_path, index, "min_ita")
        maximum = _as_optional_float(entry.get("max_ita"), rule_path, index, "max_ita")
        if minimum is not None and maximum is not None and minimum >= maximum:
            raise ValueError(
                f"Interval {index} in {rule_path} has min_ita >= max_ita "
                f"({minimum} >= {maximum}); intervals are half-open "
                "[min_ita, max_ita)."
            )
        intervals.append((group, minimum, maximum))

    _check_intervals_do_not_overlap(intervals, rule_path)

    return {
        "name": read_text(raw.get("name")),
        "source": read_text(raw.get("source")),
        "notes": read_text(raw.get("notes")),
        "intervals": intervals,
    }


def _as_optional_float(
    value: object, path: Path, index: int, key: str
) -> float | None:
    """Return ``value`` as a float, ``None`` for null, or raise ``ValueError``."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(
            f"{key} in interval {index} of {path} must be a number or null, "
            "not a boolean."
        )
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{key} in interval {index} of {path} must be a number or null, "
            f"got {value!r}."
        ) from error


def _check_intervals_do_not_overlap(
    intervals: Sequence[tuple[str, float | None, float | None]], path: Path
) -> None:
    """Raise ``ValueError`` when two intervals share ITA values."""
    for first_index, (_, first_min, first_max) in enumerate(intervals):
        for second_index in range(first_index + 1, len(intervals)):
            _, second_min, second_max = intervals[second_index]
            if _intervals_overlap(first_min, first_max, second_min, second_max):
                raise ValueError(
                    f"Intervals {first_index} and {second_index} in {path} "
                    "overlap; each ITA value must map to at most one broad "
                    "group."
                )


def _intervals_overlap(
    first_min: float | None,
    first_max: float | None,
    second_min: float | None,
    second_max: float | None,
) -> bool:
    """Return True when two half-open intervals share any value."""
    lower = max(value for value in (first_min, second_min) if value is not None) if (
        first_min is not None or second_min is not None
    ) else None
    uppers = [value for value in (first_max, second_max) if value is not None]
    upper = min(uppers) if uppers else None
    if lower is None or upper is None:
        return True  # an unbounded side means they always share a range
    return lower < upper


def assign_estimated_broad_group(
    ita_degrees: object, rule: Mapping[str, object] | None
) -> str | None:
    """Return the estimated broad group for an ITA value, or ``None``.

    Only a documented, externally supplied ``rule`` (see
    :func:`load_estimated_group_rule`) can produce an estimate. With no rule,
    or an invalid ITA, the result is ``None``. This is an *estimate*, never
    ground truth.
    """
    if rule is None:
        return None

    try:
        ita = float(ita_degrees)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(ita):
        return None

    for group, minimum, maximum in rule.get("intervals", []):
        above_minimum = minimum is None or ita >= minimum
        below_maximum = maximum is None or ita < maximum
        if above_minimum and below_maximum:
            return str(group)
    return None


# ---------------------------------------------------------------------------
# Exclusion classification
# ---------------------------------------------------------------------------


def classify_exclusion(
    *,
    image_loaded: bool,
    face_count: int,
    mask_created: bool,
    landmarks_available: bool,
    skin_pixels: object,
    ita_valid: bool,
    minimum_skin_pixels: int,
) -> str:
    """Return the exclusion reason for a processing outcome, or ``""``.

    The checks run in a fixed order so every image gets exactly one stable,
    reproducible reason. An empty string means the row is usable.

    Parameters
    ----------
    image_loaded : bool
        ``False`` when OpenCV could not read the file.
    face_count : int
        Number of faces detected; the system supports exactly one.
    mask_created : bool
        ``False`` when the skin mask could not be produced.
    landmarks_available : bool
        ``False`` when Skin Mask V2 fell back to the V1 mask.
    skin_pixels : object
        Number of selected skin pixels (or ``None``).
    ita_valid : bool
        ``False`` when ITA could not be computed.
    minimum_skin_pixels : int
        Minimum selected skin pixels required.

    Returns
    -------
    str
        One of :data:`EXCLUSION_REASONS`, or ``""`` when usable.
    """
    if not image_loaded:
        return EXCLUSION_CORRUPT_IMAGE
    if face_count <= 0:
        return EXCLUSION_NO_FACE
    if face_count > 1:
        return EXCLUSION_MULTI_FACE
    if not mask_created:
        return EXCLUSION_NO_MASK
    if not landmarks_available:
        return EXCLUSION_MASK_FALLBACK

    pixel_count = read_label(skin_pixels)
    if pixel_count is None or pixel_count < minimum_skin_pixels:
        return EXCLUSION_INSUFFICIENT_SKIN
    if not ita_valid:
        return EXCLUSION_ITA_FAILED
    return ""


def describe_exclusion(reason: str) -> str:
    """Return a human-readable description for an exclusion reason."""
    return EXCLUSION_DESCRIPTIONS.get(reason, reason)


# ---------------------------------------------------------------------------
# Row building
# ---------------------------------------------------------------------------


def build_processed_row(
    *,
    dataset_name: str,
    image_id: str,
    image_path: str,
    source_label: object = "",
    source_mst_label: object = None,
    estimated_rule: Mapping[str, object] | None = None,
    face_detected: object = None,
    landmarks_available: object = None,
    skin_pixels: object = None,
    skin_ratio_percent: object = None,
    mean_l_star: object = None,
    mean_a_star: object = None,
    mean_b_star: object = None,
    ita_degrees: object = None,
    exclusion_reason: str = "",
    intended_use: str = INTENDED_USE_TRAINING,
) -> dict:
    """Build one fully-populated manifest row.

    The broad group is taken from the official ``source_mst_label`` when it is
    present (``official_scin_mst``). Otherwise, if ``estimated_rule`` is
    supplied and the ITA is valid, an estimate is recorded
    (``estimated_from_ita``). The two are never mixed: an official label always
    wins and is kept clearly distinct from an estimate.
    """
    label = read_label(source_mst_label)
    official_group = broad_group_for_label(label)

    if official_group is not None:
        source_group = official_group
        estimated_group: str | None = None
        assignment_source = GROUP_SOURCE_OFFICIAL
    else:
        source_group = None
        estimated_group = assign_estimated_broad_group(ita_degrees, estimated_rule)
        assignment_source = (
            GROUP_SOURCE_ESTIMATED if estimated_group is not None else GROUP_SOURCE_NONE
        )

    return {
        "dataset_name": read_text(dataset_name),
        "image_id": read_text(image_id),
        "image_path": read_text(image_path),
        "source_label": read_text(source_label),
        "source_mst_label": label,
        "source_broad_mst_group": source_group,
        "estimated_broad_mst_group": estimated_group,
        "group_assignment_source": assignment_source,
        "face_detected": face_detected,
        "landmarks_available": landmarks_available,
        "skin_pixels": skin_pixels,
        "skin_ratio_percent": skin_ratio_percent,
        "mean_l_star": mean_l_star,
        "mean_a_star": mean_a_star,
        "mean_b_star": mean_b_star,
        "ita_degrees": ita_degrees,
        "processing_status": (
            STATUS_EXCLUDED if exclusion_reason else STATUS_SUCCESS
        ),
        "exclusion_reason": exclusion_reason,
        "intended_use": read_text(intended_use),
    }


def build_processed_manifest(rows: Iterable[Mapping[str, object]]) -> pd.DataFrame:
    """Assemble manifest rows into a DataFrame with the fixed column layout.

    Parameters
    ----------
    rows : Iterable[Mapping[str, object]]
        Row dicts (typically from :func:`build_processed_row`).

    Returns
    -------
    pd.DataFrame
        Frame with exactly :data:`MANIFEST_COLUMNS`, in order.
    """
    frame = pd.DataFrame(list(rows), columns=list(MANIFEST_COLUMNS))
    frame["source_mst_label"] = frame["source_mst_label"].astype("Int64")
    return frame


# ---------------------------------------------------------------------------
# Effective broad group and stratified cap
# ---------------------------------------------------------------------------


def effective_broad_group(row: Mapping[str, object]) -> str:
    """Return the group used for capping: official, else estimated, else unassigned."""
    official = read_text(row.get("source_broad_mst_group"))
    if official:
        return official
    estimated = read_text(row.get("estimated_broad_mst_group"))
    if estimated:
        return estimated
    return UNASSIGNED_GROUP


def _cap_group_series(frame: pd.DataFrame) -> pd.Series:
    """Return the per-row broad group used for stratified capping."""
    return pd.Series(
        [effective_broad_group(record) for record in frame.to_dict("records")],
        index=frame.index,
    )


def apply_stratified_cap(
    frame: pd.DataFrame,
    cap_per_group: int = 0,
    group_order: Sequence[str] = GROUP_ORDER,
    per_dataset: bool = True,
) -> pd.DataFrame:
    """Keep at most ``cap_per_group`` rows per (dataset,) broad group.

    Rows are ordered deterministically before selection so repeated runs keep
    the same images. The output is ordered by ``dataset_name``, broad group
    (``group_order`` first, then any other group), and ``image_id``.

    Parameters
    ----------
    frame : pd.DataFrame
        Candidate rows (already excluded-free).
    cap_per_group : int
        Maximum rows per stratum. ``0`` (or negative) means no cap.
    group_order : Sequence[str]
        Preferred group ordering for the output; groups not listed sort last.
    per_dataset : bool
        When ``True`` (default) the cap applies per ``dataset_name`` *and*
        broad group; otherwise it applies across the whole frame per group.

    Returns
    -------
    pd.DataFrame
        The selected subset, deterministically ordered.
    """
    if frame.empty:
        return frame.copy()

    work = frame.copy()
    work["_cap_group"] = _cap_group_series(work)
    sort_columns = ["dataset_name", "image_id"] if per_dataset else ["image_id"]
    work = work.sort_values(sort_columns, kind="stable")

    if cap_per_group and cap_per_group > 0:
        grouper = ["dataset_name", "_cap_group"] if per_dataset else ["_cap_group"]
        work = work.groupby(grouper, sort=False, group_keys=False).head(
            cap_per_group
        )

    order = {group: index for index, group in enumerate(group_order)}
    work["_order"] = work["_cap_group"].map(order).fillna(len(order))
    work = work.sort_values(
        ["dataset_name", "_order", "image_id"], kind="stable"
    ).drop(columns=["_cap_group", "_order"])
    return work.reset_index(drop=True)


def select_training_candidates(
    frame: pd.DataFrame,
    cap_per_group: int = 0,
    group_order: Sequence[str] = GROUP_ORDER,
) -> pd.DataFrame:
    """Return the clean, capped candidate subset from a processed manifest.

    Only rows whose ``processing_status`` is :data:`STATUS_SUCCESS` are kept,
    and the cap applies per dataset and broad group.
    """
    successful = frame[
        frame["processing_status"].astype(str) == STATUS_SUCCESS
    ].copy()
    capped = apply_stratified_cap(successful, cap_per_group, group_order)
    return capped.loc[:, list(MANIFEST_COLUMNS)].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Summaries
# ---------------------------------------------------------------------------


def summarize_processed(frame: pd.DataFrame) -> pd.DataFrame:
    """Return row counts by dataset and ``processing_status``."""
    return _group_counts(frame, ["dataset_name", "processing_status"])


def summarize_by_exclusion(frame: pd.DataFrame) -> pd.DataFrame:
    """Return row counts by dataset and exclusion reason (excluded rows only)."""
    excluded = frame[frame["processing_status"].astype(str) == STATUS_EXCLUDED]
    if excluded.empty:
        return pd.DataFrame(
            columns=["dataset_name", "exclusion_reason", "count"]
        )
    return _group_counts(excluded, ["dataset_name", "exclusion_reason"])


def summarize_by_group(frame: pd.DataFrame) -> pd.DataFrame:
    """Return row counts by dataset, group-assignment source, and broad group.

    The broad group column used is ``source_broad_mst_group`` for official
    labels and ``estimated_broad_mst_group`` for estimates, so official and
    estimated groups are never conflated.
    """
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "dataset_name",
                "group_assignment_source",
                "broad_group",
                "count",
            ]
        )

    work = frame.copy()
    work["broad_group"] = [
        read_text(record.get("source_broad_mst_group"))
        or read_text(record.get("estimated_broad_mst_group"))
        or UNASSIGNED_GROUP
        for record in work.to_dict("records")
    ]
    return _group_counts(
        work,
        ["dataset_name", "group_assignment_source", "broad_group"],
    )


def _group_counts(frame: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """Return a size-count frame grouped by ``columns``, or empty when needed."""
    if frame.empty:
        return pd.DataFrame(columns=[*columns, "count"])
    counts = (
        frame.groupby(list(columns), dropna=False)
        .size()
        .reset_index(name="count")
    )
    return counts.sort_values(list(columns), ignore_index=True)
