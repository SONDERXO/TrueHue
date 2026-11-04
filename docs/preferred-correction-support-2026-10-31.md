# Preferred correction regions

31October2026. After viewing the brows/lips experiment, the user said:
“I like these outputs. Lets continue using these”. This selects the support
policy for continuing development; it does not establish final model quality.

| Purpose | Included regions |
|---|---|
| ITA, MST input and facial-statistics measurements | Selected facial skin only; exclude brows, lips, neck, eyes and mouth interior |
| Correction support | Selected facial skin, associated visible neck, predicted brows and lips |

Eyes, mouth interior and other excluded predicted classes are not added.
Parser mistakes remain possible, including hair labelled as brow and objects
labelled as skin. Explicit protected pixels remain excluded from correction.
Beard-specific work stays on hold. The six exact original-mask approvals remain
limited to those facial masks; this preference is not a global approval of
neck/feature masks or every new input.

## Practical behavior

Both `run_face_neck_preview.cmd` and `run_face_neck_features_preview.cmd` use the
preferred support. Script336 defaults to including brows/lips. Its explicit
`--exclude-brows-lips` flag reproduces the historical face+neck-only option.
The older face-mask editor remains separate. Existing experiment artifacts are
not rewritten. Current desktop/Android correction demos and model presets are
not switched by this region decision.

The preview shows masks; fixed gallery results used illustrative settings, not
trained-model predictions. No new calibration is required merely by adding
correction-only regions while the facial measurement mask stays byte-identical.
The existing semantic MST mapping still has its previously recorded validation
limits; this region preference does not validate it.

Future paired data must explicitly bind generation, application and separate
face/neck/brow/lip scoring regions. Current semantic pairs were distorted only
on facial skin; applying correction to otherwise unchanged neck/brows/lips must
not be reported as recovery of corresponding simulated distortions. Keep
identity controls, outside-region preservation and exact new-mask judgments.
No repeated small training trials or automatic model adoption follows.
