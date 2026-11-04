# Desktop demo flow checks — 31 October 2026

Exercised the existing desktop application with real Tk widgets in a withdrawn
window and controlled inference/dialog responses. This verifies event handling
and state transitions, not human visual layout or new correction accuracy.

| Flow | Observed behavior |
|---|---|
| Choose a valid photo | Run enables; selected-photo preview is populated |
| Run and display a successful controlled result | Three image panels populated, trial MST/ITA text shown, save enables |
| Save a successful result | New folder, report and correction saved; source bytes unchanged |
| Select a corrupt file after success | Previous run, metrics and stages cleared; run/save disabled |
| Process a no-face failure | Specific message; partial correction discarded; failure report can be saved |
| Cancel save | No export folder created |
| Save to an invalid destination | Error shown; result retained and a valid-location retry succeeds |
| Failed-result export | Report present, no stale/partial correction image |

One usability issue was fixed: starting a new run now clears the previous
technical report immediately, so it cannot be mistaken for the processing
photo's report. Correction code, model selection, masks, lookup and tree
parameters are unchanged. The main demo remains baseline5/fold1.

Tests live in `tests/test_demo_desktop.py` and the existing service suite. The
focused run passed8 tests in4.98seconds. The full suite passed **836 tests in
28.36seconds**, cache disabled. JUnit evidence is recorded in
`outputs/demo_flow_verification_20261031_v1/tests.xml`.
Tests use synthetic images and explicit controlled pipeline outputs, without
training, reserved photos, network calls or empirical model claims. File dialogs
and error popups are intercepted, so no user interaction is required.

Visual inspection on the user's screen, native file-dialog appearance and
accessibility are not covered by these withdrawn-window checks. The previous
known-example headless real-model smoke remains documented in
[the reporting update](demo-reporting-update-2026-10-30.md); no extra real-model
quality trial was run for this UI check.
