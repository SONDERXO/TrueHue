# Source selection, provisional partitions and failure handling

Implemented 2026-10-20 by `scripts/22_prepare_source_partitions.py` and
`src/data_preparation/source_partition.py`. Reproduce from the project root:

```text
venv/Scripts/python.exe scripts/22_prepare_source_partitions.py
```

The command refuses to overwrite existing output. It writes derived records
under `data/manifests/source_preparation_v1/`, without changing original
manifests, source images, reviews, or generating any additional pairs.

## Source-selection policy

One audit row is retained for every one of the 650 candidates. Use the
`v2_complete_mouth_v1` processing results and join the latest random-50 review
over the older master entries. Automated failures take precedence over manual
decisions. Human rejection or known misplaced geometry excludes an otherwise
computational success. Uncertain landmark audit cases are held separately.
Earlier accepts are provisional candidates, not automatic proof of current
mask/reference suitability. Other sources stay on hold until reviewed.

| Source status | Count |
| --- | ---: |
| Provisional reviewed candidate | 35 |
| Hold: unreviewed source | 460 |
| Hold: uncertain geometry | 9 |
| Excluded: review or known geometry | 29 |
| Excluded: automated failure | 117 |
| Total | 650 |

83184 is excluded for known misplaced geometry despite its original accept
label, which remains preserved in the audit row. The 35 provisional sources
come from the original accepted set after withholding the nine uncertain
cases and 83184. No new human labels were invented. `training_ready` is false
for every row because reference suitability and current-version review remain
unsettled, alongside the grouping/severity method. The allocation therefore
does not establish a usable final training dataset.

## Duplicate scan and partition policy

Read every source image, record a SHA-256 of decoded dimensions/pixels, and
compute a 64-bit difference hash from a 9x8 grayscale thumbnail. Exact matches
or dHash Hamming distances at most four link images into transitive groups.
The perceptual threshold is a conservative candidate-grouping heuristic, not
proof of duplicate images or subject identity. No face recognition is used.
This run found zero exact or near-duplicate candidate pairs. Different photos
of the same person and some near duplicates can still escape this scan.

Every future variant inherits its original source's partition and duplicate
group; never randomly split variants. This group key is not a subject ID.
FairFace identity IDs are not available in these manifests, so subject-level
separation is **not verified** and must not be claimed.

- Original FairFace validation rows never enter training.
- Original validation groups used in known pipeline development are assigned
  `development_validation`; remaining validation groups are `reserved_test`.
- Original training groups use a seed-42 stable hash bucket: 20% validation
  allocation probability, otherwise training. This is not an exact 80/20 count.
- Duplicate groups crossing original train/validation boundaries would be
  quarantined instead of moving validation sources into training.

Known exposure includes the 80 development examples, fresh mouth-check 30,
smoke-test selection and synthetic pilot sources: 127 unique pool sources.
This records known use, not proof that no other manual inspection occurred.
All source images have undergone feature processing; `reserved_test` is not
a claim of an untouched external or subject-independent benchmark. Do not use
reserved-test correction outcomes for tuning after a final method is fixed.

Provisional allocations, across all rows including held/excluded sources:

| Partition | Count |
| --- | ---: |
| train | 450 |
| development_validation | 126 |
| reserved_test | 74 |

These are allocation counts, not eligible-image counts. No physical files
were moved. Partition assignment uses source metadata and stable IDs, not
race, ITA, or invented tone labels. Test suitability must be assessed with a
fixed screening policy and full exclusion accounting. Eligibility changes
should retain allocations rather than rebalancing for attractive outcomes.

## Distorted-input failure policy

Before admitting a synthetic pair to a primary technical-development table:

1. Source eligibility must be resolved and its partition inherited.
2. Rerun the actual input pipeline on the distorted saved image. A failure
   excludes that pair with the actual reason; never replace its feature vector
   with clean-reference features or a source-derived mask.
3. If input processing succeeds but distortion clips any selected source-mask
   pixels, put the pair in a separate clipped stress set. Do not claim exact
   inverse recovery there. Clipping is measured before uint8 quantization.
4. Otherwise classify it as a technical candidate; it still inherits source
   eligibility and is not automatically final training data.

Failures are kept in manifests, including source ID, variant, distortion,
correction target and reason. Retain successful sibling variants; do not invent
replacements for failures. Report attempted/successful counts by source and
variant, because input-mask failures may bias the surviving sample. A lost
input must also count as a pipeline failure when reporting overall system
reliability, even if image-quality metrics apply only to successful outputs.

The pilot failure audit contains 10 unclipped technical candidates, three
clipped stress-only cases and two insufficient-skin-pixel failures. All 15
remain pilot-only, regardless of their provisional policy class.

## Remaining before scaling

Finalize reference/current-mask suitability for the provisional sources and
the tone-conditioned severity method, then choose the final distortion scope
and ranges. Do not generate the full dataset from all 533 numerical successes.
The binary source-mask pilot had visible seams and does not yet validate
deployment blending or end-to-end correction on a newly inferred mask.
The current records settle accounting and allocation rules; they do not
resolve those scientific design questions or constitute training results.
