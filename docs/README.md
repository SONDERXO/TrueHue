# TrueHue documentation: start here

Development is ongoing. This guide distinguishes current work from the research
library; the original files stay in place to preserve links and evidence hashes.

## Current work

**Next task:** check the existing face-and-neck support on the same12 FFHQ
sources, saving a protocol first and retaining all difficult/failed cases.
ITA-to-MST is deferred for this source work. No new training is activated.

| Need | Open |
|---|---|
| Latest continuation notes | [Session handoff](session-handoff-2026-10-30.md), newest entries first |
| Current FFHQ sources and limitations | [FFHQ source results](ffhq-source-preparation-results-2026-11-03.md) |
| Local FFHQ source gallery | [Source gallery](../outputs/ffhq_source_visual_assessment_v1/review.html) |
| Adopted mask/rendering design | [Masking design](adopted-masking-design-2026-11-01.md) |
| Full development requirements | [Integrated plan](integrated-correction-development-plan-2026-11-03.md) |
| Differences from the proposal | [Panel change register](panel-change-register.md) |

## Working thesis

- [Methods and interim results,3November](thesis-methods-results-draft-2026-11-03.md).
- [Discussion, limitations and interim conclusion,3November](thesis-discussion-limitations-conclusion-draft-2026-11-03.md).
- [Verified proposal scope](proposal-scope-validation-2026-11-03.md).

These are unfinished working drafts. The submitted proposal is a separate local
reference. Older drafts/addenda remain dated evidence; use the current versions
above for editing.

## Research topics

| Topic | Key records |
|---|---|
| Masks and rendering | [Adopted design](adopted-masking-design-2026-11-01.md), [continuity](reference-r1-and-continuity-results-2026-11-01.md), [FaceOcc evidence](faceocc-comparison-evidence-2026-11-01.md) |
| ITA/MST | [Completed calibration](nostril-mst-calibration-results-2026-11-01.md), [19-subject review](mst-subject-skin-study-results-2026-11-02.md) |
| Correction recipes | [Exposure revision](directional-exposure-revision-results-2026-11-03.md), [colour/combined](core-colour-recipe-results-2026-11-03.md), [core/stress/clean roles](synthetic-development-role-results-2026-11-03.md) |
| Operator capacity | [PPR contrast](ppr10k-contrast-diagnostic-results-2026-11-02.md), [detail/region correction](ppr10k-clipping-detail-results-2026-11-02.md), [smooth boundary](ppr10k-smooth-boundary-results-2026-11-02.md) |
| App | [Android guide](../android-app/README.md), [implementation checkpoint](delivery-checkpoint-2026-11-01.md) |
| Repository and organisation | [Maintenance](repository-maintenance-2026-11-04.md), [organisation](project-organisation-2026-11-05.md) |

For all records, use the [topic-grouped research library](navigation/research-library.md).
Topic grouping is a finding aid, not a claim of acceptance, validation or current
activation. Older protocols, rejected candidates and superseded handoffs remain
available with their original paths and contents.

## Other entry points

- [Searchable local project catalogue](../PROJECT.html): current pointers,
  documents, scripts, tests and locally saved result folders.
- [Script catalogue](../scripts/README.md): descriptions and paths; read the
  individual protocol before running an experiment.
- [Optional VS Code workspace](../TrueHue.code-workspace): separate views for
  code, Android, tests, docs, scripts, data and results. It changes the workspace
  view only; the normal folder view still exposes the original layout.

Local galleries, datasets, models and generated reports are ignored by Git. Their
links work in this existing workspace; a source-only clone needs those local
artifacts separately. DAST is dropped; no STW reply or access is assumed.
