# TrueHue: adviser decision brief

**2 November 2026 | Discussion draft - not a request letter or an approved change**

**Decision needed:** Agree on a realistic way to complete and evaluate the study
without presenting the experimental model as reliable automatic correction.

## What has improved

The correction region now covers the selected face and visible neck, fills
enclosed holes and blends inward at the outside edge. Skin-tone measurement uses
a separate facial-skin mask that excludes features, hair and neck. FaceOcc is the
preferred experimental addition for rejecting obstructed areas; it is not adopted
in the current demo. Previews of the improved correction region use fixed example
adjustments, not predictions from a newly trained correction model.

## What the evidence shows

- **Earlier MST calibration:** 418 attempts, 393 measurements and 15 subject-held
  evaluation folds. Exact category accuracy was **12.98%**, with average category
  error **2.125** (previously **2.097**). This mapping was not adopted. It used the
  earlier measurement method, so it cannot be reused as a FaceOcc lookup.
- **Current skin-mask check:** one fixed photo for each of 19 existing people;
  18 received human judgments and one failed processing. Structured answers were
  favourable for **11**, with concerns or uncertainty for **7**. Facial hair,
  dark/unclear photos and lighting uncertainty remain. Favourable answers are
  visual evidence, not verified skin pixels or true-colour reference approval.
- Only MST categories **1, 4 and 5** have two people with favourable structured
  answers in this sample, before other concerns are resolved. In the full official
  inventory, categories **7 and 10** each have only one person. More photos of the
  same person do not add independent people.

**Reliable ITA-to-MST mapping and reliable automatic correction remain unfinished.**
The Python and Android demos retain their older experimental correction baseline.

## Recommendation and options

**Recommendation:** Keep the intended method and report the prototype, improvements
and limitations honestly. Pause further fitting on the same evidence. Do not claim
the original accuracy goals are met or the thesis is complete.

If the original full correction goal remains required, plan stronger measurement,
label and reference evidence under a fixed evaluation design before fitting again.
This may use qualified existing data; recruitment is not automatically required.
Better data may help but does not guarantee success.

If that evidence is impractical within the available time, discuss whether a
narrower study contribution and evaluation scope is academically acceptable.
Any formal scope change needs explicit agreement and the applicable panel process;
it cannot be inferred from the current results. A reduced scope does not make an
unreliable mapping reliable.

## Requested discussion

Should the study retain the full correction goal with a revised evidence/timeline
plan, or should a narrower contribution be proposed to the panel? Keep
**ITA + calibrated MST + facial statistics -> decision-tree gamma/red/blue
correction** unless a separate change is explicitly agreed. Professional review
through the existing Google Form follows a good initial model, then refinement
and re-review. Adviser discussion is for academic direction, not a new technical
permission gate. No new recruitment, professional contact or paper edits are
initiated by this brief.

**Supporting records:** [MST calibration results](nostril-mst-calibration-results-2026-11-01.md);
[completed 19-person skin check](mst-subject-skin-study-results-2026-11-02.md);
[adopted masking design](adopted-masking-design-2026-11-01.md);
[proposed changes register](panel-change-register.md).
