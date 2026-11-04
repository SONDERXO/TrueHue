# 40048 image-right cheek gap

25 October 2026. User identified missing cheek skin. Inspection located the image-right cheek patch aroundx200-204,y122-128 in the256input; anatomical side was not inferred from the word right.

The correction masks are limited to each detection crop. Dark crop `[20,0,184,221]` ends atx204; unchanged `[20,2,185,218]` ends atx205; mild `[20,2,184,218]` ends atx204. The dark/mild patch connects to the crop boundary and outside background. The unchanged version encloses a17-pixel cheek hole, explaining why the earlier enclosed-gap rule recovered it but left the other versions incomplete.

The annotations show where the patch is missing; no correction support was expanded and no earlier user decision was changed. A trial5x5 closing also failed to recover the dark patch, reinforcing that blindly increasing hole filling is not a justified fix. It was diagnostic only and was not adopted.

Recommended next test: a separately versioned padded **processing crop**, still constrained by selected-face landmarks, anatomical exclusions and skin/material checks. Compare across all32 candidates and earlier hair/paint regressions, not just40048. Keep detector result separate from mask-processing extent; do not label an expanded rectangle as skin. Report remaining missing skin and newly included non-skin separately.

Generation and measurement/correction use different policy roles. Current synthetic edits may leave this patch unchanged because source generation also used a bounded mask; simply expanding correction support could adjust previously undistorted pixels. A crop-policy change therefore needs explicit generation/measurement provenance and fresh consistent examples before training, not an unrecorded patch to one image. Own-neck support remains a separate unfinished requirement.

No masks, runtime models, inputs, training tables or review decisions changed.31154 remains held; original evaluationfold4 remains empty; no retraining occurred.

[Dark comparison](../outputs/40048_cheek_inspection_v1/40048_dark.png) | [Unchanged comparison](../outputs/40048_cheek_inspection_v1/40048_identity_control.png) | [Mild comparison](../outputs/40048_cheek_inspection_v1/40048_mild_bright_exposure.png) | [Crop diagnostics](../outputs/40048_cheek_inspection_v1/summary.json)

Follow-up correction: [padded-crop experiment](padded-correction-crop-test.md) shows crop clipping is not the sole cause;the cheek also failscolor/oval gates and was not altered during source generation. Padding alone does not fix the dark version.
