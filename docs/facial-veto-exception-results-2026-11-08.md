# Facial exception to the clean veto — results

8 November 2026. The fixed exception restores four useful corrections while leaving all 40 usable clean evaluation photos unchanged. The gain is small and does not meet the original comparator's joint recovery requirements. The candidate remains experimental and unadopted.

## What changed

Applied the [frozen protocol](facial-exception-to-veto-protocol-2026-11-08.md) to the existing 11 reserved-clean-veto configurations. Only an explicitly vetoed leaf can regain its original correction, and only if a usable input's facial Lab/ITA falls strictly outside at least one frozen clean range. Equality retains identity. Missing or invalid measurements cannot enable correction.

No new tree, gate, MST or target fitting. No new masks, inference, images or annotations. All original trees, actions, features, group exclusions and calibrated MST remain unchanged; the exception is a separate decision rule over those saved models. The original tree still uses scene features for routing, so this is not a background-independent system.

## Results

Lower RGB reconstruction error is better. Benefits and harms compare each corrected condition with its distorted input within the fixed scoring region.

| Check | Original aligned comparator | Reserved clean veto | Facial exception |
| --- | ---: | ---: | ---: |
| Unwanted clean edits, development | 2 / 22 | 0 / 22 | **0 / 22** |
| Unwanted clean edits, later | 2 / 18 | 0 / 18 | **0 / 18** |
| Core RGB error, development | 8.03 | 9.88 | 9.73 |
| Core RGB error, later | 9.76 | 10.94 | 10.36 |
| Core beneficial conditions, development | 106 / 176 | 90 / 176 | 91 / 176 |
| Core beneficial conditions, later | 84 / 144 | 75 / 144 | 78 / 144 |
| Core harms, development | 1 / 176 | 0 / 176 | **0 / 176** |
| Core harms, later | 5 / 144 | 0 / 144 | **0 / 144** |

The exception gains one core benefit in development and three later, losing none of the veto candidate's benefits under either RGB or CIEDE2000. The four restored conditions come from **two original photos**, including three distortions of one later original. They are not four independent photos or people.

Core CIEDE2000 improves from 4.01 to 3.97 in development and 4.47 to 4.29 later. The aligned comparator remains better on average at 3.44 and 4.19. The candidate still improves over leaving core distorted inputs unchanged (RGB 20.65 and 21.88), but this does not replace the agreed comparator.

Stress outcomes are unchanged from the veto candidate: RGB errors 38.79 and 43.86, CIEDE2000 errors 15.16 and 16.84, benefits 40 / 110 and 35 / 90, with zero development harms and one later harm under both metrics. The aligned comparator has 45 and 43 beneficial stress outcomes and lower later stress colour error (16.68).

The other 14 clean evaluation photos remain unchanged because measurements failed. They are separate from the 40 usable clean photos and are not evidence of learned protection.

## Visual and verification findings

- Independently replayed all 756 exception decisions, frozen clean bounds and 1,100 repeated fitting/reserved clean-reference occurrences. Nine boundary/failure checks passed, including equality and missing/nonfinite measurements. These reuse the same originals across configurations.
- Verified that the other **752 rendered outputs and candidate metric records exactly match** the veto candidate. All four restored outputs exactly match their frozen pre-veto counterparts.
- Inspected all four changed-condition boards, selected exhaustively by the rule's decisions rather than ranked by improvement. Existing review of unchanged outputs is reused; no claim of a new inspection of all 59 fixed boards.
- The restored edits still show partial facial coverage and visible patch boundaries. Numerical improvement does not establish acceptable naturalness or complete skin masking.

The full independent replay passed: 756 native outputs, 560 regional records, 756 scene records, 20,140 bound source hashes, colour summaries, transitions and protected/outside-alpha pixels. The nine direct boundary checks exercise the new rule's boundary and failure behaviour.

## Decision and limits

The candidate fails the unchanged joint requirements: core errors remain above the aligned comparator, beneficial core/stress counts remain below it, and later stress colour error remains worse. Clean preservation and zero core harms are progress, but do not qualify it for adoption or opening the final holdout.

Keep the policy frozen. Do not tune its ranges, add margins, select different features or alter the reserved groups after seeing this outcome. The separate eight-group, 24-photo final holdout remains byte-unread. No demo or Android integration occurred.

This is evidence from previously exposed development cohorts with synthetic distortions and uncertain masks. Outside a clean feature range does not prove that an unseen photo needs correction. The study does not establish real-world safety, fairness, true skin colour recovery or perceived naturalness. The proposal's final evaluation design remains unfinished.

Scripts 636–640. Private outputs: `outputs/facial_veto_exception_models_v1` and `outputs/facial_veto_exception_comparison_v1`. Legacy filenames/titles inherited from the evaluator do not change the model's feature scope. This turn adds zero fitted models and no new accuracy claim outside the existing development evaluation.
