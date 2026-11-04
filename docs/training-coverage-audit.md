# Training-source coverage audit and expansion plan

24 October2026. Follow-up to [the controls study](correction-controls-sourcecv-results.md).
No new fitting, eligibility promotion or runtime change.

## Findings

The existing22 development pairs represent only six source photos. Repeating
distortions does not add independent appearances. Current fitting variants are
four dark, three color-shift, three bright/warm, six unchanged and six mild.

Five of the six held-source unchanged probes fall inside every training-fold
feature's individual range. Only6236 has an out-of-range L* value. The severe
unchanged51739/75027 errors and22454 color error therefore cannot be explained
solely by crossing those marginal limits. Being inside each range does not
establish joint coverage or correct parameter identification. A simple
out-of-range gate would miss important failures.

The feature plot compares fresh256 measurements, not MST categories or intrinsic
skin tone. Different natural appearances and synthetic states still need more
representative examples; this audit does not prove a particular feature change
or model architecture will solve the problem.

## Fixed candidate search

The prior650-row source audit contains450 training-pool records. Its training
statuses are316 unreviewed holds,78 automated failures,26 provisional reviewed
candidates,22 review/known-geometry exclusions and eight uncertain-geometry holds.

Within unreviewed processing successes,284 have no recorded prior development
exposure;32 have prior exposure. Exclude current source groups and append-only
new exposure records. Select18 from the284, using six equal-count rank bins of
historical native-photo L* and a seed42 hash order, three per bin. Native L* is
only a sampling proxy; it is neither an MST label nor a severity rule.

All selected IDs belong to the existing training partition. No validation or
reserved-test image was processed/visually reviewed in this batch. Historical
metadata are read to enforce those boundaries. Subject independence remains
unverified; no face recognition or demographic inference was used.

## Screening outcome

- All18 originals were processed at256 before fresh detection/landmarks and
  complete-mouth masking; clean-source hair veto was checked separately.
-17 passed the numerical pipeline;22905 lacked usable landmarks and remains held.
- Codex inspected all18 on six contact sheets. Most show blur, occlusion,
  fragmented support, non-skin inclusion or uncertain reference rendering.
- **20555 is promising for follow-up only.** It has a relatively frontal face
  and broad coverage without obvious large occlusion. It is not accepted yet.
- The other17 are held, including the pipeline failure. Original human decisions
  remain pending; no new source enters training. Reasons are saved per image.

Low contrast or uncertain illumination is a photo/reference-quality concern,
not a claim that naturally darker skin is unsuitable. Conversely, pipeline
success does not approve a brighter image with paint, glare or missing skin.
The18-image targeted batch cannot estimate full-pool acceptance rates or prove
that FairFace is unsuitable in general.

## Concrete next steps

Completed follow-up: [20555 variants and the next18-source screen](source-screening-followup.md).
20555's color-shift estimator loses most facial support; four sources from the
second batch are promising but unaccepted. Training/model remain unchanged.

1. Inspect20555 at its saved/native resolution and run the fixed unchanged,
   mild and original distortion checks separately. Confirm mask/reference
   suitability, clipping and failures before any eligibility decision.
2. Screen another bounded18-image batch from the remaining266 eligible IDs,
   using the same selection/exposure rules. Assess source detail, occlusion,
   reference suitability and mask contamination before generating pairs. Keep
   all failed/held records; do not count them as training-ready.
3. Consolidate genuinely suitable sources and assess their observed feature
   coverage and source separation before another fixed training comparison.
   Do not choose photos because they make a model score improve. Keep unchanged
   controls, per-source/variant reporting and the no-correction baseline.
4. If suitable sources remain scarce, record that feasibility limitation and
   resolve the data/masking approach rather than repeatedly tuning depth or
   clamping outputs on the same six sources. Final MST/SCIN roles remain open.

For the requested face-and-neck correction, these tight head crops provide
limited neck evidence. This audit does not localize or validate neck support.
A later neck experiment still needs appropriate framing and separate region
assessment; do not expand the current unreliable parameters onto neck pixels.

## Exposure and evidence

All18 IDs were logged **before processing** in
`data/manifests/development_exposure_additions.jsonl`. Future candidate selection
must read this ledger as well as historical flags; these newly inspected images
are now development-exposed and cannot become a fresh final holdout. The old
master exposure field was not rewritten or presented as current truth.

- [Six source-review sheets](../outputs/training_coverage_audit_v1/review-index.md)
- [Feature coverage plot](../outputs/training_coverage_audit_v1/feature_coverage.png)
- [Pool counts and fold feature limits](../outputs/training_coverage_audit_v1/summary.json)
- [Per-source disposition](../data/manifests/training_coverage_audit_v1/candidate_disposition.json)
- [Verification](../outputs/training_coverage_audit_v1/verification.json)
- Scripts64/65 preserve their outputs and refuse overwrite.

Verified18 TRAIN-only unique selections, saved256 mask contracts/counts, removal-
only hair cleanup, exposure-ledger coverage and unchanged original model/source/
review hashes. All six review sheets and the PNG feature plot were visually
inspected. Existing full suite: **464 passed**. No training table/model was
replaced, no human label changed and no new model was fitted.
