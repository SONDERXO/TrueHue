# Desktop adviser demo update — 7 November 2026

The user selected the Python desktop demo for the 11:00 PM meeting. The
[complete briefing](adviser-progress-brief-2026-11-07.md) covers the development
history, current feature availability, evidence, needs, limitations and proposed
dates. It is a discussion artifact, not an approved experiment or timeline.

The desktop now provides a Research progress view and a button to open that
briefing. The live model is explicitly identified as the older baseline5/fold1.
No newer correction gate, mask or MST estimator is promoted. No Android edits
were made in this task; pre-existing Android changes remain in the workspace.

## Compatibility repair

The installed Python 3.14 runtime cannot initialize Tk because its Tcl script
library is absent. Its cached distribution also lacked those scripts. An attempt
to read the official upstream Tcl/Tk source was blocked by network socket policy;
no download or dependency installation occurred. This was not an approval-review
rejection. The existing Python 3.13 installation has Tcl/Tk 8.6.15, but absolute
Tcl paths through this workspace's OneDrive alias did not resolve. Relative
library paths worked.

The launcher therefore detects failed Tk initialization, copies the existing
3.13 Tcl scripts to ignored `outputs/desktop_tk_compat_20261107_v1/` if needed,
and starts a standard-library-only Python 3.13 window. Environment variables
apply only to that child. Photo processing runs through a subprocess using
`venv/Scripts/python.exe`, the unchanged `src/demo/service.py` and fixed demo
preset. No global Python installation, registry, dependency or model was changed.
The frontend reads the unchanged service's PNG/report exports; save copies the
export into a unique folder, preserving its manifest. Run artifacts stay private
under ignored `outputs/desktop_meeting_run_*`.

This is a local compatibility fallback, not a portable runtime bundle. It needs
the already installed sibling Python 3.13. Other installations with working Tk
continue to use the original desktop interface. A source-only clone still needs
the historical local demo assets.

## Verification

- Six existing headless demo-service tests passed in 1.46 seconds using a new
  workspace-local pytest temporary directory. The first attempt encountered
  permission errors in the default pytest temp folder; no permissions changed.
- Actual original-pipeline smoke test passed: historical example succeeds;
  known no-face input is rejected without a corrected export; originals remain
  unchanged. `outputs/python_demo_meeting_smoke_20261107_v1/summary.json`.
- Actual compatibility-window check passed: real worker processing, three PNG
  panels, experimental preset/report, save/manifest, progress window, no-face
  handling and corrupt-file stale-result clearing. Important controls fit the
  root's vertical bounds. `outputs/desktop_meeting_check_20261107_v2/verification.json`.
- Screen capture failed in the first GUI check; its output directory is retained.
  The second check explicitly disabled screenshots. No screenshot inspection or
  completed visual layout review is claimed. Rehearse on the meeting desktop.
- Briefing evidence links resolve and modified/new Python files parse. These
  checks do not establish scientific model quality or full-suite regression.

No fitting, sweep, data search, annotation task, scientific admission, new-model
adoption, publication, outreach, commit or push occurred. The provisional
November 28 completion planning target has low confidence and depends on model
results, integration and reviewer availability; reassess November 12.
