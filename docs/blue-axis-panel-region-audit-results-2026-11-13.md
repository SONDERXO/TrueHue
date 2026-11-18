# Six-case saved panel and scoring-region audit

13 November2026. User authorized inspection after the saved route diagnosis. [Fixed protocol](blue-axis-panel-region-audit-protocol-2026-11-13.md); scripts/audit_blue_axis_panel_regions.py; outputs/blue_axis_panel_region_audit_v1. Agent viewed the six-row contact sheet showing original input, saved output, photographic reference and selected scoring contour. No new correction was rendered and no ratings were changed.

Exactly the six input-preferred cases04,12,16,24,48,52 were inspected. This selected diagnostic set cannot estimate overall accuracy or tone-group bias. Source PNG/alpha/protection hashes agree with the prior verification. All six original primary RGB/DE metrics replay within1e-10. Fixed core/feather/outside partitions and unchanged protected/outside pixels were checked; no favorable new region substitutes for the frozen gate.

| Case | Scored fraction of crop | Primary DE benefit | Whole-crop DE benefit | Blue forward-clipped pixels inside scored region |
| --- | ---: | ---: | ---: | ---: |
| 04 red-cast | 40.4% | 0.429 | 0.173 | Not applicable |
| 12 blue-increase | 42.3% | 1.784 | 0.754 | 0 |
| 16 red-cast | 23.5% | 1.766 | 0.415 | Not applicable |
| 24 blue-increase | 36.2% | 1.707 | 0.618 | 0 |
| 48 blue-increase | 30.8% | 2.147 | 0.662 | 3 |
| 52 red-cast | 40.6% | 0.144 | 0.058 | Not applicable |

Positive means output is numerically closer to the photographic reference. Whole-crop benefit stays positive in all six cases. Because the renderer leaves alpha0pixels unchanged, whole-crop mean benefit is exactly primary benefit multiplied by its crop fraction. Region size dilutes the mean improvement; it cannot reverse that sign here. The full-frame metrics therefore do not explain these input preferences through a simple region-sign reversal. Perceptual emphasis on particular features or boundaries is not measured by this arithmetic.

For the three blue-increase cases, forward clipping inside the scored region is0,0,3pixels, versus5104,8,152outside. Thus whole-image clipping counts previously cited were mostly irrelevant to scored-skin residuals. Clipping cannot be asserted as a common explanation for the three input preferences. Within the primary region, red and green equal the reference exactly; blue mean absolute residual is approximately0.213,0.215,0.252code levels. The saved correction recovers those skin colours closely numerically; feathering and rounding still permit residual differences. This is not proof of perceptual preference or physical colour truth.

Visual inspection shows the same partial-correction context: faces/visible skin are corrected inside the saved outlines while hair, clothing and background retain the synthetic edit. Output skin appears close to the photographic reference in these blue-increase panels, with subtle differences at this analysis presentation. The contact sheet does not reproduce the user's physical display or establish which view they should prefer. No conspicuous new corruption was identified in this limited inspection; this is not a mask-accuracy validation, a substituted expert judgment or a new rating. Red-cast outputs continue to reflect the previously demonstrated wrong-axis/diluted correction, especially the weak red restoration and added blue; their numeric improvements are not equivalent to correct channel recovery.

**Conclusion:** the audit rules out a simple whole-frame mean-sign reversal and widespread scored-skin clipping as explanations for these three blue-increase preferences. The precise perceptual cause remains unresolved without additional evidence. Do not infer a user error, rewrite ratings, strengthen already nominal controls, remove unfavourable cases, reclassify the candidate or create a new pass criterion. The blue-axis route remains NOT_READY/CLOSED/NOT_ADOPTED; no further fit or repeated review is selected by this audit.

The practical limitation is now explicit: red/blue-decrease axis separation still needs a distinct learning rationale, while nominal blue-increase restoration already disagrees with some human preferences. Additional model capacity alone is not established as the solution to both. Any future correction-method proposal must address these separately and preserve the paper's photographic restoration goal and darker-skin priority. Independent tone-labelled qualification remains unestablished.

Read18savedPNGpanels and six bound alpha/protection pairs (some sources are shared), not NPZs/raworiginals/lockedholdouts. Added only diagnostic metrics/contact-sheet artifacts. All historical outputs, ratings, supports and the earlier frozen accepted recipe are unchanged. No fits/newpredictions/newcorrectionrenders/Android/manuscript changes. Modelunfinished/paperpaused/November14complete-deliverytargetatrisk/timeunspecified.
