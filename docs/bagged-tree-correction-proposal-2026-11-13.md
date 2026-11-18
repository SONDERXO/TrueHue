# Practical proposal: average source-bootstrap correction trees

13 November 2026. **Concrete research proposal, not authorized model-family replacement or an executable training plan.** User requested a realistic/good-enough way past the current limitation. Paper remains paused. The retained single-final-tree requirement needs an explicit user decision before ensemble implementation or fitting.

## Recommendation and mechanism

Test one small bagged ensemble of existing multioutput correction trees. Keep ITA/MST, the exact existing 22 input features, gamma/red/blue targets, photographic references, renderer, approved desktop ear support and manual refinement. Change the predictor from one hard partition to the arithmetic mean of 64 depth-4 trees fitted to source-bootstrap samples. This is one model-family change; no new neutral-object detector, neural representation, source acquisition or feature queue is proposed.

The gap tree recovered all 22 nominal exposure inverses but its cool family and five noticeable identities failed. Saved route diagnosis found correct pure-colour destinations, diluted mixed destinations and wrong exposure destinations. This supplies a concrete instability/bias question: can resampling the available fitting sources and averaging their fitted partitions reduce damaging single-leaf commitments while preserving useful exposure recovery? It is not a claim all errors are variance. Correlated wrong routes or a missing predictive colour relationship can persist. The test must answer that empirically, rather than assuming either success or impossibility.

Why this is more realistic than seeking a trusted white patch: it directly predicts the known photographic-restoration controls from all available input measurements and can exploit imperfect cues jointly. A feature need not be a standalone cast oracle to be useful. Earlier generated ambiguities remain valid limitations of their respective interpretations; they are not universal disqualifiers for statistical learning or permission to reopen those closed candidates.

## Literature and limits

