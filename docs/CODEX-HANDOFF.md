# TrueHue continuation checkpoint

Updated28October2026. Open this same workspace after changing accounts:
`C:\Users\NYTHAN\OneDrive\Documents\TrueHue`.
Do not assume another account has this chat. Start it with:

> Continue TrueHue. Read AGENTS.md, docs/CODEX-HANDOFF.md,
> docs/expirement-log.md, docs/thesis-method-alignment.md and
> docs/face-boundary-review-guide.md first. Prioritize the Python model and
> retain the paper's MST method. Preserve all reviews, holds and experiment
> evidence. Android is on hold and CPM is deferred.

## User decisions

- Python, Android and thesis results due before7November; working cutoff6November.
- Model first; Android temporarily paused. Existing debug APK builds and14tests
  pass, but image repository is still pass-through. Do not call it integrated.
- Retain ITA→MST→decision-tree method. DirectLab/ITA models are development-only.
- CPM/material expansion explicitly deferred; makeup handling is a limitation.
  An open `cpm-pattern-feasibility.md` tab does not resume it.
- Face plus visible neck was requested; neck implementation remains unfinished.
- Original boundary annotations imported/confirmed; do not ask to redo or edit them.
- Continue authorized work autonomously. No commits/uploads or user outreach made.

## Verified model state

Original active model remains `models/correction_prototype_v1/decision_tree.joblib`.
The control-aware22pair/six-source candidate in
`outputs/control_aware_model_build_v1/` is held for poor quality. Source-held-out
mean CIEDE2000:5.129no correction,6.865controls. All6unchanged controls harmed.
Expanded32regenerated pairs/nine sources are NOT newly approved for fitting.
Read `docs/control-aware-model-build-results.md` and
`docs/core-source-readiness-results.md`. Do not repeat small depth/feature sweeps.

## Latest work: square256 MST calibration

Frozen protocol: `docs/mst-square256-calibration-protocol.md`.
New modules: `src/ita_estimation/square_measurement.py` and
`threshold_calibration.py`. Existing `mst_lookup.py` is an artifact/feature
interface with synthetic tests, not a validated real lookup.

Script138completed all418historically reviewed/included MST-E development
images using whole-frame256INTER_LINEAR before detection/measurement, fixed
YuNet0.85and complete-mouth mask, required landmarks/min1000pixels.
`outputs/mst_square256_measurement_v1/`:396success,21detection failures,
1mask-stage failure. Original reviews untouched; new masks not human-approved.
Contract SHA256`051dfb175e1356776ea59ebb5c3d63a7e1130de49d5787a7e75b7c0fa135db73`.
Twelve preselected boards visually inspected: coverage holes and possible
hair/background/glasses selection remain; numerical success is not mask quality.

Script139completed fixed subject-median/isotonic-center calibration diagnostic:
396images/15subjects; pooled category centers block nine distinct thresholds.
Categories4,5,7,9,10have only one measured subject. All held-subject folds are
unsupported under this complete-ten-category recipe;0predictions, not0%accuracy.
`outputs/mst_square256_calibration_v1/summary.json` records the result. No real
production lookup exported; no correction-tree fit or runtime replacement.
Do not invent gaps, relax masks/pixels or claim an untouched final test.
Latest full suite:607passed in11.16s, including12new measurement/calibration tests.

Next: independently audit calibration/support accounting and document concrete
mask/reference versus subject-support limitations before choosing another
calibration design. Preserve negative findings. Resolving final data roles,
representative labeled subjects and measurement quality is necessary; do not
repeat this recipe under a different name hoping to release thresholds.
Proposal explicitly uses MST-E calibration despite elsewhere saying evaluation-only;
historical exposure must be disclosed and calibration/evaluation roles separated.
MST-E must never enter correction-tree training. SCIN India/US labels disagree
often; no silent annotator choice or new source admission.

## Environment and preservation

Run from root with `.\venv\Scripts\python.exe` (Python3.14). Tests:
`.\venv\Scripts\python.exe -m pytest tests/ -q --basetemp=outputs/<fresh-name>`.
No subagents unless explicitly authorized. Large uncommitted development tree:
do not reset, discard or commit it. Data/models/outputs are ignored local assets;
a new account on this PC needs the same folder, not only a cloned Git repo.
Cleanup already removed only caches/temporary artifacts (~388MiB); keep evidence.
Use scripts' no-overwrite behavior and fresh output folders. Preserve source
allocations, original export/polygons, exclusions and failure rows. Skills/tools
and login state may differ between accounts; rely on actual local files.
