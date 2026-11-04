# Proposed39-pair development stage

24 October 2026. Staged eight proposed additions alongside the existing31 pairs, spanning ten source images. No models were fitted. The runtime model and master source eligibility/human review records are unchanged.

Added62676's five fixed variants and6356's bright/warm, unchanged and mild variants.6356 dark/color remain held for mask coverage loss. All ten screening attempts are preserved in `all_ten_attempts.json`; previous exclusions remain excluded. These are development proposals, not final dataset approval.

The first31 manifest rows retain their original field values. A separate39-row ten-feature table follows the frozen schema byte-for-byte; all39 baseline Lab/ITA and brightness measurements were recomputed from their actual saved inputs/estimation masks. Inverse targets, generation recipes and clipping were checked; all staged pairs are unclipped TRAIN rows. No reference values, labels or source IDs enter the feature extractor.

Exact decoded-image hashes and dHash comparisons (distance at most4) across ten raw sources found no duplicate candidates. This is not an identity check or proof of independent subjects. Retain source/duplicate grouping and all variants together.

Prepared ten fold plans with source, pair and duplicate-group separation; every row appears once in held-source probes. The original31 fitting subset is nonempty in every fold. Verified39x10 features and39x3 targets, unchanged original artifacts and tables, and explicit held-case exclusions. **464 tests passed**.

Next fixed comparison: for each held source, train one depth3 tree on remaining original31 rows and another on remaining39, using the same frozen ten features, seed42 and leaf minimum1. Evaluate both plus no correction on the same39 held-source probes, separately report shared31/new8, unchanged/mild controls, each distortion and equal-source means. No depth/feature search or automatic runtime adoption. The repeated selected development cohort is not a final holdout.

Temple/side-lighting and pose/jaw boundary caveats remain. Face-and-neck correction, operational MST and final dataset/evaluation requirements remain unfinished; proposal-method distinctions continue in the alignment document.

[Staged manifest](../data/manifests/controlled_expansion39_v1/staged_train.csv) | [Ten-feature table](../data/manifests/controlled_expansion39_v1/input_features.csv) | [Frozen comparison plan](../data/manifests/controlled_expansion39_v1/comparison_plan.json) | [Readiness checks](../outputs/controlled_expansion39_v1/readiness_checks.json) | [Candidate previews](../outputs/controlled_expansion39_v1/review-index.md)

Completed follow-up: [fixed31-versus39 comparison](development39-comparison.md). Expansion did not improve the model overall.
