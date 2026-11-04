# Why acceptable images receive unwanted correction

24 October 2026. Replayed the existing models without retraining, changing thresholds or replacing the runtime model.

The current tree sometimes mistakes naturally different facial measurements for an artificial exposure or color problem. Adding nine pairs changed its branches, but did not solve that distinction.

- All eight unchanged probes receive unwanted correction with both models.
- Mild probes worse than leaving the input alone increased from two of eight to five of eight.
- Eight of the sixteen unchanged/mild probes became worse than the original22 model.
- Fourteen of sixteen controls are inside each individual training-feature range in both methods. Being inside those ranges does not establish joint feature coverage or reliable correction.

## Concrete traces

| Held source and probe | Original error | Expanded error | Expanded training leaf |
|---|---:|---:|---|
| 51739, mild | 1.02 | 15.19 | Darkened variants of6236 and84897 |
| 62331, mild | 0.74 | 8.18 | Color-shifted variants of14272,75027 and84897 |
| 75027, unchanged | 13.31 | 13.31 | Darkened variants of14272,51739 and62331 |

Lower error is better. These leaves have consistent targets for the wrong distortion, so their mistakes are not caused solely by averaging incompatible targets. For51739 mild, the nearest training example under the diagnostic distance is84897 unchanged, yet the tree sends it to the dark-only leaf. For75027 mild, the nearest is22211 unchanged while its leaf contains darkened examples. This demonstrates disagreement between the tree partition and this particular distance; it does not validate nearest-neighbor correction.

Other leaves mix different targets: eight of sixteen expanded control predictions and eleven of sixteen original control predictions come from such leaves. Their output is the mean training target, which can introduce an unwanted intermediate correction. Each prediction was verified against its actual leaf-target mean, and the exact split path is saved.

## Interpretation and next experiment

There is evidence of coarse tree partitions as well as limited feature coverage. The four inputs summarize average facial color; they do not explicitly separate original complexion from lighting. This diagnosis does not prove that these features are inherently insufficient or that another model will succeed. It also does not justify discarding the new sources.

Recommended next: one fixed tree-capacity diagnostic on the same31 pairs and eight folds, comparing the current depth3 tree with an unrestricted-depth tree (same seed, leaf minimum and other settings). Report training fit and source-held-out results, unchanged/mild controls, original22/new9 and each distortion separately. Do not search for a winning depth or adopt the unrestricted tree automatically. Better training fit with worse held-source results would indicate memorization; consistent control improvement would support revisiting the tree capacity. If failures persist, plan richer input-only measurements before collecting another similar batch. This recommendation is a pending experiment, not a result.

No final model was fitted or promoted, no external/reserved images were used, and no human review labels changed. Face-and-neck support remains pending. Continuous ITA without operational MST and the exploratory data selection remain recorded proposal distinctions.

## Evidence and limits

All32 control predictions (16 per method) replay exactly. Source, duplicate-group and pair separation were checked in every fold; every fitted model, input table and prior summary retained its hash. The diagnostic fits no model. Nearest-example distances use standard deviations from the fitting fold only, with no similarity cutoff; ITA and Lab measurements are correlated. Small selected development sources do not establish subject independence, calibrated color accuracy or final performance.

[Full traces, split paths and nearest examples](../outputs/expansion_control_diagnosis_v1/summary.json) ? [Prior image comparisons](../outputs/development_expansion_sourcecv_v1/review-index.md)

Verification after the diagnostic: **464 tests passed**.

Completed follow-up: [fixed capacity comparison](tree-capacity-comparison.md). Extra depth overfit this cohort.
