# Why the eight-source Table 2 tree still harms unchanged inputs

28 October 2026. User confirms that the compared earlier broader policies are
**not** the mask method they meant, while describing the result as better and
authorizing continuation. The intended historical mask remains unidentified;
this is not blanket approval of the new application masks or rejected sources.

Script 163 traces all 16 predictions through the existing eight saved trees.
It does not fit a tree, alter masks, change targets or introduce a no-op rule.
All training neighborhoods exclude the held source and known duplicate group.

| Probe | Fitting leaf explanation |
| --- | --- |
| Clean 62331 | Singleton leaf containing 22454's light distortion; inherits its recovery target. |
| Clean 75027 | Singleton leaf containing 67583's medium distortion; inherits its recovery target. |
| Clean 22211 | Six-member leaf mixes four identity controls with both light distortions; their mean changes the clean input. |
| Clean 84364 | Five-member leaf mixes three identity controls with both light distortions; their mean changes the clean input. |
| Light-distorted 6236 | Six identity-only fitting members; predicts no correction. |
| Light-distorted 22454 | Six identity-only fitting members; predicts no correction. |
| Medium-distorted 67583 | Four identity-only fitting members; predicts no correction. |

The seven other source groups in each fold already contain identity examples.
Adding controls alone has not established that the tree routes unseen sources
correctly. For 75027, the two nearest fitting examples by standardized mean Lab
are identity controls, yet its tree routes to the medium-distortion singleton.
This is direct evidence of finite-tree routing trouble, rather than proof that
the measurements make the task impossible.

For two of the four harmed clean inputs, a different recovery target is nearer
than any identity target using fitting-standardized Lab3 distance. This becomes
three of four using all five model features. The sensitivity is disclosed;
neither distance is a confidence score or a replacement predictor. Scaling uses
only each fold's 14 fitting pairs, never the query. Distortion recovery targets
are continuously varying reference-informed fits, so exact target-match counts
for distorted inputs are not treated as severity-class coverage.

Across the eight saved trees there are 10 L*, 9 a*, 14 b*, 12 ITA and 2 MST
splits. MST is retained and actually used in two split nodes; this does not
establish calibrated category-aware quality. The experimental MST index remains
a deterministic mapping of input ITA and does not add an independent measurement.
The limited MST evaluation and no-MST10 artifact limitations remain unchanged.

The diagnostic replays all 16 paths and leaf means, checks portable predictions,
independently recomputes all 32 neighbor rankings and checks original hashes.
No algorithm module changed. Latest full suite remains 692 passed from the
preceding application-mask stage; it was not rerun for this script-only audit.

[Per-input leaf table](../outputs/table2_expansion_route_diagnosis_v1/review-index.md) |
[Full paths and neighborhoods](../outputs/table2_expansion_route_diagnosis_v1/summary.json) |
[Verification](../outputs/table2_expansion_route_diagnosis_v1/verification.json).

The next defensible experiment needs a fixed protocol addressing source and
distortion coverage, rather than another mask widening, depth sweep or arbitrary
identity cutoff. See the [next experiment protocol](table2-next-coverage-protocol.md).
These results do not justify replacing the active model. Android remains paused.
