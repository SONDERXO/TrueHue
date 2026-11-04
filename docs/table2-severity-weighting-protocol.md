# Fixed control/severity weight experiment

28 October2026. The30pairerrorbudgetaudit finds a larger empirical learned-versus-
RGBfitted-target gap for4lightcases than for11mediumcases. Test a declared
training-coverage objective without adding reference labels to inference.

For each28pair fitting pool, give unchanged controls half the total weight.
Give distorted rows the remaining half, shared equally among severity groups
present in that fitting pool and equally among rows within each group. Identity
rows share their half equally. Compute counts only from fitting rows; no outer
held labels, scores or global counts. Reference-estimated severity is training
metadata only, not an inference feature, new intrinsic MST label or coverage of
missing dark groups. The rule does not guarantee equal source influence across
severity groups and differs from the earlier unweighted recipe.

Same15sources/30pairs/15folds,fiveLab/ITA/MSTinputfeatures,depth3/seed42/minleaf1,
targets,masks,exclusions and accepted concerns. Fit exactly15weighted regressors.
Compare ordinary leaf target means (weighted) and the existing conservative
fitting-control identity override, reusing splits. No weight ratios/feature/depth
search, extra sources or gate relaxation. Original strict overall-improvement
and zero-clean-harm gates remain. Preserve outcome even if weights worsen safety.
No runtime promotion or method amendment from this exposed-data experiment.
