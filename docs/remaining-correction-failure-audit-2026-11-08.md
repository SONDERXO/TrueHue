# Remaining correction failures: saved-output audit

8 November 2026. **There are correction-decision problems we can investigate while replacement-parser access is pending.** Missing masks do not explain every missed correction. No new training, inference, rendering or holdout access occurred.

## What was checked

Classified every one of the latest candidate's 756 existing evaluation attempts using its saved metrics, mask status and two saved alternatives: the original aligned model and the reserved pre-veto model. Both alternatives use the same evaluation input alpha, scoring region and reference as the latest candidate. A saved improvement therefore demonstrates a possible decision improvement without changing that mask; it does not provide a deployable selector.

## Core conditions

| Outcome | Development | Later photos |
| --- | ---: | ---: |
| Total attempts | 240 | 192 |
| Usable measurements | 161 | 132 |
| Conditions with reference scoring regions | 176 | 144 |
| Beneficial latest correction | 91 | 78 |
| Harmful latest correction | 0 | 0 |
| No gain, but at least one saved alternative helped | **15** | **7** |
| No gain and no demonstrated useful saved alternative | 41 | 43 |
| Failed measurement with scoring region: unchanged | 29 | 16 |
| No reference scoring region | 64 | 48 |

The outcome rows from “Beneficial latest correction” through “No reference scoring region” partition all attempts. Availability and scoring are different dimensions: an input can fail measurement but still have a scoring region from its original reference, or have a measurement without a usable original reference region. The 79 development and 60 later measurement failures total **139 core failures across all attempts**, not just the 45 with scoring regions.

The 22 demonstrated missed core benefits all receive identity controls and involve overexposure. They derive from 11 originals, not 22 independent photos. Seven occur in explicitly vetoed branches; fifteen do not. Therefore changing the veto alone cannot recover all demonstrated missed opportunities.

No useful saved alternative is not proof that no useful action exists. This audit did not render every possible action or compute a new oracle. It also does not attribute these 84 unresolved no-gain conditions to masks: the records alone cannot establish that cause.

## Stress and clean conditions

Stress outcomes in development: 40 benefits, zero harms, five no-gain conditions with a useful saved alternative, 13 unresolved no-gain conditions and 52 scored measurement failures; another 40 attempts lack reference regions. Later stress: 35 benefits, one harm, eight demonstrated missed benefits, eight unresolved no-gain conditions and 38 scored measurement failures; another 30 lack reference regions. Stress measurement failures across all attempts total 87 development and 65 later.

The 13 demonstrated missed stress benefits involve the stress colour recipe. All 35 demonstrated missed core/stress benefits derive from 18 originals. RGB and CIEDE2000 produce the same outcome classifications here, but remain different error metrics.

The one harmful case is `eval_02__stress_color_none`: regional RGB error rises from 6.67 in the input to 31.53 after correction. Both saved alternatives produce the same harmful result. This is not a new regression caused by the facial exception, and selecting one of these alternatives would not fix it.

All 40 usable clean evaluation photos remain unchanged. Fourteen clean measurement failures remain unchanged separately; none has a reference scoring region. Previously exposed clean results are not a general safety certificate.

## Recommended next bounded work

Trace the **15 non-veto core missed opportunities and the single harmful stress decision** through their saved trees. Record the features used, fitting-leaf composition, selected controls, competing saved controls and clean-reference evidence. Use these exact cases selected by the exhaustive taxonomy, not a hand-picked success gallery.

This is a decision-structure diagnosis that does not require DINO access or another fit. It should determine whether the remaining issue is an identity branch grouping different needs or an inappropriate correction direction. Do not change thresholds or relax clean protection based on these evaluation outcomes. A subsequent fit still needs one specific justified intervention and the unchanged joint requirements.

Mask failures remain a parallel problem; this audit cannot certify skin coverage or assign a causal percentage of reconstruction error to masks versus decisions. Keep DINO backbone approval recorded as **pending**, per the user; approval alone would not supply or clear the separate face decoder.

## Verification

Scripts 647–648. Independently reconciled all 756 attempts and 1,512 metric classifications, summary partitions, failure no-ops and source hashes. All passed. Private exact case lists: `outputs/remaining_correction_failure_audit_v1/audit_PRIVATE.json`. No new tests of model accuracy, fits, image-model inference, renders, annotations or source-photo reads. The final eight-group, 24-photo holdout remains byte-unread; the latest candidate remains unadopted.
