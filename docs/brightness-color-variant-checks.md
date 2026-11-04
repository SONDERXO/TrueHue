# Brightness/color candidates: fixed variant checks

24 October 2026. Checked the two previously screened TRAIN candidates under all five fixed variations. Eight pairs are proposed for separate development staging; two remain held. No pair was admitted, no model was fitted, and the runtime model is unchanged.

| Source | Proposed variants | Held variants |
|---|---|---|
| 62676 | Dark, bright/warm, color shift, unchanged, mild | None |
| 6356 | Bright/warm, unchanged, mild | Dark and color shift |

All10 attempts had available geometry, experimental correction support, finite frozen ten-feature measurements and zero clipped pixels. Numerical feature availability alone does not ensure representative skin measurements.

For6356 dark, baseline estimation retained38.9% of the clean generation region and correction support retained58.0%. For its color shift, those figures fell to18.7% and36.4%. The boards visibly show missing cheeks/forehead regions. Larger correction support does not repair biased estimation features; keep both variants out rather than substituting YCrCb-only features or relaxing thresholds.

62676 baseline estimation retained93.99% to100% of its source-generation region across variants; correction support retained93.84% to100%. Existing whole/quadrant retention screens passed all five. Its narrow pose, low detail and jaw/neck boundary remain caveats.6356 retains a temple gap and side-lighting differences even in the three passing variations. Codex inspected all ten previews; these are qualitative development observations, not human final labels or expert MOS.

The retention thresholds are the existing exploratory screens, not validated skin-quality standards. The generation mask is not annotated true skin; outside-mask pixels are not automatically non-skin. Visible neck skin belongs to the requested future scope, while collar/clothing must remain excluded. No neck-specific mask or correction was implemented here.

Independent verification reproduced all10 generation recipes, inverse targets and zero-clipping counts; recomputed20 paired baseline/YCrCb statistics and retention results; recomputed all10 brightness feature sets; confirmed frozen schema and unchanged tracked artifacts. **464 tests passed**. Exposures were already recorded in the prior batch; no fresh source was opened or assigned to final evaluation.

Next recommended step: stage these eight proposed pairs alongside the existing31 in a separate39-pair development version, retaining all ten attempts and the two held failures. Recheck duplicate grouping across all ten sources and feature/target provenance before planning a same-probe31-versus39 source-grouped comparison. Keep the ten-feature schema and tree settings fixed; do not retrain or replace the runtime model during staging. Adding pairs is not assumed to improve correction.

Final source eligibility/human decisions remain pending. Continuous ITA without operational MST, added brightness inputs and selected development data remain recorded proposal distinctions. Face-and-neck implementation and final thesis evaluation remain unfinished.

[6356: all five previews](../outputs/brightness_color_variants_v1/6356_variants.png) | [62676: all five previews](../outputs/brightness_color_variants_v1/62676_variants.png) | [Pair dispositions](../data/manifests/brightness_color_variants_v1/screen_disposition.json) | [Independent checks](../outputs/brightness_color_variants_v1/verification.json)

Follow-up: [separate39-pair stage](development-expansion39-stage.md). No fitting yet.
