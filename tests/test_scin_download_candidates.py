"""Tests for scripts/11c_download_scin_candidates.py.

Every gcloud invocation is mocked: these tests never call gcloud and never make
a network request.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
for _path in (str(PROJECT_ROOT), str(SCRIPTS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Script modules start with a digit, so import them through importlib.
download = importlib.import_module("11c_download_scin_candidates")


# ---------------------------------------------------------------------------
# Fakes and helpers
# ---------------------------------------------------------------------------


def png_bytes(width: int = 4, height: int = 4) -> bytes:
    """Return valid PNG bytes so OpenCV validation succeeds."""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:, :, 1] = 255
    ok, buffer = cv2.imencode(".png", image)
    assert ok
    return buffer.tobytes()


def runner_ok(data: bytes):
    """Fake gcloud runner: writes ``data`` to the destination and succeeds."""

    def _run(gs_uri: str, local_path, timeout: float | None = None):
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
        return download.CommandResult(0, "copied", "")

    return _run


def runner_fail(message: str = "CommandException: object not found"):
    """Fake gcloud runner: returns a non-zero exit code."""

    def _run(gs_uri: str, local_path, timeout: float | None = None):
        return download.CommandResult(1, "", message)

    return _run


def candidate_row(**overrides) -> dict:
    """Build a synthetic candidate row."""
    row = {
        "image_id": "scin__-123__1",
        "case_id": "-123",
        "image_path": "dataset/images/-999.png",
        "source_mst_label": 2,
        "source_broad_mst_group": "light",
    }
    row.update(overrides)
    return row


# ---------------------------------------------------------------------------
# Object-path normalization
# ---------------------------------------------------------------------------


def test_normalize_object_path_preserves_existing_prefix():
    value = "dataset/images/4716341186591937478.png"
    assert download.normalize_object_path(value) == value


def test_normalize_object_path_from_filename():
    assert (
        download.normalize_object_path("4716341186591937478.png")
        == "dataset/images/4716341186591937478.png"
    )


def test_normalize_object_path_from_numeric_id_adds_extension():
    assert (
        download.normalize_object_path("4716341186591937478")
        == "dataset/images/4716341186591937478.png"
    )


def test_normalize_object_path_from_nested_filename():
    assert (
        download.normalize_object_path("some/other/dir/-999.png")
        == "dataset/images/-999.png"
    )


def test_normalize_object_path_backslashes():
    assert (
        download.normalize_object_path("dataset\\images\\a.png")
        == "dataset/images/a.png"
    )


def test_normalize_object_path_blank():
    assert download.normalize_object_path("") == ""
    assert download.normalize_object_path(None) == ""


# ---------------------------------------------------------------------------
# gs:// URI and local filename helpers
# ---------------------------------------------------------------------------


def test_build_gs_uri():
    uri = download.build_gs_uri(
        "dx-scin-public-data", "dataset/images/4716341186591937478.png"
    )
    assert uri == (
        "gs://dx-scin-public-data/dataset/images/4716341186591937478.png"
    )


def test_build_gs_uri_strips_slashes():
    uri = download.build_gs_uri(
        "/dx-scin-public-data/", "/dataset/images/a.png"
    )
    assert uri == "gs://dx-scin-public-data/dataset/images/a.png"


def test_build_gs_uri_empty_bucket_raises():
    with pytest.raises(ValueError):
        download.build_gs_uri("", "dataset/images/a.png")


def test_safe_local_filename_uses_image_id_and_suffix():
    name = download.safe_local_filename(
        "scin__-123__1", "dataset/images/4716341186591937478.png"
    )
    assert name == "scin__-123__1.png"


def test_safe_local_filename_sanitizes_and_defaults_suffix():
    name = download.safe_local_filename("weird id/with:chars", "no_extension")
    assert name == "weird_id_with_chars.png"


def test_destination_path_joins_output_dir(tmp_path):
    path = download.destination_path(
        tmp_path, "scin__1__1", "dataset/images/a.png"
    )
    assert path == tmp_path / "scin__1__1.png"


# ---------------------------------------------------------------------------
# gcloud command construction
# ---------------------------------------------------------------------------


def test_build_gcloud_command_plain_executable():
    command = download.build_gcloud_command(
        "gcloud",
        "gs://dx-scin-public-data/dataset/images/a.png",
        Path("out/a.png"),
    )
    assert command[:3] == ["gcloud", "storage", "cp"]
    assert command[3] == "gs://dx-scin-public-data/dataset/images/a.png"
    assert "--recursive" not in command


def test_build_gcloud_command_wraps_cmd_on_windows(monkeypatch):
    monkeypatch.setattr(download.os, "name", "nt")
    command = download.build_gcloud_command(
        r"C:\SDK\bin\gcloud.cmd",
        "gs://dx-scin-public-data/dataset/images/a.png",
        Path("out/a.png"),
    )
    assert command[:3] == ["cmd", "/c", r"C:\SDK\bin\gcloud.cmd"]
    assert command[3:5] == ["storage", "cp"]
    assert "--recursive" not in command


def test_find_gcloud_executable_prefers_path(monkeypatch):
    monkeypatch.setattr(download.shutil, "which", lambda name: r"C:\x\gcloud.cmd")
    assert download.find_gcloud_executable() == r"C:\x\gcloud.cmd"


def test_find_gcloud_executable_falls_back_to_common_locations(monkeypatch, tmp_path):
    sdk = tmp_path / "Google" / "Cloud SDK" / "google-cloud-sdk" / "bin"
    sdk.mkdir(parents=True)
    exe = sdk / "gcloud.cmd"
    exe.write_text("@echo off", encoding="utf-8")

    monkeypatch.setattr(download.shutil, "which", lambda name: None)
    monkeypatch.setattr(
        download.os,
        "environ",
        {"LOCALAPPDATA": str(tmp_path)},
    )
    assert download.find_gcloud_executable() == str(exe)


def test_find_gcloud_executable_returns_none(monkeypatch):
    monkeypatch.setattr(download.shutil, "which", lambda name: None)
    monkeypatch.setattr(download.os, "environ", {})
    assert download.find_gcloud_executable() is None


def test_run_gcloud_cp_builds_correct_command_without_recursive(monkeypatch):
    captured: dict = {}

    class Completed:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return Completed()

    monkeypatch.setattr(download.subprocess, "run", fake_run)

    result = download.run_gcloud_cp(
        "gs://dx-scin-public-data/dataset/images/a.png",
        Path("out/a.png"),
        gcloud_executable="gcloud",
    )

    assert result.returncode == 0
    assert captured["command"][:3] == ["gcloud", "storage", "cp"]
    assert captured["command"][3] == "gs://dx-scin-public-data/dataset/images/a.png"
    assert "--recursive" not in captured["command"]


def test_run_gcloud_cp_missing_executable(monkeypatch):
    def fake_run(command, **kwargs):
        raise FileNotFoundError("gcloud")

    monkeypatch.setattr(download.subprocess, "run", fake_run)
    result = download.run_gcloud_cp(
        "gs://b/a.png", Path("out/a.png"), gcloud_executable="gcloud"
    )
    assert result.returncode == 127
    assert "gcloud" in result.stderr.lower()


def test_run_gcloud_cp_timeout(monkeypatch):
    def fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(command, 1)

    monkeypatch.setattr(download.subprocess, "run", fake_run)
    result = download.run_gcloud_cp(
        "gs://b/a.png", Path("out/a.png"), gcloud_executable="gcloud"
    )
    assert result.returncode == 124


# ---------------------------------------------------------------------------
# OpenCV validation
# ---------------------------------------------------------------------------


def test_is_loadable_image_true_for_png(tmp_path):
    path = tmp_path / "ok.png"
    path.write_bytes(png_bytes())
    assert download.is_loadable_image(path) is True


def test_is_loadable_image_false_for_garbage(tmp_path):
    path = tmp_path / "bad.png"
    path.write_bytes(b"this is not an image")
    assert download.is_loadable_image(path) is False


def test_is_loadable_image_false_for_missing(tmp_path):
    assert download.is_loadable_image(tmp_path / "missing.png") is False


# ---------------------------------------------------------------------------
# download_candidate
# ---------------------------------------------------------------------------


def test_download_candidate_downloads_and_logs(tmp_path):
    outcome = download.download_candidate(
        candidate_row(),
        bucket_name="dx-scin-public-data",
        output_dir=tmp_path,
        runner=runner_ok(png_bytes()),
    )

    row = outcome.row
    assert row["download_status"] == download.STATUS_DOWNLOADED
    assert row["remote_url"] == (
        "gs://dx-scin-public-data/dataset/images/-999.png"
    )
    assert row["error_message"] == ""
    assert row["file_size_bytes"] > 0
    assert outcome.status_code == 0
    assert download.is_loadable_image(Path(row["local_path"]))
    assert not list(tmp_path.glob("*.part"))


def test_download_candidate_normalizes_bare_id(tmp_path):
    outcome = download.download_candidate(
        candidate_row(image_path="4716341186591937478"),
        bucket_name="dx-scin-public-data",
        output_dir=tmp_path,
        runner=runner_ok(png_bytes()),
    )
    assert outcome.row["remote_url"] == (
        "gs://dx-scin-public-data/dataset/images/4716341186591937478.png"
    )
    assert outcome.row["download_status"] == download.STATUS_DOWNLOADED


def test_download_candidate_skips_existing_valid_file(tmp_path):
    local = download.destination_path(
        tmp_path, "scin__-123__1", "dataset/images/-999.png"
    )
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_bytes(png_bytes())

    def _explode(gs_uri, local_path, timeout=None):  # pragma: no cover
        raise AssertionError("runner must not be called for a skipped file")

    outcome = download.download_candidate(
        candidate_row(),
        bucket_name="dx-scin-public-data",
        output_dir=tmp_path,
        runner=_explode,
    )

    assert outcome.row["download_status"] == download.STATUS_SKIPPED
    assert outcome.row["file_size_bytes"] == local.stat().st_size


def test_download_candidate_gcloud_failure_reports_uri(tmp_path):
    outcome = download.download_candidate(
        candidate_row(),
        bucket_name="dx-scin-public-data",
        output_dir=tmp_path,
        runner=runner_fail("NoSuchKey"),
    )

    assert outcome.status_code == 1
    assert outcome.row["download_status"] == download.STATUS_FAILED
    assert "gs://dx-scin-public-data/dataset/images/-999.png" in outcome.row["error_message"]
    assert "NoSuchKey" in outcome.row["error_message"]
    assert not list(tmp_path.glob("*.png"))


def test_download_candidate_invalid_image_bytes_failed(tmp_path):
    outcome = download.download_candidate(
        candidate_row(),
        bucket_name="dx-scin-public-data",
        output_dir=tmp_path,
        runner=runner_ok(b"not an image"),
    )
    assert outcome.row["download_status"] == download.STATUS_FAILED
    assert "not a readable image" in outcome.row["error_message"]
    assert not list(tmp_path.glob("*.png"))
    assert not list(tmp_path.glob("*.part"))


def test_download_candidate_empty_image_path_failed(tmp_path):
    outcome = download.download_candidate(
        candidate_row(image_path=""),
        bucket_name="dx-scin-public-data",
        output_dir=tmp_path,
        runner=runner_ok(png_bytes()),
    )
    assert outcome.row["download_status"] == download.STATUS_FAILED
    assert "empty image_path" in outcome.row["error_message"]


# ---------------------------------------------------------------------------
# run_downloads and stop-on-failure behavior
# ---------------------------------------------------------------------------


def test_run_downloads_returns_log_with_exact_columns(tmp_path):
    log, stopped = download.run_downloads(
        [candidate_row(), candidate_row(image_id="scin__-124__1", case_id="-124")],
        bucket_name="dx-scin-public-data",
        output_dir=tmp_path,
        runner=runner_ok(png_bytes()),
    )
    assert list(log.columns) == list(download.DOWNLOAD_LOG_COLUMNS)
    assert stopped is None
    assert len(log) == 2
    assert set(log["download_status"]) == {download.STATUS_DOWNLOADED}


def test_run_downloads_stops_on_first_failure(tmp_path):
    rows = [
        candidate_row(image_id="a", image_path="dataset/images/a.png"),
        candidate_row(image_id="b", image_path="dataset/images/b.png"),
    ]
    log, stopped = download.run_downloads(
        rows,
        bucket_name="dx-scin-public-data",
        output_dir=tmp_path,
        runner=runner_fail(),
        stop_on_first_failure=True,
    )
    assert len(log) == 1
    assert stopped == "gs://dx-scin-public-data/dataset/images/a.png"


# ---------------------------------------------------------------------------
# Summaries and candidate loading
# ---------------------------------------------------------------------------


def test_summarize_by_group_counts_statuses():
    log = pd.DataFrame(
        [
            {"image_id": "1", "source_broad_mst_group": "light", "download_status": "downloaded"},
            {"image_id": "2", "source_broad_mst_group": "light", "download_status": "skipped"},
            {"image_id": "3", "source_broad_mst_group": "dark", "download_status": "failed"},
        ]
    )
    summary = download.summarize_by_group(log)
    assert list(summary.columns) == [
        "source_broad_mst_group",
        "downloaded",
        "skipped",
        "failed",
    ]
    light = summary[summary["source_broad_mst_group"] == "light"].iloc[0]
    assert (light["downloaded"], light["skipped"], light["failed"]) == (1, 1, 0)
    assert list(summary["source_broad_mst_group"])[:3] == ["light", "medium", "dark"]


def test_summarize_by_group_empty():
    summary = download.summarize_by_group(pd.DataFrame())
    assert summary.empty


def test_load_candidates_ok(tmp_path):
    path = tmp_path / "cands.csv"
    pd.DataFrame(
        [
            {
                "image_id": "a",
                "case_id": "-1",
                "image_path": "dataset/images/a.png",
                "source_mst_label": 2,
                "source_broad_mst_group": "light",
            }
        ]
    ).to_csv(path, index=False)
    frame = download.load_candidates(path)
    assert len(frame) == 1


def test_load_candidates_missing_columns_raises(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame([{"image_id": "a"}]).to_csv(path, index=False)
    with pytest.raises(download.CandidatesError):
        download.load_candidates(path)


def test_load_candidates_missing_file_raises(tmp_path):
    with pytest.raises(download.CandidatesError):
        download.load_candidates(tmp_path / "nope.csv")
