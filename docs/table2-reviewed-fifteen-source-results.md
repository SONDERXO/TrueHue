# Reviewed fifteen-source correction comparison

28 October2026. Archived the user's exact seven-source review against the saved
shortlist/processing hashes. Added only the five accepted sources; preserved all
existing records, accepted concerns and rejected-source exclusions.

| Source | User decision | Exact concern/reason |
| --- | --- | --- |
| 1398 | Accept | little bit of body captured in face mask |
| 68453 | Accept | minor holes in face mask |
| 12222 | Reject | reference support captured clothing in face mask |
| 59944 | Accept | some hair is captured in face mask |
| 66156 | Accept | little bit of background caught |
| 63087 | Accept | little bit of body captured |
| 60381 | Reject | captured a body part in face mask |

The59944acceptance explicitly includes hair contamination; it is not a hair-free
mask claim. Body/background concerns also remain unresolved limitations, not
silently corrected pixels. No reviewed mask or measurement contract changed.
The two rejected sources remain excluded alongside51739/40048/42532/63870/713.
All74other existing held sources from the24and60batches remain held.

## Fixed model comparison

Five new source groups add ten pairs, one identity and one MST-conditioned
Table2distortion each. Combined:15groups/30pairs,15held-source/known-duplicate
folds,28fittingpairs from14othergroups per fold. Estimated severity coverage:
4light,11medium,no dark. Source grouping does not prove person separation.

Ran the already established recipes without search: baseline5(meanLab/ITA/MST),
chroma9(the same five plus four distribution statistics), and the existing
training-control leaf policy on the chroma9tree. Depth3/seed42/minimumleaf1,
unweighted targets, application/scoring masks and zero-clean-harm gates stay
fixed. Exactly30regressiontrees fitted;15clean-leaf exports reuse chroma9splits.
No new depth,feature,weight,threshold,mask or partition-objective experiment.

| Mean CIEDE2000 | No correction | Baseline5 | Chroma9 | Clean-leaf |
| --- | ---: | ---: | ---: | ---: |
| All30pairs | 10.076 | 8.534 | 10.956 | 9.921 |
| Fifteen unchanged | 0.000 | 5.470 | 6.426 | 3.753 |
| Fifteen distorted | 20.153 | 11.598 | 15.485 | 16.090 |
| Harmed unchanged inputs | 0 | 6 | 8 | 2 |

Baseline5gives the lowest overall/distorted error among these fixed methods.
It passes overall improvement but harms1398,84364,75027,51803,59944,22454clean.
Chroma9fails bothgates. Clean-leaf passes overall improvement but still harms
1398and75027clean; it suppresses more useful distortion corrections. **No method
passes both adoption gates.** No active model or Android asset is replaced.

These are reconstruction scores relative to ordinary source photographs and
estimated reference support, not calibrated skin truth, photographer MOS or
independent final accuracy. The weak experimental MST mapping,noMST10artifact,
clipping/approximate-target and category-coverage limitations remain.

## Matched original cohort

The larger cohort average cannot alone establish a better model. Independently
checked that the original20images,masks,features,targets and scoring contracts
are identical, then scored those same IDs under the expanded fitting pools:

| Same original20pairs | Earlier10source fitting | Expanded15source fitting |
| --- | ---: | ---: |
| Baseline5, all | 9.643 | 8.702 |
| Baseline5, unchanged | 5.489 | 5.156 |
| Baseline5, distorted | 13.797 | 12.247 |
| Chroma9, all | 8.898 | 11.290 |
| Clean-leaf, all | 8.538 | 9.768 |

This is a genuine matched-ID descriptive improvement for baseline5under the
expanded training pool, with no significance/generalization claim. It does not
resolve clean preservation. Conversely, the additional chroma features and
their leaf policy worsen on the original cohort; earlier improvements did not
remain stable under expansion. Keep those failed candidates as evidence rather
than automatically choosing more features as the next direction.

Codex inspected the five new accepted-source boards and75027.1398clean becomes
strongly lightened under all methods;75027remains strongly lightened.68453medium
has prominent patch boundaries;59944has variable/no recovery under the more
conservative policy.66156and63087lightinputs show little/no useful correction.
Those observations cover six sentinel boards, not a new expert/user review of
all outputs. Existing accepted-source concerns are not waived by these previews.

## Verification and disposition

Script194archives review, verifies admissions, freezes cohort/methods before
feature extraction/fitting, saves all30models/45portableexports and90corrected
images. Script195independently recomputes30feature vectors and baseline
measurements, replays30regressionmodels/90methodpredictions, checks15conservative
exports against fitting controls, reconstructs corrected pixels with separate
RGB arithmetic, recomputes metrics/gates and verifies28pairfitting source/group
separation,7rejectedIDs,74holds,reviewconcerns,historical evidence and original
hashes.20matchedoriginalpaircontractsareverified. All checks pass.

No shared algorithm module changed; latest full suite remains705passed from the
control-partition stage, not a new suite run. No release-model/full-data fit,
active asset replacement or photographer collection occurred. Photographer
opinions remain deferred until model completion, using the existing GoogleForm.
Android remains paused and CPM deferred.

For subsequent model work, retain baseline5as the simpler comparison reference
and address its six unchanged failures explicitly. Do not silently drop those
controls or tune a special-case1398/75027rule. This evaluation establishes useful
distorted-recovery progress, not a finished correction model.

- [Exact user decisions](../outputs/table2_reviewed_fifteen_source_evaluation_v1/user_review.json)
- [Frozen cohort, exclusions and methods](../outputs/table2_reviewed_fifteen_source_evaluation_v1/fit_plan.json)
- [Metrics and gates](../outputs/table2_reviewed_fifteen_source_evaluation_v1/summary.json)
- [Matched original20pair results](../outputs/table2_reviewed_fifteen_source_evaluation_v1/matched_old_cohort.json)
- [Independent verification](../outputs/table2_reviewed_fifteen_source_evaluation_v1/verification.json)
- [All15source comparison boards](../outputs/table2_reviewed_fifteen_source_evaluation_v1/review.html)
