# Proposal reassessment and recommended direction — 9 November 2026

This is a review and recommendation, not an approved scope amendment or model
adoption. No experiment, training, dataset acquisition or final-holdout access
was performed. The original proposal is unchanged.

## Source and review limits

Reviewed `Thesis Proposal Document.pdf` (111 pages), SHA-256
`1426f3769ba771daadf9b6e0e0b1e347729c8f04919c214e6fedc3df272e7b8a`,
against the saved page-by-page extraction whose source hash matches the current
PDF. Fresh extraction libraries were inaccessible; no fresh rendering is claimed.
The existing full-page render of PDF page 64 was also inspected. References below
use PDF page numbers, not printed page numbers. The conference working draft is
supporting context, not a replacement for the proposal.

## Recommendation

Do not commit to a separate beard-parser training project now. Return to a bounded
decision about completing the proposed automatic photographic-correction study.
First prepare a single method/completion specification from existing evidence,
making unresolved changes explicit. This is documentation and design review, not
permission to restart the spent correction experiment cycle.

The proposal's core is automatic facial measurement, ITA/MST and a lightweight
decision tree for brightness/colour correction, evaluated on synthetic distortions
against original photographs (pages 10–14, 59–67). It explicitly calls the work
exploratory and acknowledges limitations. It does not make perfect beard/hair
segmentation or training a new dense parser a prerequisite. It also does not
establish recovery of intrinsic skin colour or correction of real camera bias.

Keep the user's fully automatic requirement. Automatic refusal/no correction
when measurement is unreliable is a possible policy to specify and evaluate;
refusals must count as failures or abstentions, with coverage reported by group.
This is not evidence that such a policy currently achieves adequate coverage.
The face-only proposal does not silently cancel later requested neck/material
features; those need an explicit scope disposition.

## What is actually blocking completion

Masking is imperfect, but it is not the only blocker. SegFace's fixed screen
increased selected skin points from 39 to 74 and usable cases from 3 to 5 of 6,
while increasing unwanted points from 3 to 7. It failed the existing protection
criterion and was not adopted. These six cases are diagnostics, not a population
accuracy estimate.

Separately, the final bounded green-feature correction comparison produced the
same 756 outputs as its parent despite using the new features in tree splits.
The candidate retained clean cases but recovered fewer useful cases and had
higher core reconstruction error than the aligned comparator. Better beard
masking cannot be assumed to fix this correction-decision limitation. The closed
cycle does not justify another automatic feature, weight or model sweep.

## Paper issues to resolve before final evaluation

| Issue | Proposal evidence | Required treatment |
| --- | --- | --- |
| Data and calibration roles | Pages 12–14 reserve MST-E for evaluation; page 62 describes using it to calibrate the lookup | Resolve the contradiction explicitly; no calibration using final evaluation data. Document actual permitted replacement sources. |
| Distortion definition | Three tone-dependent distortions, pages 59 and 62 | Freeze equations, order, units and clipping; distinguish the proposed recipes from later diagnostic conditions. Do not attribute unspecified details to the paper. |
| Correction method | ITA, MST, colour statistics and parameter prediction, page 63 | Describe actual finite-action versus direct-regression behavior and demonstrate any claimed ITA/MST influence. Merely including features does not establish conditioning. |
| Evaluation comparator | Uncorrected input, pages 65–66 | Report this baseline alongside the aligned comparator and harms. The paper's baseline and later adoption gates answer different questions. Do not quietly loosen an approved gate after failures. |
| Fairness interpretation | Per-MST results and a 10% disparity flag, pages 66–67 | Define the percentage denominator before evaluation. Tone-dependent corruption strength confounds comparisons across groups; synthetic results alone do not establish real-world fairness. |
| Completion evidence | Expert MOS and local Android, pages 11–13 and 66–67 | Actual expert ratings and device verification remain outstanding. Assistant reviews and software tests cannot substitute for them. |

Page 64's “intended corrected output / target reference” examples illustrate the
original photograph as a target; they are not trained-model predictions.

## Concrete next deliverable

Prepare one completion specification that lists the retained scope, amendments
needing a decision, frozen data roles and metrics, automatic failure policy, and
the evidence required to promote a model. Include a go/no-go decision based on
the already completed correction comparisons. Any substantive new correction
design or parser training requires a separate justified proposal, not an implied
continuation of this review.

A defensible thesis may report limited or negative feasibility findings, subject
to adviser expectations. That is different from delivering the working model
the user wants. We cannot call the current candidate finished, promise that new
parser training will finish it, or claim the consistent improvement objective
has been met. Keep the final holdout byte-unread until a model and protocol are
qualified for it.

## Supporting records

- `thesis-proposal-completion-tracker-2026-11-08.md`
- `proposal-scope-validation-2026-11-03.md`
- `proposal-full-scan-findings.md`
- `segface-loader-and-mask-screen-results-2026-11-09.md`
- `green-feature-correction-results-2026-11-09.md`

All previous artifacts remain preserved. No scope recommendation in this review
has been treated as user approval.
