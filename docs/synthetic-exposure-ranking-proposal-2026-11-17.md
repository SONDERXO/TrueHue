# Proposed diagnostic: synthetic exposure ranking on existing cached inputs

**User approved, 17 November:** "Yeah, approved. Whatever it takes to finish the correction model. Also what was the prior error that we received during the exposure problem?" Proceed with this fixed eleven-head diagnostic and necessary engineering/bindings without asking again. This is permission to execute the proposal, not evidence of model success or permission to bypass the existing data, closed-study, final-adoption or preservation boundaries.

17 November 2026. **New proposal; not approved or executed on real features.** This is a concrete alternative for the user's "so what next?", not a silent substitution for the approved PIQ23 stage. No dataset acquisition or automatic follow-on correction experiment.

## Question and paper alignment

Can one small score learned from within-source exposure comparisons place acceptable originals above both under- and overexposed versions on a source omitted from its fitting data?

Cached proposal pages 63 and 65 specify synthetic distorted-input to original-photo supervision. Existing camera-task originals and known half-stop variants already provide that limited reference ordering; no new expert scores are needed to state a synthetic restoration target. This does not supply natural photographic exposure judgments, independent training information, or new people. An external quality corpus is not necessary to formulate this limited synthetic-ranking diagnostic; its absence does not establish a ready repair either.

An auxiliary learned score is still an extra training component beyond the written single-tree predictor. It is a new method/label-design extension and needs a separate user scope decision before real fitting. PIQ23 approval was for a particular external exposure-label stage and does not automatically transfer. ITA/MST, final feature-to-control direction, full exposure AND colour objective, renderer/support and preservation remain retained; no final adoption.

## Why consider this, and what the history rules out

The proposal investigates a scalar exposure preference rather than another direct five-control predictor or correction-family classifier. An eventual score response to fixed input-only exposure probes could encode a local preference direction. This is the mechanism already proposed for PIQ23, with a different, narrower synthetic learning target. The source-held score diagnostic here must come first; no actual probes, appended features or correction fits are selected now.

Targeted history review found no completed matching 4096-feature synthetic-ranking experiment, not proof that no related idea was ever discussed. The November 12 oblique review explicitly warned that ranking loss alone does not repair zero-fitting-error/held-source failure. That warning applies. No added information or guaranteed nuisance invariance follows from changing the loss. The paired-reference projection used a clean-source rowspace projector and six prototypes over 4377 features; the global ridge directly predicted five controls from 314 features. Those closed candidates remain closed. Generic ReIQA, joint4410 and fivefold failures also remain.

Necessary feasibility distinction: a linear score can prefer an original over both exposure directions only if its feature response supplies suitable curvature or other separable structure. A purely affine feature response produces opposing preference vectors, which no linear weights can both satisfy strictly. Different natural source appearances can also demand opposite rankings on identical features. Generated algebra below retains both impossibility counterexamples. Nothing currently establishes the required transferable curvature in the actual encoder.

## One fixed real diagnostic, if separately approved

- Reuse only existing `camera_halfstop_neural_v1` 4096-feature vectors for the same 66 cases, eleven source lineages and six roles. No new photographs, encoder execution, checkpoint, masks, tone labels, reference pixels, supports or corrected renders. Preserve all actual provenance/admission flags. Actual data and code hashes must be bound and independently verified before fitting; the expected allocation is not that binding.
- Exactly four within-source preferences: identity above exposure_under; identity above exposure_over; colour_only above combined_under; colour_only above combined_over. Colour cast is matched within each comparison. Do not rank under versus over, mix sources, or fabricate JOD, confidence intervals, observers or expert labels. Colour-only is an exposure anchor, not an assertion that its colour is correct.
- Eleven source-held folds, each with ten fitting sources/60 vectors/40 pairs and one held source/six vectors/four pairs. All derivatives of a source stay together. Known person/duplicate relationships must be respected; source-held is not verified person-independent or tone qualification. If current bindings reveal a conflict, stop rather than silently change the folds.
- At most eleven real linear-score fits, not one global head fitted using the eventual held source. Width4096, bias0, zero initial weights, fitting-only mean/population-standard-deviation normalization (zero std becomes1), equal total source weight and uniform pairs within source. One fixed logistic pair loss plus L2=0.001. Existing proposed optimizer choices retained: CPU float64 Adam, lr0.01, betas0.9/0.999, epsilon1e-8, 50epochs, batch512, seed42. Forty pairs make one full batch/epoch, 50updates/fold and550total. No hyperparameter/epoch/feature/seed search.
- Use a separately verified explicit-pair adapter. Do not feed invented scores/intervals into the PIQ23 metadata API. Complete generated optimizer/scalar checks for the new adapter, explicit-pair invalid cases, source-exclusion/held-payload poison, exact allocation, failure preservation and no-overwrite guards before any real fit. Existing PIQ23 mock weights remain unusable for actual inference.
- Independently verify all fitting models and scaling/source bindings BEFORE held scoring. Freeze all 44 held margins before summaries. Report each pair, all source/family means, strict accuracy, ties (also show half-credit accuracy against0.5), logistic loss versus the zero-score log(2) baseline, score/margin ranges, and fitting-versus-held differences. These are 44 derived comparisons from eleven repeatedly inspected sources, not44 independent votes or untouched confirmation.
- The positive hypothesis is strict source-equal held mean accuracy above0.5 separately for the four declared comparison types, with all misses/ties retained. A negative result closes this fixed diagnostic without a penalty/encoder/objective/feature/source rescue queue. A positive result supplies only limited synthetic ranking evidence and does not automatically select a correction experiment, prove useful probe responses, preserve identity/colour, or qualify fairness/expert/Android results. Any later correction proposal needs its own prospective controls and fixed combined acceptance contract.

The sample is small relative to4096 weights and overfitting is a major risk. A score trained on these synthetic variants may learn rendering artifacts or prefer the wrong photographic appearance. Held-source reporting can expose some transfer failures; it cannot establish external generalization or independent darker-skin benefit.

## Preparation completed without real fitting

`scripts/check_synthetic_exposure_ranking_design.py` constructs only expected source-role allocations and fixed-weight artificial vectors. It checks60fit/sixheld rows and40fit/fourheld pairs per fold, exclusion,44unique held pairs, an exposure-curvature example, an affine-response contradiction certificate and an identical-feature contradictory-preference certificate. It does not optimize any head, read real vectors or qualify the actual encoder. Output: `outputs/synthetic_exposure_ranking_design_v1`.

This proposal is not the complete executable real-fit protocol: actual source/hash bindings and new explicit-pair trainer verification remain after scope approval and before fitting. The design makes the proposed scope concrete; it does not manufacture a ready or successful model.

## Permission and preserved boundaries

The requested scope decision would authorize only this bounded eleven-head diagnostic and its necessary generated/scalar preparation. It would not authorize new data, actual correction trees/renders, a new review batch, deployment, a final all-data fit, replacing PIQ23 labels with invented scores, or a source/model search.

No adviser technical role. No raw originals or locked contents/manifests. Ratings, clarifications, failures, manual ears, environment and checkpoint retained. Manuscript/runtime/Android unchanged. Full objective and Friday paper/expert sequence unchanged; no completion promise.
