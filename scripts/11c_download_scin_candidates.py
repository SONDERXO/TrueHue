"""
11c_download_scin_candidates.py

Purpose:
    Download ONLY the SCIN image files listed in the metadata-only candidate
    selection (scripts/11b_select_scin_subset.py) from Google Cloud Storage,
    never the full SCIN dataset and never the whole bucket.

    The official SCIN images live in the public GCS bucket
    ``dx-scin-public-data`` with object paths of the form::

        dataset/images/4716341186591937478.png

    so the full object URI is::

        gs://dx-scin-public-data/dataset/images/4716341186591937478.png

    Each image is fetched with::

        gcloud storage cp gs://<bucket>/<image_path> <local_path>

    ``--recursive`` is never used, so only the listed objects are copied.

What this script does NOT do
----------------------------
- It never downloads the full dataset or the entire bucket.
- It never runs the TrueHue pipeline and never trains a model.
- It never modifies Skin Mask V2, ITA, FairFace, or MST-E code.

Outputs:
    data/raw/scin/selected_candidates/   the downloaded image files
    data/manifests/scin_download_log.csv one row per candidate with its status

Run from the project root:
    # 1. Safe first download + confirmation skipped (single image).
    python scripts/11c_download_scin_candidates.py --limit 1 --yes

    # 2. Full selected subset, skipping files already downloaded.
    python scripts/11c_download_scin_candidates.py --yes

    # 3. See the plan without downloading anything.
    python scripts/11c_download_scin_candidates.py --dry-run

Requires the Google Cloud SDK (``gcloud``) on PATH and, for a public bucket, no
authentication.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from functools import partial
from pathlib import Path
from typing import Callable, Iterable, NamedTuple

import cv2
import pandas as pd

# Make the project root importable when this file is run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_preparation.training_manifest import GROUP_ORDER  # noqa: E402


# -------------------------------------------------------------------
# Paths, constants, and column contracts
# -------------------------------------------------------------------

DEFAULT_CANDIDATES = (
    PROJECT_ROOT / "data" / "manifests" / "scin_candidate_selection.csv"
)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "scin" / "selected_candidates"
DEFAULT_LOG = PROJECT_ROOT / "data" / "manifests" / "scin_download_log.csv"

#: Public SCIN bucket on Google Cloud Storage.
DEFAULT_BUCKET_NAME = "dx-scin-public-data"

#: Object prefix every SCIN image path must have.
OBJECT_PREFIX = "dataset/images/"

DEFAULT_TIMEOUT_SECONDS = 120

#: Columns required in the candidate CSV.
REQUIRED_CANDIDATE_COLUMNS: tuple[str, ...] = (
    "image_id",
    "case_id",
    "image_path",
    "source_mst_label",
    "source_broad_mst_group",
)

#: Exact log columns, in order.
DOWNLOAD_LOG_COLUMNS: tuple[str, ...] = (
    "image_id",
    "case_id",
    "image_path",
    "source_mst_label",
    "source_broad_mst_group",
    "local_path",
    "remote_url",
    "download_status",
    "error_message",
    "file_size_bytes",
)

STATUS_DOWNLOADED = "downloaded"
STATUS_SKIPPED = "skipped"
STATUS_FAILED = "failed"


class DownloadOutcome(NamedTuple):
    """The log row for one candidate plus the gcloud return code (``None`` if not run)."""

    row: dict
    status_code: int | None


class CommandResult(NamedTuple):
    """Result of running an external command (decoupled from ``subprocess``)."""

    returncode: int
    stdout: str = ""
    stderr: str = ""


class CandidatesError(Exception):
    """Raised when the candidate CSV is missing or malformed."""


# -------------------------------------------------------------------
# gcloud storage cp (injectable so tests do not call gcloud)
# -------------------------------------------------------------------

#: Common Cloud SDK install locations checked when ``gcloud`` is not on PATH.
GCLOUD_CANDIDATE_SUBPATHS: tuple[str, ...] = (
    "Google/Cloud SDK/google-cloud-sdk/bin/gcloud.cmd",
    "Google/Cloud SDK/google-cloud-sdk/bin/gcloud",
    "google-cloud-sdk/bin/gcloud.cmd",
    "google-cloud-sdk/bin/gcloud",
)


def find_gcloud_executable() -> str | None:
    """Locate the ``gcloud`` executable.

    Checks PATH first, then the common Cloud SDK install locations (the Windows
    installer does not always add the SDK to PATH). Returns ``None`` when no
    executable can be found.
    """
    on_path = shutil.which("gcloud")
    if on_path:
        return on_path

    env = os.environ
    roots: list[str] = []
    for key in ("LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)", "USERPROFILE"):
        value = env.get(key)
        if value:
            roots.append(value)
    home = env.get("HOME")
    if home:
        roots.append(home)
    if env.get("APPDATA"):
        roots.append(env["APPDATA"])

    for root in roots:
        for subpath in GCLOUD_CANDIDATE_SUBPATHS:
            candidate = Path(root) / subpath
            if candidate.is_file():
                return str(candidate)
    return None


def build_gcloud_command(
    gcloud_executable: str, gs_uri: str, local_path: Path
) -> list[str]:
    """Build the argument list for one ``gcloud storage cp`` call.

    On Windows a ``.cmd``/``.bat`` wrapper is launched through ``cmd /c``.
    ``--recursive`` is never added.
    """
    executable = str(gcloud_executable)
    if os.name == "nt" and executable.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", executable, "storage", "cp", gs_uri, str(local_path)]
    return [executable, "storage", "cp", gs_uri, str(local_path)]


def run_gcloud_cp(
    gs_uri: str,
    local_path: Path,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    gcloud_executable: str | None = None,
) -> CommandResult:
    """Copy one object with ``gcloud storage cp`` (never ``--recursive``)."""
    executable = gcloud_executable or find_gcloud_executable() or "gcloud"
    command = build_gcloud_command(executable, gs_uri, local_path)
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return CommandResult(
            127,
            "",
            "gcloud executable not found on PATH. Install the Google Cloud SDK.",
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            124,
            "",
            f"gcloud storage cp timed out after {timeout} seconds.",
        )
    return CommandResult(
        int(completed.returncode),
        completed.stdout or "",
        completed.stderr or "",
    )


# -------------------------------------------------------------------
# Pure helpers
# -------------------------------------------------------------------


def _cell(row, key: str) -> str:
    """Return a stripped string cell from a mapping/Series-like row."""
    value = row[key]
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):  # pragma: no cover - defensive
        pass
    return str(value).strip()


def normalize_object_path(image_path: object) -> str:
    """Return a ``dataset/images/<filename>.png`` object path.

    Paths that already start with ``dataset/images/`` are preserved. Anything
    else (a bare numeric ID or a filename, optionally with a directory) is
    reduced to its file name and placed under ``dataset/images/``; a missing
    extension becomes ``.png``.
    """
    if image_path is None:
        return ""
    try:
        if pd.isna(image_path):
            return ""
    except (TypeError, ValueError):  # pragma: no cover - defensive
        pass

    text = str(image_path).strip().replace("\\", "/")
    if not text:
        return ""

    if text.lower().startswith(OBJECT_PREFIX):
        return text

    name = text.rsplit("/", 1)[-1]
    if not name:
        return ""
    if not Path(name).suffix:
        name = name + ".png"
    return OBJECT_PREFIX + name


def build_gs_uri(bucket_name: str, object_path: str) -> str:
    """Build ``gs://<bucket>/<object_path>``."""
    bucket = str(bucket_name).strip().strip("/")
    if not bucket:
        raise ValueError("bucket name must not be empty")
    return f"gs://{bucket}/{str(object_path).lstrip('/')}"


