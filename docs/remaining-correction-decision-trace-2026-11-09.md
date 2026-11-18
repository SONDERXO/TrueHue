# Remaining correction decisions: trace results

9 November 2026. Saved-record audit while face-parser permission clarification is pending. No DINO execution or model fit.

## Two different problems

**Missed overexposure corrections:** all 15 previously identified non-veto core misses reach depth-four identity leaves containing 79–82 clean fitting examples. Identity is the only clean-feasible action and also the lowest aggregate training-cost action without that restriction. Their paths use scene median brightness, scene lower brightness and facial L*. Twenty-nine unique clean evaluation photos share at least one of these fitting configurations/leaves; counts across routes overlap.

The original aligned comparator's useful controls remain available in the action library, but would harm clean fitting examples in these mixed leaves. Removing clean protection, switching the veto or selecting a different existing action for the whole leaf is therefore not a justified repair. A new decision design would need to separate different needs while preserving clean photos; this audit does not prove any feature or increased depth will accomplish that.

**One harmful stress correction:** `eval_02__stress_color_none` reaches a full-model leaf containing 68 training conditions: 67 underexposure conditions and one stress-colour condition, with no clean fitting rows. The chosen gamma is approximately 0.700, which brightens the image under the direct-power convention. It raises regional RGB error from 6.67 to 31.53 and CIEDE2000 from 4.84 to 11.70.

That input lies outside the leaf's fitting ranges on facial a*, facial b*, scene log red/green and scene log blue/green. The branch's exposure-oriented action has much lower aggregate fitting error than identity (389.00 versus 1,978.15 summed row MAE), but is inappropriate for this evaluation case. No reserved clean reference vetoed this branch. All existing comparator outputs examined share the harm.

The two failure types require different treatment. Neither is explained solely by the pending replacement parser. These are descriptive traces on exposed cases, not independently validated causal conclusions.

## Recommended next bounded step

Audit **applicability of correction leaves across all existing evaluation attempts**, using saved fitting ranges and saved feature vectors. Count how many harmful, beneficial and clean decisions lie outside their own correction leaf's fitting ranges, with raw facial features reported separately from scene features. No optimised margin, fitted guard, altered predictions or new image rendering.

This tests whether the harmful case is part of a broader unsupported-use pattern and quantifies how much useful recovery an abstention rule could potentially discard before proposing that rule. It must not assume that out-of-range means harmful or in-range means safe. Do not design an exception only for this named case or relax the unchanged joint acceptance requirements.

For missed overexposure, keep the mixed-leaf evidence explicit; no additional capacity, threshold or feature sweep follows automatically. The latest candidate remains unadopted, and the separate 24-photo final holdout remains byte-unread.

## Verification

Scripts 652–653; private `outputs/remaining_correction_decision_trace_v1`. Exact case selection: all 15 non-veto demonstrated core misses from the exhaustive failure taxonomy, plus its one harmful case. Independent scalar replay checks 16 routes, 224 action totals, clean feasibility and bound hashes. All passed. Zero fits, inference, renders, source-image reads or new annotation. Existing private artifacts and model/runtime settings remain unchanged.
