# Clean-photo risk in correction branches

8 November 2026. Saved-record audit only; no new model fit.

The depth-four model changes the clean photo because a scene-brightness decision sends it outside the region represented by its clean fitting examples. Requiring clean examples in every correction branch would disable all corrections, so that is not a useful repair.

## Evidence

- All 12 correction leaves in the full model contain no clean fitting rows. The same is true of all 125 correction leaves across the ten development folds. These are repeated model branches, not independent samples.
- All 234 edited evaluation conditions route into those branches. A blanket clean-membership requirement would block every edit, including useful corrections. No such guard was implemented or adopted.
- For `case_28__clean`, the final decision uses the upper portion of whole-scene brightness (`scene_l_p90`). Clean fitting values in the parent branch range from 32.94 to 53.33; the decision threshold is 53.53. This clean evaluation photo has a value of 55.69 and enters the correction side, which has 56 fitting conditions and zero clean examples.
- Its other 11 features remain inside the global clean fitting ranges. The brightness difference is evidence of an unsupported clean-photo case, not evidence that the photo needs correction.

This exposes a limit of fitting constraints: they protect the clean examples used to build the tree, while a different clean photo can still enter a correction branch. It does not prove that a range guard, removal of scene brightness or a different depth will preserve clean photos generally.

## Proposed change

Use a small, explicitly reserved set of **existing development publisher groups** for a clean-photo veto. Exclude all their conditions from correction-tree fitting. After fitting, route their usable clean photos through the tree and replace any correction leaf they reach with identity. Keep the rest of the tree unchanged.

This is a concrete check against clean photos withheld from fitting that tree, rather than requiring clean fitting examples inside every correction leaf. It may still remove useful corrections or miss other clean failures. The reserved groups are already development-exposed and would be used to select the model's final behaviour; they are not independent validation.

The [proposed fixed protocol](reserved-clean-veto-protocol-2026-11-08.md) defines one comparison. No fits are authorised merely by this diagnosis, and none have started. Keep the separate eight-group, 24-photo holdout unopened and retain the original joint acceptance requirements.

## Verification

Scripts 626–627. Independently checked saved leaf memberships through the portable tree, all 40 usable clean routes and source hashes. No model fitting, image-model inference, rendering or image-source reads. Private artifacts: `outputs/correction_branch_clean_evidence_v1`. The depth-four candidate remains unadopted; masks and correction boundaries remain unresolved.
