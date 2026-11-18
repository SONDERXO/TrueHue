# Conference evidence brief — 6 November 2026

Recommendation: develop a diagnostic/prototype paper about correction capacity
and mask-dependent failure modes. This is a proposed submission framing, not
confirmation that the unidentified venue accepts this paper type or that the
adviser has approved a change in thesis scope. Do not describe the work as a
validated automatic skin-tone-aware correction model.

## Evidence to use

| Question | Executed evidence | Supported result | Boundary |
| --- | --- | --- | --- |
| Can the three-control operator recover controlled distortions? |12exposed FFHQ photographic lineages,14cases each;168attempts; reference-aware fitted controls |96core RGB8 MAE18.665→0.135 under fixed support;60stress53.593→11.034;12clean exactly unchanged |Oracle fits use reference targets; no learned prediction or ideal/intrinsic colour claim |
| What happens when masks come from distorted inputs? |Same168inputs;167technical measurements,155nonclean fits,12neutral controls;one retained failure |Core recovery MAE0.591; all60stress attempts13.526, including failed case as unchanged input |Same recipes/sources; not independent replication or automatic correction accuracy |
| Does a larger parser resolve skin selection? |Same six selected Stellenbosch reference photos; five final predictions available |Actual sparse skin points54→77/113; unwanted9→15/94 |BiSeNet family comparison; larger backbone improves selected coverage but worsens selected material inclusion; not dense accuracy |
| What do actual user regions add? |Six marked photos/five publisher keys;36polygons/3156native union pixels |On five available predictions: baseline987/2551selected patch pixels versus ResNet341558/2551 |Patches include neck; face-only recall, full-face truth and independent validation are not established |
| Is the continuous MST/correction software connected? |Generated arithmetic inputs and focused interface/tree tests |Fractional1–10prediction enters isolated five-feature tree schema;12portable replays match |No real contextual MST fit, photographic tree fit, correction benefit or category accuracy |
| Is there an app prototype? |Android debug build,18JVM tests,lint0errors/45warnings; older pipeline |Photo input and before/trial display work as prototype features |New research mask and continuous score not integrated; app quality not established by compilation |

Scientific denominators must remain separate:168variants are not168people,
six review images are not six unique subjects, points/pixels are not independent
participants, and software test counts are not accuracy observations. FFHQ and
Stellenbosch results address different questions; never pool their metrics.

## Source trail for manuscript claims

- [Fixed-support operator fits](ffhq-correction-target-results-2026-11-05.md), private source package `outputs/ffhq_correction_targets_v1/`.
- [Actual-input support experiment](distorted-input-support-results-2026-11-05.md), private source package `outputs/ffhq_distorted_input_support_v1/`.
- [ResNet34 comparison](resnet34-parser-comparison-results-2026-11-06.md), private source package `outputs/resnet34_parser_comparison_v1/`.
- [Actual sparse-point review](stellenbosch-reference-point-results-2026-11-06.md).
- [Actual patch measurements](skin-patch-measurement-results-2026-11-06.md), final private source package `outputs/stellenbosch_skin_patch_import_v2/`; v1colour statistics superseded.
- [Continuous-score software result](continuous-mst-correction-results-2026-11-06.md).
- [Android build record](android-consultation-update-2026-11-05.md).

Use scalar errors with their exact conditions; do not convert them into
percent accuracy. Fixed-support versus input-support comparison describes
mask/support dependence under this experiment, not a complete causal analysis.
Report stress clipping, perceptual regressions, object spill and the retained
technical failure alongside mean improvements.

## Proposed contribution and explicit exclusions

The contribution is a reproducible separation of operator capacity,
input-derived support behavior and reviewer-reference diagnostics in a
three-control correction prototype. It includes unfavorable findings rather
than claiming a completed final method. Novelty and venue fit still need a
focused related-work assessment once the venue and paper type are supplied.

No demonstrated real-data contextual MST performance, learned three-control
prediction, skin-tone fairness, unseen-person generalization, automatic glasses
classification, intrinsic colour recovery, expert MOS or final app validation
is claimed. Generated tests belong in implementation verification, not the main
scientific results table. Do not call partial reference overlap segmentation
accuracy or equate selected-pixel coverage with reliable measurement.

## Submission decisions still needed

The user has been asked for conference name/link, template and page limit.
Verify its deadline timezone, track, anonymization, research requirements and
artifact policy from its official instructions after receipt. Do not invent
compliance. The user/adviser should review the proposed diagnostic framing
before it is presented as the final study contribution. This does not block
preparing a clearly labelled working draft now.

Use aggregate tables and pipeline diagrams initially. Dataset access does not
authorize identifiable photo/label redistribution: no private Stellenbosch
images, crops, annotations, per-subject scores or public galleries in the
submission without necessary author consent. Retain citation of Mbatha,
Booysen and Theart, *Skin Tone Estimation under Diverse Lighting Conditions*,
Journal of Imaging10(5),109(2024), DOI10.3390/jimaging10050109. Existing FFHQ
attribution and source-specific publication permissions also remain relevant.

No training, additional sample, repeated review, source sharing, account action
or submission is activated by this brief.
