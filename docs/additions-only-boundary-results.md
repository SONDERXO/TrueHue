# Additions-only correction boundary

23 October 2026. Follow-up to [the lower-face trial](lower-face-boundary-results.md).
Status: fixed development candidate, no runtime integration or model fit.

Later user requirement: [face plus visible neck correction](face-and-neck-correction-requirement.md).
This candidate's facial boundary is not the final target for neck inclusion.
Reassess neck skin separately from clothing/collar spill; keep facial measurements fixed.

## Rule

Preserve the original HSV-and-YCrCb material/hair-filtered correction support.
Apply the existing lower-face boundary to the YCrCb-only proposal, then union
the bounded proposal with the original support. Restrict only new additions;
never remove baseline pixels. No new pixels outside either proposal are filled.

The unchanged75% proposal-retention guard runs **before** the union. A bad
outline therefore cannot appear safe just because baseline pixels are restored.
No automatic geometry fallback is implemented. Prior83184 sentinel rejections
are linked as historical controls, not rerun results; a new unit test verifies
that baseline preservation cannot hide a rejected proposal boundary.

## Results

- All38 square attempts produced an available experimental mask.
- **Zero baseline support pixels lost** in every case.
- Retained84,332 of103,581 proposed additions; blocked19,249.
- Same exploratory training coverage screen:27/30, compared with19/30 for
  restricting the entire YCrCb support. This is not final eligibility approval.
- Three training probes still fail:12288/color,22211/color and22454/dark.
- All48 original-point clean/global-color probes were available. Selected skin
  remains12/12 in each variant (shifted original baseline was9/12). Reviewed
  paint remains0/3 and other0/5 in both variants. Hair remains1/4 clean and0/4
  shifted. These are reused development points, not independent area accuracy.

Counts above sum pixels over repeated variants. Blocked additions are not
annotated non-skin pixels; some may be real skin. The preservation guarantee
applies to selected baseline pixels, not every facial skin pixel in the image.

## Visual review and limitation

Codex inspected all38 rows on eight source boards. This version retains the
baseline facial edges trimmed by the prior whole-support boundary while
reducing extra lower collar/clothing support from the YCrCb proposal.

It deliberately retains baseline errors too. Yellow clothing in12288 and some
neck/collar margins remain. Upper-face additions are not restricted by this
lower-face rule, and existing eye-rim/one reviewed hair error remains possible.
Do not describe this as complete clothing, hair or paint removal.

These are mask previews, not corrected outputs. YCrCb estimation masks/features
are unchanged across the experimental boundary variants. The original runtime
estimator,22-row screening manifest, original cohorts, human labels and frozen
correction model are unchanged. The historical excluded probe can have an
experimental support but still lacks a valid original-estimator feature vector;
mask availability never promotes it to runtime/training eligibility.

## Next step

Completed follow-up: [identical-parameter corrected-image comparison](corrected-mask-comparison-results.md).
Some patches/color errors improve, but identity/mild/stress overcorrection remains
a model problem. No mask/runtime/model was promoted by that comparison.

Freeze this candidate and compare actual corrected outputs before more mask
tuning. For a fair **application-mask-only** comparison, use the same frozen
model and the same recomputed baseline input feature vector/parameters for
every compared mask on each saved input. Do not feed new YCrCb features into
the old tree and attribute that change solely to the application boundary.
Keep unavailable baseline features explicit, stress separate and all attempts
recorded. These mask results do not establish a learned improvement or select
a replacement model.

The improved masks do not resolve MST mapping, final dataset composition or
the additional segmentation model's place in the proposed method. Preserve
these distinctions in [the thesis alignment record](thesis-method-alignment.md).

## Artifacts and verification

- [All comparison boards](../outputs/additions_only_boundary_v1/review-index.md)
- [Measurements and point observations](../outputs/additions_only_boundary_v1/summary.json)
- [Saved-mask verification](../outputs/additions_only_boundary_v1/verification.json)
- [Visual assessment](../outputs/additions_only_boundary_v1/visual_assessment.json)
- Reproduction: `venv/Scripts/python.exe scripts/59_test_additions_only_boundary.py`
  (refuses overwrite).

Verified all38 unions against independently saved lower-boundary controls,
baseline preservation, proposal containment, addition accounting,48 point
observations and tracked input/model/review hashes. Four new tests cover
baseline retention with new-spill rejection, invalid geometry before union,
baseline-only pixels and anatomical holes. Full suite: **464 passed**.
