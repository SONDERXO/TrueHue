# Reviewed ten-source Table 2 comparison

28 October 2026. User accepts 51803 with concern **"a minor hole in the mask"**,
accepts 53109 and rejects 713 because it **"captures hair in mask"**, authorizing
the next step. Script 170 archives the exact statement against the reviewed
shortlist HTML, processing summary and qualitative-screen hashes. Earlier
reviews and all 21 other held sources from the batch remain unchanged.

Admitted only four new experimental pairs: identity plus the assigned medium
Table2 distortion for each accepted source. The 51803 concern remains on both
rows. Both 713 variants remain rejected; earlier 51739/40048/42532/63870
rejections remain excluded. No counterfactual severity probes enter fitting.

Combined cohort: ten source/known-duplicate groups, 20 pairs, ten held-group
folds. Each fold trains on 18 pairs from the other nine groups. Input features
remain distorted-input mean Lab, ITA and experimental mapped MST index. The
same depth3/seed42/minimumleaf1/unweighted recipe and zero-identity-harm gate
are frozen before fitting; no search or mask changes. Severity coverage is two
estimated light and eight medium sources, with no dark source group. Source
separation does not establish verified person separation.

| Fixed-reference-support mean CIEDE2000 | No correction | Held-source tree | Fitted oracle |
| --- | ---: | ---: | ---: |
| All 20 pairs | 10.577 | 9.643 | 4.775 |
| Ten distorted inputs | 21.154 | 13.797 | 9.550 |
| Ten unchanged inputs | 0.000 | 5.489 | 0.000 |

The overall-improvement gate now passes, but the unchanged-image gate fails.
Follow-up [matched-cohort design audit](table2-training-design-audit.md) finds
that the original 16 pairs worsen slightly, 10.729 to 10.794, under the expanded
folds. Comparing the old and new cohort means alone does not establish that
expansion improved the model on the earlier sources.
Seven clean controls are harmed: 53109, 22211, 62331, 84364, 75027, 51803 and
83205. Both newly accepted sources are among them. This is insufficient evidence
for model adoption. The photographic-reference oracle remains reference-informed
capacity, not learned performance. No calibrated skin-truth, all-MST-category
or independent final-validation claim follows.

All ten source boards were inspected. Strong over-lightening remains visible
on clean 62331/75027, while some other clean changes are subtler but still
nonzero. Distorted 51803/53109 show visible patch boundaries/over-lightening;
67583's distorted output stays dark. Numerical mean improvement does not hide
these failures. This inspection is not expert MOS or new source acceptance.

Script 171 independently reloads all ten saved models and portable exports,
checks all 20 predictions and fitting-leaf target means, reconstructs corrected
pixels using a separate RGB formula, recomputes metrics and gates, verifies
source/duplicate-group separation, preserves the 51803 concern, and checks all
five rejected source IDs plus the 21 retained holds. All checks pass. The latest
full suite remains 692 passed from the prior application-mask stage; no new
full-suite run is claimed for these script-only stages. Preliminary verifier-file
generation commands had PowerShell quoting errors and did not create a verifier;
the final explicit script 171 completed successfully and is the verification
evidence used here. The model run itself completed without a failed partial fit.

Do not launch another small expansion/refit, deepen the tree or relax the clean
gate in response to this result. The completed stage establishes that this
reviewed expansion alone does not resolve clean/distorted target confusion.
Preserve the results for thesis reporting and reassess the reference/feature and
training design before another learning experiment. The existing Table2 capacity,
clipping, weak MST and incomplete category coverage findings still apply.
No active runtime model, Android asset or old experiment was replaced. Android
remains paused; CPM remains deferred.

- [Exact user review](../outputs/table2_reviewed_ten_source_evaluation_v1/user_review.json)
- [Frozen cohort and folds](../outputs/table2_reviewed_ten_source_evaluation_v1/fit_plan.json)
- [Results](../outputs/table2_reviewed_ten_source_evaluation_v1/summary.json)
- [Independent verification](../outputs/table2_reviewed_ten_source_evaluation_v1/verification.json)
- [All ten comparison boards](../outputs/table2_reviewed_ten_source_evaluation_v1/review.html)
