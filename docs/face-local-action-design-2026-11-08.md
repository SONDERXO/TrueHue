# Face-local action learning: proposed fixed comparison — 8 November 2026

## Evidence and intended change

The completed scene-context diagnostic holds each actual native face crop and
five facial/MST inputs fixed, while replacing only the outside scene with RGB32,
RGB128 or RGB224. All 451 usable conditions change action under at least one
replacement, and all disagree across replacement contexts. These conditions come
from 54 original photos, not 451 independent people. There are 305 unavailable
attempts in the full756 ledger; they are not successful invariance cases.

For example, the same clean eval_13 face receives gamma about0.700,1.428 or2.278
under the three surrounds: brightening, darkening or stronger darkening. This
isolates exported-tree sensitivity to outside-crop pixels under frozen masking;
it does not test how detection/masking would respond to an edited scene. The
artificial flat surrounds are deliberately extreme diagnostics, not natural
lighting simulations. No benefit or fairness claim follows.

Proposed change: compute the seven existing context summaries on the saved
actual-input **native face crop**, rather than the entire photograph. Retain
their definitions: log red/green, log blue/green, L10/L50/L90, any-zero and any-full
fractions. Name them `face_crop_*` in a new input contract. The original five
facial Lab/ITA/MST inputs remain exactly unchanged. This is a scope change, not
removal of brightness information and not a gamma-only feature restriction.

This cannot guarantee preservation of unseen clean photos: crop lightness still
mixes natural complexion, illumination, hair and objects. It supplies a concrete
test of a justified local representation, not a claim that the ambiguity is solved.
The crop also contains some background; only pixels outside it are excluded.

## Exact bounded training plan — not yet run

- Reuse the aligned preparation and its existing masks, alpha, scoring regions,
  measurements, failures, publisher-group splits and original synthetic recipes.
- Reuse all saved nested matching MST predictions and exclusions. No MST refit
  is needed because its four raw facial measurements do not change.
- Recompute only the seven context entries for every available row from its
  current saved native crop. Use the same scope for fitting and evaluation.
- Fit exactly11joint action trees: the same10held-publisher-group folds and full
  development fit. Reuse each fit's14action library and native blended cost
  matrix. Same greedy depth3/minleaf1/ties/clean feasibility and fitting rows.
- No parser, detector, landmark or FaceOcc forwards; no new targets, labels,
  dataset, action library, threshold, gate or capacity adjustment.
- Preserve all756evaluationattempts and original comparison supports. Failed
  measurements remain unchanged; no frozen original masks are borrowed for
  distorted inputs. Later-photo references never enter fitting or calibration.
- Compare original saved aligned-tree controls with the candidate on the same
  existing native regions and alpha. Record both per-condition and per-group
  results and paired availability. Do not compare with older differently masked
  2.83/6.00 figures.

## Acceptance and stopping rule

The development target remains zero changed clean photos on the22usable
development and18usable later originals;14failed clean measurements are reported
separately, not counted as learned protection. Also report core/stress MAE,
beneficial/harmful counts, worst harm and lost useful corrections. For a favorable
comparison, require no increase in either cohort's mean core or stress MAE or
harmful-condition counts versus the saved aligned parent, on identical supports.
These demanding checks may fail; record that outcome rather than retune.

Verify crop-context feature invariance to all three outside replacements exactly,
then replay predictions. This invariance is by construction, not an independent
performance result. Recheck original-pixel renderer/protection parity and inspect
all fixed boards plus explicitly outcome-selected worst cases. More recovery
with clean edits still fails the clean requirement. No automatic adoption,
second fit, alternative crop size or further feature sweep follows.

This comparison is not a rerun of the previous facial-root restriction: no root
feature is forced, and local lightness remains available to every split. It also
differs from removing scene lightness only from the gamma head with frozen gates.

## Work completed now

Script586 and `docs/scene-context-invariance-protocol-2026-11-08.md` define and
execute the zero-fit diagnostic. Private outputs:
`outputs/scene_context_invariance_v1`. Exported trees were replayed1353times on
fixed feature counterfactuals, with original face pixels/five facial inputs
asserted unchanged. There were no new image-model forwards, correction renders,
training, admission or app changes.

The11fits above are a proposal requiring agreement on this specific comparison,
as required by the handoff. They have not started. Roboflow access is not needed.
