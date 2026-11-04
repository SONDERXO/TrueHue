# New correction-data design frozen before image processing

28 October2026. User authorizes substantial data/training redesign rather than
continuing variations on15exposed sources. Completed the first redesign stage:
reconcile allocations/exposure, identify a larger local source pool, freeze new
candidate roles and implement a training-preparation access guard.

## Available data and corrected scope

The historical source audit covers650FairFace candidates:450train,126development
validation and74reservedtest. The actual legacy exposure ledger has198unique
source entries; combined with the historical audit's explicit development flags,
325of650have recorded development use. Every one of the650historical candidates
is excluded from the new design regardless of its exposure flag or suitability.
All old acceptances,qualified concerns,rejections,holds and experimental results
remain preserved. Historical allocations are not rewritten or physically moved.

The local FairFace training directory contains86,739files versus86,744metadata
rows,five metadata image paths unavailable. Outside the historical/processed
registries,86,175local originalTRAIN rows and10,868original validation rows are
available for metadata selection. Recent work was unnecessarily confined to the
old650candidate pool; the larger local pool permits a more substantial design.
These counts do not establish usable references,masks or skin-tone coverage.

## Frozen new candidate allocations

| New role | Candidates | Original dataset split | Current image access |
| --- | ---: | --- | --- |
| Training | 420 | TRAIN | Preparation may begin under the new guard |
| Development-validation | 90 | TRAIN | Locked from training development |
| Final test | 90 | Validation | Locked from training development |

Selected by deterministic image-ID hashes from metadata/filename availability,
before opening any image. No demographics,ITA,MST,reference judgment,model
prediction or correction outcome determines membership. No overlap between
roles or with all650historicalIDs/explicit processed exposure records. All
variants will inherit source role. Seven fixed60source preparation batches cover
the420training candidates only,without replacements.

These are600unreviewed **candidates**,not600eligible examples or independent
people. Exact420/90/90matches70/15/15candidate counts but does not implement
MSTstratification. No official FairFaceMST label is invented, and SCIN remains
an unresolved part of the full thesis dataset requirement. Selection outside
recorded registries is not proof of never having been manually seen.

No source image was opened,decoded or content-hashed at this stage. No features,
distortions,model fits or new pixel-review exposures were generated. Metadata
access is explicitly recorded. The existing exposure ledger and historical
metadata hashes remain unchanged.

## Enforced preparation boundary

`src/data_preparation/redesign_access.py`provides a dedicated new-preparation
guard: only declared originalTRAIN candidates in the train role can be returned.
It rejects unknown/duplicate IDs,nonworkspace paths and attempts to open locked
validation/test roles through this entry point. Returned records are copies,so
callers cannot mutate the frozen manifest through them. It does not automatically
mark a candidate eligible for fitting.

These are workflow locks with tested caller enforcement,not Windows filesystem
permissions or a retroactive restriction on every older script. New preparation
must call the guard; a separate declared phase is required for validation/test
access. Nobody should describe local files as physically inaccessible.

Before any fitting, the declared duplicate/content-leakage audit is still
required. Candidate subject identities and duplicate groups remain pending;
do not manufacture group IDs or claim person-disjointness. Any necessary
validation/test image access for that audit must be separately recorded and
distinguished from model/quality inspection. No duplicate audit has run here.

## Verification and next work

Scripts207/208freeze and independently reproduce all600IDs from original CSVs
and directory entries,verify420training authorizations/180locked-role denials,
all seven batches,unchanged historical partitions/exposure and CSV ordering.
Checks pass. Nine guard tests cover immutable records,locked roles,unknown and
duplicate IDs,original validation rejection and unsafe path forms. Full suite:
**724passed in33.56seconds**,fresh workspace temp directory/cache disabled.

Next: declare and execute duplicate-audit access/accounting,then prepare and
review only the frozen training candidates using one consistent processing/
augmentation policy before fitting. Development-validation is for later frozen
candidate assessment; final-test outcomes remain unavailable to tuning. Record
eligibility attrition rather than claiming the final accepted dataset keeps the
candidate split ratios. No model improvement or scientific validation is claimed
from this metadata stage.

This redesign preserves ITA/MST and decision-tree correction. Existing weak
lookup accuracy,clipping/approximate-target,reference and accepted-contamination
limitations still require disclosure. Photographer opinions wait until model
completion using the existing GoogleForm; Android remains paused;CPM deferred.

- [All frozen candidates and availability audit](../outputs/correction_data_redesign_v1/selection.json)
- [Training candidates](../outputs/correction_data_redesign_v1/train_candidates.csv)
- [Locked development-validation candidates](../outputs/correction_data_redesign_v1/development_validation_candidates.csv)
- [Locked final-test candidates](../outputs/correction_data_redesign_v1/final_test_candidates.csv)
- [Training-only preparation queue](../outputs/correction_data_redesign_v1/training_queue.json)
- [Access policy](../outputs/correction_data_redesign_v1/access_policy.json)
- [Independent verification](../outputs/correction_data_redesign_v1/verification.json)
