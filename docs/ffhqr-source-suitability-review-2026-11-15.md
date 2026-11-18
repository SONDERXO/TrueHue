# FFHQR suitability decision

15 November 2026. User: "Alright lets start with FFHQR". Completed the selected documentation-only suitability review. Decision: **DO NOT ADVANCE FFHQR as the missing paired exposure-and-colour training basis.** No image acquisition, archive probe, roster construction or fitting follows this finding.

## Decisive task mismatch

The AutoRetouch paper, Section 4, explicitly requires preservation of the original image's colour tone and distinguishes colour correction as a separate photographic task. Sections 1 and 3 describe professional skin retouching and sparse local edits. This is evidence about the intended task, not a measurement of every released pair.

Consequently, professional retouching does not mean that the targets are exposure/white-balance corrected, and it does not establish that their photographed complexion is an acceptable restoration reference for TrueHue. Local blemish removal is also not the target transformation represented by our shared correction controls. Fitting controls to these pairs would risk approximating cosmetic differences rather than learning the missing corrections. This last point is our mechanism assessment, not a published TrueHue experiment.

My earlier suggestion that FFHQR might provide the missing paired correction supervision was premature. The full paper resolves that question against advancement. No sample inspection is needed to override a known mismatch in the supervision task.

Using FFHQR targets merely as starting photographs for new synthetic distortions would be a different proposal: it would discard the purported new real correction-pair evidence and return to synthetic supervision on FFHQ-derived people. More such photographs alone supplies no demonstrated repair for our source-transfer failures. That route is not selected.

## Release, access and independence findings

The official README lists 70,000 retouched images corresponding to FFHQ, seven approximately 13 GB PNG tar archives and a 2.3 GB thumbnail archive. These are publisher listings, not verified live server availability. No archive requests, HTTP HEAD/range probes or image downloads were made. Individual bounded-sample retrieval is unestablished and no longer necessary for this rejected use.

README folder splits are training 00000 through 55000, validation 56000 through 62000, test 63000 through 69000. These are publisher folder allocations, not evidence of person-disjoint partitions. FFHQ ancestry means distinct dataset branding cannot establish independence from existing FFHQ development or frozen-encoder pretraining. Overlap remains unresolved; no locked contents or manifests were opened to investigate it.

The README and LICENSE.txt describe the retouching release as CC BY-NC-SA 4.0 with attribution, modification notice and share-alike terms; original-image terms remain separate. No deployment-license conclusion is made. The reviewed materials do not establish an official tone-labelled, person-separated correction cohort for darker-skin qualification. Described demographic variety cannot replace such evidence.

## Evidence and reproducibility

Official repository main resolved through the GitHub connector to commit `a6c3d0d2ae2afaf7ac3f1f9e356da95806561b67` (18 October 2021). README.md and LICENSE.txt were read through the connector and preserved in `outputs/ffhqr_source_suitability_review_v1/`; their content hashes are recorded in the receipt. The receipt hashes identify the cached text, not image assets. No source code was executed.

- [Official README](https://github.com/skylab-tech/ffhqr-dataset/blob/a6c3d0d2ae2afaf7ac3f1f9e356da95806561b67/README.md)
- [Official license](https://github.com/skylab-tech/ffhqr-dataset/blob/a6c3d0d2ae2afaf7ac3f1f9e356da95806561b67/LICENSE.txt)
- [AutoRetouch paper, especially Sections 3 and 4](https://openaccess.thecvf.com/content/WACV2021/papers/Shafaei_AutoRetouch_Automatic_Professional_Face_Retouching_WACV_2021_paper.pdf)

Direct publisher-page/PDF opens initially returned 403; opening the primary PDF through its search result subsequently provided its extracted text. The attempted University of Bologna-hosted copy timed out and was not used as evidence. No local PDF rendering or figure inspection is claimed. This decision rests on explicit textual task requirements.

## Current stopping point

The missing training basis remains unresolved. This closes the selected FFHQR correction-pair route, not all possible feature-to-control learning. No automatic next source or predictor queue, no retries of closed PPR10K/STW/SCIN/Stellenbosch routes, and no new user rating request is selected. A further resource proposal must demonstrate actual additional exposure-and-colour supervision before acquisition.

Model unfinished; paper paused; full automatic exposure AND colour goal and darker-skin priority retained. Working deadline Friday November 20 before noon Manila, without a completion promise. All ratings, artifacts, manual refinement and approved ears preserved. Zero photos, dataset arrays, features, fits, predictions, correction renders, raw originals or locked contents/manifests accessed; runtime, Android and manuscript unchanged. Documentation-only check; implementation tests are not applicable.
