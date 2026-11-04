# Monotone square256 mapping: experimental progress

28October2026. User explicitly confirmed adviser approval of the limited scope.
Recorded as user-reported confirmation. Executed the separately frozen
[protocol](mst-monotone-square256-protocol.md): one decreasing isotonic recipe,
equal fitting-subject total weights,15held-subject fits, no parameter search.
This reuses a historical mapping method on the fixed256measurement contract;
it is not an independent algorithm-discovery experiment.

| Held-subject metric | Monotone mapping | Same-row median baseline |
| --- | ---: | ---: |
| Image-weighted ordinalMAE | 2.222 | 2.838 |
| Equal-subject ordinalMAE | 2.306 | 3.000 |
| Exact-category accuracy | 11.11% | 14.39% |
| Within-one accuracy | 33.84% | 22.22% |
| Support-qualified equal-subjectMAE | 2.266 | 3.200 |

396predictions,15subjects,22processing failures retained.180measured images
lack same-category fitting-subject support, as previously documented. The
support-qualified subset is216images/10subjects. Both predeclared ordinalMAE
checks pass, but exact-category accuracy is worse than baseline and overall
accuracy remains weak. No final validated mapping is claimed.

Recorded poorly-lit155images have6.45%exact accuracy/2.271imageMAE; well-lit240
images14.17%/2.188. Onevideo-labeled frame is retained separately. Different
subject composition and capture factors preclude a causal lighting comparison.

## Artifact and input-only integration

Saved15fold knot sets and predictions. After the development checks passed,
one all396image fit produced23knots in an explicitly experimental portable
artifact. Its actual label range is1–9: **MST10is not emitted**. Do not force
the endpoint or claim complete ten-category output coverage. This schema is
intentionally separate from the earlier validated-lookup interface; no passing
validation declaration was fabricated.

[Evaluation/predictions](../outputs/mst_monotone_square256_v1/summary.json) ·
[Experimental knot artifact](../outputs/mst_monotone_square256_v1/development_lookup.json) ·
[Portable parity](../outputs/mst_monotone_square256_v1/artifact_verification.json).

`DevelopmentMonotoneLookup` performs standard-library linear interpolation,
endpoint clipping and explicit half-up label rounding.443training/knot/midpoint/
endpoint vectors match sklearn.15newtests cover boundaries, rounding, immutable
knots, numeric/schema/order rejection. **635tests pass in12.81s.**

Script149now executes an actual input-only256measurement→ITA→experimentalMST
report. A known existing source reproduces its saved four measurements exactly
and adds the mapped0–9MSTindex as a fifth feature. It reports experimental
status, contract/model hashes and proposal_complete=false. No source/reference
label or target enters inference. No correction is applied or model replaced.

```powershell
.\venv\Scripts\python.exe scripts/149_measure_development_mst.py --image path/to/image.jpg --output-dir outputs/new_mst_case
```

Use known development images during implementation; opening reserved/new images
requires the proper selection/exposure record. Existing smoke evidence:
[input-only report](../outputs/mst_monotone_input_smoke_v1/report.json).

## Next boundary

This establishes executable MST feature construction under a disclosed limited
scope, not final correction training readiness. Downstream correction data must
use this exact256contract; native224features cannot be joined to the lookup as
if equivalent. Existing256regenerated pairs retain unresolved eligibility and
different policies. Final tone-dependent generation also requires explicit
group boundaries and a transform/target policy consistent with the paper.

Before promoting this mapping, review whether weak exact accuracy and absent
MST10output are acceptable only for an experimental correction comparison.
Limited evaluation approval does not waive those limitations or authorize a
production claim. No further calibration-method sweep, arbitrary output fixes,
source admission or corrected-image quality claim follows. Original masks,
reviews, failed recipes and runtime remain; Android paused, CPM deferred.
