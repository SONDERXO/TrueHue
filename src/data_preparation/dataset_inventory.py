"""
Dataset inventory helpers for FairFace, SCIN, and MST-E.

What this module does
---------------------
It builds a *metadata-only* table (a pandas DataFrame) describing every image
found below a dataset folder. It never opens, copies, resizes, or edits an
image file: the only filesystem access is listing file names.

Why a dataset inventory
-----------------------
Later stages (training, evaluation, calibration) need an auditable answer to
"which images belong to which dataset, and what is each image allowed to be
used for?". The inventory is that record. Every row carries:

- ``image_id``          stable identifier (dataset name + relative path)
- ``relative_path``     path relative to the dataset root, using ``/``
- ``image_path``        absolute path on this machine
- ``source_mst_label``  the *ground-truth* Monk Skin Tone label, when it is
                        officially documented for that image
- ``intended_use``      ``training`` or ``evaluation_only``
- ``quality_review``    manual mask-quality review state (see
                        ``docs/mask-quality-review.md``)
- ``exclusion_reason``  why a row is unusable, when that is known

Dataset roles (fixed for this thesis)
-------------------------------------
==================  ==================  =========================================
Dataset             Role               Rule
==================  ==================  =========================================
FairFace            training           may be used for training
SCIN                training           may be used for training
MST-E               evaluation only    must never appear in a training,
                                       validation, or test split
==================  ==================  =========================================

``validate_intended_use`` and ``load_inventory_manifest`` enforce the MST-E
rule in code, so a later training script cannot silently pick MST-E up.

MST labels are never guessed
----------------------------
``source_mst_label`` is **only** filled from a documented, human-supplied
source:

1. a folder name in the dataset tree that matches the documented MST-E label
   folder pattern (see :func:`extract_mst_label_from_folder_name`), or
2. an official metadata CSV passed in as a label mapping (see
   :func:`load_label_metadata`), e.g. the MST-E ``mst-e_image_details.csv``.

Nothing in this module inspects image pixels, colour, brightness, or ITA to
produce a label. When no documented source is found, the label is left empty
and ``exclusion_reason`` explains why, so a human can resolve it later.
"""

from __future__ import annotations

import numbers
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Mapping, Sequence

import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Image file extensions treated as source images (case-insensitive).
IMAGE_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png")

FAIRFACE_DATASET_NAME = "FairFace"
SCIN_DATASET_NAME = "SCIN"
MST_E_DATASET_NAME = "MST-E"

#: How a dataset may be used. These are the only two allowed values.
INTENDED_USE_TRAINING = "training"
INTENDED_USE_EVALUATION_ONLY = "evaluation_only"
ALLOWED_INTENDED_USES: tuple[str, ...] = (
    INTENDED_USE_TRAINING,
    INTENDED_USE_EVALUATION_ONLY,
)

#: Default intended use per dataset, so callers cannot accidentally train on
#: MST-E by forgetting to pass ``intended_use``.
DEFAULT_INTENDED_USE: dict[str, str] = {
    FAIRFACE_DATASET_NAME: INTENDED_USE_TRAINING,
    SCIN_DATASET_NAME: INTENDED_USE_TRAINING,
    MST_E_DATASET_NAME: INTENDED_USE_EVALUATION_ONLY,
}

#: Accepted spellings of the MST-E dataset name (compared case-insensitively
#: after removing spaces, dashes, and underscores).
MST_E_DATASET_KEYS: frozenset[str] = frozenset({"mste"})

#: Review state written when no human has looked at the mask yet.
QUALITY_REVIEW_PENDING = "pending"

#: Review state written by scripts when processing fails automatically.
QUALITY_REVIEW_AUTO_FAILED = "auto_failed"

#: Monk Skin Tone (MST-E) ground-truth labels are the 10-point scale 1-10.
MST_LABEL_MIN = 1
MST_LABEL_MAX = 10

