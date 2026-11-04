# Method recommendations before expanded training

23 October 2026. This records technical recommendations and evidence, not
adviser approval or a change to the proposal. The full comparison and future
editing record is [thesis-method-alignment.md](thesis-method-alignment.md).

## Recommended decisions

| Issue | Recommendation now | Final-thesis status |
| --- | --- | --- |
| Skin measurement | Preserve `v2_complete_mouth_v1` as the versioned development baseline. Do not change measurement thresholds to improve the same reviewed examples. | Resolve the paper's HSV/YCrCb versus YCrCb wording and document actual landmark exclusions. |
| Where correction is applied | Keep the preferred `material_hair_veto_v1` as an explicitly experimental option; retain the legacy option for comparison. It improves reviewed hair exclusion while preserving reviewed paint exclusions. | The added learned segmentation model needs an explicit methodological role and phone measurements if retained. Do not claim universal paint removal. |
| ITA and MST | Retain continuous ITA as a measured feature, but do not export the tested ten-category lookup or assign guessed FairFace MST labels. | Exact MST mapping and MST-conditioned correction are unresolved requirements, not completed features. Adviser guidance is needed if replacing either requirement. |
| Training datasets | Keep FairFace for current development. Investigate SCIN using head/neck and at-distance metadata before concluding SCIN cannot contribute. | Do not replace the proposed FairFace + SCIN dataset on the strength of the earlier unfiltered 184-image sample. Candidate metadata is not acceptance. |
| Synthetic changes | Preserve current tables as controlled diagnostics. Keep the three-output gamma/red/blue operator and known inverse targets explicit. | Fixed severity and added controls do not implement the paper's tone-dependent Table 2. Resolve the grouping source and reconcile offset/contrast settings before final generation. |
| Input dimensions | Prepare a separately versioned 256x256 development preprocessing check before regenerating final features or pairs. | Confirmed mismatch: all 30 saved current training inputs are 224x224. A config constant of 256 does not establish that resizing occurs. |
| Data separation | Keep existing development, stress and reserved sources intact; split sources/known duplicates before variants. | Set the final 70/15/15 allocation, MST coverage and validation procedure once eligible labeled sources are established. Previously exposed data remain disclosed. |

## Why we cannot honestly mark MST as resolved

The subject-held-out mapping audit tested 418 reviewed images from 15 subjects.
The monotone lookup achieved 12.4% exact accuracy and 28.5% within one category;
several categories have only one reviewed subject. A later current-mask
diagnostic did not establish a reliable operational mapping either. These are
development findings, not proof that every possible approach fails. They do
not justify manufacturing ten-category labels or silently dropping the paper's
mapping step. See [mst-mapping-feasibility.md](mst-mapping-feasibility.md) and
[mst-mask-version-comparison.md](mst-mask-version-comparison.md).

## New local evidence

`scripts/48_audit_method_alignment.py` reads local files without changing them.
Its report is `outputs/method_alignment_v1/evidence.json` and contains hashes,
all 30 image dimensions and SCIN metadata candidate identifiers.

- All 30 current training inputs are 224x224. The current manifest preparation
  reads images directly; detection uses their dimensions. The 256x256 preview
  resize in the correction CLI is presentation, not pipeline preprocessing.
- SCIN metadata contains 5,033 cases; 737 are tagged head/neck.
- 368 of those cases have an at-distance image: 368 metadata candidates.
  Case-level head/neck does not guarantee that each candidate image contains
  a usable face. No new image was downloaded, visually accepted or admitted
  to training, and no label-coverage claim is made for this candidate pool.
- The implementation uses YuNet detection, while the detailed proposal names
  MediaPipe or Haar. Record this detector substitution too; it is separate
  from the added hair-segmentation model.

## Next executable work

Update: the eight-source comparison and local SCIN check are complete. See
[results and remaining work](square-preprocessing-results.md). Existing training
features and runtime defaults were not replaced.

The next development step is a bounded 256x256 preprocessing comparison on the
existing eight development sources: resize before detection, recompute masks
and features, and report failures, skin-pixel counts and changed coordinates.
Do not overwrite the 224x224 baseline, reuse its crop coordinates, or refit a
tree during this comparison. Resizing is a proposal-alignment check, not proof
of better color accuracy or a resolution of MST mapping.

After that, check SCIN candidate availability locally, prioritize the metadata
pool above, and use one candidate per case for a bounded facial-suitability
check. Record actual faces, failures and existing label coverage before
considering further acquisition or cohort selection. A future final mapping
or dataset change still needs its own documented rationale.

Before final model training, the decisions that remain for adviser guidance
are concrete: how to handle weak ITA-to-MST mapping, whether to retain the
additional hair filter, and how to reconcile the distortion and validation
procedures. No adviser message has been sent and no approval is inferred.
