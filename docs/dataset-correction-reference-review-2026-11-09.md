# Current datasets and online correction-reference review — 9 November 2026

## Decision

**There is useful paired evidence already on disk: PPR10K.** Review its existing
eight publisher-training pairs for automatic training readiness before acquiring
another dataset. This is a recommendation for bounded readiness work, not an
admission, new correction fit, additional operator comparison or guarantee.

The prior suggestion that different reference evidence necessarily required new
acquisition was incomplete. Fourteen PPR10K source/editor-A pairs have already
been acquired and investigated. They are more relevant to photographic correction
than another synthetic expansion. They have unresolved limitations; they are
not a ready replacement training set or an independent final test.

## Local analysis

This review read named dataset reports and saved metadata, listed dataset roots
and checked PPR10K original-file membership/size without decoding or hashing
image bytes. No final-photo directory was traversed. Saved counts below retain
their original audit dates; they are not fresh pixel-level audits.

| Current source | What exists / demonstrated role | Correction-reference decision |
| --- | --- | --- |
| FairFace and controlled derivatives | Ordinary face originals, reviewed subsets and many generated exposure/colour variants; current fitting preparation contains 890 conditions from 82 originals | Useful existing synthetic research evidence. More copies/variants do not supply new real photographic targets or independently establish correction need. Preserve all allocations and failures. |
| FFHQ | Twelve inspected originals and 168 derived conditions; all twelve usable photographic references with individual limits | Suitable synthetic-restoration references, not real before/after correction pairs. Actual-input measurement/support and MST remain unqualified; do not repeat completed review or select only favourable masks. |
| SCIN | Local metadata and selected candidates; prior label disagreements/facial-region concerns recorded | No eligible aligned portrait before/after correction set established by local records. Retain source and label limitations; not a newly rejected entire dataset. |
| MST-E | Existing labelled-subject files and protected evaluation roles | Skin-tone evaluation evidence, not a released corrected-pixel target for each lighting condition. Do not repurpose locked evaluation data for fitting/calibration. |
| Stellenbosch | Received research-only release: 285 publisher subjects, 75 photos each, 21,375 JPEGs at 224×224 plus decimal MST scores | Repeated real lighting captures are relevant. But no designated corrected-image target or verified registration is established; small native faces and failed/contaminated measurements remain. Do not turn arbitrary warm/cool conditions into clean/corrupt pairs. |
| FiveK | Two full-resolution editor-C RGB16 TIFFs plus six thumbnail inspections | Local full-resolution files are edited outputs; matching RAW/source renditions were not acquired. Not a local before/after pair cohort. Uneven light/beards alone do not disqualify photographic references; matching inputs and usable support are the important missing evidence. |
| PPR10K | Fourteen original source/editor-A TIFF pairs in ten publisher groups, already investigated | Best existing direct photographic-pair lead; detail below. No dataset expansion is needed to begin metadata/readiness planning. |

Stellenbosch's original study describes fifteen lighting conditions, fixed camera
settings and a chart intended to enable correction. That makes it worth retaining
for lighting robustness research, but does not establish a neutral target in our
delivered release. The chart cannot become an input requirement for the app;
usable patch values/correspondence at this release resolution are unverified.
[Author paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11122461/)

## Existing PPR10K evidence, not a new discovery of the dataset

The saved inventories bind 11,161 matching source/editor-A stems in the remote
archives. Local membership checked here:

- Six pairs: groups 1398/1487, three frames each, originally publisher-validation.
- Eight pairs: 787_0, 330_0, 767_0, 1117_0, 1188_0, 990_0, 904_0, 455_0,
  one frame in each of eight publisher-training groups.
- All 28 original TIFF paths are present and nonempty. This is a file-membership
  check, not a fresh CRC/profile/pixel verification; reuse the saved earlier checks.
- Every pair is already TrueHue development-exposed. Publisher training/validation
  status does not make these untouched TrueHue test cases or prove person identity.

Earlier six-pair target-aware three-control approximation reduced mean check-
block DE from 13.44 to 4.79. On the eight further pairs, three controls had mean
DE 4.964 and adding contrast reduced it to 2.552, with increased clipping in six
of eight. These are per-photo fits supplied with expert targets, not automatic
predictions. Approximate assistant polygons include mixed features, exclude neck,
and do not establish dense skin truth or registered correspondence. The fourth
control remains experimental; it is not adopted by this review.

These results demonstrate that local references exist and expose an operator
approximation issue. They do not prove a new dataset alone will fix the learned
decision boundary. The 1,000-normalized-pixel measurement rule is not a blanket
minimum for those historical manual diagnostic polygons; their support contracts
must not be confused.

## Online investigation after local readiness remained unresolved