def safe_local_filename(image_id: object, object_path: object) -> str:
    """Return a filesystem-safe filename based on ``image_id`` and the suffix."""
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", str(image_id)).strip("._-")
    if not stem:
        stem = "scin_image"

    suffix = Path(str(object_path)).suffix
    if not re.fullmatch(r"\.[A-Za-z0-9]{1,8}", suffix or ""):
        suffix = ".png"
    return stem + suffix


def destination_path(output_dir: Path, image_id: object, object_path: object) -> Path:
    """Return the local path an image should be saved to."""
    return Path(output_dir) / safe_local_filename(image_id, object_path)


def is_loadable_image(path: Path) -> bool:
    """Return True when OpenCV can load ``path`` as an image."""
    if not Path(path).is_file():
        return False
    image = cv2.imread(str(path))
    return image is not None and image.size > 0


# -------------------------------------------------------------------
# Candidate loading
# -------------------------------------------------------------------


def load_candidates(csv_path: Path) -> pd.DataFrame:
    """Read the candidate selection CSV and validate its columns."""
    path = Path(csv_path)
    if not path.is_file():
        raise CandidatesError(f"candidate CSV not found: {path}")

    candidates = pd.read_csv(path)
    if candidates.empty:
        raise CandidatesError(f"candidate CSV is empty: {path}")

    missing = [
        column
        for column in REQUIRED_CANDIDATE_COLUMNS
        if column not in candidates.columns
    ]
    if missing:
        raise CandidatesError(
            f"candidate CSV is missing required columns {missing}.\n"
            f"  available: {list(candidates.columns)}"
        )
    return candidates


