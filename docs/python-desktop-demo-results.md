# Working Python desktop demonstration

30 October 2026 model follow-up: a matched direct-gamma regression candidate
reduces pooled error10.6%on the historical15-source cohort, but still changes
5/15clean photos and slightly worsens distorted-only error. It does not replace
this working demo preset. [Model comparison](direct-gamma-regression-results.md).

29 October 2026. Built a local Tkinter application with choose-photo/example,
run, original/skin-overlay/correction comparison, stage results, plain failure
messages, optional technical report and save-to-new-folder. Inference runs
sequentially on a worker so the window remains responsive. Unicode photo paths
decode from bytes. Old images/results and metrics are cleared on a new choice
or failed load; a failed pipeline cannot export a stale/partial correction.
Invalid masks are not shown as valid green skin selections.

The application runs the existing **five-feature experimental MST pipeline**:
face detection, original square256 skin measurement, ITA, experimental mapped
MST, a saved portable decision tree, gamma/red/blue correction on selected
support. The preset is fixed baseline5/fold1; it is not selected from the user's
outputs. The example is an already-exposed53109distorted input held out by that
saved fold. This is a reproducibility example, not independent model evaluation.

This preset previously failed its correction quality gate. The app visibly
says it is a trial model whose results may be wrong; JSON retains the
experimental flags and quality_gate_passed=false. It does not silently activate
the rejected/new YCrCb/contour candidates, transfer their measurement pixels to
an incompatible lookup, train a new model or reinterpret old gamma targets.
The older model and mapping have matching measurement provenance; matching
software contracts do not establish scientific validity. Only face support
is corrected; neck and Android integration remain unfinished.

The launcher opens a desktop window without requiring a web server, browser,
new account or dependency install. Windows DPI awareness and screen-bounded
layout avoid cut-off controls. Technical details open in a separate scrollable
window rather than pushing controls below the screen. Save creates a unique
folder containing the model-used square image, valid skin overlay/mask,
experimental correction if available, and full report/provenance. Original
photo bytes and all active assets stay unchanged. No network calls are needed.

## Verification

- Actual end-to-end smoke test: example produces a development output;31367
  fails face detection with a plain message and no corrected export.
- Actual Tk-window/worker test: select example, run inference, open report,
  select a corrupt file (old result cleared), then run the no-face image.
  Success/failure screenshots inspected; the revised window fits the screen.
- Five service tests cover corrupt decoding, distinct face-error messages,
  stale/partial-result suppression, overlay/export integrity and invalid-mask
  suppression. The full suite passed **773 tests in13.65seconds**.

The screenshot and integration checks establish a working demonstration,
not improved correction quality or a thesis-complete model. The next model
work can use this stable interface to inspect future supported candidates
without restarting mask-review tooling or replacing the active preset silently.

- [Simple instructions](simple-python-demo.md)
- [Launcher](../run_truehue_demo.cmd)
- [Successful GUI screenshot](../outputs/python_demo_window_check_v3/success.png)
- [Failure GUI screenshot](../outputs/python_demo_window_check_v3/failure.png)
- [Actual GUI verification](../outputs/python_demo_window_check_v3/summary.json)
- [Headless pipeline check](../outputs/python_demo_smoke_v1/summary.json)
