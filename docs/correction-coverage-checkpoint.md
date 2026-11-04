# Correction coverage checkpoint

25 October 2026. User reviewed the remaining28 regenerated candidates as generally suitable, while explicitly requesting improvement to missing facial portions before applying corrections. Recorded this as qualified review, not blanket complete-mask approval. Earlier decisions, the four separately approved regenerated masks and all exclusions remain intact.

The measurement mask may use a representative subset of facial skin for ITA/color statistics. Correction support has a different purpose: selecting the visible skin to adjust. A missing correction region can leave a patch unchanged even when parameter estimation is valid. Blending can soften boundaries but does not establish correct coverage or repair unreliable measurements.

Script86 inspected correction masks for all32 regenerated candidates. It independently reconstructed intentional eye/brow/complete-mouth exclusions from the actual input landmarks, then located fully enclosed background components. Components overlapping any protected exclusion remain protected; no region was filled.

Eleven of32 masks contain122 total enclosed pixels not connected to those exclusions. Largest counts:7994 dark31,67583 dark22,40048 unchanged17,40048 dark12 and63870 mild12. These are geometric gap candidates, not verified missing skin. Missing cheek/jaw strips connected to the outer background are not counted, so122 is not a total facial-coverage error or an acceptance score. Some small holes can be intentional non-skin islands.

Codex inspected the7994/67583/40048 gap boards. Red indicates unprotected enclosed gaps; yellow indicates intentional feature exclusions; green indicates correction support. Some red regions lie near eyebrows or skin/background boundaries and need material/anatomical checks. Do not fill eyes, lips, hair, paint, fabric or background just to make a solid mask. Allnine source boards are available; none is an automatic skin annotation.

Next recommended experiment: a separately versioned correction-only gap-recovery candidate with explicit eye/mouth/brow protection, non-skin/material checks and unchanged original measurement/generation masks. Evaluate all32 cases plus earlier labeled hair/paint examples before adoption. Inspect border coverage separately; do not solve it with blind face-box expansion. Preserve failures and earlier geometry sentinels. No candidate filling rule has been adopted or tested yet in this checkpoint.

The32-pair cohort remains pending coverage improvement and final staging checks.31154 stays held; original fold4 remains empty. The separate nine-source evaluation proposal has not been executed. No model training, corrected outputs or runtime change occurred. Visible-neck support, operational MST and final thesis reference/data/evaluation requirements remain pending.

[Gap comparison boards](../outputs/correction_gap_audit_v1/review-index.md) | [Per-component diagnostics](../outputs/correction_gap_audit_v1/summary.json) | [User qualified review](../data/manifests/non_skin_regenerated_remaining28_v1/user_coverage_review.json)

Completed test: [correction-only enclosed-gap recovery](correction-gap-recovery-test.md).19experimentalpixels added,twoedgepixelsambiguous;largercoverageconcern remains.