# -------------------------------------------------------------------
# Downloading
# -------------------------------------------------------------------


def download_candidate(
    row,
    *,
    bucket_name: str,
    output_dir: Path,
    runner: Callable = run_gcloud_cp,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> DownloadOutcome:
    """Download (or skip) one candidate image and build its log row.

    The image is copied to a ``.part`` file first and only moved into place once
    OpenCV can read it, so a failed or corrupt download never leaves a bad image
    behind. An existing, loadable file is reported as ``skipped``.
    """
    image_id = _cell(row, "image_id")
    case_id = _cell(row, "case_id")
    image_path = _cell(row, "image_path")
    source_mst_label = _cell(row, "source_mst_label")
    source_broad_mst_group = _cell(row, "source_broad_mst_group")

    object_path = normalize_object_path(image_path)
    local_path = destination_path(output_dir, image_id, object_path)

    row_out = {
        "image_id": image_id,
        "case_id": case_id,
        "image_path": image_path,
        "source_mst_label": source_mst_label,
        "source_broad_mst_group": source_broad_mst_group,
        "local_path": local_path.as_posix(),
        "remote_url": "",
        "download_status": STATUS_FAILED,
        "error_message": "",
        "file_size_bytes": 0,
    }

    if not object_path:
        row_out["error_message"] = f"empty image_path for image_id {image_id!r}"
        return DownloadOutcome(row_out, None)

    gs_uri = build_gs_uri(bucket_name, object_path)
    row_out["remote_url"] = gs_uri

    # Skip files that are already present and valid.
    if is_loadable_image(local_path):
        row_out["download_status"] = STATUS_SKIPPED
        row_out["file_size_bytes"] = local_path.stat().st_size
        return DownloadOutcome(row_out, None)

    local_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = local_path.with_name(local_path.name + ".part")
    temp_path.unlink(missing_ok=True)

    result = runner(gs_uri, temp_path, timeout)

    if result.returncode != 0:
        temp_path.unlink(missing_ok=True)
        detail = (result.stderr or result.stdout or "").strip()
        if not detail:
            detail = f"gcloud exited with code {result.returncode}"
        row_out["error_message"] = f"gcloud storage cp failed for {gs_uri}: {detail}"
        return DownloadOutcome(row_out, int(result.returncode))

    if not is_loadable_image(temp_path):
        temp_path.unlink(missing_ok=True)
        row_out["error_message"] = (
            f"downloaded object is not a readable image ({gs_uri})"
        )
        return DownloadOutcome(row_out, int(result.returncode))

    temp_path.replace(local_path)
    row_out["download_status"] = STATUS_DOWNLOADED
    row_out["file_size_bytes"] = local_path.stat().st_size
    return DownloadOutcome(row_out, 0)


def run_downloads(
    rows: Iterable,
    *,
    bucket_name: str,
    output_dir: Path,
    runner: Callable = run_gcloud_cp,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    stop_on_first_failure: bool = False,
) -> tuple[pd.DataFrame, str | None]:
    """Download every candidate row and return the log plus any stop URI.

    When ``stop_on_first_failure`` is True, iteration stops at the first failed
    object and the attempted ``gs://`` URI is returned and printed.
    """
    log_rows: list[dict] = []
    stopped_uri: str | None = None
    rows = list(rows)

    for index, row in enumerate(rows, start=1):
        outcome = download_candidate(
            row,
            bucket_name=bucket_name,
            output_dir=output_dir,
            runner=runner,
            timeout=timeout,
        )
        log_rows.append(outcome.row)
        print(
            f"  [{index}/{len(rows)}] {outcome.row['download_status']:<10} "
            f"{outcome.row['image_id']}"
        )

        if (
            stop_on_first_failure
            and outcome.row["download_status"] == STATUS_FAILED
        ):
            stopped_uri = outcome.row["remote_url"] or None
            print()
            print("Stopping after the first failed object (--limit 1 mode).")
            print(f"  attempted URI : {stopped_uri}")
            break

    log = pd.DataFrame(log_rows, columns=list(DOWNLOAD_LOG_COLUMNS))
    if not log.empty:
        log["file_size_bytes"] = log["file_size_bytes"].astype("int64")
    return log, stopped_uri


def summarize_by_group(log: pd.DataFrame) -> pd.DataFrame:
    """Return downloaded/skipped/failed counts per broad group."""
    if log is None or log.empty:
        return pd.DataFrame(
            columns=[
                "source_broad_mst_group",
                "downloaded",
                "skipped",
                "failed",
            ]
        )

    pivot = log.pivot_table(
        index="source_broad_mst_group",
        columns="download_status",
        values="image_id",
        aggfunc="count",
        fill_value=0,
    )
    for status in (STATUS_DOWNLOADED, STATUS_SKIPPED, STATUS_FAILED):
        if status not in pivot.columns:
            pivot[status] = 0
    pivot = pivot[[STATUS_DOWNLOADED, STATUS_SKIPPED, STATUS_FAILED]]

    other = [index for index in pivot.index if index not in GROUP_ORDER]
    pivot = pivot.reindex(list(GROUP_ORDER) + other, fill_value=0).astype(int)
    return pivot.reset_index()


# -------------------------------------------------------------------
# Command-line options
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description=(
            "Download only the SCIN images listed in the candidate selection "
            "CSV from Google Cloud Storage with 'gcloud storage cp'. Never "
            "downloads the whole bucket."
        )
    )
    parser.add_argument(
        "--bucket-name",
        default=DEFAULT_BUCKET_NAME,
        help=f"GCS bucket holding the SCIN images (default: {DEFAULT_BUCKET_NAME})",
    )
    parser.add_argument(
        "--gcloud",
        default=None,
        help=(
            "Path to the gcloud executable. Useful when it is not on PATH "
            "(default: auto-detect)."
        ),
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_CANDIDATES,
        help=f"Candidate selection CSV (default: {DEFAULT_CANDIDATES})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Where images are saved (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help=f"Download log CSV (default: {DEFAULT_LOG})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only process the first N candidates (0 = all).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Per-request timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the plan and exit without calling gcloud.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt.",
    )
    return parser.parse_args()


