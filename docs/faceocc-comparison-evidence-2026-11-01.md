# Evidence for considering a FaceOcc measurement-veto change

1November2026. User requested a saved comparison with the previous model for
defending a possible method change. Script371 packages the already frozen
diagnostic evidence; no new source selection, predictions, tuning or fitting.

## Exact comparison

Previous method: current preferred19-class parser skin/nose measurement with
anatomical exclusions and nostril guard, contract1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7.

Candidate: that SAME measurement mask intersected with inverse-mapped FaceOcc
visible-face prediction, contract03307d45c74807a4d85a534b826ee069807e20a0bb669c6faff4c8f934c69bc8.
The fixed MediaPipe/template preprocessing adaptation and additional model are
both part of this candidate. The parser, ITA equation and correction model are
not replaced. This is not a new comparison against the original paper's
HSV/YCrCb-only method; no results for that baseline are inferred.

| Same frozen evidence | Previous method | With FaceOcc veto |
|---|---:|---:|
| Measurement availability, all25attempts | 17/25 | 17/25 |
| Original failures retained | 8 | 8 |
| Premarked non-skin points still selected | 4/4 | 1/4 |
| Premarked skin points retained | 2/2 | 2/2 |
| Selected pixels summed across17images | 85,550 | 74,712 |

Median parent-selection retention is95.44%. The10,838removed pixels are not
automatically non-skin, and retention is not true-skin recall. The sparse marks
were assistant diagnostic observations frozen before FaceOcc predictions, not
expert labels or dense actual-skin annotations. Do not turn4-to-1marks into a
general75%accuracy/error-reduction claim. All25rows and four-subject denominators
are saved; no failure or unfavourable case was removed.

## Supported reason for further evaluation

The candidate removes the flagged neck/garment pixels in case4 and worn-covering
point in case14 while retaining both premarked skin points. The paired images
show how an explicit visible-face veto can address non-skin selections that
the existing skin parser/anatomical rules miss. This supports investigating
the component, without a threshold or face-outline sweep.

## Limits that must accompany a defence

The marked beard pixel in case10 remains. Glasses-specific improvement is not
established in this sample. Hairline/boundary skin loss is visible in some cases.
No dense-mask accuracy, statistical significance, independent subject validation,
paired MST-category accuracy, intrinsic-colour recovery, correction-quality
improvement or Android runtime cost was established. ITA shifts are saved only
as feature sensitivity, not an improvement metric. These are exposed development
photos of four subjects and do not validate ten-category coverage.

Adding FaceOcc incurs model/alignment complexity. The fixed MediaPipe bridge is
a TrueHue adaptation, not the original3DDFApreparation. Correction masks and
rendering remain byte-identical. No MST lookup export, correction training,
deployment or final adoption is justified automatically by this report.

## Wording available for a future request letter

“We propose evaluating an additional pretrained visible-face/occlusion mask
within the skin-measurement stage while retaining ITA, calibrated MST, facial
statistics and decision-tree correction. In a fixed exposed development
diagnostic, the added mask removed marked neck/clothing and face-covering
contamination without losing either of two marked skin points or reducing
technical availability. Beard contamination and broader measurement validity
remain unresolved; the component is not yet adopted or independently validated.”

This is suggested factual wording, not a submitted letter, panel approval or
proof of superiority. Verify original-paper sections/pages before finalising
an amendment. The wider change from rule-based masking to learned parsing is
separately tracked in panel-change-register.md; do not conflate its evidence
with this incremental veto comparison.

## Saved package and verification

- outputs/faceocc_comparison_evidence_v1/comparison.html: three-panel paired
  gallery (original, previous measurement, combined candidate), all25attempts.
- paired_results.csv: per-image statuses, failures, pixels, retention, old/new
  ITA and signed ITA change. No reference label enters mask computation.
- diagnostic_marks.csv: exact sparse coordinates, category and selected states.
- subject_results.csv: all four subject denominators and median retention.
- comparison.json: aggregate values, exact contracts and claim limitations.
- evidence_hashes.json: source/report artifact hashes for reproducibility.

Script371 independently recomputed saved old/new Lab/ITA statistics and pixel
counts, checked exact25membership and candidate-mask hashes, and verified all
frozen model-diagnostic input hashes unchanged. It refuses overwrite. No pipeline
code changed; pytest not rerun for evidence packaging. Last broader result:
903passed/12.19s excluding desktop GUI(Tcl/Tk unavailable), not a full-suite pass.
