# Nested benefit-aware gate: fewer harmful corrections, useful corrections still missed

6November2026. The authorized benefit-aware experiment is complete. It preserves
26of29scored clean photos and lowers mean RGB error in all three layers versus
the previous synthetic-membership scene gate. However, three clean photos are
still harmed and115available cases lose corrections that would improve RGB
error. **This is an improved development trade-off, not an adopted model.**

## What was changed

The [protocol](benefit-aware-gate-protocol-2026-11-06.md) changes gate supervision
from synthetic membership to predicted correction benefit. A positive training
label means an inner held-key correction strictly reduces reference RGB8MAE;
ties/worse errors receive zero. Keep the same12facial+scene inputs, fixed
logistic procedure and zero-logit application boundary. Reference pixels supply
training supervision and evaluation only, never inference features. No
threshold/margin, classifier, feature or depth search was performed.

Use the same whole-scene420attempts,10publisher-key folds, saved source masks,
distortions/targets and outer scene-aware depth3corrector. All397available
features can supervise the gate, including target-fit failures; only the
357target-available rows supervise correction trees. Fourteen original failures
remain unsupported and nine undefined-ITA outputs remain unchanged fallbacks.
No additional dataset, masks, distortions, target fits or outer correction fits.

## Benefit labels without outer-outcome leakage

For outer key H and gate-training key S, an inner corrector excludes H and S.
For its fitting row key T, MST is estimated by a ridge excluding H,S,T. The
prediction on S uses an MST ridge excluding H,S. Thus neither S nor H labels
enter the label-generating corrector, its normalization or upstream estimates.
Its RGB error on S defines the benefit label used to train the gate for H.
Outer H outcomes are only evaluated after fitting that gate.

Caching identical exclusion sets requires120new three-key-excluded MST ridge
fits and45new two-key-excluded correction trees. Ten benefit gates are fitted;
all training keys have both classes, so no unavailable-gate fallback is needed.
The existing55MST artifacts and10outer correctors are reused. No all-data
deployment model is fitted. Inner correctors use fewer keys than outer models,
so training benefit is a proxy rather than guaranteed outer-model improvement.

## Matched operational results

| Layer | Scored / attempted | Ungated shared corrector RGB8 MAE | Previous scene gate | Benefit-aware gate |
| --- | ---: | ---: | ---: | ---: |
| Clean |29/30|14.7037|2.8495|1.4822|
| Core |232/240|10.1152|14.7630|14.2060|
| Stress |145/150|25.5244|26.3939|25.4913|

RGB8MAE is on the0–255channel scale. The unsupported14attempts receive no
fabricated image error; nine feature-failure outputs remain within the scored
stress denominator. Equal-key benefit-gate MAEs are1.6326clean,14.1803core and
25.2709stress. Relative CIEDE2000 means are0.5636clean,5.4653core and10.5605stress.
Although RGB error falls versus the previous gate, stress perceptual error
remains above the ungated corrector's10.2843. No significance or independent
generalization is claimed.

Clean changed/harmed outputs fall6→3of29. Twenty-six are exact no-ops. This is
not a subset-only improvement: four previous clean harms disappear, two persist
and one previously preserved clean photo is newly harmed. Core harms fall
20→12of232; stress harms14→4of145versus unchanged input.

## What the new decision still misses

Against actual outer-corrector RGB benefit on397available decisions:

| Decision | RGB-improving correction | RGB-harming correction |
| --- | ---: | ---: |
| Apply |164|19|
| Leave unchanged |115|99|

The19harmful applications comprise three clean,12core and four stress cases.
The115missed useful corrections comprise108core and seven stress cases, versus
101and four previously. The new gate avoids more harm but suppresses ten
additional useful corrections. A lower mean error does not remove that trade-off.
Unavailable decisions are excluded from this397decision table, not counted as
true negatives.

Synthetic-membership misses rise160→188of368(159core,29stress), but that count
does not alone assess the changed objective: some synthetics are better left
unchanged by this corrector. Of58mild-cast cases whose ungated correction would
harm, the benefit gate still applies correction in seven cases, compared with17
previously. The existing corrector's mild-cast weakness itself is unchanged.
Strict positive RGB benefit is neither aesthetic preference nor physical
skin-colour truth; tiny numeric gains are not guaranteed perceptual improvements.

## Verification and visual inspection

Script500runs the fixed nested experiment. Script501independently checks:

-120new ridge membership/scaling/normal-equation constructions.
-12852inner corrector training traces, exclusions and fitting normalization/raw
  leaf means across45trees.
-3573inner held-image rendered benefit labels, with no label refits.
-397independent outer linear logits and all406saved renderer/metric outputs.

All bound source/parent artifacts remain hash-identical. Gate models converge
in22–29iterations. Existing gate/target-scaled/portable/contextual suites:
**53passed in5.18seconds**. These are focused checks, not a new full-suite,
phone test or scientific validation. Verification performs zero refits.

All90fixed clean/core/stress boards were inspected, including three original
failure contexts. Some formerly overcorrected clean faces are now preserved;
a new conspicuous clean-region change also appears. Several core no-ops retain
imposed darkening, and severe clipped stress shadows remain. These are assistant
development observations, not new human labels or expert MOS.

Private fit outputs: `outputs/benefit_aware_gate_v1/`.
Private independent verification/boards: `outputs/benefit_gate_assessment_v1/`.
All admission flags remain false. Borrowed-support, small development-exposed
sample, limited conditions, studio/chart scene cues, source-score provenance
and calibration distribution shift remain. No runtime/Android change, source
sharing, contact, final refit or submission. Research/noncommercial, citation
and no-redistribution terms retain.

## Decision

The new objective gives a more useful decision trade-off on this development
sample than synthetic-membership supervision alone. It does not finish reliable
automatic correction or validate transfer to other photos. Close this one
comparison; do not tune the threshold, keep trying gates, or promote the three
remaining clean harms to an accepted risk without an explicit operating policy.
No new fitting/admission/runtime task is activated by this result.
