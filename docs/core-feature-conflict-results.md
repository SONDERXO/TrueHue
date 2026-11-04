# Why the control-aware tree still overcorrects

27 October2026. Completed the authorized saved-fold diagnostic. **Both
measurement/target overlap and finite-tree routing are visible; the data do
not prove that the task or every four-feature model is impossible.** No learner
was fitted, runtime rule changed, feature removed or source admitted.

[Diagnostic report](../outputs/core_feature_conflict_v1/review.html) ·
[Neighbor summaries](../outputs/core_feature_conflict_v1/neighbor_summary.csv) ·
[Exact paths/leaf members](../outputs/core_feature_conflict_v1/summary.json) ·
[Independent replay](../outputs/core_feature_conflict_v1/verification.json).

## Fixed diagnostic

The [protocol](core-feature-conflict-protocol.md) preceded calculations. Used
all30saved probes, both recipe trees and the exact earlier fitting sets:60
probe/recipe records, with22primary IDs and8held diagnostics still separate.
No held source, held ID, external development, clipped or failed input enters
a fitting neighborhood. Every saved model and original artifact is unchanged.

Primary descriptive distance uses mean L*,a*,b*, divided by each fitting pool's
population standard deviations. Scales use no query/target information.
Four-column Lab/ITA distance is a labeled sensitivity calculation. We report
fixed top3neighbors and exact nearest matching/different-target distances;
there is no learned nearest-neighbor predictor or similarity cutoff. These
distances are not perceptual color error/confidence and cannot be compared
across folds as if their scales were identical. Nearest can still be distant.

## What the revised recipe shows

| Revised recipe subset | Probes | Different target nearer than any matching target | Leaf contains only different targets | Mixed-target leaf |
| --- | ---: | ---: | ---: | ---: |
| All primary probes | 22 | 19 | 9 | 14 |
| Primary unchanged/mild controls | 12 | 11 | 5 | 7 |
| Harmful primary controls | 8 | 7 | 5 | 3 |

All22primary probes have at least one matching-target training example in their
allowed fitting pool. The issue is not simply that the revised dataset omitted
identity/mild targets. The old recipe intentionally had no matching targets
for its12primary controls; its near-conflict comparison is unavailable for
those controls, not zero ambiguity.

All five revised controls whose leaves contain no matching target are harmful.
But a mixed-target leaf is not automatically harmful: all four nonharmful
primary mild controls also use mixed leaves. Membership and averaging must be
interpreted alongside the actual prediction and reconstruction outcome.

The target here is the known inverse synthetic transform relative to an ordinary
source photograph. A different target is not an expert judgment that a person's
complexion needs a different correction. Source photos are not calibrated
neutral-color/exposure truth.

## Two concrete failure paths

**22454mild: a nearby example has a conflicting target.** Its mean Lab is
[57.3525,5.1145,14.9721]. The nearest allowed training example is6236color-shift,
Lab[59.1467,4.3173,15.1508], at standardized distance0.2330. Its target is
[1,1.17647,0.86957], whereas the mild probe's target is[0.90909,1,1]. The nearest
matching-target example is at1.5954. The probe routes into a singleton leaf
containing that color-shift example and receives its wrong red/blue adjustment.
This is a real overlap in these recorded measurements, not leakage or an
application bug, but does not establish physical equivalence or impossibility.

**51739unchanged: nearest-target agreement does not rescue tree routing.** Its
nearest Lab3example is6236unchanged, with a matching identity target, at1.9760;
the nearest different-target example is at2.0653. Yet the tree checks L*>25.1744
and b*>27.7876, routing the probe to a singleton6236dark leaf. It predicts
[1.42857,1.12049,1.03656] instead of[1,1,1]. The fitting identity example is
outside that leaf. This implicates the finite tree's splits/support, not a
proof that the measured features contain no usable information. The nearest
matching example's L*differs substantially, so "nearest" is not a validated
claim of close visual appearance.

Including ITA in the diagnostic distance changes this51739nearest-target
ordering. Across primary controls, different-target-nearer counts become12/12
instead of11/12. This metric sensitivity is disclosed; it is not a basis for
selecting a distance, removing ITA or deploying nearest-neighbor correction.

## ITA and exact collisions

For all30feature rows, saved ITA exactly reproduces the rounded
`atan((mean_L_star-50)/mean_b_star)` calculation. ITA therefore supplies no
independent measurement beyond those recorded means. It can still be a useful
nonlinear representation for an axis-aligned tree; redundancy does not imply
that it should be removed. The actual four-column model schema is unchanged.

There are **no exact cross-source collisions** among the22eligible feature
vectors, either at their saved precision or after float32conversion. Near
examples with differing targets are evidence of a difficult small-sample
learning problem, not a mathematical nonidentifiability proof. A2D projection
also cannot establish separation/overlap in the full measured space.

## Evidence-based next question

Do not add another recipe tweak, depth sweep, arbitrary no-op cutoff or guessed
MST label on these same cases. Earlier ten-feature experiments already tested
extra brightness summaries and still overcorrected; this audit does not erase
those findings or establish that a new feature will succeed.

The next justified data question is whether a **consistently processed,
reference-screened source pool provides independent control and distortion
coverage around the problematic branches**. The51739leaf is supported by only
one dark training example, while22454's nearby color-shift/clean mismatch shows
that adding more of any arbitrary source is not enough. Audit existing reviewed
candidate sources and their reference suitability first; keep failed/held cases
and source separation. Any additional data stage needs a predeclared selection
and processing policy, never source choice based on favorable predictions.
No new source screening or data admission was performed by this diagnostic.

If that coverage cannot be established, the appropriate result is a documented
limitation of the present measurement/training setup, rather than an unsupported
accuracy claim. Clarifying reference exposure/color and the unresolved MST role
is part of the core thesis method; CPM remains deferred. A category guessed
from the same ITA would not constitute new independent evidence.

## Verification and scope

Independently reconstructed all60routes/leaf means,120neighbor rankings/scales,
360top3records and16denominator/count rows using separate arithmetic. Verified
target matching, absent support, feature ordering/float32routing, ITA relation,
exact-collision claims and all original model/source/input/review/ledger hashes.
The figure was visually inspected with its2D/projection limitations retained.
**555tests passed in11.22s**, including9new diagnostic tests for fitting-only
normalization, deterministic ties, constant-axis/query-shift handling, absent
matching targets and invalid input rejection.

No new model, prediction rule, mask, threshold, training pair, source exposure,
review/fold change or runtime adoption. This remains deliberately selected,
previously exposed development evidence, not independent final accuracy,
calibrated skin truth or expert MOS. Operational MST, face/visible-neck,
finaldata/reference/splits/evaluation and Android remain unfinished; paint/
makeup protection remains a limitation.
