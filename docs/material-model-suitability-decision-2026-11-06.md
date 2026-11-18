# Facial-hair model suitability decision — 6 November 2026

The proposed targeted exclusion comparison cannot yet run with a verified,
accessible explicit facial-hair checkpoint. This closes the suitability check;
it does not establish that automated beard exclusion is impossible. ResNet34
remains an isolated candidate, not an adopted measurement mask.

The existing [model inventory](explicit-facial-hair-model-inventory.md),
[acquisition record](facial-hair-checkpoint-acquisition.md) and
[two local auxiliary-model results](facial-hair-exclusion-results.md) already
cover this dependency. Both local EasyPortrait conversions removed genuine
cheek/chin skin in their bounded checks. Their background output is not an
explicit beard label. Those failed rules will not be rerun or tuned.

The [DINO-based parser](https://github.com/jseobyun/FaceParsing) was checked
again on 6 November. Its documented classes include beard, hair, glasses and
facewear. It needs a separate decoder and DINOv3 backbone; the documented
predictor defaults to 512 by 512 input. A glasses class alone does not establish
separate transparent lenses and frames. Exact preprocessing, tensor contracts
and checkpoint hashes would still need verification before execution.

The repository's licence section refers to the DINOv3 weights' terms without
establishing separate decoder/code reuse terms. The
[official backbone page](https://huggingface.co/facebook/dinov3-vitb16-pretrain-lvd1689m)
still requires login and agreement to share account information. No access form
was submitted, agreement accepted, decoder downloaded or network executed.
The Roboflow lead retains its previously recorded authentication and
project-specific weight-access/terms dependency; no repeated unauthenticated
request was made. No suitable new complete model was established in this check.

## Scope supported by current evidence

- The correction operator has synthetic photographic recovery diagnostics.
  They measure conditional operator capacity, not learned correction accuracy.
- The masking experiments show a coverage/protection trade-off. On the same
  available sparse development points, ResNet34 selects 77/113 skin points
  versus 54/113, but also 15/94 unwanted points versus 9/94. These are not dense
  segmentation accuracy or independent evaluation results.
- The contextual ITA + Lab estimator software is tested on generated arithmetic
  data. No real-data calibration cohort or real contextual MST fit is admitted.
- The Android demo continues to use its existing pipeline. Automatic beard,
  object and transparent-glasses handling is not validated for general use.

Next substantive work should specify a correction-model experiment whose input
features, targets and evaluation claims match the evidence actually available.
A controlled synthetic correction experiment may be designed separately, with
source lineage held together and existing exposed sources declared development
data. It must explicitly resolve the unavailable compatible MST feature before
any full-method fit; do not round decimal labels, reuse incompatible lookups or
silently drop MST. Designing this experiment does not activate training or
declare the mask/calibration problem solved.

The alternative route is obtaining a complete explicit beard checkpoint with
verified local access, label mapping, preprocessing and reuse terms. That
dependency can reopen one bounded material test when it actually changes.
No further model sweep, sample expansion, annotation task, account action or
author contact is activated by this decision.

No new inference, mask changes, dependencies, fits, admissions, runtime changes
or uploads occurred. No new tests were needed for this documentation-only
decision. Historical test counts remain historical. Private dataset evidence
and author research/noncommercial, citation and no-redistribution terms remain
unchanged.
