"""Tests for src.data_preparation.dataset_inventory.

These tests are pure filesystem/metadata tests: they create empty placeholder
files in pytest's ``tmp_path`` folder and never need a real dataset, an ONNX
model, MediaPipe, or any network access.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.data_preparation.dataset_inventory import (
    INTENDED_USE_EVALUATION_ONLY,
    INTENDED_USE_TRAINING,
    LABEL_SOURCE_FOLDER,
    LABEL_SOURCE_METADATA,
    LABEL_SOURCE_NONE,
    MST_E_DATASET_NAME,
    QUALITY_REVIEW_PENDING,
    REQUIRED_INVENTORY_COLUMNS,
    build_inventory,
    enumerate_image_files,
    extract_mst_label_from_folder_name,
    find_mst_label_folder,
    is_mst_e_dataset,
    load_inventory_manifest,
    load_label_metadata,
    make_image_id,
    normalize_relative_path,
    resolve_source_mst_label,
    summarize_inventory,
    validate_intended_use,
    validate_mst_label,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _touch(path) -> None:
    """Create an empty placeholder file (with its parent folders)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


@pytest.fixture()
def mst_e_tree(tmp_path):
    """Fake MST-E tree: label folders holding a few placeholder images."""
    root = tmp_path / "mst-e_data"
    _touch(root / "1" / "face_a.jpg")
    _touch(root / "1" / "face_b.JPEG")
    _touch(root / "10" / "face_c.png")
    _touch(root / "3" / "nested" / "face_d.png")
    # Unsupported files and non-image files must be ignored.
    _touch(root / "1" / "notes.txt")
    _touch(root / "1" / "clip.mp4")
    _touch(root / "metadata.csv")
    return root


@pytest.fixture()
def subject_tree(tmp_path):
    """Fake MST-E tree organised by subject, with no label folders."""
    root = tmp_path / "mst-e_data"
    _touch(root / "subject_0" / "a.jpg")
    _touch(root / "subject_1" / "b.jpg")
    return root


# ---------------------------------------------------------------------------
# Recursive enumeration
# ---------------------------------------------------------------------------


def test_enumerate_image_files_is_recursive(mst_e_tree):
    """Images in nested sub-folders must be found."""
    found = enumerate_image_files(mst_e_tree)

    names = sorted(path.name for path in found)

    assert names == ["face_a.jpg", "face_b.JPEG", "face_c.png", "face_d.png"]


def test_enumerate_image_files_ignores_other_extensions(mst_e_tree):
    """Only .jpg, .jpeg, and .png (any case) count as images."""
    found = enumerate_image_files(mst_e_tree)
    suffixes = {path.suffix.lower() for path in found}

    assert suffixes <= {".jpg", ".jpeg", ".png"}
    assert not any(path.name.endswith(".txt") for path in found)
    assert not any(path.name.endswith(".mp4") for path in found)
    assert not any(path.name.endswith(".csv") for path in found)


def test_enumerate_image_files_is_deterministic(mst_e_tree):
    """Two calls must return the same order so manifests are reproducible."""
    first = [path.as_posix() for path in enumerate_image_files(mst_e_tree)]
    second = [path.as_posix() for path in enumerate_image_files(mst_e_tree)]

    assert first == second


def test_enumerate_image_files_empty_folder(tmp_path):
    """An empty dataset folder yields an empty list, not an error."""
    empty_root = tmp_path / "empty"
    empty_root.mkdir()

    assert enumerate_image_files(empty_root) == []