#: Folder names that may carry an MST-E label. Documented, allowed forms:
#: "1" ... "10", "01", "MST1", "MST-1", "MST_01", "class3", "label_4",
#: "skin5", "type6". Anything else is rejected (for example "MST-E",
#: "Very Light", "1.5", "0", "11", "unknown").
MST_FOLDER_PATTERN = re.compile(
    r"^(?:mst|class|label|skin|type)?[\s_\-]*(\d{1,2})$",
    re.IGNORECASE,
)

#: Extra official MST-E metadata carried through for later analysis, as
#: ``inventory column -> metadata column``. These are *recorded*, never used to
#: derive a label.
MST_E_DETAIL_COLUMNS: dict[str, str] = {
    "source_pose": "pose",
    "source_lighting": "lighting",
    "source_wearing_mask": "mask",
}

#: Columns of the returned inventory DataFrame, in order.
INVENTORY_COLUMNS: tuple[str, ...] = (
    "dataset_name",
    "image_id",
    "relative_path",
    "image_path",
    "source_mst_label",
    "source_pose",
    "source_lighting",
    "source_wearing_mask",
    "label_source",
    "intended_use",
    "quality_review",
    "exclusion_reason",
)

#: Columns every inventory CSV must contain.
REQUIRED_INVENTORY_COLUMNS: tuple[str, ...] = (
    "dataset_name",
    "image_id",
    "relative_path",
    "image_path",
    "source_mst_label",
    "intended_use",
    "quality_review",
    "exclusion_reason",
)

#: Values written into ``label_source`` to document where a label came from.
LABEL_SOURCE_FOLDER = "folder_name"
LABEL_SOURCE_METADATA = "metadata"
LABEL_SOURCE_NONE = "none"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def dataset_name_key(dataset_name: str) -> str:
    """Return a comparison key for a dataset name.

    ``"MST-E"``, ``"MST_E"``, ``"mst e"``, and ``"MSTE"`` all become
    ``"mste"``, so the MST-E rules apply however the name is written.

    Parameters
    ----------
    dataset_name : str
        Human-readable dataset name.

    Returns
    -------
    str
        Lowercase name containing only letters and digits.

    Raises
    ------
    ValueError
        If ``dataset_name`` is empty or not a string.
    """
    if not isinstance(dataset_name, str) or not dataset_name.strip():
        raise ValueError("dataset_name must be a non-empty string.")
    return re.sub(r"[^a-z0-9]+", "", dataset_name.strip().lower())


def dataset_slug(dataset_name: str) -> str:
    """Return a readable lowercase slug for use inside an image ID.

    ``"MST-E"`` becomes ``"mst_e"`` and ``"FairFace"`` becomes ``"fairface"``:
    non-alphanumeric characters collapse to a single underscore.

    Parameters
    ----------
    dataset_name : str
        Human-readable dataset name.

    Returns
    -------
    str
        Slug safe to embed in an ID (it may still contain ``_``).

    Raises
    ------
    ValueError
        If the name is empty or contains no letters or digits.
    """
    if not isinstance(dataset_name, str) or not dataset_name.strip():
        raise ValueError("dataset_name must be a non-empty string.")
    slug = re.sub(r"[^a-z0-9]+", "_", dataset_name.strip().lower()).strip("_")
    if not slug:
        raise ValueError(
            f"dataset_name {dataset_name!r} contains no letters or digits."
        )
    return slug


def is_mst_e_dataset(dataset_name: str) -> bool:
    """Return True when ``dataset_name`` refers to MST-E."""
    return dataset_name_key(dataset_name) in MST_E_DATASET_KEYS


