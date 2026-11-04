# Seven accepted-note cases: layer inspection

24 October 2026. Confirmed that the three concerns arise at different stages. Your seven acceptance decisions and notes remain unchanged; separate technical holds prevent premature training. No mask repair or feature replacement was performed.

| Source | Generation | Measurement | Correction | Consequence |
|---|---|---|---|---|
|31154, three accepted variants|Hair/background patch included|Same patch included|Same patch included|Affects synthetic edits, features and correction selection|
|60162, two accepted variants|Background patch included|Chosen patch excluded|Chosen patch excluded|Synthetic input still alters background that application support will not correct|
|63870, two accepted variants|Chosen fabric patch excluded|Fabric included|Chosen fabric patch excluded|Features are contaminated despite cleaner correction support|

These findings use small visually inspected diagnostic rectangles in the saved256 images, not exhaustive human skin annotations. Counts below establish concrete examples only. They do not quantify every non-skin pixel or establish that all pixels outside the rectangles are clean.60162 still has other boundary uncertainties; zero overlap here does not establish globally clean masks.

- 31154 hair/background rectangle `[10,205,50,235)` contains614 generation pixels,620-624 measurement pixels and611-624 correction pixels. Bright and mild inputs change614 pixels there; identity correctly changes none.
- 60162 background rectangle `[225,160,248,220)` contains45 generation pixels and zero selected measurement/correction pixels in either accepted case. Both inputs actually change all45 background pixels.
- 63870 upper-left covering-fabric rectangle `[0,0,20,40)` contains692 measurement pixels and zero generation/correction pixels for both accepted controls. That fabric still influences their feature vectors.

Coordinates are half-open x0,y0,x1,y1 bounds. Red rectangles on boards identify the witnesses; green indicates selected pixels. These regions were selected by Codex after inspecting the images; they are diagnostic evidence, not user-provided segmentation labels. A trial removal was used only to record feature sensitivity; no altered feature values enter a training table.

## Training consequence

All seven cases remain accepted by you but technically held. The other28 accepted pairs remain candidates for staging, not final training approval. Removing these seven leaves original fold pair counts4,13,8,0,3. The planned fourth fold is empty, so the declared five-fold analysis is currently **not ready**. Do not silently reassign sources, restore uncertain/rejected cases or call a four-fold result the planned five-fold experiment.

The next recommended experiment is a separately versioned non-skin exclusion check covering generation, measurement and correction together. Fix one candidate rule before running it across all75 existing attempts, with unchanged controls and earlier hair/paint regression cases. Compare facial retention and non-skin removal, preserve baseline outputs and failures, and seek user review of changed masks before considering new inputs or fitting. Manual deletion of these witness rectangles is not a general mask solution. Keep the user's requested own-neck support distinct from hair, clothing/background or another person's skin.

Changing generation requires fresh variants from the source; changing measurement requires recomputing all inputs consistently and later refitting. Replacing only the correction mask cannot repair an already contaminated measurement or source-generation recipe. Do not overwrite earlier review decisions or silently adopt YCrCb-only features.

All input/model/review/schema/ledger hashes stayed unchanged. Seven cases and three layer boards were inspected, acceptance/note provenance preserved, and **464 tests passed**. No model was fitted or promoted. Operational MST, face-and-neck correction, final cohort/reference eligibility and final thesis evaluation remain unfinished; this experiment is recorded for later method edits, not a proposal amendment.

[Layer comparison boards](../outputs/source60_note_inspection_v1/review-index.md) | [Detailed technical findings](../data/manifests/source60_note_inspection_v1/technical_findings.json) | [Verification and fold readiness](../outputs/source60_note_inspection_v1/verification.json)

Completed follow-up: [fixed three-stage non-skin veto](non-skin-veto-experiment.md). Partial improvement, unresolved hair and facial-loss risks; not adopted.
