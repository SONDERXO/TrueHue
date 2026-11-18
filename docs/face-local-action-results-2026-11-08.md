# Face-local context comparison — 8 November 2026

Using context from the face crop removes the outside-crop sensitivity by
construction, but makes correction performance worse. **The candidate is rejected
and not integrated.** This does not mean scene shortcuts are acceptable or that
the task cannot be solved; outside-crop invariance alone is insufficient.

The user's instruction to keep working authorises completing the recommended
fixed comparison. Exactly11joint trees were fitted: ten saved held-publisher-group
folds and one full development tree. Only the seven context summaries changed
scope from whole photograph to native actual-input face crop. All fitting rows,
fourteen-action libraries, native blended pixel costs, depth3/minleaf1/greedy
settings, clean constraints, masks and splits stayed fixed. The five facial
Lab/ITA/MST inputs and saved nested calibrations were reused unchanged. There
were no new MST, target, gate, parser, detector, landmark or FaceOcc fits/forwards.

## Same-support results

| Measure | Saved aligned parent | Face-local candidate |
| --- | ---: | ---: |
| Development clean photos changed,22usable | 2 | 3 |
| Later clean photos changed,18usable | 2 | 3 |
| Development core RGB MAE,176scored conditions | 8.03 | 12.45 |
| Later core RGB MAE,144scored conditions | 9.76 | 13.69 |
| Development core harmful conditions | 1 | 10 |
| Later core harmful conditions | 5 | 13 |
| Development stress RGB MAE,110scored conditions | 39.22 | 39.55 |
| Later stress RGB MAE,90scored conditions | 43.95 | 44.04 |
| Development stress harmful conditions | 0 | 1 |
| Later stress harmful conditions | 1 | 2 |

Core benefits fall106→76development and84→68later; stress benefits fall45→40and
43→35. Equal-publisher-group mean errors also worsen. All predeclared clean,
core and stress acceptance checks fail. Do not pool these conditions as people.

There are still756attempts,451available measurements and560region-scored
conditions. Some measurement failures have a usable clean reference region and
are scored as no-ops; this explains why scored and measurement-available counts
differ. Fourteen clean measurement failures remain separate from learned clean
preservation. No failed source or condition was replaced.

## Changed errors and visual findings

The four former unwanted clean edits are now unchanged. However, six other clean
photos are changed: case_01,case_03,case_14,eval_04,eval_16,eval_18. Regional RGB
MAE introduced ranges25.76–32.39; these are not small neutral edits. The worst
development/later core excess errors are32.19and30.73. The two selected worst
core cases are colour-only inputs incorrectly receiving darkening behavior.

Across11trees,34splits use crop L90,10crop L10 and1crop L50. Other splits use
crop chroma or facial Lab; none selects ITA or MST, though both remain available.
The representation still allows absolute local appearance to stand in for
illumination. This observation is not a controlled proof of reflectance/lighting
ambiguity or mask causality.

All59fixed boards were inspected in15contact sheets, plus four explicitly
outcome-selected worst clean/core boards. New clean darkening/brightening,
fragmentary boundaries and lost recovery are visible. Unavailable cases remain
unchanged. The gallery is private:
`outputs/face_local_action_comparison_v1/review_PRIVATE.html`.

## Verification

Scripts588–592 fit, evaluate, verify and assess this comparison. Independent
training verification checked2270nested feature rows,220repeated fitting-clean
constraints,165nodes,53865candidate split options and all756predictions. All
reused calibration, fitting membership, action and cost arrays match the parent.
There were exactly11research tree fits; verification refits none.

Independent output verification reproduced all756RGB8outputs,560regional and
756scene metric records, checked protected/outside-support equality and summary
counts. Original and prior experiment source hashes remain unchanged. Native
crop feature invariance was checked against all three fixed outside contexts.
Invariance is a construction check, not independent correction accuracy.

The focused existing action-tree/blended-cost suite passed8tests in3.14seconds.
Its small generated fixtures are software checks, not additional research-photo
fits or validation. A hash-bound visual-review completion receipt is saved with
the private comparison outputs.

Private model/comparison outputs remain ignored under
`outputs/face_local_action_models_v1` and `outputs/face_local_action_comparison_v1`.
All earlier artifacts remain preserved. No Android/desktop integration, external
sharing, scientific admissions, commit or push occurred.

## Consequence for continued development

Close this single scope comparison. Do not try progressively adjusted crop sizes,
percentile subsets or thresholds to chase these same clean examples. The next
substantive design must address illumination evidence and action direction,
including the colour-only cases darkened here. A model that only learns absolute
brightness shortcuts in a smaller region does not meet that requirement.

Existing small exposed cohorts, synthetic distortions, unverified masks and
RGB-versus-naturalness limitations still apply. The correction model is unfinished;
this cycle provides a rejected intervention, not an integration-ready model.
