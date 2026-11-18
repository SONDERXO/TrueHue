# Bounded non-greedy training: held-photo comparison

11 November2026. The requested comparison is complete and independently
verified. **Better fitting did not produce a reliable correction model. The
candidate fails its frozen checks and is not adopted.**

Used exactly the saved11FFHQ photo-group folds,40fitting/4held cases each,44held
predictions and48attempted roles. All four29863roles remain excluded by the
user's underexposed-reference decision. The first feasibility candidate was
reused byte-for-byte; only10additional searches ran. All searches finished before
any held-photo prediction/rendering. No incumbent/baseline refit, all-data fit,
ensemble, new feature, target/mask/map change or held-error-driven adjustment.

## Training result versus actual correction

All11candidate fitting objectives improve. Summed SSE across440repeated fitting
appearances falls2.55610013?0.41827826 (about83.6%). Those appearances reuse44
images from11originals; they are not440independent examples or subjects. Ten
searches stop at5,000nonterminal expanded states within the fixed60second limit.
The48879fold completes at zero fitting SSE, which certifies its fitting optimum
by the nonnegative-SSE bound. The ten capped searches are best-found, not globally
optimal. There is no inference-quality certificate.

All scoring uses the same actual-input alpha-positive regions, renderer,
reference originals and RGB/standard CIEDE2000 metrics. Lower is better.

| Held input | Input RGB | Saved-tree RGB | Search-tree RGB | Input DeltaE | Saved-tree DeltaE | Search-tree DeltaE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Unchanged | 0.0000 | 17.0042 | 16.2146 | 0.0000 | 5.8562 | 5.7335 |
| Underexposure | 27.5404 | 20.4676 | 17.6021 | 9.5749 | 7.1828 | 6.1666 |
| Overexposure | 25.3998 | 12.2891 | 17.2908 | 8.7053 | 4.2783 | 5.9195 |
| Mild cool cast | 2.1413 | 17.2566 | 18.5255 | 2.2693 | 6.0623 | 6.6566 |

Underexposure improves relative to the saved tree; unchanged-image mean error
also decreases slightly. Overexposure and cool-colour mean errors worsen. Both
exposure means remain better than uncorrected input, with individual harms.
All11held original identities are still altered. Cool RGB harms versus input
fall10to8of11, yet mean cool error rises; fewer harmed cases is not uniform or
aggregate improvement. Cool DeltaE harms remain8of11. Overexposure RGB harms
increase3to5, DeltaE3to4. Underexposure harms remain2RGB/3DeltaE.

Exactly22outputs match the parent's PNG hashes. Among22changed outputs,8improve
and14worsen in both RGB and DeltaE relative to parent. Matched counts by role:
identity2better/3worse/6same; under3/4/4; over0/4/7; cool3/3/5. Parameter MAE is
gamma0.24136364/red0.01233766/blue0; blue targets remain constant, not evidence of
learned blue-gain correction. These are exposed development photo-held outcomes,
not new unseen final data or verified person-disjoint validation.

Coverage/protection pass. Per-recipe improvement over input, nonworsening versus
saved parent and unchanged-identity checks fail. No checks were relaxed. Exact
identity is an engineering check rather than a verbatim paper requirement; the
colour-benefit regression independently fails the photographic-restoration aim.
Even the fold with zero fitting SSE still alters its held original: the saved
target audit's feasible controls and improved optimization do not establish
correct choices for a different original photo.

## Verification, visual evidence and recording incident

Corrected verifier825 independently checks362nodes across candidate/parent trees,
880fitting routes, exact rational/serialized leaf SSE, depth/threshold contracts,
all44held routes/renders/RGB-DeltaE metrics and every frozen quality check. It
confirms exact reuse of the first candidate and0verification refits. All11candidate
file hashes now match their saved pre-verification model records.

Verifier823had an output-path variable-shadowing bug: after its numeric checks,
it wrote the verification report over the last candidate file. The report is
preserved as verification_misdirected_v1_PRIVATE.json. The candidate was restored
from its saved aggregate model, including original WindowsCRLF bytes, matching
its originalSHA256exactly. Recovery is recorded separately. All44renders and
aggregate models were unaffected; no search or prediction was repeated.823is
preserved as historical bound evidence; use825for the corrected verification.
The initial assessor consequently found no top-level verification file; it was
rerun only after corrected verification. This incident changes no model outcome.

All22changed case boards were freshly inspected on6contact sheets. They include
useful corrections and visible over-brightening/darkening of unchanged/cast
inputs. The22byte-identical outputs reuse the prior bound44-case visual review;
this is not44fresh inspections or new user ratings. Existing support limitations
are retained. User-painted protection/zero-alpha pixels are unchanged in all44.

## Decision and stop

This fixed bounded-search candidate is CLOSED/not adopted. Do not increase search
time/states, change depth/weights/targets/leaf policy, add an identity gate or
start a recipe/feature/mask variant as an automatic repair. Its result supports
the narrow finding that greedy training left avoidable fitting error, but rejects
using that fitting gain alone as justification for model completion or deployment.
It does not prove that every decision tree or globally optimized tree must fail.

No more human reviews are pending. Keep the working-model objective, one final
decision tree, ITA/MST, single-photo/face-visible-neck scope and optional manual
refinement. Research decisions remain ours; no adviser approval is required or
inferred. There is no tested replacement or newly selected repair in this result.
Further work needs substantive correction-learning/data evidence beyond the
closed search budget or another small descriptor change; no new campaign starts
by default. Full-task blue/combined/severity coverage, calibrated group claims,
independent final evaluation/MOS and Android work remain unresolved as recorded.

All existing datasets, annotations, baselines and failure reports are preserved.
No original photos/final24/older locked pixels, image-model calls, mapping fits,
acquisition, contact/upload/commit/push, runtime or Android changes. Model quality
remains unfinished; there is no production promotion or physical-colour claim.
