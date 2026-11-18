# Fixed occlusion and final-support stage — 8 November 2026

User approves continuing the83parent passes from96development originals. The
24candidate holdout photos stay unopened. All13parent failures remain unavailable;
no replacements, new parser/detector/landmark runs, fitting or distortions.

Align each saved original256input using its saved landmarks and the existing
FaceOcc template/bridge. Run at most83new raw-input CPU FaceOcc forwards, exactly
once per successfully aligned parent, using the pinned existing checkpoint and
unchanged ImageNet preprocessing, zero-logit cutoff and inverse validity veto.
Keep the1000normalized-pixel minimum. No CLAHE/fallback/threshold tuning.

Use the same desktop-derived correction-support renderer and inward blend as
the aligned research pipeline, with identity controls only. Keep glasses mode
uncertain for these unlabelled photos; this is not a lens-type classifier.
Project binary measurement masks by the existing nearest rule, alpha linearly,
protection conservatively with area>0. Outside the crop remains unchanged.
Save diagnostic masks/support even if a final measurement fails, but mark them
unusable; no correction is applied and no MST estimate/model is fitted.

Report all96attempts, parent/final availability, failure reasons, per-interval
and per-publisher counts, native sample/support sizes and explicit glasses-choice
requirements. Technical success does not establish correct-skin measurement or
scientific training admission. Inspect all96fixed mask/support boards, including
failures; retain fragmentation and beard/glasses limitations. Verification replays
saved logits and masks and must not add forwards or fits. Stop before synthetic
generation or model fitting so those decisions use the final-support evidence.
