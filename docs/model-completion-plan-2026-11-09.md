# TrueHue correction-model completion plan

9 November 2026. The user asked to review the overall strategy and prioritise
finishing the working correction model. This replaces an automatic sequence of
small repairs. It does not declare an experimental candidate finished or open
the final holdout.

## Decision

**Stop changing individual leaves on the current evidence. Work toward one
coherent candidate with a compatible mask, measurement/calibration, correction
policy and runtime package.** More fitting constraints or more examples are
not, by themselves, a completion strategy.

The next model work must address useful exposure recovery AND preservation of
clean/colour-only inputs together. Colour-only expansion remains a possible
part of that work, not the default next experiment. It does not directly repair
the mixed clean/overexposed identity leaves or missing facial coverage.

Do not silently narrow the requested face/visible-neck scope, remove ITA/MST,
relax acceptance, or present the older desktop controls as the finished model.

## What the review established

Script 680 checked the verified result/assessment bindings of all four recent
candidates. All four fail the joint criteria. It also confirmed exact equality
of the 756 local-refinement and previous-exception candidate metric records.
Private review and receipt: `outputs/model_completion_strategy_v1`.

| Blocker | Evidence | Consequence for finishing |
| --- | --- | --- |
| Recovery versus preservation | Global nonharm loses six useful conditions; fixed structure weakens recovery; local refinement reproduces all earlier outputs and harm | Another variation of the same leaf repairs is not a justified next cycle |
| Missed overexposure | 22 demonstrated missed core benefits, including 15 outside veto, reach mixed clean/overexposed identity leaves | A colour-only intervention alone does not cover the recovery problem |
| Exposure/colour ambiguity | Colour-only transforms also lower measured L; local split protects a fitting blocker but sends the known stress input to strong brightening | Fit nonharm checks cannot substitute for source-held evaluation |
| Incomplete correction support | Parser contract/backend checks found no explaining implementation mismatch; alternatives and inward fade did not meet the trade-off | More correction-tree training cannot restore omitted pixels |
| Runtime mismatch | Desktop uses current masks with old baseline5/fold1 controls and old measurement/MST features; newer candidates are research only | A good research result still needs a compatible export and actual app parity |

Sources: [latest comparison](local-nonharm-refinement-results-2026-11-09.md),
[training audit](training-exposure-colour-audit-2026-11-09.md),
[remaining failures](remaining-correction-failure-audit-2026-11-08.md),
[decision traces](remaining-correction-decision-trace-2026-11-09.md),
[parser decision](parser-suitability-decision-2026-11-08.md), and
[desktop integration](desktop-current-masking-integration-2026-11-07.md).
These are reused development findings, not fresh independent validation.

## What counts as finished

There are three distinct checkpoints; none is implied by passing another.

1. **Correction candidate qualifies.** On the fixed development/later comparison:
   zero edits to usable clean photos; no increase versus the original aligned
   comparator in core/stress regional RGB or CIEDE2000 mean error or harms; no
   reduction in benefits in either cohort. All failed measurements and missing
   references stay in the accounting. Protection, source hashes, prediction and
   rendering replay pass. Every changed output is reviewed. Existing numerical
   criteria stay unchanged; a known large harm is explicitly reported even if
   its count is no higher than aligned.
2. **The intended pipeline qualifies.** Masking has demonstrated improvements
   under the existing fixed coverage/protection comparison, with retained
   failures and zero newly included definite unwanted reviewed points. Sparse
   checks alone cannot certify dense accuracy. Face/neck boundaries, glasses and
   object protection are explicitly reviewed. Measurement, ITA/MST calibration,
   features and rendering all share a documented compatible contract. A new
   mask invalidates automatic reuse of old fitting costs/calibrations.
3. **The working deliverable qualifies.** Freeze one complete candidate and its
   protocol, then seek the specific final-evaluation decision before any final
   holdout read. Record the independent result without tuning on it. Export the
   same model/calibration/mask package into Python, verify exact controls and
   image/protection parity, exercise failures and save/export, and record actual
   latency. Android parity/device work follows for the Android deliverable.
   Professional review/refinement and frozen final appraisal retain their
   separate roles; no responses or outreach are assumed.

The original aligned core targets remain RGB <= 8.028694 / 9.756669 and
benefits >= 106 / 84 (development/later); the full bound metrics, including
stress and DE, remain authoritative. These are exposed-data gates, not a claim
of universal skin-colour accuracy, unseen clean safety or fairness.

