# Deeper correction-tree comparison

30 October 2026. Increasing tree depth from 3 to 5 recovered some distorted
correction, but increased unwanted clean-photo changes from two to eight.
Reject this candidate and retain the current demo and prior research baseline.

The [protocol](clean-control-tree-depth-protocol.md) fixed both depths before
training. Everything else stays matched: the approved historical 30 pairs plus
eleven admitted clean originals, five Lab/ITA/experimental-MST input features,
direct gamma/R/B regression targets, seed 42, minimum leaf size 1 and
fitting-control leaf protection. This is an engineering capacity comparison,
not a claimed setting from the proposal. All 26 source/known duplicate groups
are held out in turn, with both variants of a historical source held together.

Lower CIEDE2000 is better. Changing an image does not itself establish benefit.

| Measure | Depth 3 | Depth 5 | No correction |
|---|---:|---:|---:|
| Historical 30-pair error | 8.091 | 8.471 | 10.076 |
| Historical distorted 15 error | 16.181 | 14.196 | 20.153 |
| Historical clean changed /15 | 0 | 2 | 0 |
| Additional clean changed /11 | 2 | 6 | 0 |
| Combined 41-pair error | 7.314 | 9.382 | 7.373 |
| Historical distorted changed /15 | 7 | 9 | 0 |

The deeper candidate worsens combined error by about 28% against depth 3 and
also loses to leaving all inputs unchanged. Neither method passes the unchanged
clean-photo requirement. The earlier historical-only protected tree remains a
separate stronger research baseline on its original 30 pairs (7.132); it was
not replaced or confused with this augmented depth-3 comparator.

Depth-5 held clean failures are 68453, 75027, 29880, 56839, 62105, 68073,
75898 and 85815. Depth 3 still fails 29880 and 68073. Exact tree paths and
the fitting members of each reached leaf are saved in
`outputs/clean_control_tree_depth_v1/clean_failure_routes.json`. All ten failure
occurrences across both methods reach leaves containing distorted fitting
examples only. Fitting-control leaf protection works as specified but provides
no safety guarantee when a new clean face routes into such a leaf. The deeper
tree creates more opportunities for that separation to fail on unseen sources.

`scripts/256_compare_clean_control_tree_depth.py --verify` passes 52 independent
raw-tree refits, reconstruction of protected values and exact fitting membership,
82 saved output pixel/metric replays, source separation, unchanged outside-mask
pixels, aggregate/gate consistency and exact reproduction of the preceding
depth-3 predictions. `scripts/257_report_clean_control_routes.py` checks all ten
failure routes and their fitting-only members. Verification and SHA256 records
are saved in the output folder. No core library changed; the last full core
suite remains 780 passing tests, not a new test-suite run for this experiment.

No new source, mask, target, calibration, reserved evaluation data or review
decision was added. Existing mask concerns, clipped synthetic targets, weak MST
calibration, limited tone coverage and historical development exposure remain.
The demo is unchanged; this does not establish final thesis accuracy.

Further depth searching on these same exposed sources is not justified by this
result. The next training design needs to address overlap between naturally
clean facial statistics and synthetic distorted statistics, while preserving
the paper's ITA/MST/tree method. Any new feature, augmentation or independent
evaluation must have its own recorded rationale and source/mask eligibility;
do not add per-image exceptions or claim that more depth solves the problem.
