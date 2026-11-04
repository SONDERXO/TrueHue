# Mask versus parameter diagnosis — 23 October 2026

Follow-up: [training and tree audit](training-tree-audit.md) traces the wrong
brightness adjustments to missing exposure coverage and mixed-target leaves.

**Prediction errors are the main remaining problem on the one-source development
validation and bright stress cases. Some training examples still have severe
mask failures.** The transform/inverse itself reconstructs closely when given
both known parameters and the original generation mask. No model was improved
or retrained by this diagnostic.

## Fixed comparison

The current `material_hair_veto_v1` masks and tree predictions were loaded from
the completed integration run, without rerunning inference. Each successful pair
was evaluated with four combinations: tree or known parameters, applied on the
current or source-generation mask. The saved input was verified pixel-for-pixel
against its recorded synthetic distortion; inverse targets and clipping counts
were checked. No correction was retained as a baseline.

Known parameters and source masks are **oracle diagnostic information**, not
available inference features. The source region is synthetic generation support,
not human skin segmentation truth. Source-mask variants are not exposed through
the correction command and must not become a way to bypass paint/hair handling.

All24 prior attempts were accounted for:23 diagnosed and one original excluded
input preserved. Results remain separated into16 training reconstructions, three
development variants of one source, and four nonindependent clipped stress pairs.

## Mean color difference, lower is better

| Method | Training:16 | Development:3 | Clipped stress:4 |
| --- | ---: | ---: | ---: |
| No correction | 10.284 | 10.666 | 7.227 |
| Tree parameters, current mask | 5.484 | 6.643 | 13.741 |
| Known parameters, same current mask | 2.545 | 0.832 | 0.417 |
| Tree parameters, source-mask oracle | 4.185 | 6.302 | 14.036 |
| Known parameters, source-mask oracle | 0.096 | 0.073 | 0.107 |

Changing parameters alone sharply reduces validation and stress error. Changing
only the mask to the source mask leaves the tree's validation error high and
slightly worsens stress error. This rules out treating those large stress errors
as a mask-only problem. Residual oracle errors reflect quantization and clipping;
no calibrated physical skin-color accuracy is inferred.

For example, bright/warm51739 and6236 need inverse gamma0.8, but the frozen tree
predicts1.4286. Under the implemented transform it brightens those images when
they need darkening. The known-parameter/current-mask images remove most of this
overcorrection without changing where the correction is applied.

## Remaining mask failures

Known parameters still leave color error13.617 in22454/dark and8.261 in
12288/color-shift. Their current masks miss26,230 and21,541 pixels respectively
from the original generation support. Source-mask oracles largely remove the
residual, consistent with their visible uncorrected facial regions.

Color-shift62331 also retains known/current error3.928. These cases must stay
flagged in development diagnostics; this run does not silently remove them from
training or change earlier human decisions. An input-only quality rule would
need separate validation; oracle overlap must not be used during deployment.

Region tables distinguish shared support, missed source support, extra current
support and neither. Error on shared pixels is identical between current/source
masks with the same parameters. Missed regions remain unchanged by both current-
mask corrections; extra regions reveal edits outside the generation area.

The factorial gaps preserve signed differences and interactions. Stress mask
gap at tree parameters is negative: applying a wrong correction to fewer pixels
can look better numerically. Do not convert these gaps into independent causal
percentages or optimize the mask solely to hide a bad prediction.

## Visual review and artifacts

Source19/color-shift factorial image and source boards22454,51739,12288 and62331
were visually inspected. Known parameters remove the bright overcorrection on
51739 but leave the lower-face-only correction on22454/dark and the large cheek
patch on12288/color-shift. These observations agree with the numerical diagnosis.
Other pairs were checked numerically; no expert aesthetic rating was collected.

Open [the diagnostic image index](../outputs/mask_parameter_diagnosis_v1/review-index.md).
Source boards show reference / input / tree-current / known-current / known-source
oracle. Per-pair three-by-three grids additionally show tree-source and both masks.

Reproduce from the project root:

```text
venv/Scripts/python.exe scripts/42_diagnose_mask_vs_parameters.py
venv/Scripts/python.exe scripts/43_make_error_diagnosis_boards.py
```

Outputs are in `outputs/mask_parameter_diagnosis_v1/`:115 image-metric rows,
460 region rows,23 signed factorial comparisons, all24 attempts, parameter
provenance, diagnostic images, hashes and a completed status file. Existing
artifacts are protected from overwrite.

439 tests passed, including a synthetic case isolating missed and extra support,
empty-region handling, mask validation and preservation of signed interactions.
All saved tree/current images reproduced the integrated outputs exactly. Known
inverse targets, exact synthetic-input generation, clipping provenance, weighted
region/source score agreement and original run input hashes were verified.

## Recommended next work

Audit the training variation and tree split behavior behind the wrong-direction
exposure predictions before changing model size or collecting another review
batch. Keep the correction mask fixed for that learning comparison, with the
identified mask-limited cases explicitly flagged. Resolve input-quality handling
before expansion; do not treat the current masks as universally solved.

These are diagnostics on previously exposed development/training examples.
The0.832 result is from known synthetic parameters, not a new learned-model
score. No final-test evaluation, source expansion, feature change, MST lookup,
human-label reinterpretation, model fitting or approved thesis change occurred.
