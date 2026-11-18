# Reserved clean-photo veto results — 8 November 2026

The reserved clean-photo check removed the unwanted clean edit while retaining more useful corrections than the previous expanded depth-four candidate. It still fell short of the original aligned comparator's recovery requirements, so it has not been adopted.

## What we implemented

- Used the eight development groups frozen in the [protocol](reserved-clean-veto-protocol-2026-11-08.md). Excluded all 227 available conditions from those groups from every correction-tree fit.
- Completed exactly 11 depth-four tree fits using the remaining saved rows, features, costs and actions. The full fit used 890 conditions from 82 clean references across 34 publisher groups. Conditions and folds are not independent people.
- Kept the 56 MST calibrations, masks, features, action choices and clean fitting constraints unchanged. No new MST fits or image-model inference.
- Routed the 20 reserved usable clean photos through each tree and replaced every reached correction leaf with identity. Exactly one leaf per tree was vetoed; no thresholds or other leaf values were changed.
- Preserved pre-veto and post-veto models and evaluated both on the same 756 prepared conditions. No reserved distorted outcome selected the veto.

Four selected clean originals had unusable measurements. They were retained as failures, not replaced or counted as successful safety checks. The reserved groups are already development-exposed and determine the final model behaviour; they are not an independent test set.

## Clean preservation and core recovery

Lower RGB reconstruction error is better. These errors are measured against the original photo in fixed scoring regions, not against intrinsic skin colour or human judgments of naturalness.

| Check | Original aligned comparator | Previous expanded depth four | Reserved pre-veto | Reserved post-veto |
| --- | ---: | ---: | ---: | ---: |
| Unwanted clean edits, development | 2 / 22 | 1 / 22 | 1 / 22 | **0 / 22** |
| Unwanted clean edits, later | 2 / 18 | 0 / 18 | 0 / 18 | **0 / 18** |
| Core RGB error, development | 8.03 | 11.78 | 9.19 | 9.88 |
| Core RGB error, later | 9.76 | 12.12 | 10.11 | 10.94 |
| Core beneficial outcomes, development | 106 / 176 | 74 / 176 | 96 / 176 | 90 / 176 |
| Core beneficial outcomes, later | 84 / 144 | 67 / 144 | 80 / 144 | 75 / 144 |
| Core harms, development | 1 / 176 | 1 / 176 | 1 / 176 | **0 / 176** |
| Core harms, later | 5 / 144 | 0 / 144 | 0 / 144 | **0 / 144** |

All 40 usable clean evaluation photos remain unchanged after the veto. Another 14 clean evaluation photos remain unchanged through the measurement-failure policy; those do not demonstrate learned clean preservation.

The post-veto candidate improves average core RGB error over leaving distorted inputs unchanged (20.65 in development and 21.88 later). It also improves on the preceding expanded depth-four candidate. However, the fixed acceptance comparator remains the original aligned model, against which error is higher and fewer conditions benefit.

Post-veto core CIEDE2000 errors are 4.01 and 4.47, versus the aligned comparator's 3.44 and 4.19. Harm and benefit counts under that metric match the RGB counts above.

## What the veto itself costs

Holding out the reserved groups changes the fitted trees before any veto: core RGB error improves from 11.78 to 9.19 and 12.12 to 10.11. That observation does not prove that using less data generally improves the model.

The veto then removes the clean error in `case_28__clean` and one harmful development core correction, but also removes **six useful development core corrections and five useful later core corrections**. It gains no new core benefits over the same pre-veto model. Stress predictions are unaffected by the veto.

The selected visual examples illustrate the conflict:

- The clean forehead error falls from 24.56 RGB units to zero.
- In an explicitly outcome-selected development combined-overexposure example, error rises from 1.72 to 31.19 when a useful correction is vetoed.
- In an explicitly outcome-selected later overexposure example, error rises from 2.46 to 32.23.

These examples explain the trade-off; they are not independently selected validation evidence. The veto disables a whole leaf, so it cannot preserve the useful action for some photos sharing that leaf while declining it for clean photos.

## Stress results and decision

Post-veto stress RGB errors are 38.79 in development and 43.86 later, versus aligned values of 39.22 and 43.95. CIEDE2000 errors are 15.16 and 16.84, versus 15.26 and 16.68. Beneficial counts remain 40 / 110 and 35 / 90, below the comparator's 45 and 43. One later stress harm persists under both metrics; development has none.

**Rejected under the unchanged joint requirements.** Clean preservation passes, but core RGB/colour error, core/stress beneficial counts and later stress colour error do not all meet the aligned comparator. No integration, additional reservation seed, reserve-size change, depth sweep or criteria relaxation follows automatically.

The separate eight-group, 24-photo final holdout remains byte-unread. The zero-clean result comes from previously exposed development evaluation groups and does not establish real-world clean-photo safety. Mask fragmentation, missed skin, beard/glasses uncertainty, correction boundaries, acquisition cues, synthetic coverage and incomplete highest-tone coverage remain limitations. The proposal's final evaluation design remains unfinished.

## Verification and artifacts

Independent fitting replay verified 11 trees, 303 nodes, 272,889 greedy split options, 880 repeated fitting-clean constraints, all 756 pre-veto predictions, exact reserved-group exclusions, and preserved matrices/calibrations. It also verified all 11 leaf vetoes, 220 repeated reserved-clean checks and final predictions. These 220 checks reuse the same 20 clean references across fits.

Both stages passed independent pixel/metric/protection replay: 756 outputs, 560 regional records, 756 scene records and 20,136 source hashes per stage, plus colour summaries and harm/benefit transitions. Across all attempts, post-veto whole-scene RGB harm counts are zero except for the one later stress case. The final visual review covers 59 fixed boards on 15 contact sheets, four outcome-selected aligned-comparator diagnostics, and three pre/post attribution boards (one fixed clean case and two outcome-selected losses). This does not claim visual inspection of all outputs or every pre-veto board.

Focused tests: **8 passed in 2.74 seconds**. Scripts 629–633; private models in `outputs/reserved_clean_veto_models_v1`, attribution comparison in `outputs/reserved_clean_veto_pre_comparison_v1`, and final comparison in `outputs/reserved_clean_veto_comparison_v1`. Legacy evaluator filenames/titles do not imply a change to the whole-scene feature contract. The inherited `new_fitting_cases` source list describes the earlier expanded cohort; the actual fitted row lists are `training_cases`, with reserved conditions explicitly recorded and excluded.

## What this establishes

A reserved clean veto can prevent this observed clean regression without cancelling all corrections. Its whole-leaf action still discards useful recovery. The next model decision must address that shared-leaf conflict; changing the reservation seed or reducing clean protection to improve the reported average would not resolve it. No further fit has been started.
