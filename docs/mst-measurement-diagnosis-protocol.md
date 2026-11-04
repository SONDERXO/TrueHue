# Saved measurement diagnosis

28 October2026. Read the existing418attempt/396success square256report only,
and join its existing historical table by exact image ID for lighting metadata.
No image inference, new labels, mask edits, calibration fit or threshold search.

Report per subject: official MST, attempted/successful counts, ITA minimum,
quartiles/median/maximum, meanL/b summaries, nonpositive-b counts and face/mask
selected-pixel coverage. Report per subject/recorded lighting group, retaining
missing/unknown values. Lighting labels are observational metadata; contrasts
are confounded by pose, mask selection and photographed conditions.

Compare all distinct subject-median pairs: expected higher ITA for lower MST,
with ties, ordered pairs and reversals counted separately. Same-label pairs
are separate. Rank reversals are descriptive, not a classifier accuracy metric.
Count the number of subjects supporting each category and identify category
loss when its only subject is held out. Preserve unsupported calibration folds.

Independently recompute ITA from saved roundedL/b to check feature accounting.
Absence of arithmetic error does not establish physical skin-color accuracy.
No empirical filtering cutoff or proposal amendment follows from the report.
