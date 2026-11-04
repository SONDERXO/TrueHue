# Project organisation — 5 November 2026

The user requested organising the whole workspace after the successful repository
update. Current source is on `android-ui`; the verified previous checkpoint is
`d52f6f478dbd83e20ebf05a848bad1a2299742be`. The local backup of the earlier
unpublished checkpoint remains preserved. No source/history cleanup is implied
by topic placement in the catalogue.

## Entry points

| Entry point | Purpose |
|---|---|
| Root `README.md` | Project status, setup and primary links |
| `docs/README.md` | Current work, thesis drafts and topic guide |
| `PROJECT.html` | Searchable offline catalogue; open in a browser |
| `docs/navigation/research-library.md` | Complete document list grouped by topic |
| `scripts/README.md` | Experiment/helper script catalogue grouped by topic |
| `TrueHue.code-workspace` | Optional grouped VS Code Explorer views |

The workspace file is opt-in. Use **File → Open Workspace from File** in VS Code
and choose `TrueHue.code-workspace`. Its Explorer groups source, Android, tests,
documents, scripts and local artifacts. It hides duplicate subfolders from the
overview and common caches/toolchains; no files or global editor settings are
changed. Reopen the ordinary project folder to return to the original view.
Local data/model/result roots may be empty or absent in a fresh checkout.

## What stays where

Python source already has module folders; Android and tests retain their current
package paths. Numbered scripts, research documents, frozen result folders,
datasets, original photographs, model files and the local proposal PDF remain
in their existing locations. Moving the historical documents/scripts or nesting
the saved result directories would break hard-coded paths, links or saved
source hashes. No broad move, rename, deletion or duplicate archive is used.
The local JDK remains ignored at its existing location so this organisation does
not change IDE runtime paths.

The catalogue exposes historical work without presenting all of it as active.
Current pointers are curated explicitly. Topic assignments use file names and
titles as a navigation aid; they do not decide that a method is approved or a
result is good. Research failures and superseded protocols remain available.
Saved result folders are listed without recursively reading datasets, models,
environments or access-controlled test directories. Third-party notices remain
with their original files.

## Regeneration and checks

`scripts/411_organize_project_navigation.py` regenerates only the navigation
HTML, research/script catalogues and ignored local navigation metadata. It never
executes an experiment. `outputs/project_navigation/` is a regenerable navigation
folder rather than a frozen experiment snapshot. Existing artifact manifests and
the integrated plan's pinned source hashes are checked for preservation.

Validation covers catalogue links, record membership, workspace JSON/root paths,
JavaScript syntax and unchanged existing research files. There are no new photo,
mask, MST, correction or device experiments and no reason to repeat the entire
model test suite for navigation-only changes. The prior973Python(excluding GUI)
and18JVM results remain dated maintenance evidence.

## Current development priority

Check the same12 FFHQ sources for face/neck mask/support feasibility under a
recorded bounded protocol; preserve every failure and concern. No new sample,
review batch, fit or synthetic generation is activated by this organisation.
ITA-to-MST remains deferred for source work and retained in the full method.
