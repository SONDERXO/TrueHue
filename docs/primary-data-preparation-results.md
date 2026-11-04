# Primary data prepared and frozen for one planned training cycle

30 October 2026. User authorized the focused finish plan. Prepared data from
the same 26 approved originals, without opening reserved or new raw sources.
No correction tree was fitted and the demo remains unchanged. The output is
a frozen candidate dataset with an exact-mask review prerequisite, not a
finished or independently validated correction model.

## Original recipe preserved and separated

The [preparation protocol](primary-data-preparation-protocol.md) fixes the
original measurement mask, matching experimental MST and existing three-variant
recipe. Source severity values and all prior concerns remain unchanged.
Prepared 26 original controls and 78 exposure/color/combined attempts:

| Route | Cases | Meaning |
|---|---:|---|
| Approved original controls | 26 | Existing exact approvals, no new label |
| Primary candidates | 11 | Unclipped, measurement/target available, existing support screen passes; exact new mask pending |
| Clipped stress candidates | 52 | Preserved in separate authorized stress lane; exact new mask pending |
| Unclipped mask-screen holds | 15 | Not sent to primary training or the primary review page |

The eleven primary candidates span eleven sources: ten color components and
one exposure component, with no combined cases. Thus the unchanged full recipe
does not produce balanced recoverable exposure training data on these sources.
This is a data-readiness observation, not a failed correction-tree experiment.
Zero clipping and a screen pass do not establish skin-mask correctness.

## Declared normal-exposure supplement

The [supplemental specification](gamma-control-data-specification.md) was written
before generating 52 gamma-only inputs: lightening and darkening per approved
source using the existing source gamma and its reciprocal. No strength search,
extra color threshold, new mask method or source exception is used. The normal
controls omit contrast/brightness/color offsets and therefore do **not** claim
to be the complete Table 2 recipe. Full Table 2 and all stress evidence remain
preserved. This engineering addition must be described separately in the thesis.

Both positive-power directions remain within [0,1] before rounding, with known
algebraic inverse targets in the same direct gamma/red/blue correction family.
Uint8 encoding is not exactly reversible. The largest observed mean inverse
RGB error on generation support is 0.001148 normalized (about 0.293 on the
0–255 scale); this is a per-image mean, not a maximum per-pixel error bound.
Across 52 inputs, rounding introduces 1,671 new zero channel samples; these
are disclosed rather than incorrectly called lossless data.

All 52 inputs produce technical measurements. Fifty pass the unchanged support
screen: **25 lightening and 25 darkening**, covering all 26 sources collectively.
84364 lightening and 29880 darkening remain screen holds, without label changes
to their original clean masks or other variants.

The final prepared inventory has 156 attempts: 26 original controls, 61 primary
distorted candidates, 52 clipped stress candidates and 17 mask-screen holds.
The 61 comprise 50 gamma controls, ten original color components and one original
exposure component. They are synthetic variants, not 61 independent people.
All sources are already exposed development; this adds no independent final
validation set, validated MST strata or dark-severity coverage.

## Frozen method and next gate

The [single-comparison protocol](primary-training-single-comparison-protocol.md)
keeps the eleven endpoint-model input features, original mask/lookup contract,
depth 3, seed 42, minimum leaf 1, unweighted direct gamma/R/B regression and
fitting-control protection. After exact reviews, only accepted technically
eligible primary rows may join the original controls. Existing clipped-stress
models/results remain the frozen comparison; the old authorized stress path is
not globally banned or silently removed.

All variants of a held source must remain outside its fitting set. Evaluation
will show clean, normal-exposure, color and original stress results separately
on matched inputs, including unfavorable results and failures. Zero held-clean
correction changes and benefit versus unchanged remain necessary. One planned
comparison is followed by a blocker/data-method decision if it fails, not a
new feature/depth/threshold search on the same cases.

No new distorted row is admitted yet. Exact image/mask/contract matching finds
no applicable prior distorted-mask decision for the new primary candidates.
Prior accepts/rejects and notes therefore remain separate rather than being
transferred to different variants.

## Review exactly the missing evidence

Open [the source-grouped primary-mask review](../outputs/primary_training_review_v1/review.html).
It shows **26 existing photos and 61 mask decisions**. Original clean photos
need no re-approval. Only the pending primary masks are shown, not the 52 stress
variants or 17 screen holds. Each mask has accept/reject/unsure and notes. The
explicit “Accept every mask on this photo” action applies only to masks currently
shown for that source, and does not overwrite notes or approve another source.

Download `truehue_primary_mask_decisions.json` into that review folder when
finished. Its manifest SHA256 binds decisions to the exact 61 cases. No option
is preselected and no tree fitting follows automatically from clicking a button.

## Verification

- Script 278 independently reconstructs all 78 original variants, clipping,
  masks/geometry/features and saved target curves/residuals, retains 26 controls
  and verifies all routing holds. The 33 variants shared with earlier preparation
  reproduce previous input/mask pixels exactly.
- Script 279's verification independently checks all 52 gamma power curves and
  inverse targets, quantization and 52 mask/feature reconstructions. Both
  pre-generation specifications and original source hashes are checked.
- Script 280 freezes data lanes, feature/tree settings and the pending-review
  manifest, verifies source/input/mask provenance and all 61 review boards.
  Inspected the 1398 darkened comparison board locally.
- Script 281 tests group-scoped acceptance, individual rejection/notes, manifest-
  bound 61-row export and persistence in an in-memory DOM. JavaScript syntax
  passes `node --check`. These tests write no real user decisions. Live browser
  interaction was not tested; the earlier browser runtime was unavailable.

Artifacts: `outputs/primary_training_preparation_v1/`,
`outputs/gamma_exposure_controls_v1/`, and
`outputs/primary_training_review_v1/`. No core library changed; the last full
suite remains 798 passing tests. This preparation is verified through the
recorded data/mask/target reconstructions and review logic checks, not a claim
of another full-suite run. Weak experimental MST validation, tone/source coverage,
natural-reference assumptions and final model quality remain explicit blockers.
