# TrueHue: decision needed before the next development cycle

30 October 2026 · Prepared for adviser discussion; not sent. No new collection,
method change or experiment is authorized by this draft.

**Recommendation:** retain ITA + calibrated MST + facial-statistics decision-tree
correction, stop small trials on the current sources, and decide whether a
controlled photographic-reference collection is feasible and within thesis scope.
It would improve reference evidence; it is not a promised fix for the model.

## What the completed comparisons establish

Both cycles used frozen settings and held every source's variants out together.
Lower mean CIEDE2000 is better; numbers are comparable within each row only.

| Completed cycle | Matched evaluation | Endpoint reference | New candidate | Clean originals changed: reference → candidate |
|---|---|---:|---:|---|
| Added reviewed normal variants | 105 cases /26 source groups | 6.964 | 7.561 | 1/26 → 3/26 |
| Added six reviewed sources | 121 cases /32 source groups | 6.613 | 7.956 | 2/32 → 4/32 |

The latest candidate also worsened the four new primary cases versus no
correction:5.439 versus3.782. Neither candidate was adopted. All outcomes and
reviews are preserved; no parameter sweep follows. These are development
results, not independent final validation or proof the method is impossible.
See [primary results](reviewed-primary-training-results.md) and
[source-expansion results](broader-source-comparison-results.md).

## The unresolved evidence

Accepted masks are not evidence of correct reference lighting. Current clean
controls mean “preserve this dataset photograph,” not measured intrinsic skin
color. ITA and mapped MST derive from the same facial color measurements; MST
does not add independent illumination evidence. This is a plausible limitation,
not an established sole cause of the failures. Lighting also affects perceived
skin-tone annotations. [Google Research](https://research.google/pubs/consensus-and-subjectivity-of-skin-tone-annotation-for-ml-fairness/)

The lookup remains experimental and tied to the original mask contract. The
previously **user-reported adviser approval of limited MST evaluation** remains
recorded; this brief does not ask to repeat it. We still need honest category/
subject support, matching masks, exposure disclosure and separate validation.
MST-E remains mapping/evaluation data, never correction-tree training.
See [the existing scope decision](adviser-mst-limited-scope-proposal.md).

## Decisions requested

1. **Reference collection:** may we collect controlled smartphone portraits with
   a neutral/color reference, using the chart only to establish offline targets
   and quality evidence? Runtime would still accept one ordinary photograph;
   no reference-guided inference is proposed. Agree participant access, equipment,
   institutional permissions, budget, sample-size rationale and schedule first.
2. **Claim:** should the target be fidelity to a documented photographic
   reference under stated conditions? Without separate physical measurement,
   avoid claiming recovery of intrinsic/absolute “true skin color.” If collection
   is infeasible, agree a narrower research claim and its remaining limitations,
   rather than repeating the same training cycle.
3. **Separate masking question, currently on hold:** may the original rule-based
   stage be replaced by the better-coverage learned face parser? It still includes
   facial hair and is not integrated. If accepted, document this method amendment
   and rebuild matching measurement/calibration evidence before adoption.
   No additional beard model is proposed for immediate integration.

[Draft capture protocol](controlled-reference-capture-proposal.md) separates
known synthetic inverses from real-lighting captures and proposes person-level
data separation before model use. Scope, counts and quality criteria await
agreement; no thresholds, purchases or recruitment have been assumed.

The software and demo work, but automatic correction is not yet reliable.
Neck correction, final MST validation and Android integration remain unfinished.
Photographer opinions stay after model completion using the existing Google Form.
**Record the adviser decision before another correction cycle; no messages have
been sent on the student's behalf.**
