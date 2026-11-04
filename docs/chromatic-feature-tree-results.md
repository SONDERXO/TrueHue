# Facial color-distribution features and next training-data step

30 October 2026. Four input-only facial chromatic statistics were implemented
and tested: masked a* median/IQR and b* median/IQR. In the fixed comparison,
they slightly improve distorted correction but add another held clean failure.
They are not activated in the demo. ITA, experimental MST, ordinary direct
gamma/R/B targets, depth 3 and fitting-control protection remain unchanged.

The [protocol](chromatic-feature-tree-protocol.md) declared this single feature
extension before fitting, using the existing 41 pairs and 26 source-held folds.
There was no subset or percentile search. All additional statistics use only
pixels in the original input mask; no reference measurements enter features.

| Measure | Existing five features | Nine features | No correction |
|---|---:|---:|---:|
| Historical 30-pair CIEDE2000 | 8.091 | 7.681 | 10.076 |
| Distorted 15 CIEDE2000 | 16.181 | 15.362 | 20.153 |
| Historical clean changed /15 | 0 | 0 | 0 |
| Additional clean changed /11 | 2 | 3 | 0 |
| Combined 41 CIEDE2000 | 7.314 | 7.749 | 7.373 |

Lower error is better. New clean failure 75898 joins 29880 and 68073. Both
procedures fail the zero-held-clean-change requirement; the nine-feature
candidate also loses to unchanged inputs on combined error. These repeatedly
exposed development cases are not final validation. The stronger historical-only
protected research baseline remains separate from this augmented comparator.

Four new tests cover known channel distributions/units, invariance outside the
mask, constant-color spread/no mutation and support/dtype contracts. The full
suite passes **790 tests in 13.01 seconds**, cache provider disabled.
`scripts/262_compare_chromatic_features.py --verify` independently reconstructs
all 41 feature vectors using sorted-sample linear interpolation, refits 52
trees, verifies protected membership/source separation, replays 82 output
images/metrics and reproduces the five-feature parent exactly. Evidence:
`outputs/chromatic_feature_tree_v1/verification.json`.

## Focused next step: eleven missing distorted-mask decisions

Further small feature/depth searches on these same sources are yielding limited
benefit. The eleven additional clean originals have accepted original-reference
masks, but their existing distorted masks have not been approved. Preparing
those exact distorted-mask checks is a concrete route to paired training
coverage; it does not require finding or reviewing another large photo batch.

`scripts/263_prepare_distorted_mask_review11.py` prepares
`outputs/distorted_mask_review11_v1/review.html`: eleven items, three panels
(original photo, existing distorted photo, distorted green mask), explicit
accept/reject/unsure, notes, navigation, browser saving and JSON download.
No decision is preselected. The export includes the exact manifest SHA256 and
review scope. Notes and choices stay separate from prior reference approvals.

All original saved input/image/mask hashes are checked against the preparation
verification, and all eleven existing measurements and approximate target fits
are available. These are the original Table-2 composite inputs, not the newer
three-variant or YCrCb candidates. Existing clipping and synthetic-recipe limits
remain. Reference approval does not approve a distorted mask, and a new mask
acceptance will still require technical/role/lineage checks before fitting.
No training eligibility was granted by preparing the page.

Visually inspected the generated 85815 comparison board. Live browser interaction
could not be tested because the browser runtime reported no available browsers;
do not describe UI persistence or download as browser-verified. The saved boards,
manifest and source hashes were verified by the producer. When the user finishes,
import the downloaded `truehue_distorted_mask_review11_decisions.json`, retain
all decisions/notes and admit only eligible exact accepted masks. Do not silently
infer decisions or activate a failed candidate.
