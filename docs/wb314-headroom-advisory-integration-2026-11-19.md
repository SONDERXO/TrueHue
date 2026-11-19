# Research headroom advisory integrated; primary edits unchanged

The research API now retains the frozen model's result as its primary image and returns the existing facial-headroom proposal separately. It does not apply the cap automatically. This is a non-replacing integration, not a claim that either failed cap assessment passed or that normal-photo overcorrection is solved.

## API contract

Use `WB314WithHeadroomAdvisory` from `scripts/wb314_headroom_advisory.py` in the existing scripts-based research environment. Its `correct(rgb, measurement, alpha, protected)` delegates to the unchanged `FrozenWB314` and returns:

- `output` and `controls`: exactly the original frozen model result.
- `features` and `leaf`: the unchanged base prediction metadata.
- `headroom_advisory`: availability, scope, reason and whether the separate candidate controls differ.
- `headroom_candidate` and `headroom_candidate_controls`: a separately labelled alternative, never substituted into the primary result.
- `headroom_applied_to_primary=False` and `automatic_overcorrection_fix=False`.

The two output arrays are independent, so modifying an alternative cannot mutate the primary. Invalid canonical inputs fail before the base is called. If the facial/application intersection is empty, the advisory explicitly reports unavailable, returns no candidate and does not count that as a safety pass; the valid base result is retained. No editor UI, new mode-selection system, dataset, model family or app default was added.

Keeping the primary edits exactly also retains their original highlight behaviour. An advisory does not remove clipped highlights from that primary image. Applying an alternative changes pixels and can change the preferred brightness. Do not silently select different alternatives per image and report those as one declared automatic correction policy.

## Actual verification

`scripts/check_wb314_headroom_advisory.py` replayed the actual cached106base results, features, controls and existing masks through the composed API. This uses a cached-result base stub, not new trained predictor or encoder inference. The results were:

| Contract check | Result |
| --- | --- |
| Primary RGB8exactly matches previous output |106/106|
| Primary controls/features preserved |106/106|
| Separate candidate exactly matches existing scoped output |106/106|
| Input arrays unchanged |106/106|
| Primary preview PNGs byte-identical to previous previews |20/20|
| Separate candidate PNG checks |2|
| Embedded PNG byte/dimension checks |22|

Native model construction was checked without calling correction. New trained model/encoder calls and fits were0. The frozen tree hash remains `7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f`, with total final CARTfits still1. The old predictor source and both cap policies remain unchanged.

Generated API tests cover primary preservation, independent arrays, explicit advisory unavailability and rejection before base invocation. The final result was7passed in5.44s, with one pre-existing NumPyimport deprecation warning. The initial uniform-white test fixture incorrectly expected different RGB8results even though both controls could quantize to white. Its assertion failed, and orchestration mistakenly proceeded to the cached replay with a premature QAflag. The initial fixture, inaccurate flag and sequencing issue are preserved locally. Production wrapper code did not change: the fixture gained midtones, the affected7-test suite passed, and `scripts/finalize_wb314_headroom_advisory.py` bound that corrected proof to the already completed replay and independently checked images/hashes. No false initial pass or new model run is claimed.

## Delivery and qualification

Local viewer: `output/wb314-headroom-advisory-2026-11-19/START_HERE.html`. It displays original input versus unchanged main correction, with a collapsed, clearly labelled alternative only where the existing scope calculation differs. The research interface does not replace the expert Form images, questions or existing20-pair packet. Those synthetic outputs remain unchanged.

Local evidence: `outputs/wb314_headroom_advisory_integration_v1`, including final summary, initial sequencing record, cached replay verification and finalization receipt. Individual judgments, raw replies, image bindings and authorization context stay private. Only source and aggregate checked results are published.

Both cap exact-match screens remain failed. The scoped cap is not adopted as an automatic primary-output policy. The new interface is a research advisory/alternative, not an autonomous correction-necessity detector or a finished model. Current256px processing, approximate masks, prior source exposure and incomplete final/MST/new-photo/device qualification remain. No Android deployment, live Form edit, invitation, expert response, HDexport or new human rating occurred.
