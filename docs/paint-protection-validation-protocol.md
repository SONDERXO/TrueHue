# Broader protected-material development validation

26 October 2026. Frozen before mask evaluation on the broader set. Continue
autonomously under the user's existing direction; no routine approval pause.
Original user annotations, review decisions, technical holds and artifacts stay
unchanged. Regenerate training pairs only if the protection/coverage gates pass.

## Inventory and frozen sources

Repeat visual inventory of all114 previously exposed TRAIN sources in the
development exposure ledger, with original images and no new candidate overlays.
Cross-check prior review notes and source partitions. No new source or reserved
image may be opened. Record all114 inventory rows, even those not selected.

Freeze17 source frames:

- Existing user references:16798paint,40048/60162clear-skin coverage.
- Cosmetic challenges:3183,58397,67436,84888.
- Visible forehead-mark challenge:81250.
- Ambiguous colored appearance:13529,72347; no asserted paint/skin truth.
- Lighting challenges:81965,76160; do not call shadows/lighting paint.
- Existing contamination controls:31154hair/background,63870fabric,
  51446scarf,55007hair,56444foliage.

16798 remains the only user-annotated broad face-paint example. The four new
cosmetic frames test localized makeup/feature protection, not independent
validation of arbitrary cheek paint. Forehead-mark origin is not inferred.

Keep exact saved224/256 frames. Reuse the original user reference rasters and
separately documented paint/feature groups. New small conservative protected
interiors are Codex diagnostic annotations, marked provisional/unverified by
the user, with original-image coordinates and source hashes. Never relabel them
as user annotations or exhaustive makeup masks. No positives are invented on
cosmetically covered faces. Ambiguous/lighting cases have no new material truth;
unmarked pixels stay unlabeled. Old witness rectangles remain illustrative,
not exhaustive reference masks.

Review the new region overlays against original pixels before freezing the
manifest hash and before executing candidate masks. No region enters inference.

## Fixed candidates and probes

Freeze the existing parser/model/preprocessing and A/F/C/C2 recipes. No new
classifier, radius/threshold sweep, image-specific selection or parameter fit.
F and C use the earlier robust material recipe; C2 retains its fixed2pixel
outlier-neighbor margin. Stage anatomical exclusions and selected detector
processing bounds remain unchanged.

For each frozen frame, evaluate clean plus two previously defined global stress
probes: dark gamma0.7/red0.85/blue0.95, and color gamma1/red0.85/blue1.15. These
are diagnostic whole-image probes, NOT mask-generated training-pair regeneration.
Save clipping counts and exact recipe hashes. Reuse spatial material regions
because no geometry is warped; clipping/appearance limitations remain explicit.

Generation support is evaluated on clean source pixels only. Measurement and
correction masks are recomputed from each actual probe. Frozen V2 complete-mouth
measurement anchors and original-image-only seeds are used, with at least1000
seeds; no reference colors or annotation leakage. New failures are unavailable,
not negative predictions or fallback passes. All cases and all failures remain.

## Scoring and decision gates

Score each unchanged user reference and each provisional protected interior
separately, including one-pixel-interior sensitivity. Distinguish facial features,
paint, makeup/feature overlap and visible marks. Report ordinary-skin retention
on the user references, protected-region selection, inference availability,
CIELAB/ITA/brightness validity, clipping and original-generation retention.
Ambiguous/lighting cases are qualitative challenges, not material-label accuracy
scores. No aggregate population/fairness/skin-tone accuracy claim.

Protection requires zero selected pixels in each assessable fixed protected
paint/cosmetic interior and no new protected paint selection relative to prior
paint evidence. Reference skin-coverage losses, all historical failures and user
holds must also be resolved before admission. A missing/unverified region or an
unavailable mask cannot establish a pass. Small cosmetic interiors cannot prove
whole-paint protection, even when they pass.

Independently replay all diagnostic transforms, class selection, material masks,
reference scoring and available measurement statistics/features. Verify all
original source/model/review/label/ledger hashes. Inspect all mask/source/region
boards. Run the Python suite as appropriate. Do not regenerate training pairs,
change runtime policy, reassign folds or fit a correction model unless the gates
actually pass; otherwise save the precise failed gate and useful candidate.

## Thesis distinctions

This deliberately selected, already exposed set and provisional Codex interiors
are development diagnostics, not independent final evaluation or expert labels.
The added learned parser/material guards remain departures from the proposed
rule-based mask; no calibrated skin truth or automatic paint-recognition claim.
No required application-user annotation step is added. Operational MST, selected
person's neck support, final data/splits/evaluation, expert MOS and Android remain
unfinished. No approved proposal amendment is implied.
