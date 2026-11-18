# Authorized fixed bagged-tree development protocol

13 November 2026. User approved the proposed ensemble trial and required alignment with the paper. This supersedes the one-final-tree constraint ONLY for this candidate assessment. No candidate adoption, manuscript edit, general model-family search or holdout access follows.

## Paper alignment

Primary question remains synthetic-distorted input restored toward its original photographic reference, compared with uncorrected input. Preserve input ITA/mapped MST, 22 existing traditional measurements, gamma/red/blue controls, single-photo inference, face/visible-neck/manual refinement and approved desktop ears. Identity controls are supplementary preservation checks. Document source-bootstrap averaging as a method extension if eventually adopted; do not describe it as the originally proposed single tree. No physical skin truth, illuminant ground truth, fairness, MOS, phone or full-proposal-completion claim follows from FFHQ development. Paper stays paused.

## Frozen candidate and sampling

64 axis multioutput squared-error trees, depth4/minleaf1/minsplit2/all features/no weights or pruning; other settings exactly the ordinary gap-tree settings. Member seeds42..105. Bootstrap 10 fitting sources with replacement per member, retain each sampled source's four records in original fitting-roster order, yielding40 occurrences. Source order = first occurrence in bound fitting roster, not sorted filenames. No selection or rejection of members by fit or output quality.

Freeze a platform-independent own RNG: for member m=0..63 and draw d=0..9, hash UTF8 `42:m:d:a` with SHA256, starting rejection-attempt a=0. Interpret first4 digest bytes as unsigned big-endian integer z. With n fitting sources, accept z only when z < floor(2^32/n)*n; otherwise increment a. Selected source index=z modulo n. This removes modulo bias without searching seeds. Engineering fixtures may use other n, but real n=10. No dependency on Python/random/NumPy generator versions. Scalar verifier independently reconstructs the draws.

Prediction is math.fsum of all64 member values per control divided by64. Float32 inputs, float64 split thresholds, <= routing. No median/trim, strength, uncertainty veto, MST cutoff or learned classifier. Runtime module imports no NumPy/sklearn. Structural limits: <=1984nodes and <=256splits/prediction, not a device benchmark.

## Engineering gate, binding and order

Before real fits, generated checks must establish source-block bootstrap membership/duplicates/exclusion, scalar routes/leaf means/mean arithmetic, immutable export roundtrip, invalid schema rejection, float32 boundaries and import safety. A separate scalar verifier imports no optimizer/runtime and independently verifies all bootstrap draws, fitting joins, each member's depth/routes/duplicate-weighted target leaf means and final mean. Missing/wrong member, setting, source, input or replay must fail. Generated fixture labels stay separate.

A metadata-only design script binds exact existing 11 folds/44 records/22names/raw targets/48role ledger plus saved gap primary support manifests and declared NPZ hashes. Only the44 explicit development packs may later be opened, and only after all fits verify. Do not resolve or enumerate final24/older locked content. Allowed saved support paths must be under the exact gap-comparison/supports source folders, with four known files bound by saved manifest hashes. No masks regenerated. Bind old-plan, rows, gap audit, mapping provenance, approved-support receipts, renderer/conversion code and protocol plus runtime versions/code/test hashes. QA receipt and plan bindings checked before execution.

Real stage1: ONE64-member ensemble on first40fit/10source rows excluding16061, with new output directory that refuses existing complete/partial attempts. Save canonical fit rows, source draws/occurrence IDs, model, replay and independent verifier. Leaf means account for bootstrap multiplicity. No held predictions and no photographic arrays in stage1. Fitting loss may be worse than one tree; it is not an image-quality gate or a selector.

Real stage2: reuse the EXACT stage1candidate SHA and fitting inputs, fit the other10ensembles, independently verify every ensemble BEFORE any held inference or pixel decoding. Total704memberfits in11ensembles, no restart/extra candidates/all-data fit. Seal the reuse SHA before starting the remaining fits. Engineering failures preserve outputs and stop; do not silently retry. All old candidates/results unchanged.

## Scoring and stopping

Exactly44held control vectors:11identity,11under,11over,11cool; all4roles of excluded29863 retained as exclusions in48attempt ledger. Same approved-ear primary support/reference/scoring region as saved gap comparison. Render gamma then channel gains, clipping before alpha blend and round-to-even RGB8. Reuse sealed support bytes; require measurement/protection unchanged. Saved gap primary numbers descriptive only; old models not rescored. No old-geometry second diagnostic arm.

Independently replay all704member trees, joins, 28160original-fit member routes plus bootstrap mean checks, 2816held member routes,44means/renders/metrics/protection checks and11support alpha replays. Verify output PNGs exactly and RGB/CIEDE2000 within carried abs/rel1e-10 arithmetic tolerance. No fit in verifier. Aggregate input-minus-output DE by source equally per family; report all per-case harms, controls, RGB, unchanged/misses/worst cases. All44initial panel assignments SHA256(protocolID+caseID)low bit and public assets fixed before ratings; no old answers copied.

Frozen numerical requirement: positive source-equal DE benefit separately under/over/cool; full accounting/protection/parity. Numerical failure closes this candidate, needs no user ratings to establish failure. Do not serve numerical/control/model results before initial ratings if a numerically eligible candidate proceeds to review. Numerical pass remains NOTADOPTED/PENDINGVISUAL: all44anonymous primary reviews, existing durable Save/Reload/Download procedure, usual display recorded, practical identity noticeability and distorted preference/artifact rules unchanged. No synthetic invisibility threshold or allowed-harm percentage. No conspicuous visual harm concealed by means. Overall readiness cannot pass with a failed/unresolved required check.

Failure ends this fixed trial: no member-count/depth/seed/feature/weight/threshold/mask rescue or ensemble distillation. A development pass only supports subsequent separate final/integration planning. Constantblue targets, small exposed11source cohort, absent independentMSTlabels and limited recipes remain limits. Final24/older locked holdouts remain byte-unread throughout. No Android, contact, acquisition, dependency change, upload or commit.