- [Breiman, Random Forests (2001), original manuscript](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf), introduction and regression discussion: ensembles combine randomized tree predictors; error reduction depends on individual errors and their dependence. This motivates averaging, not an accuracy guarantee. Our source bootstrap with all features is a bagged-tree design, not a claimed reproduction of feature-randomized forests.
- [Cheng, Price, Cohen and Brown, CVPR 2015](https://www.cv-foundation.org/openaccess/content_cvpr_2015/html/Cheng_Effective_Learning-Based_Illuminant_2015_CVPR_paper.html), full paper sections 2.1–2.4 read: simple colour measurements can support learned tree-ensemble illuminant estimates. Their method uses four features, locally weighted tree banks and cross-feature consensus, not our features/targets/bagging. It does not establish processed-photo restoration, a single-tree equivalent or benefit on TrueHue. Their features are not being appended here.
- [Barron, ICCV 2015](https://www.cv-foundation.org/openaccess/content_iccv_2015/html/Barron_Convolutional_Color_Constancy_ICCV_2015_paper.html): colour-distribution learning is another statistical route, but its learned convolution is not adopted and is not concealed as a traditional feature extractor. No histogram branch is selected by this proposal.

Targeted docs/source search found no implemented or completed random-forest, ExtraTrees, bagged-tree or boosting comparison. Historical no-ensemble clauses restricted the old experiments; they remain unchanged. Oblique search optimized one tree; it was not prediction averaging. Source-held inner minimum-leaf selection selected one candidate; it was not an ensemble. Split-output predictors/classification-induced partitions, relative losses, weights and clean-leaf guards are distinct closed designs and are not repeated. Search absence is limited evidence, not proof of exhaustive historical novelty.

## Proposed fixed candidate

These settings are design choices, not tuned or proven optimal:

- 64 members, same 22 float32 inputs and unchanged three positive raw targets in the existing ordered schema. No learned feature extractor or additional prediction stage.
- Each member: ordinary squared-error multioutput axis tree, depth 4, minimum leaf 1, minimum split 2, all features considered, no pruning/weights/output scaling. Other ordinary settings match the saved gap-tree configuration.
- Bootstrap unit is a fitting source, not a condition row: draw 10 fitting-source indices with replacement for each member and include all four conditions for each drawn source occurrence. Thus each member receives 40 row occurrences. Duplicate occurrences are literal copies, explicitly recorded. This respects the related-condition structure; it does not create 40 independent people or new examples.
- Canonical fitting-source order comes from the bound roster, never filesystem order. Own deterministic RNG design will be frozen and independently replayed before real execution; seed 42. Per-member tree seeds 42 through 105, fixed in advance. No choosing seeds after outcomes.
- Predict each control by the equal arithmetic mean of all 64 member outputs. No median/trimmed/uncertainty veto, confidence threshold, majority role gate, strength multiplier, MST cutoff or source-specific rule.
- Theoretical maximum 1,984 tree nodes (64 times 31) and 256 split comparisons per prediction. These are structural bounds, not measured file size, latency or Android certification. Averaged controls remain inside member-output ranges, but that does not guarantee image safety or correct interpretation.

Keeping depth and leaf settings fixed isolates averaging/source resampling operationally from another capacity/regularization search. Source bootstrap reduces distinct sources within a member; that may worsen bias or produce members lacking relevant structure. All such members stay included. No rejecting inconvenient bootstraps or resampling until a desired leaf appears.

## Bounded engineering before real training

If the user authorizes the one-tree scope change, first write an executable engineering protocol and build the isolated ensemble exporter/portable mean predictor plus generated source-bootstrap checks. Verify exact roster expansion, held-source exclusion, source/role labels never becoming inputs, all 64 members included, member routes/leaf means, mean arithmetic, serialization and unchanged inputs. Use an independently written scalar verifier. No generated fixture enters scientific training or evaluation records.

Bind exact saved fitting records, feature order, fold roster, code hashes, software versions and RNG algorithm before training. A concrete new immutable output destination and one-shot failure-preservation behavior are required. This proposal intentionally has no execute flag and supplies no authority to bypass those bindings.

First real stage, only after those checks: one ensemble on the existing first 40 fitting rows (10 sources; 16061 excluded), independently verify all 64 exported members and averaged training controls. Fitting quality is diagnostic only; lower fitting error is neither required to prove variance reduction nor sufficient to justify adoption. A valid implementation can proceed to the prespecified source-held test without a post-result parameter adjustment. Engineering failure stops execution and preserves partial artifacts.

## Proposed source-held development test

Before the first real fit, a separate fully bound comparison protocol must fix all 11 source-held folds, reuse the exact verified first ensemble, and fit the other 10 ensembles without any held prediction before every ensemble passes fitting verification. Total budget: 11 ensembles/704 member-tree fits, no extra seeds/settings/all-data fit. This is a fixed structural test, not 704 candidate models from which to choose a winner. No old tree is refitted or promoted.

Use the same 44 available conditions/11 sources and four excluded 29863 roles. They are already exposed development, not untouched validation. Reuse the sealed approved-ear primary support exactly, with the same cached reference and scoring contract. No new mask experiment or secondary geometry rescue. Primary comparison is uncorrected input; compatible SAVED gap-primary metrics may be descriptive only.

Carry forward the accepted practical assessment: source-equal CIEDE2000 benefit separately for under/over/cool; RGB reported; every harm/miss/worst case retained; protected/outside-alpha exact; useful visual improvement within each family; no noticeable identity changes under the existing user policy. No new numerical invisibility cutoff or accepted harm percentage. Complete all 44 initial anonymous ratings before unblinding; never copy old ratings to new outputs. If frozen numerical requirements already fail, stop adoption and do not demand another review merely to establish that failure. Numerical pass still requires the saved visual procedure before acceptance.

Averaging can dilute correct colour controls or spread small wrong exposure corrections across many identities. These are explicit failure modes, not acceptable-by-definition conservatism. No family pooling can hide them. Failure closes this fixed candidate without a forest-size/depth/features/weight/loss/veto sweep.

A development pass would justify planning further qualification, not declaring the model finished: this cohort still has fixed blue targets, limited severity/combined coverage and no independent tone labels. Final24 and older locks stay byte-unread; no inference on them, Android deployment or expert MOS is authorized by this trial. No deadline completion claim.

## Decision required

The current handoff retains "one final decision tree". A bagged ensemble changes that method and would need honest paper documentation if eventually adopted. Ask the user whether they allow this one bounded ensemble trial. Do not interpret their request for a realistic method as silently removing the single-tree requirement. If they retain one tree, this proposal stays unexecuted; no automatic distillation or substitute learner follows.

This review read only local documentation/source and primary literature online. No dataset/cache/reference/mask arrays, raw originals, final24/older locked contents, model fitting/predictions, downloads, installation, contacts, commits or runtime changes. Existing failures and artifacts preserved. User's model-research priority and paper pause remain active.