def test_enumerate_image_files_missing_folder_raises(tmp_path):
    """A missing dataset folder must raise a clear FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        enumerate_image_files(tmp_path / "does_not_exist")


# ---------------------------------------------------------------------------
# Stable image IDs
# ---------------------------------------------------------------------------


def test_make_image_id_is_stable():
    """The same inputs must always produce the same ID."""
    first = make_image_id("MST-E", "subject_3/PXL_20220922_193502239.jpg")
    second = make_image_id("MST-E", "subject_3/PXL_20220922_193502239.jpg")

    assert first == second
    assert first == "mst_e__subject_3/PXL_20220922_193502239.jpg"


def test_make_image_id_normalises_separators():
    """Windows and POSIX separators must produce the same ID."""
    windows_style = make_image_id("MST-E", "3\\face.jpg")
    posix_style = make_image_id("MST-E", "./3/face.jpg")

    assert windows_style == posix_style == "mst_e__3/face.jpg"


def test_make_image_id_includes_dataset_name():
    """The same file in two datasets must get different IDs."""
    fairface_id = make_image_id("FairFace", "0001.jpg")
    mst_e_id = make_image_id("MST-E", "0001.jpg")

    assert fairface_id != mst_e_id
    assert fairface_id.startswith("fairface__")
    assert mst_e_id.startswith("mst_e__")


def test_make_image_id_does_not_depend_on_absolute_location(mst_e_tree, tmp_path):
    """Moving the dataset must not change the IDs."""
    original = build_inventory("MST-E", mst_e_tree, INTENDED_USE_EVALUATION_ONLY)

    moved_root = tmp_path / "moved_elsewhere"
    moved_root.mkdir()
    for source in enumerate_image_files(mst_e_tree):
        _touch(moved_root / source.relative_to(mst_e_tree))
    moved = build_inventory("MST-E", moved_root, INTENDED_USE_EVALUATION_ONLY)

    assert original["image_id"].tolist() == moved["image_id"].tolist()


def test_normalize_relative_path_rejects_absolute_and_escaping_paths():
    """Absolute paths and '..' escapes must be rejected."""
    with pytest.raises(ValueError):
        normalize_relative_path("/abs/3/face.jpg")
    with pytest.raises(ValueError):
        normalize_relative_path("C:/data/3/face.jpg")
    with pytest.raises(ValueError):
        normalize_relative_path("../outside/face.jpg")
    with pytest.raises(ValueError):
        normalize_relative_path("")


# ---------------------------------------------------------------------------
# MST label validation and extraction
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, 1),
        (10, 10),
        ("3", 3),
        ("03", 3),
        (" 7 ", 7),
        (4.0, 4),
    ],
)
def test_validate_mst_label_accepts_valid_values(value, expected):
    """Documented label forms must be accepted and normalised to int."""
    label = validate_mst_label(value)

    assert label == expected
    assert isinstance(label, int)


@pytest.mark.parametrize(
    "value",
    [0, 11, -1, 2.5, "0", "11", "1.5", "abc", "Very Light", "", None, True],
)
def test_validate_mst_label_rejects_invalid_values(value):
    """Anything outside integer 1-10 must raise ValueError."""
    with pytest.raises(ValueError):
        validate_mst_label(value)


@pytest.mark.parametrize(
    ("folder_name", "expected"),
    [
        ("1", 1),
        ("10", 10),
        ("01", 1),
        ("MST1", 1),
        ("mst-1", 1),
        ("MST_01", 1),
        ("class3", 3),
        ("label_4", 4),
        ("skin5", 5),
        ("type6", 6),
    ],
)
def test_extract_mst_label_from_folder_name_valid(folder_name, expected):
    """All documented label-folder spellings must parse."""
    assert extract_mst_label_from_folder_name(folder_name) == expected


@pytest.mark.parametrize(
    "folder_name",
    ["subject_3", "MST-E", "mst_e_data", "Very Light", "3.5", "0", "11", "", "abc"],
)
def test_extract_mst_label_from_folder_name_invalid(folder_name):
    """Non-label folder names must never produce a guessed label."""
    with pytest.raises(ValueError):
        extract_mst_label_from_folder_name(folder_name)


def test_find_mst_label_folder_walks_upwards():
    """The nearest label folder is used, even when nested deeper."""
    assert find_mst_label_folder("3/photo.jpg") == ("3", 3)
    assert find_mst_label_folder("MST-E/03/photo.jpg") == ("03", 3)
    assert find_mst_label_folder("subject_4/portrait/photo.jpg") is None
    assert find_mst_label_folder("photo.jpg") is None


# ---------------------------------------------------------------------------
# Metadata mapping
# ---------------------------------------------------------------------------


def test_load_label_metadata_matches_official_mst_e_columns(tmp_path):
    """The official MST-E metadata layout must load and validate."""
    csv_path = tmp_path / "mst-e_image_details.csv"
    pd.DataFrame(
        [
            {
                "image_ID": "a.jpg",
                "pose": "frontal",
                "lighting": "well_lit",
                "mask": "0",
                "subject_name": "subject_1",
                "MST": "1",
            },
            {
                "image_ID": "b.jpg",
                "pose": "side",
                "lighting": "poorly_lit",
                "mask": "0",
                "subject_name": "subject_9",
                "MST": "9",
            },
        ]
    ).to_csv(csv_path, index=False)

    metadata = load_label_metadata(
        csv_path,
        key_column="image_ID",
        label_column="MST",
        dataset_name=MST_E_DATASET_NAME,
        detail_columns={"source_pose": "pose", "source_lighting": "lighting"},
    )

    assert metadata.labels["a.jpg"] == 1
    assert metadata.labels["b.jpg"] == 9
    assert metadata.labels["mst_e__a.jpg"] == 1
    assert metadata.details["a.jpg"]["source_pose"] == "frontal"
    assert LABEL_SOURCE_METADATA in metadata.source


def test_load_label_metadata_rejects_missing_file(tmp_path):
    """A missing metadata CSV must raise a clear FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_label_metadata(tmp_path / "nope.csv")


