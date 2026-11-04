# Predeclared nested leaf-size selection

28 October2026. Test whether fitting-leaf regularization improves the supported
five-feature method, rather than tuning support-guard margins. Use exactly the
same15reviewedsourcegroups/30pairs and five input Lab/ITA/MST features. Keep
depth3,seed42,unweighted targets, masks,approved concerns and exclusions fixed.
Candidate minimum leaf sizes are exactly1,2,4. No depth or feature search.
Apply the established identity-if-any-fitting-control leaf policy to each tree;
do not apply the later range guard in this experiment.

For each outer held group, use only its28fittingpairs/14groups to perform14inner
held-group folds per candidate size. Each inner model fits26pairs/13groups.
Fit630inner regressors total. Record all1260inner predictions. A size is eligible
only when its pooled inner error strictly improves versus no correction AND
zero inner held clean inputs are harmed. Choose the eligible size with lowest
inner meanCIEDE2000; ties favor larger minimum leaf size. If none is eligible,
select identity. Save that selection before scoring the outer held pair.

Only a selected size is refitted on all28outerfittingpairs and receives the same
fitting-control leaf policy. Save all inner models/labels/decisions and outer
results. No held outer label,reference,target or reconstruction metric may enter
setting selection. Inner references are scoring evidence,never features.
No retry with extra sizes or relaxed criteria if no size qualifies. This is
training-only selection,not per-image identification of distortion.

Report all decisions, fitted-model count,clean harm,distortion intervention and
overall/clean/distorted errors. Identity-only output is safe abstention,not
successful correction, and fails strict overall improvement. Repeated cohort
exposure during hypothesis development remains disclosed; nested selection does
not create independent final validation. No active model promotion or change
to MST, masks, source allocations or photographer timing/GoogleForm decision.