def validate_intended_use(
    dataset_name: str, intended_use: str | None = None
) -> str:
    """Validate (and default) the intended use of a dataset.

    MST-E must always be ``evaluation_only``. This is a hard rule for the
    thesis, so it is checked in code rather than left to documentation.

    Parameters
    ----------
    dataset_name : str
        Dataset the rows belong to, e.g. ``"FairFace"`` or ``"MST-E"``.
    intended_use : str | None
        Requested use. ``None`` uses the default for the known datasets
        (FairFace/SCIN -> ``training``, MST-E -> ``evaluation_only``).

    Returns
    -------
    str
        The validated intended use.

    Raises
    ------
    ValueError
        If the value is not one of the allowed uses, or if MST-E is requested
        for anything other than ``evaluation_only``.
    """
    if intended_use is None:
        for known_name, known_use in DEFAULT_INTENDED_USE.items():
            if dataset_name_key(known_name) == dataset_name_key(dataset_name):
                intended_use = known_use
                break

    if intended_use not in ALLOWED_INTENDED_USES:
        raise ValueError(
            f"intended_use must be one of {ALLOWED_INTENDED_USES}, got "
            f"{intended_use!r} for dataset {dataset_name!r}."
        )

    if is_mst_e_dataset(dataset_name) and intended_use != INTENDED_USE_EVALUATION_ONLY:
        raise ValueError(
            f"Dataset {dataset_name!r} is MST-E and may only be used as "
            f"{INTENDED_USE_EVALUATION_ONLY!r}, never as {intended_use!r}. "
            "MST-E must not appear in model-training, validation, or test "
            "splits."
        )

    return intended_use


def normalize_relative_path(relative_path: str | Path) -> str:
    """Normalise a dataset-relative path to a portable ``a/b/c.jpg`` string.

    Windows separators are converted to ``/``, a leading ``./`` is dropped, and
    repeated slashes are collapsed, so the same image always produces the same
    string on any operating system.

    Parameters
    ----------
    relative_path : str | Path
        Path relative to the dataset root.

    Returns
    -------
    str
        Normalised path using forward slashes and no trailing slash.

    Raises
    ------
    ValueError
        If the path is empty, absolute (drive letter or leading ``/``), or
        escapes the dataset root with ``..``.
    """
    text = str(relative_path).strip()
    if not text:
        raise ValueError("relative_path must not be empty.")

    unified = text.replace("\\", "/")

    if PureWindowsPath(text).is_absolute() or PurePosixPath(text).is_absolute():
        raise ValueError(
            f"relative_path must be relative to the dataset root, got the "
            f"absolute path {text!r}."
        )

    parts = [part for part in unified.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        raise ValueError(
            f"relative_path must stay inside the dataset root, got {text!r}."
        )
    if not parts:
        raise ValueError(
            f"relative_path {text!r} does not contain a file name."
        )

    return "/".join(parts)


def make_image_id(dataset_name: str, relative_path: str | Path) -> str:
    """Build the stable image ID for one image.

    The ID is ``"<dataset slug>__<relative path>"``, e.g.
    ``"mst_e__subject_3/PXL_20220922_193502239.jpg"``. It is stable because it
    depends only on the dataset name and the path *inside* the dataset: the same
    image keeps the same ID when the project moves to another folder or drive.

    Parameters
    ----------
    dataset_name : str
        Dataset the image belongs to, e.g. ``"MST-E"``.
    relative_path : str | Path
        Path relative to the dataset root.

    Returns
    -------
    str
        Stable image ID. Treat it as a key, not as a file name.

    Raises
    ------
    ValueError
        If the dataset name or the relative path is invalid (see
        :func:`normalize_relative_path`).
    """
    slug = dataset_slug(dataset_name)
    return f"{slug}__{normalize_relative_path(relative_path)}"


# ---------------------------------------------------------------------------
# Image enumeration
# ---------------------------------------------------------------------------


def enumerate_image_files(
    dataset_root: str | Path,
    extensions: Sequence[str] = IMAGE_EXTENSIONS,
) -> list[Path]:
    """Recursively list supported image files below ``dataset_root``.

    Only file names are read: images are never opened, copied, or modified.
    Results are sorted by their path parts so repeated runs produce the same
    order (and therefore the same inventory).

    Parameters
    ----------
    dataset_root : str | Path
        Folder to scan, e.g. ``data/raw/mst-e_data``.
    extensions : Sequence[str]
        Extensions to keep, compared case-insensitively.

    Returns
    -------
    list[Path]
        Sorted list of image paths.

    Raises
    ------
    FileNotFoundError
        If ``dataset_root`` does not exist.
    NotADirectoryError
        If ``dataset_root`` exists but is a file.
    ValueError
        If ``extensions`` is empty.
    """
    root = Path(dataset_root)
    if not root.exists():
        raise FileNotFoundError(
            f"Dataset folder was not found: {root}. Create the folder and "
            "place the dataset images inside it, or pass the correct path."
        )
    if not root.is_dir():
        raise NotADirectoryError(
            f"Dataset path is not a folder: {root}."
        )

    allowed = {str(extension).lower() for extension in extensions}
    if not allowed:
        raise ValueError("extensions must contain at least one extension.")

    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in allowed
    ]
    return sorted(files, key=lambda path: path.parts)


