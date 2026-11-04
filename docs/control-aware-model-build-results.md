# Control-aware model build: reproducible, quality held

28 October2026. User prioritized the Python model and paused Android. Built
one control-aware decision-tree artifact from the existing fixed recipe,
without admitting the unresolved expanded cohort or changing the active model.

## What was built

Exactly22historically development-eligible pairs from six FairFace sources;
8held pair IDs never fit. Native224/current-core measurements, four input-only
Lab/ITA features, gamma/red/blue inverse targets. Depth3, seed42, leaf1,
unweighted, no scaling. One full-data development fit and zero new CV fits.
The resulting tree has6leaves. Known source/duplicate groups are preserved;
subject identity separation is not established.

- [Model metadata](../outputs/control_aware_model_build_v1/metadata.json).
- [Frozen fitting manifest](../outputs/control_aware_model_build_v1/fit_manifest.json).
- [Joblib model](../outputs/control_aware_model_build_v1/decision_tree.joblib):2129bytes,
  SHA256`28c49d4386f2d0b2926593432735cbc195964219625ed7ed3f4c7cff5a64098e`.
- [Portable JSON](../outputs/control_aware_model_build_v1/decision_tree.json):3501bytes.
- [Build/provenance report](../outputs/control_aware_model_build_v1/build_report.json).

The [pre-fit protocol](control-aware-model-build-protocol.md) fixes the entire
recipe. The all22fit is the artifact form of a previously evaluated recipe;
it is not a new scientific comparison or evidence that training now generalizes.
The22-ID gate remains historical exploratory eligibility, not new final cohort
or native-mask-quality approval.

## Quality decision

The pre-existing, source-held-out comparison remains the relevant recipe test:

| Method | Pair mean CIEDE2000 | Equal-source mean |
| --- | ---: | ---: |
| No correction | 5.129 | 4.746 |
| Control-aware recipe | 6.865 | 6.774 |

It worsens6/6unchanged and2/6mild primary controls. The build therefore records
`held_quality_failure`. No default configuration, active joblib model or Android
asset was replaced. A conservative numerical gate is an artifact-activation
check, not a new prediction-time no-op rule or proof of statistical significance.
Even passing it would not establish final thesis readiness.

## Actual image replay

A [separately declared frozen replay](control-aware-model-evaluation-protocol.md)
applies the one candidate to all38existing core attempts with exactly the saved
input application masks and source scoring masks.37outputs are available;
the original measurement failure stays failed. No new image/source or mask.

| Separate diagnostic cohort | Available | Sources | No correction | Candidate | Original runtime |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eligible, seen-source/all-row fit | 22 | 6 | 5.129 | 2.807 | 6.294 |
| Held IDs, training-source diagnostics | 8 | 4 | 8.866 | 7.524 | 7.021 |
| External development, previously exposed | 3 | 1 | 10.666 | 10.913 | 7.609 |
| Clipped stress | 4 | 4 | 7.227 | 11.311 | 13.916 |

All entries are source-mask CIEDE2000; lower is better. Do not aggregate these
cohorts or compare the seen-source2.807against held-source6.865as an improvement.
Even fitted unchanged controls all remain altered (6/6,mean3.096); fitted mild
probes improve but do not rescue generalization. External development covers
only one already exposed source, not a fresh final test.

[Image gallery](../outputs/control_aware_candidate_replay_v1/review.html) ·
[Exact replay records](../outputs/control_aware_candidate_replay_v1/summary.json) ·
[Independent verification](../outputs/control_aware_candidate_replay_v1/verification.json).

All eight source boards were inspected. Visible patch boundaries/holes and
wrong-tone regions remain, notably22211/22454/6236and clipped51739. These are
observations on the unchanged legacy support and new predictions, not new
segmentation labels or a reversal of any prior source/pair acceptance or hold.
The gallery does not show calibrated neutral-color ground truth.

## Verification and use

The data contract rejects invalid partition/routing, clipping, duplicate/group
inconsistency, nonfinite features and inverse-target mismatch. Saved evaluation
IDs, folds, exact features/targets and hashes are checked before fitting.
Joblib reload and portable JSON match all30probes and20split-boundary witnesses.
Isolated `-I -S` prediction needs no NumPy/sklearn. Independent arithmetic checks
22inverse targets, actual membership/means of all6leaves, the quality gate from
individual held-source predictions,37pixel transforms and image metrics,
outside-mask invariance, the original failure and original model/asset hashes.
**574Python tests pass in25.37s**, including19new training-contract/gate tests.

Reproduce into a fresh directory (one explicitly bounded development fit):

```powershell
.\venv\Scripts\python.exe scripts/134_build_control_aware_model.py --output-dir outputs/control_aware_model_build_v2
.\venv\Scripts\python.exe -I -S scripts/114_predict_portable_tree.py --tree outputs/control_aware_model_build_v2/decision_tree.json --features-file outputs/control_aware_model_build_v2/sample_features.json
```

Scripts135/136 replay and independently verify the canonicalV1build without
additional fits. Training error in metadata is explicitly in-sample. No raw
data/model binaries were committed or uploaded.

## What remains before a final model

The training/export/verification path now exists; data and method validity are
the remaining bottlenecks. Do not substitute another depth/feature/cutoff sweep
on these same cases for resolving them. The32regenerated candidates still need
a consistent accepted processing recipe and relevant quality concerns resolved
before admission. Photographic inverse-transform targets support reconstruction
research, not calibrated intrinsic complexion claims.

The paper's MST-conditioned method remains unresolved: continuous ITA/Lab is
the current development implementation and no validated operational MST rule
exists. Adviser-approved changes must be actual decisions, not inferred from
deadline pressure. User was asked which method is required. Preserve the
proposal baseline until answered. Final FairFace/SCIN roles,256processing,
tone-dependent distortion requirements, source/subject splits, mask/neck scope,
independent evaluation and expert MOS remain explicit unfinished requirements.
Android remains on hold; CPM stays deferred and paint/makeup remains a limitation.
