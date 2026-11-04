# Smooth boundary experiment: less endpoint flattening, similar colour match

2 November2026. Following the user's instruction to address the detail/region
issues, one bounded experiment corrected the two identified diagnostic regions
and applied one fixed smooth clipping rule to all14saved adjustments. **Endpoint
flattening decreased substantially while average colour match stayed similar.**
This is a promising isolated rendering candidate, not runtime adoption or proof
that all detail is preserved. No new photos, fits, inference or training.

Gallery: `outputs/ppr10k_detail_repair_v1/review.html`.
Script398, frozen `protocol.json`, results/replays/verification in that folder.

## Exactly what changed

Source-only coordinate-grid inspection preceded two conservative region revisions:
904_0 removes the identified blue shirt;1188_0 removes bright background around
the profile. Source outline boards visually inspected. Region pixels904:1716->818;
1188:753->510. These are still approximate, partial facial regions with features,
hair/makeup/eyewear, not anatomical truth or measurement masks. Other12regions
unchanged. Old masks, fits, scores and all six older output manifests preserved.

No parameters were refitted. Both originals and the smooth candidate were
recomputed from the saved source/adjustments on identical revised support per
photo. These parameters were originally optimised on old regions, including
contamination in two cases. New scores are sensitivity evidence, not newly
validated fitting or held-out accuracy. Original checker pattern scores also
saved, but not called clean validation after region revision.

One smooth boundary, fixed before evaluating outputs, replaces hard channel clip:

`soft(x) = s*log(1+exp(x/s)) - s*log(1+exp((x-1)/s)), s=0.02`.

Input x is the existing four-control raw encoded-RGB result. Stable symmetric
evaluation avoids overflow/cancellation. No width search, alternative candidate,
new output parameter or spatial skin smoothing. Gamma/red/blue/contrast unchanged.
This changes near-endpoint colour response and cannot recover information already
absent in the input. Flat inputs remain flat; RGB8 quantisation can still collapse
differences. Raw overflow remains unchanged, so reporting zero raw clipping would
be misleading: instead compare actual rendered RGB8 endpoint/detail counts.

## Results on identical revised regions

All14saved photographs included. Equal-image mean relative CIEDE2000 over each
entire diagnostic region: four hard2.548 ->four smooth2.522. This pool contains
related exposed photographs, not independent people or representative skin-tone
coverage. It also includes fitting pixels; do not compare directly to earlier
check-block-only means or interpret as new-photo performance.

|Measure|Four hard|Four smooth|
|---|---:|---:|
|RenderedRGB8channel samples at0or255, summed across14regions|1461|364|
|Adjacent channel pairs with source+target variation flattened at the same endpoint|986|153|
|Equal-image mean relative colour difference, all-region|2.548|2.522|

Endpoint samples fall75.1%; the specified adjacent-pair count falls84.5%.
These are descriptive code-level changes, not percentages of texture recovered.
Pair counts overlap, depend on source/target correspondence and include mixed
facial features. A smooth curve can move endpoint codes inward without proving
useful visual detail preservation. Residual364endpoint samples/153pairs remain.

Colour error improves slightly in11/14, worsens slightly in330_0,1117_0,455_0.
No threshold search or exclusion follows from these regressions. Earlier two
indoor regressions versus the three-control model remain unresolved.

Selected endpoint counts: wedding1398_0/1/2 hard162/127/394 ->smooth25/25/64;
787 hard462->178;767 hard219->65. Source-highlight variation is less flattened
by the candidate, but substantial quantisation loss remains particularly787.
Revised904hard14->smooth7; revised1188zero->zero. This distinguishes genuine
face-region endpoint behaviour from their former shirt/background clipping.
All metrics are retained per-photo, including RGB MAE and original check pattern.

## Visual inspection and limits

All14source/three-hard/four-hard/four-smooth/expert boards inspected. Overall
appearance of the four-control result is largely retained; changes around
extreme highlights/shadows are subtle. Wedding forehead/nose/chin and787/767
highlight transitions remain closer in broad appearance to expert than the
three-control fits, but low-resolution crops cannot certify fine texture.
Revised904/1188output coverage no longer includes the identified clothing or
bright background; they remain partial, difficult profile faces. No blanket
full-face/skin validity or human approval inferred.

Diagnostic sharp outline edges and uncorrected neck/background remain. The
adopted whole-face+neck support and inward blending are not changed or evaluated
by this isolated check. No modern mask inference or MST measurement performed.
No synthetic/admitted training labels or automatic predictions produced.

## Verification and decision

14outputs independently agree with the direct softplus-difference formula within
5e-16; metrics recalculated, outside-region float pixels unchanged, protocol
predates outputs. All six old artifact manifests still match. Six focused tests
pass/0.70s, including monotonic/symmetric/bounded response, retained variation
from distinct raw values beyond the hard endpoint, flat-input behaviour and
the existing clipping-audit safeguards. No full-suite run claimed.

Keep this fixed smooth boundary as an experimental candidate alongside contrast.
The two known region contaminations were addressed for this diagnostic, not
certified globally solved. No additional refit/width tuning/batch, production
integration or training follows automatically. Runtime and original three-output
design remain unchanged pending explicit adoption and justified evidence.
ITA + calibrated MST + facial statistics and decision-tree family retained;
reliable MST, training cohort and automatic prediction remain unfinished.
Panel register distinguishes this implemented experiment from method adoption
or panel approval. Submitted paper and immutable delivery snapshots unchanged.
