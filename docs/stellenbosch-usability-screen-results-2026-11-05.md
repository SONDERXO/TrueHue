# Case-level skin usability screen — 5 November 2026

The requested screen is complete for all30latest cases. The assistant recorded
18visually usable selections,7uncertain selections and5pipeline failures, with
an individual reason and source/mask hashes for every case. **Visually usable
means plausible selected facial skin for development assessment, not automatic
calibration admission or validated colour measurement.**

Scripts452–453 followed the [frozen visual rubric](stellenbosch-usability-screen-protocol-2026-11-05.md).
All30native crops, normalized masks, selected original colours and native-grid
mask zooms were inspected. Native crops were also shown without enlargement;
nearest-neighbour zoom adds no detail. Source scores were hidden on boards,
but prior exposure means this was neither blinded nor independent review.

## Outcomes with full denominators

| Previously declared descriptive score interval | Visually usable | Uncertain | Failed | Attempts |
|---|---:|---:|---:|---:|
| [1,3) | 6 | 0 | 0 | 6 |
| [3,5) | 6 | 0 | 0 | 6 |
| [5,7) | 3 | 2 | 1 | 6 |
| [7,9) | 3 | 2 | 1 | 6 |
| [9,10] | 0 | 3 | 3 | 6 |
| All | 18 | 7 | 5 | 30 |

Six of ten publisher subject keys have three visually usable conditions. Each
condition has6/10visually usable selections. These are small-sample observations,
not estimated population performance. Intervals are descriptive sampling aids,
not integer MST categories. All source decimals and original failure reasons
remain unchanged; no uncertain case was silently counted as a failure or success.

## What the individual review adds

Many selections visibly follow cheek, forehead and chin skin without an obvious
dominant object. They can still contain small hairline/feature-border errors.
Missing central or lower-face skin is recorded separately: incomplete coverage
alone is not proof that the remaining selected pixels are non-skin. In particular,
the screen does not reject every partial face or impose perfect contour accuracy.

The seven uncertain selections involve glasses/reflections or very dim, sparse
or fragmented native support. The highest-interval selections include narrow
forehead strips and a fragmented broader face; detail/context is insufficient
for a confident usability judgement. This is not a numeric pixel cutoff, a
label-driven exclusion rule, or proof that those photos cannot ever be measured.
No intrinsic colour reference or new dense annotation requirement is invented.

The five failed cases retain two detector failures, two no-skin-overlap parser
failures and one below-minimum parent measurement. No model was rerun or mask
changed in this screen. Assistant decisions are not attributed to the user,
an expert or the adviser. No annotation task has been imposed on the user.

## Conditional model-comparison decision

This screen **does not establish a defensible cohort for the proposed cross-score,
cross-lighting calibration claim**. The visually plausible subset has no highest-
interval cases and only six complete subject keys. Promoting those18photos to a
general calibration cohort would conceal uncertainty and missing score coverage.
In addition, the preceding shared-location check showed large original-colour
ITA variation; the new contextual estimator has no real-data evidence yet.

Therefore no real-data ridge/median comparison was run, no admission flag was
changed to true, and neither MST calibration nor the correction tree was fitted.
The generated-data implementation remains available for a separately justified
cohort. This does not prove that an explicitly limited exploratory question is
mathematically impossible; no such narrower scope or adequate support has been
established here. Software fit capability is not the reason to fit this subset.

Close the repeated30case review/enhancement sequence. Do not recommend another
automatic mask sweep or the same usability audit. If data development continues,
the next substantive option is a separately specified, source-first cohort using
different preselected subject keys, the frozen candidate and an explicit support
screen, retaining every uncertain/failing case. Its size/roles/acceptance need
justification before processing; it is not activated here. The result does not
reject all285subjects or require another dataset, recruitment or author contact.

## Verified record and privacy

All bound original inputs and parent artifacts remain hash-identical. Source
and final-mask identities are bound case by case; all30membership/decimal/status
records and JSON/CSV dispositions match. Counts reconcile to25technical passes,
five failures, ten subject keys and six complete visually usable groups. No
new software algorithm was changed in this visual-record task; script assertions
and source/CSV checks were run, with no new pytest/full-suite claim. The earlier
55focused contextual-method tests remain historical software evidence.

Private native/mask gallery: `outputs/stellenbosch_usability_screen_v1/review_PRIVATE.html`.
Individual decisions: `outputs/stellenbosch_usability_decisions_v1/decisions_PRIVATE.json`
and matchingCSV. All are ignored local evidence. Individual scores, photos,
identifiers and decisions must not be redistributed without author consent;
research/noncommercial use and citation conditions remain. No dataset upload,
model inference, fits, admissions, runtime/Android changes, paper approval,
contacts or participant requests occurred.