def test_load_label_metadata_rejects_missing_column(tmp_path):
    """A CSV without the label column must raise a clear ValueError."""
    csv_path = tmp_path / "bad.csv"
    pd.DataFrame([{"image_ID": "a.jpg", "tone": "3"}]).to_csv(
        csv_path, index=False
    )

    with pytest.raises(ValueError, match="MST"):
        load_label_metadata(csv_path)


def test_load_label_metadata_rejects_out_of_range_label(tmp_path):
    """Labels outside 1-10 must be rejected, not clipped."""
    csv_path = tmp_path / "bad_label.csv"
    pd.DataFrame([{"image_ID": "a.jpg", "MST": "11"}]).to_csv(
        csv_path, index=False
    )

    with pytest.raises(ValueError):
        load_label_metadata(csv_path)


def test_load_label_metadata_rejects_conflicting_duplicate_keys(tmp_path):
    """The same key with two different labels is a data error."""
    csv_path = tmp_path / "conflict.csv"
    pd.DataFrame(
        [{"image_ID": "a.jpg", "MST": "3"}, {"image_ID": "a.jpg", "MST": "4"}]
    ).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Conflicting MST labels"):
        load_label_metadata(csv_path)


def test_resolve_source_mst_label_prefers_metadata(subject_tree, tmp_path):
    """Official metadata wins over folder names."""
    metadata = load_label_metadata(
        _write_metadata(tmp_path, {"subject_0/a.jpg": 2}),
        key_column="relative_path",
        label_column="MST",
        dataset_name=MST_E_DATASET_NAME,
    )

    label, label_source, reason, _ = resolve_source_mst_label(
        MST_E_DATASET_NAME, "subject_0/a.jpg", metadata
    )

    assert label == 2
    assert LABEL_SOURCE_METADATA in label_source
    assert reason == ""


def test_resolve_source_mst_label_falls_back_to_folder(mst_e_tree):
    """A label folder is used when no metadata is supplied."""
    label, label_source, reason, _ = resolve_source_mst_label(
        MST_E_DATASET_NAME, "3/nested/face_d.png"
    )

    assert label == 3
    assert label_source.startswith(LABEL_SOURCE_FOLDER)
    assert reason == ""


def test_resolve_source_mst_label_unknown_leaves_label_empty(subject_tree):
    """Without a documented source the label stays empty with a reason."""
    label, label_source, reason, _ = resolve_source_mst_label(
        MST_E_DATASET_NAME, "subject_0/a.jpg"
    )

    assert label is None
    assert label_source == LABEL_SOURCE_NONE
    assert "no documented MST label" in reason


def _write_metadata(tmp_path, entries: dict[str, int]) -> "pd.io.common.Path":
    """Write a tiny metadata CSV mapping relative paths to MST labels."""
    csv_path = tmp_path / "labels.csv"
    pd.DataFrame(
        [
            {"relative_path": path, "MST": label}
            for path, label in entries.items()
        ]
    ).to_csv(csv_path, index=False)
    return csv_path


# ---------------------------------------------------------------------------
# Intended use rules
# ---------------------------------------------------------------------------


