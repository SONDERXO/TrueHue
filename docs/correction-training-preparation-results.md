# New training cohort: preprocessing and review

**Planned comparison completed; small-model trial cycle stopped.** Imported
58 accepts / 3 rejects, preserving notes. Candidate normal-case error improves
8.312 to 6.629, but clean changes rise 1 to 3 and total error worsens 6.964 to
7.561. No adoption or follow-up tweak. Verified 26 refits and 210 outputs.
[Review and fixed comparison results](reviewed-primary-training-results.md).
[Required data/method decision before another trial](primary-comparison-decision-checkpoint.md).

**Focused plan implemented: primary data prepared, no new tree fit.** Reused 26
approved originals; preserved 52 new clipped stress candidates and 17 mask
holds. Prepared 61 normal-case candidates: 25 lighter gamma, 25 darker gamma,
10 original color components and 1 original exposure component. Gamma-only
controls are an explicit supplemental recipe, not the full Table 2 recipe.
[Review the 61 masks grouped into 26 photos](../outputs/primary_training_review_v1/review.html).
[Data preparation, verification and frozen comparison](primary-data-preparation-results.md).

**Current direction: stop small same-cohort tweaks.** User requests a focused
path without repeating the loop. The current candidate has 26 clean approvals
and 21 distorted approvals, all with some generation clipping; no unclipped
distorted row is approved in this plan. Six earlier screened unclipped variants
remain unreviewed, not a ready dataset. Preserve authorized stress fitting;
prepare a primary data/method specification before another model experiment.
[Focused finish plan and stopping rules](correction-model-focused-finish-plan.md).

30 October patch audit: saved reference-fitted settings still produce red
patches in 1398 JPEG85. A verified RGB-only bound separates missing support
from invariant channel endpoints; it is not a CIEDE2000 bound. Learned-versus-
target differences still show prediction opportunity on other cases.
**798 tests pass**; 141 floor decompositions and 282 image/metric replays checked.
[Patchy-output causes and limits](patchy-correction-limits-results.md).

30 October mask-stage follow-up: traced all 141 masks and tested fixed cleanup
reordering for application support only. JPEG85 error improves 5.704 to 5.447
and forehead coverage recovers in 1398, but extra outside-reference pixels and
visible patchy color remain. Same clean failure; no adoption or demo change.
[Stage attribution and cleanup comparison](jpeg-mask-stage-and-cleanup-results.md).

30 October full-path check: all **141 detection/mask/measurement/correction
attempts complete**, with benefit retained after JPEG compression. Same one
clean failure (68453); no demo replacement. JPEG85 can substantially reduce
facial coverage (worst mask IoU 0.520), so successful execution is not mask
quality approval. All 141 detection and geometry/output replays verified.
[Full-path JPEG results](endpoint-full-path-jpeg-results.md).

30 October frozen-candidate JPEG check: correction error remains below unchanged
at quality 95/85 (5.357/5.491 versus 9.520/9.653). No additional clean failures;
68453 still changes. 141 decoded feature/output replays, no model fitting.
Fixed masks only; not an end-to-end detection/mask test.
[Encoding sensitivity results](endpoint-jpeg-sensitivity-results.md).

30 October improved candidate: masked R/G/B endpoint fractions reduce matched
47-pair error **8.013 to 5.300**, and clean changes **2/26 to 1/26**. Both
distorted subsets improve. Source 68453 still visibly overcorrects, so the demo
is unchanged. **794 tests pass**; 26 candidate refits/47 output replays verified.
[Endpoint candidate results and all comparisons](endpoint-feature-tree-results.md).

Completed eleven-mask review: **6 accepted, 5 rejected, no pending decisions**.
Exact notes preserved; accepted original-rule distorted pairs pass technical
and target checks. Fixed paired training raises held clean changes from 2 to
5, so no promotion. All 52 tree refits and 94 outputs independently verified.
[Review import and paired training results](reviewed-six-pair-training-results.md).

30 October color-feature check: nine features improve distorted error modestly
but raise held clean changes from 2 to 3; no promotion. **790 tests pass**;
52 trees and 82 outputs independently verified. Prepared one focused page for
the eleven missing distorted-mask approvals on already accepted originals:
[Review eleven masks](../outputs/distorted_mask_review11_v1/review.html).
[Comparison and review scope](chromatic-feature-tree-results.md).

