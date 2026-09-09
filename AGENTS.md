# AGENTS.md

TrueHue is a Python ML pipeline (thesis project) for smartphone-based skin-tone correction. Pipeline: face detection → skin mask → ITA → MST → decision-tree correction → corrected image.

## Commands (run from project root)

- `venv\Scripts\activate` then `pip install -r requirements.txt` — Python env lives in `venv/` (Windows, Python 3.14; `requires-python` is >=3.10 but the actual env is 3.14).
- `pytest tests/ -v` — run the test suite. No linter or typechecker is configured; pytest is the only verification step.
- `python scripts/run_hello_world.py` — environment sanity check.

## Import convention

All package imports use the `src.` root namespace: `from src.utilities.config import get_config`, `from src.ita_estimation.compute_ita import compute_ita`.

- Always run scripts and pytest from the **project root** — `src.*` imports resolve only because `src/` is importable from cwd (pyproject sets `pythonpath = ["."]` for pytest; scripts require same cwd).
- The distributable name is `truehue` but code imports `src.*`, not `truehue.*`.

## Current state (important — don't assume features exist)

Core algorithmic modules are **placeholders with documented TODOs**, not implemented:
- `src/face_detection/detect_faces.py` returns `[]`.
- `src/skin_masking/skin_mask.py` returns a zero mask (docs say to implement HSV + YCrCb thresholding).
- `src/ita_estimation/compute_ita.py` and its tests are the only functional portions.

The `android-app/` directory appears in the README tree but **does not exist** in the repo yet. Keep it that way unless explicitly asked to build it.

## Structure & conventions

- Central config: `src/utilities/config.py` (`Config` dataclass) — holds data/model/output paths, `IMAGE_SIZE`, and the `MST_LABELS` (10 Monk Skin Tone labels 0–9). Reuse these constants instead of hardcoding paths/labels.
- `data/`, `models/`, `outputs/` subdirs are fully gitignored (only `.gitkeep` files tracked). Do not commit raw datasets or model binaries.
- MST-E, FairFace, SCIN datasets are extern/not in-repo — never upload raw datasets.
- The ML polymer output targets on-device Android, but all current work is Python.

## Branching (from README)

- `main` = stable/demonstrable only; `develop` = WIP; `ml-pipeline`, `android-ui`, `testing-documentation` = feature branches. Don't commit to `main` for work-in-progress.

## Docs

`docs/` holds `implementation-plan.md` (fixed scope: Android, on-device, single face; model = decision-tree regression of gamma/red gain/blue gain), `setup-guide.md`, `decision-log.md`, `expirement-log.md`. Read `implementation-plan.md` before designing new pipeline stages.
