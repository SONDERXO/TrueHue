# Partner setup and collaboration

5 November 2026. The repository is public and `main` is the shared source branch.
Development is ongoing; publishing to main does not validate the correction
model or ITA-to-MST mapping.

## 1. Clone the source

Install Git, then run:

```powershell
git -c core.autocrlf=false clone https://github.com/SONDERXO/TrueHue.git
cd TrueHue
git config core.autocrlf false
git switch main
```

The line-ending setting is local to this checkout and helps preserve byte-based
source hashes; it does not change the computer's global Git settings. No GitHub
invitation is needed to clone/read a public repository.

Open `TrueHue.code-workspace` using **File → Open Workspace from File** in VS Code,
or open the folder normally. Start with [the current documentation guide](README.md).

For thesis writing, Git/VS Code and the Markdown documents are sufficient. Python
and the research datasets are needed only for the corresponding software work.
Use the dated3November methods/results and discussion drafts; the older drafts
remain historical records. The proposal PDF is a separate local reference.

## 2. Set up Python when needed

The current working machine uses Python3.14. Create a new environment on the
partner's computer; copying the original `venv/` will not make a portable install.
Run commands from the repository root.

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe scripts/412_check_collaborator_setup.py --require-python-deps
venv\Scripts\python.exe scripts/run_hello_world.py
```

`requirements-tested.txt` records the direct dependency versions observed on
the existing Windows/Python3.14 machine. It is a reference snapshot, not a full
transitive/cross-platform lock or a claim that every operating system has been
tested. Use it instead of `requirements.txt` when matching that environment is
appropriate. No dependency version sweep is required for thesis editing.

On macOS/Linux, use `venv/bin/python` for these Python commands. Package/native
availability on that system still needs checking. The setup checker reports
missing local assets separately, and does not download anything or enable training.

A source-only numerical/software check, which needs no model weights or photos:

```powershell
venv\Scripts\python.exe -B -m pytest tests/test_paper_gamma.py tests/test_blended_recovery_targets.py tests/test_core_colour_recipe.py tests/test_development_distortion_roles.py -q -p no:cacheprovider
```

This smoke check is not the full research suite or a correction-model evaluation.
Some other tests and historical scripts require ignored saved artifacts. The
desktop GUI tests additionally need Tcl/Tk. Source-only validation on the owner's
machine uses the existing installed environment; a clean dependency installation
on the partner's computer has not been performed by this guide.

## 3. Understand what cloning includes

| Included in Git | Local/separate setup |
|---|---|
| Source, numbered scripts and tests | Raw datasets and downloaded/trained model weights |
| Protocols, experiment reports and working thesis drafts | Saved galleries, measurement arrays, manifests and evidence snapshots |
| Android source, Gradle wrapper and component-test assets | Android SDK/JDK, generated pipeline assets, APKs and device-test photographs |
| Searchable catalogue and workspace views | Proposal PDF, Python environments and machine settings |

Missing local galleries after cloning are expected, not evidence that the source
checkout failed. Do not run historical training/calibration/acquisition scripts
just to replace missing artifacts. The existing script411 navigation rebuild
expects the owner's complete local evidence; use the committed catalogue and
document guide on a source-only checkout until those artifacts are available.

For research reproduction, agree on the exact required artifact/version first.
Obtain third-party data/models from their documented sources or transfer only
material permitted by the applicable licences, retaining attribution and hashes.
Do not upload the entire local workspace to GitHub or copy credentials, `venv/`,
SDKs or signing keys. Do not call a source group a verified distinct person.

## 4. Optional: obtain the same12 FFHQ source photographs

This is an explicit photographic source download, separate from the basic clone
and thesis-writing setup. It needs about268MB of metadata plus16MB of photos.
The published script preserves the fixed selection and verifies publisher file
and decoded-pixel checksums; it does not assign MST, fit a model or approve masks.

```powershell
venv\Scripts\python.exe scripts/413_restore_ffhq_support_metadata.py
venv\Scripts\python.exe scripts/408_prepare_ffhq_sources.py
venv\Scripts\python.exe scripts/409_build_ffhq_source_gallery.py
```

The first command restores only pinned public repository-tree metadata that
script408 needs. It does not recreate the old assessment experiment. The next
two create the bounded source sample and gallery. They refuse overwriting
existing output/raw-sample folders. If those folders already exist, preserve
them and check their provenance rather than deleting them to force a rerun.

Do not run script410 as a general bootstrap: it records the owner's assistant
observations and checks historical local plan evidence. Its observations are
already described in the [source report](ffhq-source-preparation-results-2026-11-03.md).
Mask/support checks on the same12 sources are the next research task, with a
recorded protocol before inference. ITA-to-MST remains deferred for source work.

## 5. Work together without overwriting each other

Before a task:

```powershell
git switch main
git pull --ff-only origin main
git switch -c thesis/your-topic
```

Commit only the relevant source/document changes and inspect `git diff --staged`
before publishing. If the owner adds the partner as a collaborator with Write
access, she can push her branch to this repository and open a pull request.
Otherwise she can fork the public repository, push to her fork and open a pull
request back to `main`. An invitation is not needed for that fork workflow.
Do not share the owner's GitHub login/token. No invitation is sent by this setup.

Agree on separate writing sections/tasks where practical. Keep original results,
failures, raw review decisions and pinned paths intact; add dated updates rather
than silently rewriting historical experiment outcomes. Avoid blanket
`git add .` when local data or environments have been added. Regenerated local
catalogues may change according to available outputs: commit those only when a
catalogue update is intended.

The owner's earlier973Python(excluding desktop GUI) and18JVM maintenance checks
remain dated evidence. They do not mean the partner's environment, physical
device, latest masks or final research model have been validated.

Setup validation on5November used an export of the staged source checkout with
all seven checked local assets absent, running in the owner's existing Python
environment. The setup report and hello-world command passed; the source-only
smoke check passed45tests in7.74seconds. The support-metadata copy, idempotent
rerun and refusal to overwrite differing metadata were checked. No photos/models
were downloaded, and no fresh dependency installation or partner-machine test
is claimed. Local check evidence is under `outputs/collaborator_setup_20261105_v1/`.
