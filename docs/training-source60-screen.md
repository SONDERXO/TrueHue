# Fixed60-source screening results

24 October 2026. Screened the exact predeclared60 TRAIN sources without replacement. **15 are promising for variant checks;45 remain held. None are admitted to training.** No distortions or correction models were generated.

All60 passed current numerical face/landmark/mask processing and provided the fixed brightness measurements. Codex inspected all60 input/estimation/hair-clean previews across12 boards. Numerical success did not guarantee representative facial support: held cases include blur, eyewear/foreground occlusions, facial-hair contamination, fragmented masks and uncertain existing lighting/cosmetics.

The15 follow-up candidates are:

51446, 83205, 42532, 84364, 7994, 69531, 56444, 55007, 31154, 67454, 40048, 67583, 47217, 60162, 63870.

These have broad visible facial support and are provisional photographic reconstruction references only. Pose, hairline, lighting and jaw-boundary caveats remain; do not treat their source colors as calibrated truth. Their status does not overwrite pending human review or final eligibility. No source was assessed using model predictions.

Each of all60 records separately stores numerical status, reference suitability, baseline-measurement concerns and correction-region status. Experimental correction support has not yet been generated or reviewed for this batch. All45 holds retain individual reasons; they are not deleted or replaced. The15/60 follow-up yield describes this selected batch, not a population acceptance rate or a final accepted sample size.

## Verification

The exact fixed list and original five fold assignments were preserved. Exposures were appended before raw-image reading; previous54 ledger records are unchanged and60 new records bring the total to114.170 candidates remain under the current unused-training filter. All60 saved input statistics and brightness measurements were independently recomputed; original artifact/model/schema hashes stayed unchanged. No reserved/external-development source was opened.

Promising sources per planned fold:4,4,2,4,1. This is not a robustly balanced final evaluation cohort. The fifth fold has only one follow-up source; variant failures could leave a fold empty. Preserve the assignments and report insufficient coverage if that happens, rather than silently resampling or changing folds.

## Next step

Attempt the same five variants for all15 follow-up sources, including unchanged and mild controls:75 planned attempts. Keep the ten-feature schema, existing masks, transform settings and exploratory coverage screens fixed. Preserve every failed or clipped case, check source duplicates before staging, and freeze all variant dispositions before fitting. No further replacement source selection is implied.

Do not fit now:15 provisional sources still require variant and correction-region checks, and the planned five-fold structure may prove insufficient. Broader screening has exposed a data/segmentation-quality bottleneck; it has not established that a larger cohort will solve overcorrection. The original31/39 artifacts and runtime model remain unchanged.

**464 tests passed.** Operational MST, face-and-neck support, final reference/data eligibility, Android completion and expert/final evaluation remain pending. The selection, ten-feature schema and proposed source-weighted development analysis remain recorded method distinctions, not a proposal amendment.

[All12 review boards](../outputs/training_source60_screen_v1/review-index.md) | [All60 dispositions](../data/manifests/training_source60_screen_v1/source_dispositions.json) | [Verification](../outputs/training_source60_screen_v1/verification.json) | [Predeclared protocol](../data/manifests/training_design_checkpoint_v1/proposed_protocol.json)

Follow-up: [completed75 variants and user review](training-source60-variant-checks.md).
