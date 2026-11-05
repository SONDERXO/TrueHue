# FFHQ mask/support feasibility: technical success, visual holds

5 November 2026. The same twelve fixed FFHQ photographs were processed once
under the [protocol recorded before inference](ffhq-mask-support-protocol-2026-11-05.md).
All twelve remain in the evidence. **No photograph is admitted for training.**
The check supplies new mask evidence; it does not establish a finished correction
model, reference quality, skin accuracy or reliable MST.

## What the check established

All12 passed the existing single-face/landmark/parser parent checks, produced
whole-face correction support and completed one fixed CPU FaceOcc forward each.
All12 also passed the existing minimum1000-pixel candidate measurement guard.
The unchanged preferred experimental service contract is
`89c7a3963dcc72bfa8c7b73433789b058093131662c88a6d30a7f25d791823fd`.

Analysis uses the existing whole-frame256x256 image, reduced from1024x1024.
Original source bytes are unchanged. Correction uses the parent facial support,
associated predicted neck, whole-face outline, enclosed-hole filling and inward
union blending. FaceOcc affects measurement only. Its fixed alignment, model,
strict logit>0 threshold and inverse validity veto were reused without tuning.
The existing landmark helper's ordered margin fallbacks were retained, not a
new framing search. No new algorithm or runtime switch was adopted.

Eleven cases have some associated predicted-neck pixels;52445 has none.
Small fragments do not establish usable visible-neck coverage. Nine correction
masks reach an image border, a crop warning rather than automatic failure.
FaceOcc retains64.18–99.73% of parent measurement pixels (median97.09%).
Retention is not accuracy: the beards show that retaining pixels can preserve
unwanted material. Source IDs/photo URLs are not verified independent people.

## What the assistant saw

All12 saved five-panel boards were inspected. These observations concern the
256px working images, not dense annotations or full-resolution reference
approval. Correction includes internal features/objects by the adopted design;
measurement should exclude non-skin. Keep those judgments separate.

| ID | Correction / neck finding | Measurement / source limitation |
|---|---|---|
| 54632 | Broad face; lower support reaches crop | White beard/moustache visibly remain selected; neck partly obscured |
| 39568 | Broad face and partial neck | No obvious large object inclusion on board; directional shadow and hair-edge uncertainty |
| 29617 | Glasses and part of hand inside outline corrected by design | Most glasses/hand excluded; fine boundaries uncertain; occluded cheek/jaw |
| 29863 | Clear correction spill onto white head covering | FaceOcc removes upper contamination but beard/moustache remain; dim uneven light |
| 16061 | Glasses corrected; irregular fringe boundary; collar/crop limits neck | Lens region largely excluded; fringe/rim boundaries uncertain |
| 52445 | Face available; zero associated neck pixels | Fine boundaries unverified; clothing/foreground close to chin |
| 32685 | Small lateral neck fragments; possible collar inclusion | Downward pose and fringe; neck association not reliable complete coverage |
| 53146 | Face and narrow lateral neck; crop edge reached | Hard sunlight/shadow, squint and cap boundary uncertainty |
| 48879 | Broad hair-covered area inside correction; outer extent uncertain | Diagonal blond-hair strip appears selected near temple/outer cheek; oblique pose |
| 49131 | Broad face/neck; lower crop reached | No obvious large occluder on board; stubble/lighting/fine boundaries unverified |
| 59807 | Glasses/microphone inside outline corrected; necklace/collar near neck | Most lens/microphone excluded; rim/fringe/occlusion boundaries uncertain |
| 46795 | Only79 associated neck pixels; largely unavailable neck | Strong light/shadow, fringe and high collar; not a complete neck result |

The head-covering spill and persistent beard selection are substantive mask
limitations. They are retained rather than repaired silently. A less obstructed
board is not automatically an admitted reference or a favourable-only subset.

## Evidence and verification

- [Gallery with assistant findings](../outputs/ffhq_mask_support_assessment_v1/review.html).
- [Processing gallery](../outputs/ffhq_mask_support_v1/review.html).
- [Per-case assessment JSON](../outputs/ffhq_mask_support_assessment_v1/assessment.json)
  and [CSV](../outputs/ffhq_mask_support_assessment_v1/assessment.csv).
- [Technical records](../outputs/ffhq_mask_support_v1/results.json).
- [Original attribution/source ledger](../outputs/ffhq_source_visual_assessment_v1/attribution_and_source_ledger.csv).

Script414 freezes the input/dependency hashes before processing and refuses
output overwrite. It saves boxes, landmark details/arrays, categories, baseline
mask, correction/neck masks, exact float alpha, aligned input/matrix, candidate
mask and reports. Script415 reuses the fixed isolated CPU runner; no PyTorch
installation or import was added to the main environment. Script416 records
assistant observations in a separate package without changing the technical
package. The galleries activate no annotation task.

Verification completed:

- 12 exact saved-service replays (plus a second saved replay per case), including
  mask/report parity, aligned inputs and no additions outside parent support.
- 12 saved-statistics checks and independent alpha-equation/RGB8 demonstration
  checks. All neutral renders are exact identity; demonstration pixels outside
  correction support are unchanged. Demonstration parameters .85/1.05/.95 are
  fixed illustrations, not predictions or fitted targets.
- 31 focused tests passed in4.34seconds for measurement, FaceOcc, full-face/neck,
  continuity and blending. This is not a full-suite run or scientific validation.
- All original image hashes,23 pinned historical sources, seven integrated-plan
  parent manifest hashes and seven older parent manifest hashes remain unchanged.
  New packages carry their own artifact SHA256 manifests.

Local derived images preserve original attribution via the source gallery and
ledger. No photographs/models were published or transferred. Rights, grouping,
reference quality and final evaluation remain unresolved.

## Decision and stopping point

The software can produce saved support on these sources, but **technical success
does not justify automatic training admission**. The next mask decision should
address the observed head-covering spill, beard/hair measurement contamination
and missing/uncertain neck support, using this retained evidence. Do not replace
the hard cases, auto-expand, create variants, tune thresholds or fit a model
from this result. No new repair experiment is activated by this document.

ITA-to-MST remains deferred for this source check and retained in the eventual
method. MST is unavailable, not invented. Zero MST calibration, tree/target
fits, synthetic variants, new photos, human annotation requests or contacts.
Desktop/Android defaults and the submitted proposal/working thesis drafts are
unchanged. Existing departures C01–C06/C12 are documented in the
[panel register](panel-change-register.md); no panel approval is claimed.
