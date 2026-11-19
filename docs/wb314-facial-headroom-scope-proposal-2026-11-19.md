# Approved facial-measurement headroom scope specification

This public summary omits per-image user judgments and private expected-output bindings. The exact specification approved by the user is preserved locally with its approval hash. Authorization covers one scoped assessment and research-wrapper integration only if every declared check passes. Results are recorded separately; approval is not proof of a successful result.

## Exact algorithm change

```python
# Earlier, unadopted application-region candidate:
selected = (alpha > 0) & ~protected
# Approved facial decision scope:
selected = (measurement > 0) & (alpha > 0) & ~protected
```

Keep the half-code quantization interval, sRGBdecode, raw tree controls, luminance equation, cap formula and identity/no-headroom handling unchanged. Use the existing supplied measurement mask. Reject malformed or empty intersections explicitly. No source/role exception, new threshold, percentile, model feature, learned coefficient, mask generator, package or asset is introduced. The rendering/application mask remains unchanged.

The facial scope is a subset of the old decision region. It cannot introduce a stricter cap on a previously uncapped input solely by reducing that region. Excluding an old maximum can loosen a limit, but does not guarantee restoration of a particular preferred appearance. Actual RGB8preservation must be checked. The scope protects measured facial skin only; clipping or mask leakage outside it remains a separate limitation.

## Fixed validation and limits

Reuse the same106cached inputs and their existing masks:66earlier development outputs,20synthetic expert-packet cases and20normal inputs. Freeze source/code/QA, authorization and exact private expected-output hashes before the pass. Seal effective controls before outcome comparison. No trained-model inference, fitting, source-JPEGdecoding, new masks or source acquisition is required.

Required checks include exact preservation of all86earlier development/synthetic outputs, all10previously unchanged normal inputs and all20privately bound expected normal outputs, plus input/protection/outside invariance and independent scalar/native PNG proof. The private targets implement the actual approved preservation requirements; they do not label every normal output as human-accepted. No criteria may be relaxed after the result. A failed mandatory check stops this assessment without a parameter/guard/refit queue.

Only a complete pass permits the explicitly approved research-wrapper integration. Raw tree controls and effective controls must be reported separately, with policy/mask provenance and source hashes. The original frozen predictor and failed prior candidate remain preserved. No final model adoption, Android deployment, expert questionnaire edit, HDexport or general-photo quality guarantee is implied.

The earlier instruction against new variants remains in force for every other variant; this one was explicitly approved. Exact approval, full private specification and preservation bindings remain in local outputs/.