def test_validate_intended_use_defaults_per_dataset():
    """FairFace/SCIN default to training, MST-E to evaluation_only."""
    assert validate_intended_use("FairFace") == INTENDED_USE_TRAINING
    assert validate_intended_use("SCIN") == INTENDED_USE_TRAINING
    assert validate_intended_use("MST-E") == INTENDED_USE_EVALUATION_ONLY
    assert validate_intended_use("mst_e") == INTENDED_USE_EVALUATION_ONLY


def test_validate_intended_use_blocks_training_on_mst_e():
    """MST-E may never be marked for training."""
    with pytest.raises(ValueError, match="MST-E"):
        validate_intended_use("MST-E", INTENDED_USE_TRAINING)


def test_validate_intended_use_rejects_unknown_value():
    """Only the two documented values are accepted."""
    with pytest.raises(ValueError):
        validate_intended_use("FairFace", "validation")


def test_is_mst_e_dataset_matches_written_names():
    """MST-E detection must work for every spelling used in the project."""
    assert is_mst_e_dataset("MST-E")
    assert is_mst_e_dataset("MST_E")
    assert is_mst_e_dataset("mst e")
    assert not is_mst_e_dataset("FairFace")
    assert not is_mst_e_dataset("SCIN")


# ---------------------------------------------------------------------------
# Inventory construction
# ---------------------------------------------------------------------------


def test_build_inventory_columns_and_rows(mst_e_tree):
    """Every image becomes a row with all required columns."""
    frame = build_inventory(
        MST_E_DATASET_NAME, mst_e_tree, INTENDED_USE_EVALUATION_ONLY
    )

    assert len(frame) == 4
    for column in REQUIRED_INVENTORY_COLUMNS:
        assert column in frame.columns
    assert list(frame["intended_use"].unique()) == [INTENDED_USE_EVALUATION_ONLY]
    assert list(frame["quality_review"].unique()) == [QUALITY_REVIEW_PENDING]
    assert frame["image_id"].is_unique


def test_build_inventory_labels_from_folders(mst_e_tree):
    """MST labels come from the label folders, never from image content."""
    frame = build_inventory(
        MST_E_DATASET_NAME, mst_e_tree, INTENDED_USE_EVALUATION_ONLY
    )
    labels = dict(zip(frame["relative_path"], frame["source_mst_label"]))

    assert labels["1/face_a.jpg"] == 1
    assert labels["1/face_b.JPEG"] == 1
    assert labels["10/face_c.png"] == 10
    assert labels["3/nested/face_d.png"] == 3


def test_build_inventory_leaves_unlabelled_rows_empty(subject_tree):
    """Rows without a documented label keep an empty label plus a reason."""
    frame = build_inventory(
        MST_E_DATASET_NAME, subject_tree, INTENDED_USE_EVALUATION_ONLY
    )

    assert len(frame) == 2
    assert frame["source_mst_label"].isna().all()
    assert (frame["exclusion_reason"] != "").all()
    assert (frame["quality_review"] == QUALITY_REVIEW_PENDING).all()


def test_build_inventory_leaves_training_labels_empty(tmp_path):
    """FairFace and SCIN labels stay empty until official metadata is joined."""
    root = tmp_path / "fairface"
    _touch(root / "train" / "0001.jpg")

    frame = build_inventory("FairFace", root, INTENDED_USE_TRAINING)

    assert len(frame) == 1
    assert pd.isna(frame["source_mst_label"].iloc[0])
    assert frame["intended_use"].iloc[0] == INTENDED_USE_TRAINING


def test_build_inventory_rejects_training_for_mst_e(mst_e_tree):
    """Building an MST-E training inventory must fail loudly."""
    with pytest.raises(ValueError, match="MST-E"):
        build_inventory(MST_E_DATASET_NAME, mst_e_tree, INTENDED_USE_TRAINING)


def test_build_inventory_missing_root_raises(tmp_path):
    """A missing dataset folder raises instead of writing an empty manifest."""
    with pytest.raises(FileNotFoundError):
        build_inventory("SCIN", tmp_path / "nope", INTENDED_USE_TRAINING)


def test_build_inventory_empty_folder_shape(tmp_path):
    """An empty dataset still returns a correctly shaped, empty frame."""
    root = tmp_path / "scin"
    root.mkdir()

    frame = build_inventory("SCIN", root, INTENDED_USE_TRAINING)

    assert frame.empty
    assert list(frame.columns) == list(
        build_inventory("SCIN", root, INTENDED_USE_TRAINING).columns
    )
    for column in REQUIRED_INVENTORY_COLUMNS:
        assert column in frame.columns


