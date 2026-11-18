# Why the current correction tree chooses the wrong operation

11 November2026. The user authorised reviewing the learning approach before
another annotation campaign. Scripts812?813 use saved JSON only: no images,
new fits, inference API calls, changed masks, acquisitions or runtime changes.
The failed44-case experiment remains closed, and its results/gates stay intact.

## What the saved trees actually do

A regression-tree leaf returns the average fitting gamma/red/blue controls of
its examples. All44 held outputs reproduce those means and routing exactly.
Seven of11 unchanged originals reach leaves containing only exposure examples:
the model applies the exposure control those examples taught it. Six of11 cool
inputs also reach exposure-only leaves. Nine of11 original/cool pairs reach the
same leaf despite requiring different red gains.

The failure is not only transfer to new photographs. Of110 fitting-identity
appearances across11folds,95 receive nonidentity controls from the saved trees.
These are repeated uses of11 unique identity images, not110 subjects or independent
training samples. The actual fitting set is balanced10identity/10under/10over/
10cool per fold. Identity examples are present; a missing-label flag or an absent
clean population is not the explanation. Ordinary regression imposes no hard
identity constraint, unlike the earlier action-cost learner.

Raw joint squared-error targets have root SSE29.64948980 for gamma versus
0.13744273 for red and0 for blue, summed across folds. Gamma therefore supplies
99.53858% of the available raw target variation. This describes numeric loss
scale at the root, not99.5% of causal failure, split importance or pixel error.
It explains why mild red-gain error has little numerical influence compared with
exposure error; it does not prove a weighting change will improve held images.

All four green-only features are exactly unchanged for each original/cool pair:
the recipe changes only red. They can carry exposure information but no direct
response to this particular perturbation. Other existing Lab/scene chromatic
features do change; those feature families are already present, so "add colour"
is not a sufficiently specific new intervention. Colour information is not wholly
absent, and absence of green response does not prove all current inputs inadequate.

The varied external MST score is not split on in these saved trees. It is derived
from ITA and adds no independent captured illumination evidence. That fact is not
permission to drop MST or refit a map merely to force its use. Blue targets are
constant, so this batch cannot teach nontrivial blue-gain recovery.

No exact float32 feature duplicates with conflicting nominal controls were found.
This rules out that narrow duplicate-conflict explanation on these44 records;
it does not prove general identifiability, adequate separation or a guaranteed
repair. Small-cohort diversity, support uncertainty and scene/content differences
remain confounders. Physical/intrinsic colour truth is not a prerequisite for the
paper's photographic-restoration experiment.

## What follows for the paper and model

The manual reviews provided real, reproducible support evidence. Repeating them
will not change how saved fitting controls are averaged. Do not request another
mask pass, reopen the old automatic mask experiment, or call this a finished model.

Do not jump from the99.5% finding to another target-standardization trial: the
historical fixed target-scaling comparison worsened reconstruction/identity harm;
the later key/layer-balanced regression also failed. Both remain closed. Relative
rendered-loss normalization failed on the recent seven-base data as well. These
are related negative evidence, not proof that every possible loss is equivalent.
More depth, clean overrides, extra weights, new recipe strengths or arbitrary
colour ratios are not selected by this diagnosis.

The next useful design must explain how the retained tree will distinguish
exposure need, colour need and no correction on an unseen photograph. It must
name genuinely additional input evidence or a substantively justified learning
formulation, compare it against already failed approaches, and define a bounded
validation before any fit. Distortion names, original targets, person IDs and
second-photo comparisons cannot secretly become inference inputs. Mere leaf
relabeling or a classifier on the same failed summaries is not new evidence.

Keep decision-tree prediction, ITA/MST, single-photo use, face/visible-neck scope
and optional manual refinement. No model-family change, adviser approval, broader
acquisition or additional annotation is inferred. This diagnosis supplies a
concrete learning-design problem, not a tested replacement or a new acceptance
barrier. There is not yet evidence for a specific repair, so no new training
candidate is selected here. The working-model objective remains unresolved.

## Verification

Independent saved-route replay verifies44 held contexts,440 fitting control
replays and11 paired paths. An exact-decimal Fraction pairwise-variance identity
independently reproduces all11 fitting target budgets. Checks pass. No refits,
image bytes, private original reads, locked/final reads or new quality ratings.
All prior artifacts/annotations remain preserved; no runtime/Android/contact/
upload/commit/push changes. Original proposal and historical results unchanged.