30 October measurement audit: all 41 input Lab/ITA/MST vectors reproduce exactly.
In fitting-standardized five-feature distance, 7/26 clean inputs are closer to
a distorted example than a clean example; there are no exact cross-source
float32 collisions. Descriptive evidence only, not a new predictor or proof of
impossibility. [Measurement and overlap audit](measurement-neighbor-audit-results.md).

30 October mask follow-up: topology-only hole completion changes 14/40 exposed
candidate frames, but recovers only about 1.3% of missing paired support and
visual inspection finds beard/glasses risks. No promotion or new source
approval. Separate experimental module; **786 tests pass**.
[Mask-hole results](enclosed-hole-mask-results.md).

30 October target check: log-multiplier training leaves the same two held clean
failures, so it is not promoted. Separately, all fifteen saved recovery targets
improve distorted inputs when applied directly (20.153 to 8.902 mean error).
Missing application-mask support alone leaves a 4.445 mean error contribution.
These reference-informed diagnostics are not learned accuracy.
[Target comparison and audit](log-target-tree-results.md).

30 October capacity check: fixed depth 5 improves distorted error against the
augmented depth-3 model, but clean changes rise from 2/26 to 8/26 and combined
error worsens. All 52 fits and 82 outputs verified; tree paths explain the
clean failures. Candidate rejected; demo unchanged.
[Tree-depth results](clean-control-tree-depth-results.md).

30 October clean-control comparison: eleven already accepted original photos
were added as unchanged training examples. Historical clean-photo changes fell
from 1/15 to 0/15, but two new held clean photos still changed and distorted
correction weakened. All 78 fits and 123 outputs were independently replayed.
No candidate promotion. [Clean-control results](accepted-clean-control-results.md).

30 October model follow-up: fixed brightness features did not help. Protected
eleven-feature error8.525versus7.132forfivefeatures;clean harm3versus1. Keep
the stronger research baseline and existing demo unchanged.780tests pass.
[Negative comparison preserved](direct-gamma-brightness-results.md).

Latest model comparison: fitting-control protection on the direct-gamma tree
reduces clean-photo harm5→1of15and pooled error7.628→7.132,but distorted
error worsens and75027stillfails.776tests pass; no demo replacement or source-ID
exception. [Protected-tree results](direct-gamma-clean-leaf-results.md).

Latest model work (30 October 2026): matched training on the approved historical
15-source/30-pair set tests direct-gamma regression targets, retaining input
ITA/MST and tree settings. Overall error8.534→7.628;clean harm6→5of15;distorted
error slightly worsens. No demo replacement because the safety gate still fails.
No new mask cohort admitted. [Model results](direct-gamma-regression-results.md).

New working desktop demo: open `run_truehue_demo.cmd` in the project root.
Choose a photo, run the existing experimental pipeline and compare/save results.
No rejected mask candidate was promoted; correction quality remains unfinished.
[Simple demo instructions](simple-python-demo.md).

Latest development comparison: fixed face-contour containment removes selection
outside the predicted oval while retaining18/20technical measurements per frame.
Hands/hair inside the contour remain; no new acceptance or promotion is inferred.
The former check cases are explicitly exposed development data for this step.
768tests pass. [Containment results and limits](postcheck-contour-development-results.md).

Frozen YCrCb check finalized: **4accepted,16rejected,0pending** after all five
clarifications. Preserve paired-panel hair/exclusion reasons for2879/38620/7526.
The candidate remains unpromoted; no further review clarification is needed.
[Final check findings](ycrcb-training-check-review-results.md).

Check clarification recorded:7571and37974rejected. Current check totals are
4accepted,13rejected,3pending (2879,38620,7526). Original export preserved;
no candidate promotion. [Clarification](ycrcb-training-check-review-results.md).

Latest check export: all20entries validated; six accepted, eleven rejected,
three blank. Clarify2879/38620/7526 selections and7571/37974 acceptances with
failure notes. No need to redo the entire review. Candidate remains unpromoted.
[Imported check findings](ycrcb-training-check-review-results.md).

