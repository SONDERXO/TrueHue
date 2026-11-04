# Fresh 256x256 development dataset

23 October 2026. Built as `controlled_square256_v1`; no learner was fitted.

## What was built

| Routing | Pairs |
| --- | ---: |
| Training candidates | 30 |
| Development-validation, source19 only | 3 |
| Clipped stress, separate from fitting | 4 |
| Excluded | 1 |

All 38 attempts were regenerated from the same eight original sources.
Each source was resized to 256x256 with INTER_LINEAR **before** fresh detection,
landmarks and generation-mask computation. Distortions use the existing fixed
gamma/red/blue settings on that new binary source mask. Identity and mild
brightening additions remain limited to the seven training sources.

The saved distorted inputs were decoded and measured afresh. Four input-only
Lab/ITA columns and three known inverse-parameter targets retain their explicit
schema. Source/duplicate groups and partitions are preserved. Historical stress
and exclusions cannot be promoted automatically. Seven inner source-group fold
plans were generated; no folds were fitted. Subject identities remain unverified.

The old 224x224 data, frozen model and runtime defaults remain unchanged.
The new files are separate, with new pair IDs and parent-pair provenance.

## Checks

Scripts51/52 generated and independently checked all 38 saved pairs against
their resized references, transforms and generation masks. Checks cover exact
saved pixels, unchanged outside-mask regions, identity equality, clipping,
inverse targets, recomputed Lab/ITA, feature blanks on failures, fold separation
and unchanged original-file/model/table hashes. Existing **447 tests passed**.

- Routing counts are unchanged, with zero per-pair routing changes.
- Four bright/warm cases have clipping: 2,239 clipped pixels across the table.
  They remain stress-only. No clipping occurs in the training candidates.
- Source22454/color-shift remains excluded: 392 selected skin pixels, below
  the unchanged 1,000-pixel minimum. Features remain blank.
- On unclipped pairs, known-inverse reconstruction differs by at most **3
  uint8 channel levels** after saving/quantization. This is not perfect recovery
  and is not a learned result. The earlier mild/identity-only one-level result
  must not be generalized to all dark distortions.

Fresh experimental correction support was also computed using the existing
material check and MediaPipe hair veto, without loading or invoking the
correction decision tree. Every available support excludes predicted hair and
anatomical exclusion pixels. Unavailable support is explicitly marked; its
saved empty image is not a successful fallback. This does not guarantee paint
or all hair is excluded.

## Mask assessment before retraining

Follow-up: [consistent development screen and case disposition](square-mask-quality-screen.md)
holds eight training candidates and retains 22 in separate manifests. Original
30-candidate data remain unchanged; the screen is not final eligibility approval.

Codex visually inspected all eight source boards (all 38 attempts). This is
development inspection, not human annotation or a new approval of old labels.

The dataset passes generation checks, but **is not cleared for automatic
retraining**. In particular:

- Source22454/dark still has a very sparse estimation region; correction
  support remains concentrated around the lower central face.
- Source12288/color-shift lacks much of the upper face, with an abrupt upper
  boundary in correction support.
- Source62331/color-shift retains substantial missing face coverage despite
  expansion. Source19/color-shift also has incomplete estimation/forehead
  coverage; source19 stays development-only.
- Other boards still have smaller boundary, shading and baseline-selection
  limitations. Passing the pixel minimum does not establish a suitable mask.

These observations are saved separately in `mask_quality_assessment.json`.
The original 30-candidate table is preserved as an audit artifact, rather than
silently dropping difficult examples after reviewing them.

## Files and next step

- Tables/policy: `data/manifests/controlled_square256_v1/`
- [Review boards](../outputs/controlled_square256_v1/review-index.md)
- [Generation and input hashes](../data/manifests/controlled_square256_v1/schema_and_summary.json)
- [Verification results](../outputs/controlled_square256_v1/readiness_checks.json)

Reproduction requires fresh output locations or a separately versioned run;
scripts refuse to overwrite existing outputs:

```text
venv/Scripts/python.exe scripts/51_build_square_development_table.py
venv/Scripts/python.exe scripts/52_verify_square_development_table.py
```

Next, resolve the flagged mask cases with a documented quality rule before
selecting a training cohort or fitting a new model. Do not broaden thresholds
only to improve these examples. Keep the proposal's unresolved MST, dataset
and distortion decisions visible in [the thesis alignment record](thesis-method-alignment.md).
