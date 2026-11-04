# Accepted fuller-face masks and rebuilt paired data

31 October 2026. All six new reference masks were accepted by the user, each
with the note “Good facial coverage”. The downloaded file was found inside
`outputs/semantic_reference_readiness_v1/` and imported by script331. Exact
membership, image/mask hashes and the measurement contract matched. No source
review was repeated, and all notes were preserved.

## What was completed

The [fixed preparation protocol](semantic-paired-data-preparation-protocol.md)
was saved before generation. We rebuilt the existing five engineering variants
on each newly approved semantic generation mask, then measured each generated
input with the matching semantic measurement path. Old input masks, features,
targets and MST predictions were not copied into the new set.

| Prepared item | Count |
|---|---:|
| Accepted exact original masks | 6 |
| Unchanged control records | 6 |
| Newly generated inputs | 30 |
| Unclipped primary candidates passing existing support screen | 17 |
| Clipped stress candidates passing existing support screen | 13 |
| Processing/target/support holds in this pass | 0 |

Each source has exposure, color, combined, gamma-lightened and gamma-darkened
inputs. The existing Table2 decomposition and supplemental gamma choices were
retained without tuning. Recipe severity assignments are explicitly inherited
engineering assignments, not validated new-mask MST labels. Unclipped status
does not certify reference lighting or mask quality. All clipped cases remain.

These six source groups were already development-exposed. This is preparation
under a changed masking method, not independent source expansion or a new
six-source training trial. The original accepted-mask notes remain exact-scope
judgments; they do not approve masks on the 30 altered inputs.

## Verification and boundaries

Script333 replayed all 30 generated inputs pixel-for-pixel and checked every
source/dependency hash. Script334 independently replayed all 30 full-frame
Lab/ITA/endpoint feature sets and all 30 target parameter applications. Outside
the approved generation support, pixels remain unchanged. For gamma-only pairs,
targets are known floating-point inverses with quantization residuals saved.
Composite/color targets use the existing bounded approximate fit, with direct
gamma conversion and residuals verified; this is not correction-tree training.

MST is explicitly unavailable in these preparation records because no matching
all-row development lookup has been adopted. No old lookup was substituted.
No correction model was trained, no input-mask approval was invented, no
reserved evaluation data were opened, and both demos remain unchanged.
Beard-specific work stays on hold. No adviser-request gate was introduced.

## Next decision

The data pipeline can now generate and measure consistent examples using the
newly approved masks. The next correction comparison still needs a bounded
broader-source decision, explicit experimental MST-use decision, new-input mask
admission and a frozen evaluation plan. Do not train on these six alone merely
because preparation succeeded, repeat the failed old comparison, or keep
adjusting recipe intensities. Do not request a further manual batch before
those remaining decisions make its purpose concrete. No new review is requested
at this checkpoint.

Evidence:

- `outputs/semantic_reference_mask_import_v1/summary.json` and `decisions.json`.
- `outputs/semantic_paired_preparation_v1/plan.json`, `controls.json`,
  `records.json`, `verification.json` and `independent_verification.json`.
- Read-only examples: `outputs/semantic_paired_preparation_v1/gallery.html`.
  This is a data gallery, not corrected output or a review export.
- Scripts331,333–334. No core algorithm changed in this phase; no full-suite
  rerun is claimed. Last full suite remains841passed in32.72seconds; five
  importer tests subsequently passed separately.
