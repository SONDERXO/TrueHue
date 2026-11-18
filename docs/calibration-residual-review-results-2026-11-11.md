# Saved calibration residual review — 11 November 2026

The expanded recipe retains a systematic brightness-associated error pattern
across these ten exposed development subjects. The loss on original conditions
is not confined to a single outlier. This is a diagnostic finding, not a new
model, proof of physical causation or evidence that the user's masks are wrong.

Scripts 770–771 inspect saved sixty-row features, predictions, ten model
coefficient sets and thirty matched subject/lighting-family pairs. No images,
prediction APIs or fits are used. All frozen admission failures remain unchanged.

| Group | Candidate signed bias | Comparator signed bias | Cases improved / worsened |
|---|---:|---:|---:|
| Original 600 captures | +0.867569 | +0.000317 | 8 / 22 |
| Brighter 1200 captures | −0.916179 | −2.315083 | 27 / 3 |

Positive bias means predicted MST exceeds the exact publisher decimal score.
For **all thirty matched pairs**, reviewed L* increases and predicted MST
decreases, while each person's reference remains unchanged. The candidate's
average paired decrease is 1.783748 MST units versus 2.315400 for the comparator.
The candidate paired changes range from −2.907607 to −0.591120.

| Lighting family | Candidate mean paired change | Comparator mean paired change |
|---|---:|---:|
| F_cool | −0.870127 | −1.231941 |
| H_warm | −2.449039 | −3.127445 |
| L_warm | −2.032078 | −2.586814 |

This occurs in every subject/family pair, not thirty independent subjects.
Capture conditions also alter colour and reviewed mask selections; the pair
comparison cannot isolate illumination alone. Statistical significance or a
universal population claim is not established.

Within-person-centered candidate signed error has descriptive Pearson
correlation −0.970396 with L*, −0.208173 with a*, −0.235582 with b*, and −0.108561
with ITA. These repeated observations and correlated features do not establish
causal attribution or justify selecting a new feature from the four correlations.
Only two original and six brighter cases lie outside a fitting-fold feature
marginal range, so passing those range checks plainly does not guarantee accurate
estimation. Conversely, marginal overlap is not joint support or transfer proof.

The recipe is affine in the four input coordinates after standardization. It
has no constraint making a person's estimate invariant across illumination.
Pooling reviewed brightness examples reduces brighter-condition underestimation
while moving original-condition estimates upward. The changed affine terms
exactly reconstruct all sixty recorded raw model shifts; that decomposition is
coordinate dependent and not causal evidence for a particular coefficient fix.
The recorded arithmetic passes independent replay. The failed comparison is
therefore not explained by a demonstrated arithmetic or saved-model binding bug.

Independent verification checks sixty residuals, thirty exact pairs, all
condition/person/illumination bias and MAE summaries, sixty affine shift sums,
and four centered correlations without fits or image reads. Private evidence:
`outputs/combined_calibration_residual_review_v1`.

The appropriate next step is a **design feasibility review of illumination
stability using the existing paired evidence**, before selecting another
calibrator. Any future proposal must preserve single-photo inference, ITA/MST
and the final decision tree, use no condition label or identity at inference,
keep subject-disjoint evaluation and the original-preservation gates, and address
accuracy as well as stability. This review selects no new estimator, penalty,
normalization, sweep or fit. It does not establish that an illumination-stable
MST estimate is identifiable from these four single-photo statistics. Additional
mask edits are not requested; seven photographic inputs still exceed reviewed
brightness coverage. Neither saved model is qualified for that application.

No acquisition, contact, upload, commit, runtime or Android changes occurred.
All prior artifacts remain preserved; final 24 and older locked images remain
byte-unread. The fixed failed comparison stays closed with admission flags false.
