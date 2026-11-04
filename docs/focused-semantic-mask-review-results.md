# Candidate mask review imported

29 October 2026. Found the semantic24 export in the original focused review
folder. Its scope and manifest match the semantic comparison. Validated all
24 IDs and unchanged comparison evidence, preserved the export byte for byte,
and recorded paired baseline/candidate decisions with exact original notes.

| Paired outcome | Sources |
| --- | ---: |
| Baseline reject → candidate accept | 8 |
| Baseline accept → candidate accept | 4 |
| Baseline accept → candidate reject | 1 |
| Baseline reject → candidate reject | 10 |
| Baseline reject → candidate uncertain | 1 |

Candidate totals: **12 accepted, 11 rejected, 1 uncertain**, versus baseline
5 accepted/19 rejected. These are judgments on a purposive, development-exposed
sample. They do not estimate population accuracy, establish pixel-level mask
quality, or measure correction-model performance. Six accepted candidate
entries have notes; some describe improvements, others retain contamination or
coverage concerns. Do not treat all accepted masks as clean.

The regression is 66413: accepted baseline, rejected candidate because facial
hair was not excluded. 34898 is uncertain because background remains included
and forehead spots are missed. Qualified accepted cases retain missed forehead
(72663), hand inclusion and missed side-face coverage (75050), clothing
inclusion (12559), missed chin (43909 and 18034). 14418 has a positive coverage
note. Exact wording remains in the reconciled record.

Other explicit rejections include holes (52056), inadequate coverage (77889,
59484), no detected mask as visually reported (13718, 30236, 31367, 20653,
9149), and major forehead holes plus improper eye exclusion (25129). Human
descriptions do not overwrite recorded technical counts: for example, a mask
can contain some pixels yet be described as visually absent or inadequate.

**Source suitability direction:** user rejects 55166 and explicitly requests
rejecting black-and-white filtered photos. Preserve 55166 as rejected in any
future training table and screen other known monochrome/filtered references
as unsuitable for skin-color correction. No arbitrary saturation threshold
or automatic classification of all other photos is introduced here.

Next candidate work should target the remaining failure mechanisms and the
accepted-mask regression using these same development references. Do not
promote this version by the higher acceptance count alone, automatically fill
holes across excluded anatomy, or restore baseline pixels known to contain
foreign objects. Reuse this evidence before requesting more photos from the
user. The reserved training check remains closed until a candidate is frozen;
no need to request another complete 24-photo review immediately.

No mask weights, calibration, correction trees, active assets or training
eligibility changed during import. Candidate masks remain outside the existing
MST measurement contract. Human candidate acceptance is not approval of input
distortions or correction outputs.

- [Paired exact decisions and notes](../outputs/focused_semantic_mask_review_import_v1/reconciled_reviews.json)
- [Preserved export](../outputs/focused_semantic_mask_review_import_v1/original_user_export.json)
- [Summary](../outputs/focused_semantic_mask_review_import_v1/summary.json)
- [Verification](../outputs/focused_semantic_mask_review_import_v1/verification.json)