Current task: [20-photo separate frozen-mask check](../outputs/ycrcb_training_check20_v1/review.html).
Candidate definition and IDs frozen before check outcomes; original reserved12
plus8fixed-hash training sources, excluding the60 development-reviewed sources.
Review panels3and6 and source suitability. No old MST lookup transfer or model
adoption. [Check details](ycrcb-training-check-results.md).

Latest review imported: eight YCrCb-only reference/color-input pairs,
six accepted and two rejected. Four acceptances retain notes; 66413's blur
needs source assessment and 14418 remains rejected for background inclusion.
Next is a separately frozen training-mask check, not automatic fitting.
[Review findings](color-cast-ycrcb-review-results.md).

Current small review: [8YCrCb-only changed/risk cases](../outputs/color_cast_ycrcb_refinement_v1/review.html).
Removing onlyHSV raises color-input support-screen passes5→14of20but increases
outside-oval selection. Review both candidate reference and candidate input
masks,not all60sources again. No automatic approval/calibration transfer.
[Refinement results](color-cast-ycrcb-refinement-results.md).

Current candidate design now contains three declared distortions plus identity
per source:80attempts from the same20accepted references. This is an explicit
engineering decomposition, not an exact recipe quoted from the paper. Exposure
passes the exploratory support screen17/20; color5/20; combined6/20.58approximate
targets verify; all fitting holds remain.762tests pass.
[Candidate set and remaining gates](three-variant-candidate-results.md).

Latest matched-source implementation: a separate direct-gamma path follows
the paper definition while preserving legacy models. On20accepted references,
clipped support pixels drop306,080→13,650and support-screen passes3→6, but
17inputs still clip and14418has no usable target because the mask intersection
is empty.19targets have verified reciprocal-gamma conversion.755tests pass;
no active model or automatic admissions. [Detailed results](paper-gamma-input-comparison-results.md).

Full-paper scan update: gamma convention is stated in PDF38 (below1 brightens);
the current reciprocal-exponent parameterization behaves oppositely for the
same numeric gamma. PDF59 calls for three distorted versions per source;
the current one-composite-plus-control cohort is only a development subset.
Complete augmentation units/order remain unspecified. Preserve legacy models
until a versioned convention is implemented.
[Verified source requirements](proposal-full-scan-findings.md).

Latest finding: the current Table 2 numerical interpretation produces much
darker outputs than the proposal's embedded simulated examples in a native-image
formula comparison. Resolve augmentation equations/provenance before further
regeneration or fitting; no replacement is inferred automatically.
[Source audit and comparison](proposal-augmentation-specification-audit.md).

Post-review audit:20accepted sources have measurable reference/input pairs,
but19inputs clip and17trigger the existing exploratory support-loss screen.
Only14418isunclippedandscreen-passing; its accepted coverage concern remains.
43909stillfailslandmarks. No new primary correction fit or additional review
is justified yet. [Accepted-pair audit](accepted-training-pair-audit-results.md).

Review update: the planned60 original-mask development sources are now reviewed
(21 accepted/39 rejected). No need to repeat their source reviews. No training
admission follows automatically; concerns and distorted-mask/clipping checks
remain separate. [Completed review findings](training-review36-import-results.md).

Current task: [36 additional development photos](../outputs/training_review36_v1/review.html).
These complete the planned 60 unique development sources with the previous24;
do not redo all seven batches or the same failed24 again. Original rule-based
masks only; no automatic admissions. [Selection details](training-review36-results.md).

Current follow-up (29 October 2026): the completed 24-photo annotations now
support a separate semantic-mask comparison on the **same 24 photos**. Review
the rightmost candidate against the preserved baseline; no new full batch is
requested. Candidate support is technically available on 21/24, not yet human
approved or MST calibrated. [Comparison results](focused-semantic-mask-results.md).

Current review task (29 October 2026): **review only the new 24-photo focused
reference/mask page**, rather than completing all seven batches. Twelve separate
training sources are reserved for a later frozen-mask check, not requested now.
All existing processing records and decisions remain preserved.
[Open the focused review](../outputs/focused_mask_review24_v1/review.html) ·
[Selection and next steps](focused-mask-review-results.md).

