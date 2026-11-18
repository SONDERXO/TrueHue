# Next correction comparison — plain-language plan

The plan is fixed and verified. It has not started generating distorted inputs
or training models yet.

- **Change one thing:** add80new reference photos to the existing22, giving102
  references from42publisher groups. More groups may improve generalization;
  this is a hypothesis, not a promised fix.
- **Keep the model method fixed:** same features, skin-tone calibrations,
  correction choices, masks, tree settings and clean-photo constraints. This
  avoids mixing a data-expansion test with another feature or calibration change.
- **Prepare1040distorted inputs:**13existing non-clean conditions for each of80
  new sources. Reuse their existing clean preparation; retain all16clean failures
  separately. Do not replace failures or borrow clean masks for distorted inputs.
- **Train11trees once:** the same10old held-group folds and one full development
  model. No new skin-tone calibration or target-parameter fitting.
- **Compare on the same756existing evaluation attempts.** These are development
  checks, not a new independent final test.
- **Require both safety and benefit:** zero changed usable clean photos; no
  worsening core/stress mean RGB or CIEDE2000 error, harmful counts or beneficial
  counts; no protected-pixel leakage. Leaving everything unchanged will not pass.
- **Keep the new holdout closed:**8groups/24photos remain unopened until a
  candidate passes development and its complete pipeline is frozen.

Verification checked880new-source/calibration-role combinations,32unchanged
runtime/model bindings and80clean preparation records. No image-model calls,
image reads, synthetic generation or fitting were added by the planning step.

The masks are still imperfect and the source labels are continuous scores.
There is no fresh highest-[9,10]group in this pool. We cannot claim validated
skin masks, verified identity separation or all-tone fairness from this plan.
The existing14condition matrix is a development diagnostic, not the proposal's
exact three tone-dependent distortion recipes.

Next: prepare and verify the1040actual distorted-input masks, keeping all failed
attempts. Then run the fixed learning comparison if preparation remains compatible.

[Full protocol](expanded-correction-training-protocol-2026-11-08.md).
Private frozen manifest: `outputs/expanded_correction_training_plan_v1`.