## Bounded work programme

| Stage | Concrete deliverable | Advance only when | Stop/change direction when |
| --- | --- | --- | --- |
| 0. Consolidate evidence — completed here | Four-candidate review, blocker register and this plan | Existing receipts reconcile | Any contradiction is resolved before a new experiment |
| 1. Design one substantive correction cycle | Written training-only design covering clean, over/underexposure, colour and combined conditions; exact source roles, one intervention, fixed fitting/validation protocol and compute scope | The proposed change supplies information or coverage missing from the current design and addresses both documented decision failure types | No justified change beyond another threshold/depth/weight tweak; do not fit just to maintain activity |
| 2. Resolve mask qualification | One permitted local material-aware candidate and one fixed comparison, or an explicitly agreed alternative masking/scope decision | Complete assets, permitted use, verified class/preprocess/interface, fixed comparison and protection checks | Permission/package absent, or fixed comparison fails; no automatic parser sweep or unsafe background-veto removal |
| 3. Execute one integrated candidate cycle | Matched preparation/calibration/costs if support changed; otherwise exact frozen existing contracts; one predeclared model comparison and independent verification | Both readiness conditions above are met for a full-pipeline claim | A failed training constraint or joint acceptance requirement: freeze result and review the design; no automatic rescue fit |
| 4. Freeze and evaluate | Candidate manifest, final-evaluation protocol and independent report | Exposed development, visual/protection and compatibility gates pass, plus specific holdout authorisation | Holdout result fails: retain it as final evidence, never recycle it for tuning |
| 5. Ship the working model | Versioned runtime assets, Python checks, Android/device parity and honest results/limitations | The exported application uses the qualified pipeline and passes its checks | Runtime mismatch or visible/protection failure: fix integration without claiming the model complete |

Stages 1 and asset/permission readiness for stage 2 can progress without new
inference. Correction research can continue under the current mask if justified,
but cannot be called full-face completion while stage 2 remains unresolved.
Do not rerun all old audits as new gates: reuse bound evidence wherever the
underlying artifacts are identical.

**Attempt limit:** one predeclared correction design/comparison in this programme,
and at most one qualified new parser comparison once its prerequisite changes.
No serial variants after a failure. A second cycle would require an explicit
design review identifying new information, rather than a promising score on
these exposed photos. This limit governs automatic continuation, not a promise
that one experiment will succeed.

## Immediate execution boundary

The next technical deliverable is the stage-1 design and readiness record,
not another fit on the existing eleven conflicting leaves. It must specify:

- What will distinguish clean overexposure-like inputs and colour-only
  underexposure-like inputs without clean-reference differences at inference.
- Whether the intervention changes fitting coverage, input representation or
  decision objective; choose one and explain why the existing failed variants
  do not already test it. Do not hide multiple interventions in one comparison.
- Exact fitting/reserved/evaluation roles and group exclusions; no moving
  exposed evaluation examples into fitting or opening the final holdout.
- One frozen candidate construction and unchanged acceptance, independent
  verification, exhaustive changed-output review and a failure disposition.

Do not claim that a valid design is already selected by this review. The saved
evidence supports a need for a different source-generalising decision boundary,
but does not prove that merely adding colour recipes or tree capacity supplies
it. Naming a specific new representation without checking its availability and
training-side rationale would repeat the earlier pattern.

For masking, DINO backbone access is granted and its files are inventoried;
separate decoder/code permission remains unresolved. No DINO execution, renewed
search, author contact, cloud upload or automatic dependency install follows
from this plan. The prior completed human references remain available; do not
ask the user to repeat them.

## Reporting progress and stopping

Report progress as a changed completion checkpoint: a qualified decision model,
qualified support, frozen independent result, or verified runtime integration.
An additional diagnosis is labelled diagnosis. Tests passing establish software
checks, not improved photographs. A candidate numerically identical to a failed
one does not count as model improvement.

If either decision or mask readiness cannot be resolved, the honest outcome is
an experimental prototype with the blocked requirement named. Do not substitute
that for the user's requested finished automatic model without agreement. The
November 14 submission target does not change these criteria. No defensible
completion date can yet be promised; update the schedule when a coherent
candidate actually qualifies.

This strategy review performed zero fits, predictions, renders, image reads,
holdout reads or runtime changes. All old artifacts and uncommitted work remain
preserved. No external contact, publication, upload, commit or push occurred.
