# TrueHue

Smartphone-based post-capture skin-tone correction using ITA estimation and
machine learning. University of San Carlos thesis project.

**Development is ongoing. Reliable ITA-to-MST mapping and reliable automatic
correction remain unfinished.** Software checks and target-aware diagnostic
fits do not establish a validated correction model.

## Retained approach

Face detection -> facial skin measurement -> ITA -> calibrated MST -> facial
statistics and decision-tree gamma/red/blue correction -> corrected photograph.
The written task is synthetic photographic restoration toward an original
reference, rather than proof of recovery of intrinsic skin colour.

Correction development uses whole-face and visible-neck support with enclosed
hole filling and inward edge blending. Measurement excludes internal features,
hair and neck. FaceOcc is a preferred experimental measurement candidate.
The Android/desktop demos still use their older experimental baseline.
The fourth contrast control is a separate experiment, not an adopted output.

## Start here

- [Partner clone/setup and collaboration guide](docs/collaborator-setup.md).

- [Organised documentation guide](docs/README.md).
- [Searchable project catalogue](PROJECT.html) (open locally in a browser).
- [Grouped VS Code workspace](TrueHue.code-workspace) (open as a workspace).
- [All documents by topic](docs/navigation/research-library.md) and [script catalogue](scripts/README.md).

- [Current session handoff](docs/session-handoff-2026-10-30.md) (latest entries first).
- [Methods and interim results](docs/thesis-methods-results-draft-2026-11-03.md).
- [Discussion, limitations and interim conclusion](docs/thesis-discussion-limitations-conclusion-draft-2026-11-03.md).
- [Changes from the proposal](docs/panel-change-register.md).
- [Integrated correction plan](docs/integrated-correction-development-plan-2026-11-03.md).
- [FFHQ source preparation](docs/ffhq-source-preparation-results-2026-11-03.md).
- [Android setup and current implementation](android-app/README.md).
- [Repository maintenance record](docs/repository-maintenance-2026-11-04.md).

The FFHQ check acquired 12 fixed photographic candidates. Mask/support checks
are next; ITA-to-MST work is deferred for this source-preparation phase. No
full-method training or invented MST labels follow from that deferral.
DAST has been dropped from active acquisition at the user's request.

## Repository layout

| Folder | Contents |
|---|---|
| `src/` | Python implementation, imported using the `src.` namespace |
| `tests/` | Python verification |
| `scripts/` | Numbered experiment, acquisition and verification entry points |
| `docs/` | Protocols, results, decisions and dated working thesis drafts |
| `android-app/` | Kotlin/Compose app and Android/JVM tests |
| `data/`, `models/`, `outputs/` | Local datasets, model weights and experiment evidence; ignored by Git |
| `tmp/`, `output/` | Local build/render intermediates and generated reports; ignored by Git |

Historical scripts and results are retained for provenance. Do not treat every
script as a current workflow. Follow its protocol and current handoff before
running it; old approvals, lookups and mask contracts may be incompatible.

## Python setup

Run commands from the repository root. The current local environment uses
Python 3.14; package metadata allows Python 3.10 and later.

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe scripts/run_hello_world.py
venv\Scripts\python.exe -m pytest tests/ -q
```

The full suite includes desktop GUI checks requiring a working Tcl/Tk install.
For this Windows environment, the documented broader check excludes that file:

```powershell
venv\Scripts\python.exe -B -m pytest tests/ --ignore=tests/test_demo_desktop.py -q -p no:cacheprovider
```

Some research scripts require separately acquired model weights and local saved
artifacts. A fresh clone is the source/documentation checkout, not a complete
copy of the research datasets or a turnkey reproduction of every experiment.
FaceOcc inference uses its separate local environment; do not install its
optional research stack into the main environment automatically.

## Local artifacts and data

Raw photos, trained/downloaded model binaries, APKs, SDKs, virtual environments,
private machine settings, generated galleries and experiment snapshots stay
local. Removing them from Git consideration does not delete them from disk.
Dataset licences and per-photo attribution still govern their use. Preserve
saved failures, source hashes, user decisions, reserved roles and frozen evidence.
The proposal PDF is an unchanged local reference and is excluded from Git;
place it locally when reproducing checks that require its bytes. Dated Markdown
files are working drafts and are not a submitted or approved replacement.

## Team

Nythan John Rivera and Oceane Rim Dardare, University of San Carlos.