# ---------------------------------------------------------------------------
# MST label validation and extraction
# ---------------------------------------------------------------------------


def validate_mst_label(value: object) -> int:
    """Validate and return an MST-E ground-truth label as an ``int``.

    Accepts integers, zero-padded digit strings (``"03"``), and whole floats
    that arrived from a spreadsheet (``3.0``). Everything else raises a
    ``ValueError`` that names the offending value.

    Parameters
    ----------
    value : object
        Candidate label.

    Returns
    -------
    int
        The label, guaranteed to be within 1-10 inclusive.

    Raises
    ------
    ValueError
        If the value is not an integer in the range 1-10.
    """
    if isinstance(value, bool):
        raise ValueError(
            f"Invalid MST label {value!r}: booleans are not MST labels."
        )

    if isinstance(value, numbers.Integral):
        label = int(value)
    elif isinstance(value, numbers.Real):
        numeric = float(value)
        if not numeric.is_integer():
            raise ValueError(
                f"Invalid MST label {value!r}: MST-E labels are whole numbers "
                f"{MST_LABEL_MIN}-{MST_LABEL_MAX}, not fractional values."
            )
        label = int(numeric)
    elif isinstance(value, str):
        text = value.strip()
        if not re.fullmatch(r"\d{1,2}", text):
            raise ValueError(
                f"Invalid MST label {value!r}: expected a whole number written "
                f"as digits (for example \"3\" or \"03\")."
            )
        label = int(text)
    else:
        raise ValueError(
            f"Invalid MST label {value!r}: expected an integer or a digit "
            f"string between {MST_LABEL_MIN} and {MST_LABEL_MAX}."
        )

    if not MST_LABEL_MIN <= label <= MST_LABEL_MAX:
        raise ValueError(
            f"Invalid MST label {label!r}: MST-E ground-truth labels run from "
            f"{MST_LABEL_MIN} to {MST_LABEL_MAX}."
        )

    return label


def extract_mst_label_from_folder_name(folder_name: str) -> int:
    """Read an MST-E label out of a dataset folder name.

    Documented accepted forms (case-insensitive, optional leading zeros):
    ``"1"``-``"10"``, ``"01"``, ``"MST1"``, ``"MST-1"``, ``"MST_01"``,
    ``"class3"``, ``"label_4"``, ``"skin5"``, ``"type6"``.

    Names that are not a label folder are rejected rather than guessed, so a
    folder called ``"subject_3"`` or ``"MST-E"`` never produces a label.

    Parameters
    ----------
    folder_name : str
        A single folder name (not a full path).

    Returns
    -------
    int
        The MST label within 1-10.

    Raises
    ------
    ValueError
        If the name is not a documented label folder, or the number is outside
        1-10.
    """
    if not isinstance(folder_name, str) or not folder_name.strip():
        raise ValueError("folder_name must be a non-empty string.")

    name = folder_name.strip()
    match = MST_FOLDER_PATTERN.match(name)
    if match is None:
        raise ValueError(
            f"Folder name {name!r} is not a documented MST-E label folder. "
            f"Use a plain number 1-{MST_LABEL_MAX} (optionally zero-padded, "
            "optionally prefixed with MST, class, label, skin, or type) or "
            "supply the label through official metadata instead."
        )

    return validate_mst_label(match.group(1))