29 October 2026 review presentation update: all seven batch pages now show one
candidate at a time with individual enlarged panels, search, status/decision
filters, keyboard navigation, accept/reject/uncertain buttons and concerns.
Decisions save in browser storage when available; export JSON backups for
sharing or recovery. Batch-specific imports reject mismatched manifests.
These are review annotations only and do not override processing failures or
admit sources for fitting. Original pages are preserved in
`original_review_pages_v1/`; the original verification's HTML hashes refer to
those copies. All original scientific evidence hashes remain unchanged.
JavaScript syntax and mock-DOM interaction checks passed, as did all 418 image
links and seven data blocks. No connected browser was available for visual QA.

Processed the complete frozen queue of 418 training candidates after duplicate
quarantine. The two quarantined training IDs were excluded without replacement.
No development-validation or final-test candidate entered this preparation.
All processing used the unchanged square256 measurement contract, experimental
monotone MST lookup and reference-conditioned Table2 severity policy.

| Outcome | Sources |
| --- | ---: |
| Measurable reference/input and available approximate recovery target; review pending | 261 |
| Reference processing failed | 80 |
| Distorted-input processing failed | 62 |
| Recovery target unavailable | 15 |
| Total attempted | 418 |

Reference failures comprise 57 unavailable landmarks, 3 violations of the
single-face requirement, 14 empty skin selections and 6 insufficient skin
selections. Distorted-input failures comprise 24 unavailable landmarks,
33 single-face failures and 5 insufficient skin selections. Every attempt is
retained in the JSONL record. No failure received a replacement source.

The 338 measurable references receive experimental severity estimates:
60 light, 276 medium and 2 dark. Among the 261 successful target candidates,
55 are light and 206 medium; none is dark. These are lookup-derived severity
groups, not verified intrinsic tones or official FairFace MST annotations.
The larger candidate pool has not resolved dark-severity coverage.

Of the 261 target candidates, 254 contain clipped pixels in synthetic reference
support. They must retain that annotation and cannot silently enter an
unclipped primary analysis. Recovery targets are bounded RGB fits on explicit
mask intersections, not exact inverses or evidence of learned reconstruction
performance. The 276 target-optimizer calls are distinct from correction-tree
training: **zero trees fitted and zero sources admitted for fitting**.

Each measurable reference supplies an unchanged identity control with target
`[1,1,1]`, plus one distortion chosen by reference-estimated severity. Distorted
inference features come from the distorted input and its own MST estimate;
reference features are not substituted at inference. Reference and input masks
are saved separately. The seven review pages display original reference,
reference support, distorted input and input support, including failed cases.
Green pixels indicate algorithmic selection and do not certify mask quality.

Every new preparation attempt is logged before source access in this run's
separate access ledger. Historical exposure metadata, frozen roles and audit
dispositions remain unchanged. Future exposure reconciliation must include
this new ledger as well as the historical one. All 418 sources now have
training-development processing exposure; visual human decisions remain pending.

Scripts 211/212 prepare the queue and independently reconstruct saved
composites, recompute measurement features, check source/dependency hashes and
verify training-only membership. The full existing test suite passed:
**724 tests in 31.37 seconds**. Artifact verification is recorded separately in
the linked verification file; software checks do not establish suitability.

Next, review source/reference suitability and both displayed masks before
fitting, preserving qualified concerns as well as rejections. Begin with batch
1 and record decisions against these exact saved images. Any subsequent mask,
augmentation or coverage-policy change needs a declared comparison; it must
not rewrite this run. Existing MST calibration, photographic-reference and
clipping limitations remain unresolved. Photographer evaluation waits until
the correction model is complete, using the user's existing Google Form.

- [Review index: seven batches](../outputs/correction_training_preparation_v1/review.html)
- [Batch 1: 59 candidates](../outputs/correction_training_preparation_v1/batch_1.html)
- [Complete attempts](../outputs/correction_training_preparation_v1/attempts.jsonl)
- [Summary](../outputs/correction_training_preparation_v1/summary.json)
- [Verification](../outputs/correction_training_preparation_v1/verification.json)
