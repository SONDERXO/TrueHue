# Correction training/action coverage review — 11 November 2026

**The failed comparison did not lack unchanged examples or identity constraints.**
Each fitting fold contains six reviewed source examples and six reference/identity
examples, with all fitting identity constraints satisfied. The problem is how the
small set of correction examples transfers to held inputs, not a demonstrated
missing clean flag. Do not add another preservation boundary as the default fix.

Scripts789–790 inspect saved rows, action costs, seven trees and fourteen held
decisions. No images, predictions, fitting or alternative model selection occurs.
The previous comparison remains closed and unadopted.

## What is represented

| Evidence | Entire available package | Per fitting fold |
|---|---:|---:|
| Defined unchanged reference roles | 7 | 6 |
| Source/reference correction examples | 7 | 6 |
| Source catalogue minima with gamma>1 | 2 | 1 or2 |
| Source catalogue minima with gamma<1 | 5 | 4 or5 |
| Explicit physical exposure/cast labels | 0 | 0 |

The catalogue supports both gamma directions, but only five distinct nonidentity
oracle actions occur among seven sources: action4 three times, actions1/5/7/11
once each. These are target-aware RGB-cost minima, not physical exposure labels
or automatic prediction results.455's best exponent is0.999966, effectively
neutral with a red-gain adjustment, so describing all five gamma<1 examples as
genuine underexposure would be misleading. There are no explicitly labelled
colour-only cases in this photographic package. The existing controls/targets
do not isolate exposure from editorial colour changes.

330's near-unchanged reference preference is not an assertion that its source
must be an identity example. Preserve the actual reference and costs; do not
change that label to make the result pass. The two904 unavailable roles remain
outside fitting and retained in the full sixteen-role attempt ledger.

## Where coverage becomes thin

Across seven saved trees, there are38 leaves;25 contain only one fitting row
from one publisher group. All three wrongly edited held references reach one
of these single-source-example leaves, with no fitting identity example there.
The fitting constraints are satisfied; they do not extend automatically to a
different held reference routed into that leaf.

The two sources with gamma>1 catalogue minima,1117 and330, are left unchanged.
In each corresponding fitting fold only one other source with such a minimum
is available. Those held sources reach leaves containing the fitting identity
roles.1188 is also left unchanged in a mixed leaf. A fixed action can preserve
those fitting references while missing a useful correction on a held source.

These records support the diagnosis of sparse context/action coverage and weak
held-group separation. They do not prove singleton leaves caused the problem,
that a minimum-leaf-size setting would solve it, or that the tree family is
incapable. No depth/weight/leaf/guard sweep or alternative prediction is run.
The RGB-versus-DeltaE disagreement on787 also remains; a coverage audit cannot
turn its RGB gain into a perceptual success.

## Narrow recommendation

The justified next design question concerns **the supervision examples**, not
more masks, calibration accuracy requirements or constraints. Specify whether
source-matched identity and known-direction controlled restoration examples can
be constructed from the already accepted reference photographs, so the same
photographic content anchors both preservation and correction. This returns to
the paper's original-to-distorted restoration logic and supplies explicit
corruption provenance rather than guessing a photographic editor's intent.

This is a recommendation for a single data-coverage proposal, not approval to
generate images or train. It must first state the actual recipes/operator,
which already-reviewed references and roles are used, and which one supervision
change it tests. Keep all derivatives of a source in one group and preserve the
existing mapping, feature definitions and tree family. Freeze the paper's three
distortion choices explicitly; do not claim unspecified choices were in the
proposal, regenerate the old closed experiment, or start an augmentation sweep.

There is no evidence yet that this proposed coverage change will solve the held
identity problem. If it simply repeats the already failed supervision, it is not
a new experiment and should not proceed. The purpose of the next specification
is to establish that distinction concretely before spending another fitting
cycle. A new dataset, colorimeter, user review round or classifier is not needed
to make that design decision.

## Verification and paper use

Independent checks pass fourteen original role/action joins, seven6/6 fold
balances, fourteen held-leaf support joins,38 recorded leaves and all three
reference harms in singleton correction leaves. Actual immutable labels/costs
remain unchanged. Private evidence:
`outputs/reviewed_correction_training_coverage_v1`.

For the paper, this explains why fitting-time preservation and average gains did
not establish generalization. It does not change the earlier failed checks,
prove physical tone recovery, establish per-MST fairness or demonstrate useful
MST conditioning from the constant column. No new model is selected or adopted.
All prior artifacts, annotations and original paper are preserved; runtime and
Android remain unchanged. Zero photos, image-model calls, fits or predictions;
final24 and older locked images remain byte-unread. No acquisition, contacts,
uploads, commits or pushes. Keep ITA/MST, the final decision tree and the user's
authorized manual-refinement option.
