# Discussion, limitations and conclusion — thesis draft

31 October 2026. Based on completed evidence through30 October; no new model
experiment was run for these sections. This is a writing draft for review,
not a declaration that the proposed system or thesis evaluation is complete.
Use alongside the [methods/results draft](thesis-methods-results-draft.md) and
[generated result tables](thesis-results-tables-2026-10-30.md).

## Discussion

The research demonstrates an executable and reproducible Python implementation
of the retained face-detection, skin-selection, ITA, experimental MST and
decision-tree correction sequence. Stage failures are explicit, correction
parameters can be exported in a portable tree representation, and image results
can be traced to source, mask, feature, target and model artifacts. These are
implementation contributions. They do not establish that the estimated
correction reliably preserves natural skin appearance on unseen photographs.

Adding encoded-channel endpoint fractions improved the earlier47-case
development comparison: mean CIEDE2000 decreased from8.013 for its matched
five-feature comparator to5.300, and25 of26 clean originals remained unchanged.
This supports the usefulness of endpoint information within that exposed cohort.
The remaining clean failure prevented adoption. It also shows why a favorable
average cannot be the only acceptance criterion: a method can improve most
distorted examples while visibly altering an image that should remain unchanged.

The two subsequent frozen comparisons tested substantive data changes without
adjusting model settings after observing outcomes. In the105-case primary
comparison, normal-primary error improved from8.312 to6.629, but stress error
worsened from11.279 to18.000 and clean failures increased from one to three.
In the121-case source-expansion comparison, the expanded candidate's total error
was7.956 against6.613 for the endpoint reference, and it changed four of32
clean originals. Its four newly accepted primary inputs had mean error5.439,
compared with3.782 when left uncorrected. Both candidates were therefore rejected.
The totals from the two cycles have different evaluation membership and must
not be interpreted as a controlled comparison between105 and121 cases.

The broader experiment added six source groups, but only two supplied the four
accepted new primary variants. Its negative result does not show that diverse,
well-controlled data cannot help. It shows that this particular reviewed
expansion, with the frozen procedure, did not meet the declared requirements.
More variants of a reference are not independent people, and more approved masks
do not automatically establish better illumination or photographic targets.

ITA and the mapped MST feature are both functions of the measured facial color.
MST provides an ordinal representation of that information; it does not supply
an independent observation of illumination. Confusion between darker natural
appearance and inadequate exposure is consequently a plausible interpretation
of some failures. The experiments do not isolate this as the sole cause, prove
an exact feature ambiguity or establish mathematical impossibility. Mask
selection, limited data, target approximation and the correction operator may
also contribute.

The mapping evidence likewise supports a limited development claim. The later
monotone recipe improved equal-subject ordinal MAE from3.000 for the same-row
median baseline to2.306. However, exact-category accuracy was11.11%, below the
baseline's14.39%, and the packaged lookup emits labels1–9. Development ordinal
improvement is therefore insufficient to claim a validated ten-category MST
estimator. Mapping accuracy and downstream correction quality remain distinct
questions; neither can validate the other by implication.

## Limitations and threats to validity

**Reference validity.** Identity controls mean preservation of a selected dataset
photograph. Reference and mask acceptance do not establish intrinsic skin color
or correct illumination. Approximate reference-fitted targets and the partially
specified augmentation recipe add uncertainty. The supplemental gamma recipe
is a documented engineering choice, not an exact reproduction of every Table2
operation. Synthetic reconstruction is not equivalent to restoring photographs
captured under arbitrary real lighting.

**Data size, selection and exposure.** The latest comparison contains121 cases
but only32 development-exposed source groups. Repeated variants increase case
counts without establishing independent participant coverage. Source/duplicate
groups are not verified person identities. Rejected masks and preparation holds
limit which photographs and distortions enter evaluation. Those counts remain
reported rather than silently removed. Reserved data was not used for the
latest fitting/tuning, but earlier duplicate auditing decoded held-out pixels;
the reserved sets cannot honestly be described as never opened.

**MST support.** The396 measured mapping images represent15 subjects, with180
images lacking same-category fitting-subject support in their held fold.
Measured categories4,5,7,9 and10 each contain only one subject. Historical
development exposure, photographed lighting and weak exact accuracy limit
generalization claims. The prior user-reported adviser approval of limited
evaluation scope is not scientific validation of the lookup. No unsupported
category endpoint should be invented to give an appearance of completeness.

**Masking and image processing.** The evaluated rule-based support can omit
facial skin and include non-skin regions; patchiness and hard correction
boundaries remain visible. Whole-frame square resizing, JPEG artifacts and
encoded-color assumptions can affect detection, support and measurements.
Zero-clipping filters alone cannot establish reference quality. The fuller
learned-parser preview and facial-hair work are separate and currently on hold;
they have not repaired the evaluated correction pipeline. Visible neck
correction remains unfinished.

**Operator capacity and metrics.** Positive direct gamma/gain correction cannot
restore an encoded zero channel, and its unscaled green channel preserves255.
Pixels outside the application mask remain unchanged by design. The saved
RGB-MAE lower-bound audit is not a CIEDE2000 lower bound or an explanation of all
artifacts. CIEDE2000 over a reference mask measures reconstruction disagreement,
not preference, identity preservation or absolute skin reflectance. Real paired
captures with motion would require separately declared alignment and scoring;
the current synthetic geometry does not establish that capability.

**Inference and deployment claims.** Source-held development comparisons are
stronger than fitting-row evaluation, but the repeatedly exposed cohorts are
not independent final validation. No statistical significance or adequately
powered ten-category comparison is claimed. The desktop demo still runs the
older ten-source baseline5/fold1, not the endpoint research reference or either
rejected successor. An executable demo, portable tree or passing software suite
does not establish a completed Android correction system. Android integration
and device evaluation remain paused/unfinished. Photographer opinion scores
have not been collected and must not be inferred from quantitative error.

## Conclusion

TrueHue has produced a functioning research pipeline, portable decision-tree
inference, reviewed and traceable development data, and verified comparisons
under the retained ITA/MST method. Endpoint features improved an early matched
development result, but subsequent normal-data and source-expansion candidates
failed clean-image safety and comparative quality requirements. The evidence
does not yet justify a claim of reliable automatic skin-tone correction or
completion of the original thesis deliverables.

Rejecting those candidates preserves the validity of the evaluation rather than
turning the observed clean failures into source-specific rules. The appropriate
next research decision concerns photographic reference quality, achievable
claims and independently supported MST evaluation. A controlled-reference
collection is proposed for discussion, not assumed to guarantee improvement or
approved for execution. Any parser amendment requires a separate method decision
and matching measurement/calibration evidence.

While that decision is pending, thesis writing, evidence organization and app
usability work can proceed. New training and parser/beard changes remain on
hold. Future work should follow one substantive, predeclared data/method cycle
after the required decision, rather than another series of small same-cohort
adjustments. Photographer opinions remain scheduled after model completion
using the existing Google Form; no messages or recruitment are initiated here.

## Evidence anchors for thesis editing

- [Endpoint feature results](endpoint-feature-tree-results.md).
- [Completed primary comparison](reviewed-primary-training-results.md).
- [Completed source-expansion comparison](broader-source-comparison-results.md).
- [Current MST evidence audit](mst-evidence-checkpoint-2026-10-30.md).
- [Operator and patch limits](patchy-correction-limits-results.md).
- [Adviser decision brief](adviser-decision-brief-2026-10-30.md).

These sections require alignment with the institution's chapter structure and
reference style before insertion. They do not replace independent evaluation,
an adviser response or the unfinished technical requirements.