def find_mst_label_folder(relative_path: str | Path) -> tuple[str, int] | None:
    """Find the nearest ancestor folder that carries an MST-E label.

    Starting at the folder directly containing the image and walking upwards,
    the first folder that parses as a label folder wins. This supports both
    ``<root>/3/photo.jpg`` and ``<root>/MST-E/03/photo.jpg`` layouts.

    Parameters
    ----------
    relative_path : str | Path
        Dataset-relative path of the image.

    Returns
    -------
    tuple[str, int] | None
        The folder name and its label, or ``None`` when no ancestor folder is a
        label folder.
    """
    parts = normalize_relative_path(relative_path).split("/")[:-1]
    for folder in reversed(parts):
        try:
            label = extract_mst_label_from_folder_name(folder)
        except ValueError:
            continue
        return folder, label
    return None


# ---------------------------------------------------------------------------
# Official metadata (label mapping)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LabelMetadata:
    """Official labels (and optional extra fields) for dataset images.

    Attributes
    ----------
    labels : dict[str, int]
        Lookup key -> MST label. Keys are exactly the values in the metadata
        file, plus the image-ID form of the key column (see
        :func:`load_label_metadata`).
    details : dict[str, dict[str, str]]
        Lookup key -> auxiliary official fields, keyed by *inventory* column
        name (for example ``"source_pose"``).
    source : str
        Human-readable origin of the mapping, recorded in ``label_source``.
    """

    labels: dict[str, int]
    details: dict[str, dict[str, str]]
    source: str


def _read_text(value: object) -> str:
    """Return a stripped string for a metadata cell, or ``""`` when missing."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):  # pragma: no cover - defensive
        pass
    return str(value).strip()


def load_label_metadata(
    csv_path: str | Path,
    key_column: str = "image_ID",
    label_column: str = "MST",
    dataset_name: str = "",
    detail_columns: Mapping[str, str] | None = None,
) -> LabelMetadata:
    """Load MST labels from an official dataset metadata CSV.

    The MST-E release ships ``mst-e_image_details.csv`` with the columns
    ``image_ID, pose, lighting, mask, subject_name, MST``, where ``MST`` is the
    annotator's ground-truth label. Pass that file here and labels are joined
    onto the images by file name.

    Parameters
    ----------
    csv_path : str | Path
        Metadata CSV to read.
    key_column : str
        Column holding the image identifier, matched against the image's
        relative path, then its file name.
    label_column : str
        Column holding the ground-truth MST label.
    dataset_name : str
        Optional dataset name, used to add the ``<slug>__<key>`` image-ID form
        of every key to the mapping.
    detail_columns : Mapping[str, str] | None
        Optional ``{inventory column: metadata column}`` pairs to carry through
        (see :data:`MST_E_DETAIL_COLUMNS`).

    Returns
    -------
    LabelMetadata
        Validated labels plus any extra fields.

    Raises
    ------
    FileNotFoundError
        If the CSV does not exist.
    ValueError
        If a required column is missing, a label is invalid, or the same key
        appears twice with *different* labels.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Metadata CSV was not found: {path}. Download the official "
            "metadata file and pass its path."
        )

    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    for column in (key_column, label_column):
        if column not in frame.columns:
            raise ValueError(
                f"Metadata CSV {path.name} has no column {column!r}. Columns "
                f"found: {list(frame.columns)}."
            )

    details_by_column = (
        dict(detail_columns) if detail_columns is not None else {}
    )
    for metadata_column in details_by_column.values():
        if metadata_column not in frame.columns:
            raise ValueError(
                f"Metadata CSV {path.name} has no column {metadata_column!r} "
                f"requested for {details_by_column}. Columns found: "
                f"{list(frame.columns)}."
            )

    slug = dataset_slug(dataset_name) if dataset_name else ""
    labels: dict[str, int] = {}
    details: dict[str, dict[str, str]] = {}

    for record in frame.to_dict(orient="records"):
        key = _read_text(record.get(key_column))
        if not key:
            continue

        label = validate_mst_label(record.get(label_column))
        if key in labels and labels[key] != label:
            raise ValueError(
                f"Conflicting MST labels in {path.name} for {key!r}: "
                f"{labels[key]} and {label}. Remove the duplicate rows before "
                "building the inventory."
            )

        extra: dict[str, str] = {}
        for inventory_column, metadata_column in details_by_column.items():
            text = _read_text(record.get(metadata_column))
            if text and inventory_column not in extra:
                extra[inventory_column] = text

        labels[key] = label
        details.setdefault(key, {}).update(extra)
        if slug:
            labels[f"{slug}__{key}"] = label
            details.setdefault(f"{slug}__{key}", {}).update(extra)

    return LabelMetadata(
        labels=labels,
        details=details,
        source=f"{LABEL_SOURCE_METADATA}:{path.name}",
    )