def test_build_inventory_with_metadata_joins_labels(tmp_path):
    """Metadata labels are carried through, with the extra official fields."""
    root = tmp_path / "mst-e_data"
    _touch(root / "subject_0" / "a.jpg")
    _touch(root / "subject_0" / "b.jpg")
    csv_path = tmp_path / "details.csv"
    pd.DataFrame(
        [
            {
                "relative_path": "subject_0/a.jpg",
                "MST": 2,
                "pose": "frontal",
                "lighting": "well_lit",
                "mask": 0,
            },
            {
                "relative_path": "subject_0/b.jpg",
                "MST": 2,
                "pose": "side",
                "lighting": "poorly_lit",
                "mask": 1,
            },
        ]
    ).to_csv(csv_path, index=False)

    metadata = load_label_metadata(
        csv_path,
        key_column="relative_path",
        label_column="MST",
        dataset_name=MST_E_DATASET_NAME,
        detail_columns={
            "source_pose": "pose",
            "source_lighting": "lighting",
            "source_wearing_mask": "mask",
        },
    )
    frame = build_inventory(
        MST_E_DATASET_NAME,
        root,
        INTENDED_USE_EVALUATION_ONLY,
        metadata=metadata,
    )

    assert frame["source_mst_label"].tolist() == [2, 2]
    assert frame["source_pose"].tolist() == ["frontal", "side"]
    assert frame["exclusion_reason"].eq("").all()


def test_summarize_inventory_counts(mst_e_tree):
    """The console summary counts labelled and flagged rows."""
    frame = build_inventory(
        MST_E_DATASET_NAME, mst_e_tree, INTENDED_USE_EVALUATION_ONLY
    )
    summary = summarize_inventory(frame)

    assert summary["images"] == 4
    assert summary["labelled"] == 4
    assert summary["unlabelled"] == 0
    assert summary["intended_use"] == INTENDED_USE_EVALUATION_ONLY


# ---------------------------------------------------------------------------
# Manifest round-trip
# ---------------------------------------------------------------------------


def test_load_inventory_manifest_round_trip(mst_e_tree, tmp_path):
    """A written inventory CSV must read back with the same values."""
    frame = build_inventory(
        MST_E_DATASET_NAME, mst_e_tree, INTENDED_USE_EVALUATION_ONLY
    )
    csv_path = tmp_path / "mst_e_inventory.csv"
    frame.to_csv(csv_path, index=False)

    loaded = load_inventory_manifest(csv_path)

    assert len(loaded) == len(frame)
    assert loaded["image_id"].tolist() == frame["image_id"].tolist()
    assert loaded["source_mst_label"].tolist() == [1, 1, 10, 3]
    assert loaded["source_mst_label"].dtype.name == "Int64"


def test_load_inventory_manifest_missing_file_raises(tmp_path):
    """A missing manifest points the user at script 04."""
    with pytest.raises(FileNotFoundError, match="04_build_dataset_inventory"):
        load_inventory_manifest(tmp_path / "nope.csv")


def test_load_inventory_manifest_rejects_mst_e_training_rows(tmp_path):
    """A manifest that marks MST-E for training must be refused."""
    csv_path = tmp_path / "bad_inventory.csv"
    pd.DataFrame(
        [
            {
                "dataset_name": "MST-E",
                "image_id": "mst_e__1/a.jpg",
                "relative_path": "1/a.jpg",
                "image_path": "/tmp/1/a.jpg",
                "source_mst_label": 1,
                "intended_use": "training",
                "quality_review": QUALITY_REVIEW_PENDING,
                "exclusion_reason": "",
            }
        ]
    ).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="MST-E"):
        load_inventory_manifest(csv_path)


def test_load_inventory_manifest_rejects_missing_columns(tmp_path):
    """A manifest without the required columns is refused."""
    csv_path = tmp_path / "incomplete.csv"
    pd.DataFrame([{"dataset_name": "MST-E", "image_id": "x"}]).to_csv(
        csv_path, index=False
    )

    with pytest.raises(ValueError, match="missing required column"):
        load_inventory_manifest(csv_path)
