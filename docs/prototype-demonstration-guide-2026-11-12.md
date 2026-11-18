# Research-prototype demonstration guide

12 November 2026. This guide presents existing software and preserved results. It does not request another photo, mask review, training run or expert rating. No live application or new photo inference was executed when preparing this milestone.

## Opening statement

"TrueHue is a local research prototype for single-photo skin-region measurement and decision-tree correction. Mask inspection, optional manual refinement and exports work. The tested correction models are not validated for reliable use, and the current demonstration retains historical controls. I will show both restoration benefits and failures."

## A five-minute walkthrough

1. Open the [milestone report](../outputs/research_prototype_paper_milestone_v1/index.html). Show the status statement before any examples. This read-only report does not run a model or write annotations.
2. Explain the two supports: facial measurement for Lab/ITA and a separate face/visible-neck correction area with protection. Explain optional manual refinement as a supported interaction, not a new request to edit the completed review queue.
3. Open all four linked saved spatial-comparison sheets. Within each case, panels are **input / held-model output / original reference**. Together they show all 44 cases from eleven source photos. They are a failed developmental candidate, not the current app, an independent final test or a best-result gallery. Include the identity and mild-cast failures as well as exposure improvements.
4. Show the matched table in the report. Explain that useful average exposure restoration coexists with unwanted edits and colour harms. The larger experiment is a separate cohort and cannot be pooled into the 44-case averages.
5. Close with what remains unresolved: source transfer, honest tone-group evidence, an end-to-end compatible frozen model, final evaluation, expert MOS and Android measurements. Keep the working-model objective explicit.

## Existing desktop software, if already demonstrating it

The current launcher is `run_truehue_demo.cmd`. Its UI has **Choose photo**, **Run demo**, **Save result / report**, and **Refine mask**. This guide does not run it or select any new image. Use an existing permitted development example only when a live demonstration is separately intended; never browse to locked images. Do not imply that the saved experimental report is a live application run.

The UI itself labels the workflow as current masks with older experimental controls. Source inspection of `src/demo/current_masking.py` confirms separate historical feature/MST/control provenance and `combined_pipeline_validated=False`. The refinement callback updates displayed measurement and reloads the refined run; it does not retrain the tree or recalculate the historical controls. Save applies to the export, not scientific model admission. A better painted beard exclusion may improve measurement while leaving an overly bright correction unresolved.

The root `review_ffhq_support.cmd` is a completed data-review queue, not the presentation launcher. Its eleven saves were audited; do not use it to redo the reviews. Earlier labelled, brightness and photographic reviews likewise need no repetition. Do not run numbered training/acquisition scripts as a demonstration setup step, especially script 665.

## Accurate wording

| Say | Avoid claiming |
|---|---|
| "The prototype supports manual mask refinement and export." | "Manual refinement fixed the learned correction model." |
| "This preserved developmental comparison improved exposure means." | "These examples prove correction works on unfamiliar photos." |
| "The correction predictor is a decision tree using ITA/MST features." | "The experiment demonstrated fair correction across MST groups." |
| "The broad model preserved 40 usable clean references." | "All 54 clean photos were successfully analyzed and preserved." |
| "The current app uses historical controls and is unvalidated." | "The new experimental model is already integrated." |
| "Final evaluation and expert MOS are pending." | "Visual inspection here is an expert MOS or final test." |

No screenshots, new visual assessments, user reviews, app execution or phone benchmarks are claimed by this guide. The linked boards were inspected in their recorded experiment; this milestone only links them. No photos are embedded in the paper draft or copied into a distributable package. Keep source licences and permission requirements in mind before sharing images externally; no sharing is performed here.