def make_label_lookup_keys(
    dataset_name: str, relative_path: str | Path
) -> tuple[str, ...]:
    """Return the keys a metadata mapping may use for one image.

    Order matters: the exact relative path is tried first, then the bare file
    name (how the official MST-E CSV identifies images), then the image ID.

    Parameters
    ----------
    dataset_name : str
        Dataset the image belongs to.
    relative_path : str | Path
        Dataset-relative path of the image.

    Returns
    -------
    tuple[str, ...]
        Candidate lookup keys, without duplicates.
    """
    normalized = normalize_relative_path(relative_path)
    candidates = (
        normalized,
        PurePosixPath(normalized).name,
        make_image_id(dataset_name, normalized),
    )
    seen: list[str] = []
    for candidate in candidates:
        if candidate not in seen:
            seen.append(candidate)
    return tuple(seen)


def resolve_source_mst_label(
    dataset_name: str,
    relative_path: str | Path,
    metadata: LabelMetadata | None = None,
) -> tuple[int | None, str, str, dict[str, str]]:
    """Look up the ground-truth label for one image from documented sources.

    Official metadata wins over folder names. If neither source has the image,
    the label is left empty and a reason is returned - the label is never
    guessed from the image itself.

    Parameters
    ----------
    dataset_name : str
        Dataset the image belongs to.
    relative_path : str | Path
        Dataset-relative path of the image.
    metadata : LabelMetadata | None
        Optional official metadata mapping.

    Returns
    -------
    tuple[int | None, str, str, dict[str, str]]
        ``(label, label_source, reason, extra_fields)`` where ``label`` is
        ``None`` when unknown, ``label_source`` documents the origin, ``reason``
        is empty on success, and ``extra_fields`` holds any carried-through
        official metadata.
    """
    extra: dict[str, str] = {}

    if metadata is not None:
        for key in make_label_lookup_keys(dataset_name, relative_path):
            if key in metadata.labels:
                extra.update(metadata.details.get(key, {}))
                return metadata.labels[key], metadata.source, "", extra

    found = find_mst_label_folder(relative_path)
    if found is not None:
        folder, label = found
        return label, f"{LABEL_SOURCE_FOLDER}:{folder}", "", extra

    return (
        None,
        LABEL_SOURCE_NONE,
        "no documented MST label: no label folder and no official metadata "
        "entry for this image",
        extra,
    )


# ---------------------------------------------------------------------------
# Inventory construction and loading
# ---------------------------------------------------------------------------


