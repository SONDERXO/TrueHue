# 22-input gap-cue fitting-only feasibility results

12 November 2026. **One real fitting-only run completed; independently verified fitting improvement. No source-held correction result or model adoption.**

Used the frozen first40fittingrows/10sourcegroups with16061excluded, old16inputvalues plus the frozen6gapfeatures, unchanged nominal3controls and one ordinary depth4seed42squared-error tree. No scaler, weights, alternate fit or oblique trainer. Generated fixtures excluded. Saved16input parent was replayed only on fitting rows, never refitted or reclassified.

| Raw fitting SSE | Saved16input tree | New22input tree |
|---|---:|---:|
| Total |0.08404474326173622|0.003702161136563477|
| Gamma |0.07714285714285717|1.232595164407831e-31|
| Red gain |0.006901886118879054|0.003702161136563477|
| Blue gain |0|0|
| Identity role |0.008961147141072141|0.002056756186979696|
| Under role |0.06642844393067518|1.232595164407831e-31|
| Over role |0|0|
| Cool role |0.008655152189988894|0.001645404949583781|

The~95.6%drop describes fitting parameter loss, not photographic correction accuracy. Both new scene_blue_low_internal_gap_fraction and scene_red_high_internal_gap_fraction are used in splits; retained input_mean_a_star and scene_any_full_fraction are also used. The tree has11nodes/sixpopulatedleaves. All10fitting underexposure cases share a correct-control leaf, and all10overexposure cases share another. Gamma error is numerical rounding only. Blue targets are constant, so zero blue error is not blue-correction learning evidence.

Four of ten fitting identity cases reach a mixed identity/cool leaf with red_gain1.0226757369614512; six have exact identity controls. Maximum identity gamma deviation is0,red deviation.0226757. These are fitting diagnostics, not visible-harm determinations; no preview or reviewer assessment occurred. The result does not establish why any future held case will route correctly, especially given prior zero-loss transfer failures and gap-feature JPEG/resize/palette sensitivity.

Independent script863 passed all40canonical routes/control replays, sklearn/portableleafparity, full22input join against the original40fittingrecords and auditfeatures, exact saved-parent identity, graph/depth, sixleafmeans, rawSSE/control/role metrics and original code/data hashes. Runtime versions/settings and single fit call are saved. Fit time was.14914seconds on this computer, not an Android benchmark. No rerun or verification fit.

## Decision and next step

The observed incremental feature use and fitting gain support specifying a new source-held development comparison; they do not authorize it automatically. Freeze the remaining10newfoldfits with these SAME22inputs/settings, reuse this exact firstcandidate byhash, finish all fits before held scoring, and independently verify. Bind support/scoring semantics before any render: the approved desktopearrevision does not silently replace the old evaluated masks. A feature-effect comparison and a combined-pipeline claim must identify which alpha/reference region they actually use. Do not refit old failed trees or change their gates/results.

The accepted practical criterion remains uncorrected-primary/source-equal per-family benefit, useful visual exposureANDcolour correction, tiny-unnoticeable identity changes and exact protection. No numerical invisibility cutoff, tone-veto or further feature/weight/depthgrid is introduced. Current diagnostic blue/strength/combined/MSTlabel limits remain; development success alone will not finish the study or supply fresh independent final qualification. Modelfirst/paperpaused; final24/olderlocks byte-unread; old failuresclosed; approvedearintegration/manual/tree/ITA/MST/traditional/singlephoto/neck retained.

This run read saved fitting JSON and previously exposed descriptor metadata only. Exactly40fittingrows joined; no held rows enter X/Y, no original/reference subtraction or source/role features. Zero photos/masks/NPZdecoded, heldpredictions/renders, newreviews, runtime/Android changes or external communications. Evidence is preserved under outputs/histogram_gap_training_feasibility_v1 (candidate,baseline,fitting inputs,replay,executionplan,verification,assessment,status).