| Source | Verified offering and access | Practical assessment |
| --- | --- | --- |
| [PPR10K official repository](https://github.com/csjliang/PPR10K) | Portraits, three expert targets and human-region masks; noncommercial research. Pre-rendered sRGB 360p files avoid a RAW pipeline; the advertised rendered collection is 91 GB, full collection 406 GB | Best task fit, already partially local. Do not download full collection. Human-region masks are not hair-excluding skin labels; targets include edits beyond gamma/R/B. |
| [Exposure Correction / MSEC](https://github.com/mahmoudnafifi/Exposure_Correction) | Public split links; RAW-rendered FiveK exposure data, subject to original FiveK terms | More realistic rendering than our simple transforms, but still rendered exposure variation, not new paired physical captures. General scenes, portrait/MST coverage unverified, FiveK source overlap must be checked. Secondary lead. |
| [Rendered WB](https://yorkucvil.github.io/projects/public_html/sRGB_WB_correction/dataset.html) | Chart-referenced WB targets; chart coordinates and split metadata; public download links. Publisher notes copyright/fair-use basis | Potential separate colour-correction diagnostic. Portrait coverage and recipient rights unresolved; charts must be excluded from model input/scoring. No direct exposure solution. The separate rendered-FiveK subset explicitly lacks WB ground truth. |
| [PIQ23](https://github.com/DXOMARK-Research/PIQ2023) | 5,116 smartphone portraits and expert quality annotations including facial exposure. Approximately 5 GB; access via form and terms | Interesting independent evidence about whether exposure looks good, not aligned corrected-pixel targets or gamma/R/B supervision. Would change the learning/evaluation design. No form submitted. |
| [REED author publication](https://openaccess.thecvf.com/content/ICCV2025/html/Wang_From_Abyssal_Darkness_to_Blinding_Glare_A_Benchmark_on_Extreme_ICCV_2025_paper.html) | Real burst-based under/overexposure benchmark with alignment; author links a repository | Relevant physical-capture lead, but usable portrait coverage, recipient terms and file-level access not established here. Raw README retrieval failed; do not claim acquired/ready. Extreme texture restoration exceeds the retained operator. |
| [RPO official repository](https://github.com/whiteknight-WJN/RPO-Dataset) | 2,600 real overexposure pairs across 650 static scenes, RAW/JPEG; about 22.32 GB via Baidu | Exposure-only general-scene evidence; face coverage and dataset-use terms unverified. Does not address colour-only ambiguity or MST by itself. Low priority. |
| [DAST official repository](https://github.com/dasec/DAST-SkinTone-database) | Controlled nominal/under/overexposed faces; examples public, full access by request | User previously dropped acquisition. Keep that decision; no new contact/payment/request. CST is not MST, and metadata inconsistencies remain. Not the recommended route. |

Only primary author/publisher sources support the online findings. Documentation
links do not establish functioning image downloads or permission beyond the
stated terms. No photos, models or dataset archives were downloaded this turn.

## Recommended next bounded action

Use the eight already acquired publisher-training pairs as a **readiness cohort**,
not a new fit and not final validation. Reuse existing source-only face-selection
decisions, TIFF/profile/hash evidence and target-fit diagnostics. Prepare an
explicit ledger for all eight covering:

1. Input/target geometric correspondence and automatic face-selection feasibility,
   preserving small/profile/multiple-face failures and the original selection rule.
2. Automatic measurement and face/visible-neck correction support under the current
   permitted pipeline. Historical hand-selected polygons do not meet this need.
3. Compatible ITA/MST input construction without inventing MST labels or fitting
   calibration from final data. Missing supplied MST does not prohibit photographic
   pair inspection, but prevents claims of verified per-MST fairness/coverage.
4. Target representability with the retained three controls using existing
   diagnostics, without another oracle fit or quietly adding contrast. Decide
   whether residual mismatch permits the intended limited claim before learning.
5. Group/duplicate/source relationships, intended research-only use and a frozen
   separate evaluation design. Eight exposed pairs cannot certify generalisation.

First classify these requirements from saved records. If a requirement needs new
automatic inference or annotation, write one fixed protocol and scope for that
step before running it. Do not manufacture admission from the existing visual
screen, launch a fit, expand PPR10K, or relax current joint gates automatically.

This is a more economical next decision than collecting new photos, downloading
another large dataset, or training a parser. If PPR10K readiness fails, preserve
the reason and assess a specific alternative role; do not cycle through the
table as automatic experiments. No working-model success is promised.

## Supporting local records

- [PPR10K first inspection](ppr10k-fixed-sample-inspection-2026-11-02.md)
- [PPR10K three-control diagnostic](ppr10k-operator-diagnostic-results-2026-11-02.md)
- [PPR10K eight-group comparison](ppr10k-new-group-comparison-results-2026-11-02.md)
- [FiveK full-resolution result](fivek-full-resolution-results-2026-11-02.md)
- [Stellenbosch release](stellenbosch-received-data-results-2026-11-05.md)
- [Stellenbosch support/lighting](stellenbosch-support-lighting-results-2026-11-05.md)
- [FFHQ reference eligibility](ffhq-source-eligibility-results-2026-11-05.md)
- [Earlier search and DAST disposition](mst-cohort-source-investigation-2026-11-05.md)

No training, new image decoding, correction rendering, final-holdout access,
calibration, runtime adoption, external contact, form submission, upload, commit
or push. All original and derived artifacts are preserved.