def _display_path(path: Path) -> str:
    """Return a path relative to the project root when possible."""
    try:
        return Path(path).resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def confirm_download(count: int, output_dir: Path) -> bool:
    """Ask the user to confirm; an empty answer means no."""
    prompt = (
        f"Download {count} selected SCIN images to "
        f"{_display_path(output_dir)}/? [y/N] "
    )
    try:
        answer = input(prompt)
    except EOFError:
        return False
    return answer.strip().lower() in {"y", "yes"}


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------


def main() -> None:
    """Download the selected SCIN images from GCS and write the download log."""
    args = parse_arguments()

    try:
        candidates = load_candidates(args.candidates)
    except CandidatesError as error:
        print(f"ERROR: {error}")
        print(
            "Run scripts/11b_select_scin_subset.py first to create the "
            "candidate selection."
        )
        sys.exit(1)

    if args.limit and args.limit > 0:
        candidates = candidates.head(args.limit).reset_index(drop=True)

    gcloud_executable = args.gcloud or find_gcloud_executable()
    if gcloud_executable is None and not args.dry_run:
        print(
            "ERROR: could not find the 'gcloud' executable.\n"
            "Install the Google Cloud SDK, add it to PATH, or pass "
            "--gcloud <path-to-gcloud>."
        )
        sys.exit(1)

    print("=" * 72)
    print("SCIN selected-candidate download (Google Cloud Storage)")
    print("=" * 72)
    print(f"Candidate CSV : {args.candidates}")
    print(f"Selected rows : {len(candidates)}")
    print(f"Bucket        : gs://{args.bucket_name}")
    print(f"gcloud        : {gcloud_executable or '(not found)'}")
    print(f"Output folder : {_display_path(args.output_dir)}/")
    print(f"Log CSV       : {args.log}")
    print(f"Mode          : {'dry-run' if args.dry_run else 'download'}")
    print()
    print("First 5 image paths:")
    for image_path in candidates["image_path"].head(5).tolist():
        print(f"  - {image_path}")

    if args.dry_run:
        print()
        print("Dry run: gcloud will not be called. Planned downloads:")
        for row in candidates.itertuples(index=False):
            object_path = normalize_object_path(row.image_path)
            gs_uri = build_gs_uri(args.bucket_name, object_path)
            local_path = destination_path(
                args.output_dir, row.image_id, object_path
            )
            print(f"  {row.image_id}: {gs_uri} -> {local_path.as_posix()}")
        print()
        print("No files were downloaded (dry run).")
        return

    if not args.yes:
        if not confirm_download(len(candidates), args.output_dir):
            print("Aborted. Nothing was downloaded.")
            return

    args.output_dir.mkdir(parents=True, exist_ok=True)

    stop_on_first_failure = bool(args.limit == 1)
    runner = partial(run_gcloud_cp, gcloud_executable=gcloud_executable)
    log, stopped_uri = run_downloads(
        candidates.to_dict("records"),
        bucket_name=args.bucket_name,
        output_dir=args.output_dir,
        runner=runner,
        timeout=args.timeout,
        stop_on_first_failure=stop_on_first_failure,
    )

    args.log.parent.mkdir(parents=True, exist_ok=True)
    log.to_csv(args.log, index=False)

    summary = summarize_by_group(log)
    downloaded = int((log["download_status"] == STATUS_DOWNLOADED).sum())
    skipped = int((log["download_status"] == STATUS_SKIPPED).sum())
    failed = int((log["download_status"] == STATUS_FAILED).sum())

    print()
    print("=" * 72)
    print("Download summary")
    print("=" * 72)
    print(f"Attempted rows : {len(log)}")
    print(f"Downloaded     : {downloaded}")
    print(f"Skipped        : {skipped}")
    print(f"Failed         : {failed}")
    print()
    if not summary.empty:
        print(summary.to_string(index=False))
    print()
    print(f"Images folder  : {_display_path(args.output_dir)}/")
    print(f"Log CSV        : {args.log}")

    if stopped_uri is not None:
        print()
        print(f"Stopped on a failed object: {stopped_uri}")

    if failed and not args.limit == 1:
        print()
        print("Failures (first 5):")
        failures = log[log["download_status"] == STATUS_FAILED].head(5)
        for failure in failures.itertuples(index=False):
            print(f"  - {failure.remote_url}: {failure.error_message}")


if __name__ == "__main__":
    main()
