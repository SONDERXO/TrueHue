# Brightness/color training-source screening

24 October 2026. Screened18 additional TRAIN sources. Two are promising for follow-up;16 are held. No source or pair was added to the training table and no model was fitted.

The selection rule was saved before image processing: divide remaining candidates into three equal-rank groups by recorded native-photo L*, then three b* rank groups within each; select two per cell using SHA256 of `brightness_color_seed42/{image_id}`. These are image-appearance proxies, not MST labels or intrinsic complexion groups. One color axis does not represent all color variation.

Eligible sources had prior numerical success, pending human review, no recorded prior active-development exposure, a singleton duplicate group, TRAIN allocation and no overlap with current31 source groups or the append-only exposure ledger.248 sources were eligible;230 remain after this batch. All18 exposures were appended before processing, preserving the previous ledger. None may subsequently be represented as a fresh final holdout.

All18 freshly resized256 inputs passed face/landmark/minimum-mask processing and provided the frozen brightness measurements. Numerical success is not mask/source quality approval. Codex inspected all nine boards. Several masks retained only a small unilateral region or had large gaps; other sources had severe blur, glasses, mouth objects or strong pre-existing lighting effects.

| Follow-up source | Why investigate | Caveats |
|---|---|---|
| 6356 | Broad facial support | Temple gap, oblique pose and side lighting |
| 62676 | Broad facial support | Narrow pose and jaw/neck boundary |

The other16 remain held with individual reasons in the disposition file. These are qualitative development observations, not new human labels or formal rejection of every source. Valid neck skin is not automatically unwanted spill; clothing and collar must be assessed separately.

Next recommended step: generate the same five fixed variants for6356 and62676, retaining identity and mild controls; check clipping, baseline-mask retention, availability of the frozen ten features and the existing experimental correction support. Preserve failures and clipped variants separately. Do not fit or admit new pairs until that screen is complete. No source was chosen based on whether it fixes a known prediction error.

Independent verification reproduced all18 selected IDs from the pre-run pool, confirmed ledger prefix/appends and allocation/exposure exclusions, and checked all tracked original hashes. The ten-feature schema and runtime model are unchanged. **464 tests passed**. No reserved or external development images were used; operational MST, final cohort eligibility, face-and-neck support and final evaluation remain pending. Selection and feature-method distinctions remain recorded for later thesis edits.

[All nine review boards](../outputs/brightness_color_source_screen_v1/review-index.md) | [Individual dispositions](../data/manifests/brightness_color_source_screen_v1/candidate_disposition.json) | [Selection policy](../data/manifests/brightness_color_source_screen_v1/selection_policy.json) | [Verification](../outputs/brightness_color_source_screen_v1/verification.json)

Follow-up: [completed fixed variant checks](brightness-color-variant-checks.md).