def build_inventory(
    dataset_name: str,
    dataset_root: str | Path,
    intended_use: str | None = None,
    metadata: LabelMetadata | None = None,
    extensions: Sequence[str] = IMAGE_EXTENSIONS,
) -> pd.DataFrame:
    """Build the metadata inventory for one dataset.

    Only file names are read. Every image below ``dataset_root`` becomes one
    row; nothing is copied, resized, or edited.

    Parameters
    ----------
    dataset_name : str
        Dataset name written into the ``dataset_name`` column, e.g. ``"SCIN"``.
    dataset_root : str | Path
        Folder to scan recursively for images.
    intended_use : str | None
        ``training`` or ``evaluation_only``. ``None`` uses the default for the
        known datasets and fails for unknown ones.
    metadata : LabelMetadata | None
        Optional official label mapping (see :func:`load_label_metadata`).
        FairFace and SCIN normally do not need one: their labels live in
        official metadata that is joined in a later stage, so their
        ``source_mst_label`` stays empty here.
    extensions : Sequence[str]
        Extensions to treat as images.

    Returns
    -------
    pd.DataFrame
        Table with the columns in :data:`INVENTORY_COLUMNS`. ``source_mst_label``
        uses pandas' nullable ``Int64`` type, so "no label" is a real missing
        value rather than a magic number. The frame is empty (but correctly
        shaped) when the dataset folder holds no supported images.

    Raises
    ------
    FileNotFoundError
        If the dataset folder does not exist.
    NotADirectoryError
        If the dataset path is a file.
    ValueError
        If the dataset name or intended use is invalid (for example MST-E with
        ``intended_use="training"``).
    """
    use = validate_intended_use(dataset_name, intended_use)
    root = Path(dataset_root)

    image_files = enumerate_image_files(root, extensions)

    rows: list[dict[str, object]] = []
    for path in image_files:
        relative_path = normalize_relative_path(path.relative_to(root))
        label, label_source, reason, extra = resolve_source_mst_label(
            dataset_name, relative_path, metadata
        )
        rows.append(
            {
                "dataset_name": dataset_name,
                "image_id": make_image_id(dataset_name, relative_path),
                "relative_path": relative_path,
                "image_path": path.resolve().as_posix(),
                "source_mst_label": label,
                "source_pose": extra.get("source_pose", ""),
                "source_lighting": extra.get("source_lighting", ""),
                "source_wearing_mask": extra.get("source_wearing_mask", ""),
                "label_source": label_source,
                "intended_use": use,
                "quality_review": QUALITY_REVIEW_PENDING,
                "exclusion_reason": reason,
            }
        )

    frame = pd.DataFrame(rows, columns=list(INVENTORY_COLUMNS))
    frame["source_mst_label"] = frame["source_mst_label"].astype("Int64")
    return frame


def load_inventory_manifest(csv_path: str | Path) -> pd.DataFrame:
    """Read an inventory CSV written by a build script.

    Parameters
    ----------
    csv_path : str | Path
        Inventory CSV such as ``data/manifests/mst_e_inventory.csv``.

    Returns
    -------
    pd.DataFrame
        The manifest with ``source_mst_label`` read as nullable ``Int64`` and
        string columns kept as strings.

    Raises
    ------
    FileNotFoundError
        If the CSV does not exist.
    ValueError
        If a required column is missing, or if an MST-E row is marked for
        training/validation/test use.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Inventory manifest was not found: {path}. Build it first with "
            "scripts/04_build_dataset_inventory.py."
        )

    frame = pd.read_csv(path, dtype={"source_mst_label": "Int64"})

    missing = [
        column for column in REQUIRED_INVENTORY_COLUMNS if column not in frame.columns
    ]
    if missing:
        raise ValueError(
            f"Inventory manifest {path.name} is missing required column(s): "
            f"{missing}. Expected at least {list(REQUIRED_INVENTORY_COLUMNS)}."
        )

    mst_rows = frame[frame["dataset_name"].map(is_mst_e_dataset)]
    if not mst_rows.empty:
        bad = sorted(
            set(mst_rows["intended_use"].dropna().astype(str))
            - {INTENDED_USE_EVALUATION_ONLY}
        )
        if bad:
            raise ValueError(
                f"Inventory manifest {path.name} marks MST-E rows with "
                f"intended_use {bad}. MST-E must be "
                f"{INTENDED_USE_EVALUATION_ONLY!r} only."
            )

    return frame


def summarize_inventory(frame: pd.DataFrame) -> dict[str, object]:
    """Summarise an inventory frame for console output.

    Parameters
    ----------
    frame : pd.DataFrame
        Frame returned by :func:`build_inventory`.

    Returns
    -------
    dict
        Counts of images, labelled images, and images flagged with an
        ``exclusion_reason``, plus the dataset name and intended use.
    """
    total = int(len(frame))
    if total == 0:
        return {
            "dataset_name": "",
            "intended_use": "",
            "images": 0,
            "labelled": 0,
            "unlabelled": 0,
            "flagged": 0,
        }

    labelled = int(frame["source_mst_label"].notna().sum())
    flagged = int((frame["exclusion_reason"].fillna("") != "").sum())
    return {
        "dataset_name": str(frame["dataset_name"].iloc[0]),
        "intended_use": str(frame["intended_use"].iloc[0]),
        "images": total,
        "labelled": labelled,
        "unlabelled": total - labelled,
        "flagged": flagged,
    }
