# Paper-method correction progress

29 October 2026. User reiterates that the implementation must stay aligned with
the thesis. Retain detection → rule-based skin support → ITA → calibrated MST
with facial statistics → decision-tree regression of gamma/red gain/blue gain.
The learned dense-parser experiments remain diagnostic evidence, not an
approved replacement for the paper's masking stage. Android remains paused
while Python is prioritized; expert opinions come after model completion using
the existing Google Form.

## Rule-based containment comparison

Implemented a versioned component-selection refinement using existing HSV AND
YCrCb thresholds, morphology, landmark framing and feature exclusions. Apply
the face contour before selecting the largest connected component. Compare
this against both the saved baseline and removal-only oval clipping on the
same 24 reviewed training references. No new learned segmentation model,
threshold changes, missing-geometry fallback or extra hole filling was used.
The oval is an existing anatomical refinement; this is not a claim that every
implementation detail is explicitly specified in the paper. Its scope/detailed
HSV-versus-YCrCb discrepancy remains documented.

| Rule-based candidate result | Sources |
| --- | ---: |
| At least 1000 selected pixels | 16 |
| Required geometry unavailable | 6 |
| Insufficient color support | 2 |
| Total | 24 |

Inspected 32903 shows reduced selection outside the facial contour. However,
the candidate adds no pixels on these sources and does not recover missing
coverage. Component reordering differs from simple oval clipping only on 25129
(10 fewer pixels). Do not attribute the visible containment gain to component
reordering alone. 43909 remains landmark-unavailable despite visual acceptance.
66413 still illustrates that geometric containment does not identify facial
hair. These are diagnostic results, not new human approvals or mask accuracy.

The candidate cannot yet replace the current mask or solve the correction
model's generalization problems. No further full-batch review is requested.
Keep the 12 reserved training sources closed until a candidate is frozen.

## Reference color suitability

Implemented an explicit reference check for exactly equal B/G/R pixel channels,
plus the user's source rejection. It rejects exact achromatic encoded images,
not all filtered photographs, and introduces no saturation cutoff. Near-gray
or color-cast references still require suitability assessment. It does not
estimate tone, manufacture MST labels, or certify all remaining references.

Audited saved references for 406 non-reserved training sources. **13 exact
monochrome sources are excluded**, including user-rejected 55166; 393 remain
unapproved. The 12 reserved training sources were skipped. Original 418-source
processing records remain intact; the new dispositions are separate and must
be joined before future training eligibility, not mistaken for automatic
modification of older scripts. There were no new raw dataset downloads,
validation/test accesses or correction-model fits.

## Verification and next implementation gates

Saved rule masks were independently reconstructed on 18 geometry-available
cases, including the 2 insufficient-support results; all 24 attempts are
accounted for. Original references, masks, dependency hashes and the old
measurement contract remain unchanged. Tests cover background-versus-face
component selection, preserved color/exclusion holes, missing geometry,
monochrome rejection and near-gray handling. The full suite passed:
**739 tests in 11.24 seconds**.

No perfection or thesis-completion claim follows. Prioritize these concrete
gates before another correction-tree fit:

1. Select a defensible rule-based measurement policy with explicit coverage
   failures and source rejection; do not silently use parser-only acceptances
   as approvals of different rule masks.
2. Freeze that measurement contract, then validate MST calibration on matching
   pixels with disclosed calibration/evaluation roles. Existing thresholds
   cannot be transferred to the new mask without checks.
3. Build training rows only from eligible references; preserve source groups,
   exact identity controls, input-only features, Table2 severity and clipping
   annotations. Dark-severity coverage remains unresolved.
4. Compare the decision tree with no correction using source-separated training
   resampling and the existing clean-harm/benefit gates. Open held-out roles only
   after model and reporting rules are frozen.

These gates preserve the thesis architecture while preventing contaminated
features, unsuitable color references and unsupported model-quality claims.

- [Rule-mask comparison](../outputs/rule_mask_ordering_v1/review.html)
- [Rule-mask verification](../outputs/rule_mask_ordering_v1/verification.json)
- [Predeclared rule comparison](rule-mask-ordering-protocol.md)
- [Reference-quality exclusions](../outputs/training_reference_color_audit_v1/source_dispositions.json)
- [Reference audit summary](../outputs/training_reference_color_audit_v1/summary.json)
