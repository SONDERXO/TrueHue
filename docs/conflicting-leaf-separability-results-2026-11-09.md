# Conflicting-leaf fitting separability — 9 November 2026

The saved-data audit is complete. Eight of the eleven changed leaves have at
least one existing feature whose fitting ranges strictly separate the colour
blocker from all exposure rows benefiting from the old action. Three leaves
have overlapping ranges on every feature. This supports considering a bounded
local refinement protocol, but does not establish a successful new model.

## Scope and definitions

User instruction: continue the next step proposed in the completed
[fixed-structure report](fixed-structure-nonharm-results-2026-11-09.md).
The [audit protocol](conflicting-leaf-separability-protocol-2026-11-09.md) fixes
selection to all pre-veto leaves whose actions changed. Scripts 672/673 read
saved fitting vectors, costs and tree structures only; no evaluation vectors or
outcomes were used to choose axes or thresholds. All source artifacts remain
unchanged. No thresholds were enumerated or selected, no child action costs
were optimised, and no new split, fit, prediction, rendering or image read ran.

A blocker is a colour-only row harmed by the old action relative to identity.
An exposure beneficiary is an exposure-only or combined under/over row, including
stress recipes, helped by that action. Features use the portable model's exact
float32 inputs. Strictly disjoint ranges exclude touching endpoints.

## Findings

Every changed leaf contains exactly one colour blocker: the same saved fitting
condition, `diversity_017__stress_color_none`. These are eleven repeated
appearances, not eleven independent photos. There are no clean-row blockers
for these old actions. Exposure beneficiaries total 788 repeated occurrences,
covering 111 unique condition IDs; condition IDs themselves include repeated
distortions of originals and are not independent people.

| Configuration | Leaf | Exposure beneficiaries | Features with strictly disjoint ranges |
| --- | ---: | ---: | --- |
| stellenbosch_124 | 7 | 64 | L, a, b, MST, scene R/G, scene B/G, zero fraction |
| stellenbosch_132 | 7 | 67 | Same seven |
| stellenbosch_176 | 5 | 64 | Same seven |
| stellenbosch_186 | 9 | 96 | None |
| stellenbosch_194 | 9 | 96 | None |
| stellenbosch_212 | 11 | 39 | L, MST |
| stellenbosch_231 | 7 | 64 | Same seven as first row |
| stellenbosch_260 | 7 | 103 | None |
| stellenbosch_72 | 7 | 64 | Same seven as first row |
| stellenbosch_89 | 7 | 64 | Same seven as first row |
| Full fitting | 7 | 67 | Same seven as first row |

Here L/a/b are `input_mean_l_star`, `input_mean_a_star`, and
`input_mean_b_star`; MST is `input_mst_score`; scene R/G and B/G are the existing
log-ratio features; zero fraction is `scene_any_zero_fraction`. All 12 features
were audited and saved, including features whose intervals overlap.

The blocker lies outside the exposure beneficiaries' axis-aligned bounding box
in the same eight configurations. In the other three it lies within that box.
No blocker/exposure pair has an identical complete float32 feature vector in
any of the eleven leaves.

These facts distinguish a local fitting conflict from an unavoidable identical-
input contradiction. They do not establish that a single split suffices in all
configurations. Marginal overlap can still permit multivariate separation;
absence of duplicate vectors does not prove useful generalisation. The audit
compares the blocker and exposure-beneficiary sets, not every other row's
possible constraints. Any refinement must also enforce those other rows, the
reserved-clean veto and frozen facial exception.

## Independent verification

The independent scalar verifier passed 132 feature-range checks, 788 complete
vector-pair checks and 9,563 saved fitting-route checks. It independently
reconstructed blocker/beneficiary membership, costs, float32 extrema, strict
disjointness, bounding-box status and exact-vector collisions. It verified all
selected source hashes and the aggregate model against its existing verified
model receipt. This is not a new replay of all historical image-source hashes.

An initial verifier assertion compared index-list order, although the historical
leaf trace stores rows in a different order from scalar routing. Membership
comparisons were corrected to compare sorted indices; the saved audit output
was unchanged. Verification then passed.

Private artifacts: `outputs/conflicting_leaf_separability_v1/audit_PRIVATE.json`
and `verification_PRIVATE.json`. No existing file in the previous model or
comparison output folders was changed. No adoption, app integration, external
contact, upload, commit or push occurred. DINO remains unused; all 24 final
holdout photos remain byte-unread.

## Recommended next intervention; not executed

Prepare a fixed protocol for **one additional constrained split at most in each
of these eleven conflicting leaves**, using fitting data and the existing
cost/action objective only. Preserve all ancestor splits, untouched leaves,
clean/colour constraints, roles, features, calibrations, veto and exception.
Predeclare deterministic candidate/tie rules and keep a leaf unchanged when no
feasible improvement exists. Do not choose features from evaluation results,
exempt the blocker, relax constraints or run a depth sweep.

The three overlapping leaves are a reason to avoid promising full recovery;
even an improved fitting objective would still need the unchanged independent
checks and full fixed evaluation/review. This audit has not selected a split
or authorised that experiment. A specific comparison protocol must precede
new fitting. The current candidate remains rejected and the holdout closed.
