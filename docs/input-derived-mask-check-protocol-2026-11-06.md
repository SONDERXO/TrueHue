# Input-derived-mask correction check

6 November 2026. User authorises the proposed end-to-end check. Freeze one
comparison on the same now-exposed eight publisher keys / 24 originals / 336
saved whole-scene synthetic inputs. No new subjects, fitting, tuning or adoption.
Use the frozen bundle from frozen_split_candidate_v1 without any changes.

Run source anchor, native crop, redetection, landmarks, CLAHE parser and aligned
CLAHE FaceOcc independently on each actual distorted 224-pixel scene. Keep
0.85 detector / logit > 0 / 1000 measurement-pixel guard and existing assets.
Never borrow original geometry/masks for candidate inference or application.
Failures and undefined features produce the unchanged scene, with reasons.
Clean cases are deliberately rerun to check pipeline repeatability.

For a common coordinate comparison, project each predicted measurement mask to
the native 224 scene using existing native_projection, then render the three
predicted controls directly on those scene pixels. No feathering, filling or
resizing corrected RGB back into the scene. Feature extraction remains on the
actual predicted 256 working crop. This explicit native-scene rendering differs
from the previous working-crop renderer; do not conflate their metrics.

Score input-derived ungated/gated and borrowed-support ungated/gated counterparts
on the same original native-grid measurement region, using original scenes as
references. Borrowed counterparts use previous saved parameters and original
native-grid masks, rendered by the same native-scene rule. The reference mask
is scoring-only for the input-derived path. Also report full-scene error, changed
pixels outside the reference region, support intersection/union and availability.
Support overlap is agreement with an imperfect original mask, not skin accuracy;
changes outside it are not automatically object errors. Original failures remain
unscored in reference-region summaries; full-scene errors can still be computed.

Inspect fixed clean / combined_cool_under / stress_combined_over outputs for all
24 sources, with predicted mask overlays. Replay saved render/features/metrics
and hashes without refitting. No reference-region selection may be used to
choose candidate actions. Current data are development-exposed, not a new test
cohort. Private research/noncommercial/citation/no-redistribution terms remain.
Stop after reporting this comparison, including failures and visible boundaries.
