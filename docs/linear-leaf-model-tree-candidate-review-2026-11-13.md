# Candidate: one multi-output tree with linear leaves

13November2026. User requested a distinct justified method after closing blue-axis coverage. **Recommended for a bounded engineering feasibility design, not qualified for photographic fitting or adoption.** No old experiment is reopened.

## Concrete mechanism

The current tree sends each input to a leaf and returns the same constant three-control vector for every input there. Our saved fitting diagnosis shows that these averages blend red-cast, blue-decrease and identity targets even on fitting examples. A model tree retains one hard root-to-leaf route but returns a vector-valued affine function at the selected leaf: controls=A_leaf*x+b_leaf. Different inputs in one leaf can therefore receive different red and blue corrections without adding another split or another tree.

This changes the leaf hypothesis class. The previous oblique trial changed branch geometry but explicitly kept constant leaves. Deeper trees subdivide regions; normalized losses change which splits are preferred; split heads use multiple predictors. None is the same as one hard tree with an input-dependent three-output function inside each leaf. It is a plausible response to within-leaf pooling, not a claim that the currently available coordinates contain a source-invariant correction signal.

## Primary research basis

- Quinlan1992, Learning with Continuous Classes, introduces M5 model trees with multivariate linear models at leaves: https://sci2s.ugr.es/keel/pdf/algorithm/congreso/1992-Quinlan-AI.pdf . The paper discusses controlling complexity because regression models with many parameters and few cases give optimistic fitting errors. Its original formulation is not by itself a verified three-output drop-in for TrueHue.
- Zharmagambetov and Carreira-Perpinan2020, section3.1 and Theorem3.3, explicitly define hard trees with vector outputs and constant or linear leaf functions. Their linear leaf fitting example uses L1-penalized regression: https://proceedings.mlr.press/v119/zharmagambetov20a/zharmagambetov20a.pdf . Section4 separately introduces bagged forests. The forest benchmark gains are not evidence that one TrueHue model tree will work. No author-code parity or package compatibility is claimed.

The existing joint-log-colour feature work borrowed a representation, not these linear predictors. A learned convolutional colour-constancy system would be another architecture and task/prior change, so it is not the recommendation here. The earlier bin-merge/gap forensic mechanisms remain closed; no post-result frequency-template rescue is selected.

## Local history check

Scoped docs and src/model_training search found mentions of linear leaves as explicitly excluded alternatives, but no implemented TrueHue linear-leaf correction trainer. Relevant exclusions: correction-training-contract-2026-11-11.md, oblique-tree-candidate-review-2026-11-12.md, oblique-tree-engineering-protocol-2026-11-12.md and histogram-gap-training-feasibility-protocol-2026-11-12.md. The deployed portable schema only supports constant-leaf values. This is therefore a proposed method extension, not already authorized implementation of an old recipe, an untried claim about the general literature or proof of exhaustive repository absence.

The earlier normalized capacity and split-head failures remain relevant overfitting warnings. They do not test this exact leaf mechanism, and they do not justify its success. No old scores or failures are reclassified.

## Paper alignment and material limitations

Retain single-photo inference, traditional input features including ITA/MST, one tree, three gamma/red/blue controls, original photographic-reference restoration, face/visible-neck manual support/protection and the darker-skin priority. A model tree is a substantive extension of the paper's ordinary constant-leaf CART implementation and must be described as such. It is not literal completion of the currently proposed sklearn model or an Android JSON swap.

Do NOT fit all281 coordinates freely in every leaf: three outputs need846affine coefficients per leaf, or13536at16leaves, before branch parameters. That is indefensible as an unregularized60-record default. A bounded proposal must predeclare a compact leaf input policy or a single regularized formulation, with no post-result subset/penalty grid. No coordinates, penalty, leaf count, optimizer or real fitting roster are selected in this candidate review.

Raw affine functions can extrapolate to nonpositive or extreme controls, requiring an explicitly specified valid-output treatment and independent portable parity before images. Do not silently clip to a newly invented safety threshold or use a reference/role/source-ID override. Tree boundaries can still be discontinuous; small fitting loss does not establish transfer. Added leaf flexibility may memorize source complexion and amplify bias. Source-group-held qualification and eligible independent tone evidence are still necessary; never label naturally darker skin as an exposure error.

This mechanism addresses the fitting colour-axis blend only. It does not explain why the three mathematically restored blue-increase outputs were input-dispreferred, and cannot promise to fix those preferences by recovering controls more exactly. Existing gates and all ratings remain unchanged.

## Next bounded step

Specify one generated-only vector-output linear-leaf mechanism check: fixed architecture/coefficient policy, regularization/valid-output semantics, deterministic fitting/solver and a new portable schema; demonstrate red/blue separation inside one leaf, neutral/exposure behavior, rank-deficiency/small-sample cases, extrapolation and source-nuisance confounds, with scalar inference and serialization checks. Stop on unsupported engineering; no automatic alternative feature/penalty/topology rescue.

Generated success would justify considering a separately bound fitting feasibility trial, not real-photo success or reopening blue-axis recipes. Actual method-extension selection and the concrete generated design must precede implementation/fitting. No new user ratings, sources/captures, dependency installation, training, dataset arrays, runtime/Android/manuscript work or locked/raw-original access occurred here. Earlier baseline and all artifacts remain intact. Modelunfinished/paperpaused/November14complete-deliverytargetatrisk/exacttimeunspecified; no completion promise.
