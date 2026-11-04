# Corrected-image comparison with identical model settings

23 October 2026. Follow-up to [additions-only boundary](additions-only-boundary-results.md).
Development experiment only; no fitting, runtime adoption or cohort promotion.

Later user requirement: [include the visible neck](face-and-neck-correction-requirement.md).
These face-region reconstruction metrics do not establish neck performance.
Correction-strength failures remain relevant before expanding the affected area.

## Comparison contract

All38 saved square hair-clean-generation attempts were considered, including
held training-source probes. Baseline HSV/YCrCb input Lab/ITA features were
recomputed and checked against earlier values. The frozen original decision
tree predicts **once per successful input**; identical gamma/red/blue parameters
are then applied through three masks: original material/hair support,
unrestricted YCrCb support and the additions-only boundary candidate.

No clean-reference statistics, inverse targets or YCrCb feature substitutions
enter prediction. The old model was trained on the tiny224 pilot, so this is
a diagnostic at256, not evidence that it is validated for the new resolution.

Reference and scoring regions are identical across methods: resized source
photo and hair-clean generation mask. Error is relative synthetic reconstruction
under an sRGB assumption, not calibrated true skin color. Outside-generation
error measures induced changes outside the synthetic region, not annotated
hair/clothing error. No-correction outside-generation error is zero here.

## Outcomes

37 inputs succeeded, producing111 corrected PNGs and148 metric rows including
no correction. Source22454/color remains excluded for insufficient baseline
skin pixels. Its experimental YCrCb support does not supply missing baseline
features, so it is not substituted into this comparison.

Mean CIEDE2000 on the common generation region; lower is better:

| Development source role | Pairs/sources | No correction | Original mask | Unrestricted YCrCb | Additions boundary |
| --- | --- | ---: | ---: | ---: | ---: |
| Training-source probes | 30/7 | 6.153 | 6.320 | 5.988 | 6.006 |
| Development-validation | 3/1 | 10.768 | 7.061 | 6.670 | 6.690 |
| Clipped stress | 4/4 | 7.176 | 13.753 | 13.754 | 13.754 |

The new mask modestly improves the one-source development color-error mean.
It is slightly worse than unrestricted YCrCb on the scoring region but induces
less outside-region change: normalized outside RGB MAE0.000908 versus0.001462
on development, compared with0.000624 for the original mask. Thus the boundary
reduces the unrestricted candidate's side effects but does not eliminate
existing baseline spill or outperform the original outside-region behavior.

These values must not be compared directly with older7.61/6.62 results using
different resolution/generation masks. The training-source probes overlap the
model's development sources; they are not held-out validation, and validation
contains one subject-unverified source. No final-test or fairness result follows.

## Main remaining failure: correction settings

Completed follow-up: [fixed source-held-out controls comparison](correction-controls-sourcecv-results.md).
Adding controls helps on average but does not resolve unnecessary corrections;
the experimental fold models were not promoted to the runtime.

Training-source variants, scored separately to avoid hiding controls:

| Variant | Pairs | No correction | Original mask | Additions boundary |
| --- | ---: | ---: | ---: | ---: |
| Dark | 7 | 13.122 | 4.228 | 3.269 |
| Color shift | 6 | 8.063 | 6.503 | 6.032 |
| Bright/warm, unclipped | 3 | 8.391 | 5.656 | 5.656 |
| Unchanged control | 7 | 0.000 | 7.415 | 7.415 |
| Mild brightening | 7 | 2.739 | 7.446 | 7.463 |

All seven unchanged inputs are altered by the old model. Its old fitting set
did not include these unchanged/mild additions. Larger mask coverage cannot
solve wrong correction parameters; it can spread the wrong adjustment farther.
Stress remains substantially worse than no correction under every mask.
An unchanged source is a synthetic reconstruction control, not a calibrated
claim that the original photo can never need real-world correction.

## Visual review and disposition

Codex inspected all37 successful rows on eight source boards. Color-shift
patchiness improves noticeably in62331 and parts of12288/19, but forehead/side
seams remain in12288,22211 and22454/dark. Binary generation boundaries and
unchanged anatomical regions remain visible. Bright stress, identity and mild
inputs show parameter-driven overcorrection. This is not photographer MOS.

Keep the additions-only mask fixed as a development candidate and stop using
mask tuning to address wrong adjustment strengths. Next, plan a source-grouped
comparison of correction learning that includes unchanged/mild controls and
reports failures/held cases, without touching reserved evaluation sources.
Keep the no-correction baseline, mask policy and metric region fixed. Preserve
the old model for comparison; do not claim the30 candidate pairs are a finalized
thesis cohort or silently bypass unresolved MST/dataset/method decisions.

The existing hair/paint mask regression is retained, but these37 images do not
constitute a new labeled paint challenge. No universal material-protection or
deployment-readiness claim is made.

## Evidence and verification

- [Corrected-image boards](../outputs/corrected_mask_comparison_v1/review-index.md)
- [Full parameters and metrics](../outputs/corrected_mask_comparison_v1/summary.json)
- [Saved-output verification](../outputs/corrected_mask_comparison_v1/verification.json)
- [Visual assessment](../outputs/corrected_mask_comparison_v1/visual_assessment.json)
- Script60: `scripts/60_compare_corrected_mask_outputs.py` (refuses overwrite).

All111 PNGs were checked against an independently written gamma/gain formula
using each pair's one parameter vector. Pixels outside each support are
unchanged; original-mask output pixels are identical under the additions mask.
All38 attempts,148 metrics, original model/table/review hashes and baseline
feature checks passed. Existing full suite: **464 passed**.
