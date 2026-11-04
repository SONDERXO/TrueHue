# Thesis 2 Implementation Plan

31 October2026 latest direction supersedes the parser hold below: the user
authorized proceeding with the existing fuller-face mask and matching ITA/MST
development while recording changes/results. Beard/mustache-specific work stays
on hold. Desktop/Android presets stay unchanged during candidate evaluation.
Follow `semantic-measurement-single-cycle-protocol.md`; no new small correction
trials on the old cohort. Approval paperwork is not a technical prerequisite
under the user's clarified process; do not represent this as a panel decision.

31 October2026: user resumed Android integration while awaiting the adviser.
This supersedes the historical Android pause below. Port the existing Python-demo
baseline5/fold1 only as experimental integration; retain ITA/MST and original
rule-based masking. New training and parser/beard changes remain on hold.
Thesis finalization waits for completed implementation/evaluation; reviewed Word
comments are not assumed resolved or accepted.

30 October2026 mask implementation direction: the user explicitly authorized
the existing local face parser for whole-face coverage and exclusions, while
retaining ITA+calibrated MST+facial-statistics decision-tree correction. This
changes the formerly rule-based masking stage and needs matching calibration
before pipeline adoption. See [mask repair results](face-mask-coverage-repair-results.md).
The new mask is a standalone preview; the existing demo and lookup remain unchanged.

Latest user decision (28 October2026): **retain the proposed MST method**.
The final correction model must use computed ITA, calibrated mapped MST and
facial color statistics (proposal PDF62–63). The four-feature continuous
ITA/Lab models remain development baselines. Android is on hold while this
Python path is completed. See [MST implementation checkpoint](mst-method-retained.md).

Current method checkpoint (23 October 2026): see
[thesis-method-alignment.md](thesis-method-alignment.md) for proposal differences,
unfinished requirements and the record to consult during future thesis edits.
The checkpoint does not amend the fixed scope below.

Current execution direction (27 October2026): the user set CPM/material-model
expansion aside and retained paint/makeup protection as a limitation. Resume the
core ITA/MST/decision-tree/on-device work. [Portable frozen-tree inference](core-tree-portability-results.md)
now matches the existing prototype without sklearn/NumPy at prediction time;
this is software parity, not final correction quality or completed MST/Android.
Historical experiments, review decisions and source holds remain preserved.

[Unified core runner](core-pipeline-check-results.md) now records detection,
masking, Lab/ITA, explicit unavailable MST and development correction in one
stage ledger.37/38known attempts produce outputs; the original failure remains.
Software consistency does not resolve unchanged/mild overcorrection or MST.

## Objective

Develop a smartphone-based, post-capture skin tone correction application that uses ITA-based skin tone estimation and a decision-tree model to improve exposure and color across Monk Skin Tone categories.

## Fixed Scope

The list below records the proposal baseline. User-requested implementation
direction added on23 October2026: correct **face and visible neck skin** of the
selected person while retaining facial skin for current ITA measurement.
See [face-and-neck requirements](face-and-neck-correction-requirement.md).
This expansion is recorded for future thesis edits; it is not yet implemented
or represented as a formally amended proposal.

- Platform: Android, on-device only
- Input: Gallery image (single face)
- Pipeline: face detection → skin mask → ITA → MST → decision-tree correction → corrected image
- Model: decision-tree regression (gamma, red gain, blue gain)
- Datasets: FairFace + SCIN (training), MST-E (evaluation only)
- Evaluation: MAE, CIEDE2000 ΔE, inference time, expert MOS (2 photographers)
- Out of scope: iOS, live camera, cloud processing, full-body correction, ISP modification

## Milestones

1. Python prototype (face + mask + ITA + MST)
2. Synthetic distortion generator
3. Baseline and decision-tree model
4. Android integration
5. System testing
6. Quantitative + expert evaluation
7. Thesis documentation


## 28 October2026 delivery checkpoint

User explicitly requires Python prototype, Android app and thesis results before7November. Target6November cutoff; follow [delivery schedule](deadline-delivery-plan.md). Existing Android scaffold is present and authorized for extension. Java tree core now passes44Python-parity vectors and15invalid cases; APK and actual device integration remain pending. Historical proposal baseline and unresolved MST/model-quality/data/expert requirements are unchanged.
