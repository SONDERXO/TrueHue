# Three-variant development candidate set

29 October 2026. Implemented a versioned decomposition of the paper's Table2
settings into three distorted versions per source, with a separate unchanged
control. **The grouping and unspecified numeric conventions are explicit
engineering choices, not recipes supplied verbatim by the proposal.**

- Exposure: direct gamma → contrast → brightness.
- Color: additive red/blue shifts, green unchanged.
- Combined: direct gamma → contrast → brightness → red/blue shifts.

Use the existing Table2 severity values without tuning: contrast about0.5,
brightness and channel offsets divided by255, one final clip and uint8 round.
These remaining units/order choices are documented. The gamma definition
matches PDF38; the table's “midtone” versus darkening wording remains a paper
ambiguity. Existing legacy recipes, models and target meanings remain intact.

## Generated evidence

The same20 technically usable accepted original-mask references now supply
**80 candidate attempts:20unchanged controls plus60distortions**. All variants
inherit source/duplicate group and use the source's existing estimated severity.
No reserved training check or validation/test source was used. Reference
approvals and exact concerns, including16033hair, are retained.

| Variant | Attempts | Available approximate targets | Existing support-screen passes | Inputs with any clipping | Summed clipped support pixels |
| --- | ---: | ---: | ---: | ---: | ---: |
| Exposure | 20 | 20 | 17 | 17 | 31,235 |
| Color | 20 | 19 | 5 | 2 | 15 |
| Combined | 20 | 19 | 6 | 17 | 13,650 |

All60 inputs produced technical measurements. Color and combined targets for
14418 are unavailable because selected input support has no usable overlap
with reference support; no fallback was supplied. All20 combined inputs match
the previous direct-gamma version byte for byte. Identity controls keep exact
target[1,1,1] and verified original input features.

This diagnostic separates a remaining failure mechanism: color-only inputs
have almost no clipping but poor retention under fixed color thresholds,
whereas exposure-only inputs pass the existing retention screen much more
often. This suggests chromatic sensitivity deserves targeted investigation,
not further claims that darkness/clipping alone explains mask losses. The
exploratory screen and original masks are not skin ground truth, so these are
not mask accuracy or learned correction success rates.

The unclipped, screen-passing, target-available counts are2exposure,4color,
0combined. These six are still unreviewed variant-mask candidates, not six
automatically eligible training pairs. Preserve the clipped stress route,
unavailable targets, all original source concerns and held fitting status.

## Verification and next gate

Scripts233/234 reconstruct all60distortions and clipping records, verify80
input feature vectors,58approximate target curves and residuals, and20prior
combined-image parity checks. Each input uses its own detection/mask; reference
support supplies only generation/target/scoring evidence. The original
measurement contract and experimental MST artifact remain unchanged and are
not newly validated. Explicit reciprocal-gamma conversion preserves the old
optimizer report while naming the new target coordinates correctly.

The full suite passed **762 tests in21.56seconds**. This is software and
artifact verification, not completed correction-model validation. No
regression tree was fitted, no input-mask approval fabricated, and no active
model/calibration/Android asset was replaced.

Next, resolve color-shift mask robustness and freeze per-variant dispositions
before a source-separated correction comparison. Keep the three variants and
identity controls grouped by source; do not select only favorable variants and
call the resulting cohort the full design. No new full-source review batch is
requested: these are the same20already reviewed photos under distinct inputs.

- [Candidate comparison boards](../outputs/three_variant_training_candidates_v1/review.html)
- [All80attempts and exact holds](../outputs/three_variant_training_candidates_v1/attempts.jsonl)
- [Per-variant summary](../outputs/three_variant_training_candidates_v1/summary.json)
- [Verification](../outputs/three_variant_training_candidates_v1/verification.json)
- [Declared recipe/protocol](three-variant-augmentation-protocol.md)
