# Face and visible neck correction

User requirement recorded: 23 October 2026.

31October2026 implementation update: the user reaffirmed visible-neck coverage
and authorized proceeding. A separate correction-support candidate and photo
picker now exist; facial ITA/MST measurement masks remain unchanged. Read
[current neck implementation/results](face-neck-support-results-2026-10-31.md).
The historical plan below remains as provenance; neck quality and final
correction validation are still unfinished. No adviser-response gate applies.

The intended correction region now includes the selected person's **face and
visible neck skin**. Neck skin should not be rejected merely because it lies
below the jaw or outside the detected face box. This is an authorized project
direction from the user; it is not a claim that the proposal has been formally
amended or that neck correction is already implemented.

## Measurement and correction have different regions

- Keep facial skin as the current ITA/color measurement region. Adding neck
  correction does not automatically change the model's four input features.
- Build correction support over the full input image: facial skin plus visible
  neck skin belonging to that same person. Keep region masks separately so
  neck behavior can be assessed without changing facial measurements.
- Start any neck prototype with the same correction parameters for face and
  neck, recording that choice. Do not force neck pixels to match facial color;
  natural color and lighting differences must remain possible. Shared parameters
  need evaluation where face and neck lighting differ.
- Exclude clothing/collars, hair/beard, paint, jewelry and background. The
  existing material/hair checks are not guaranteed to identify all such regions.
  Preserve explicit protected pixels under both facial and neck correction.
- If no suitable neck is visible, correct eligible facial skin only. Record
  neck status explicitly; do not manufacture a region or select another person.

## Consequences for existing experiments

The current estimation/correction helpers work inside a face bounding box.
They may incidentally include neck pixels, but do not provide reliable neck
localization. A face-box expansion or generic body-skin segmentation class
alone would also admit clothing, arms or other people's skin.

The lower-face oval was designed for the previous facial-only target. It must
not become the final face-and-neck boundary: it would intentionally remove
the neck now requested. Keep it as historical facial-only evidence.

Earlier reports group some neck and collar additions together as spill. Under
the new target, actual neck skin may be desirable; clothing/collars and unrelated
skin remain errors. Do not reclassify all old spill as correct. Preserve the
historical reports and reassess their actual regions under the new target.

The recent color-error scores use generation regions primarily covering the
face. They do not establish neck quality. Expanding correction into an
undistorted neck can worsen reconstruction in the current simulations; a neck
experiment needs separately documented generation/scoring regions.

## Development plan

Update24 October2026: [source-held-out controls study](correction-controls-sourcecv-results.md)
completed. Adding unchanged/mild examples alone did not fix overcorrection.
No new model or neck support was integrated; correction strength remains open.

1. Finish the current correction-strength diagnosis while keeping the recorded
   masks/model unchanged. The old model alters unchanged and mild inputs;
   extending its affected area would spread that error.
2. Freeze a separately versioned face-and-neck support experiment using input
   geometry to associate visible neck with the detected face. Retain the face
   estimation region and feature schema. Do not use clean references at inference.
3. Use wider-framed development photos with an actual visible neck, alongside
   no-neck, collars, long hair, beard, paint and multiple-person boundary cases.
   Existing tight FairFace crops cannot demonstrate broad neck performance.
4. Compare face-only and face-plus-neck corrected outputs with identical settings.
   Score face and neck separately, preserve outside-support pixels, and report
   neck availability/failures and face-neck transition quality. Keep prior data
   exposure, original splits and held-case history visible.

## Completion criteria

- Visible neck skin of the selected person can be corrected beyond the face box.
- Face measurements remain reproducible unless an estimator revision is explicit.
- No new selection of clothing/collars, unrelated people or non-neck body regions
  is accepted solely because a generic skin detector selected them.
- Neck unavailable/absent cases do not silently fall back to broad body correction.
- Face and neck outcomes, seams, protected-pixel behavior and failures have
  separate evidence. Existing hair/paint limitations are reported honestly.

## Thesis editing record

The proposal's Scope and Limitations explicitly restrict detection, estimation
and correction to the facial region (PDF page13, printed page6). Face-and-neck
correction is therefore a requested scope expansion to record for later thesis
editing, alongside [the method distinctions](thesis-method-alignment.md).
Do not label this merely a bug fix already covered by the facial-only method.
The proposal PDF, datasets, runtime and model were not changed by this record.
