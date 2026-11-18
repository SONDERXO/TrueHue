# Mask-dependent failure modes in a three-control facial colour-correction prototype

**Working diagnostic-paper draft, 6 November 2026.** Proposed framing for review;
not venue-formatted, submitted, adviser-approved or a claim of completed thesis
validation. Author details, venue format and related work remain to be completed.
The [evidence brief](conference-evidence-brief-2026-11-06.md) binds the numerical
claims below to executed local experiments.

## Abstract

Facial colour correction depends on both the correction operator and the
regions selected for measurement and application. We examine these components
separately in a prototype using gamma and red/blue gains. Twelve development
photographic lineages supplied168controlled cases. Reference-aware fitting on
fixed support reduced mean RGB8 error from18.665to0.135on96core distortions;
rebuilding support from distorted inputs increased recovery error to0.591.
For60stress cases, corresponding recovery errors were11.034and13.526,
including a retained technical failure in the latter average. A separate
six-photo development review found that a larger face-parser backbone increased
selected skin reference points from54to77of113, but also increased unwanted
selections from9to15of94. Human-selected patch measurements corroborated
incomplete automatic coverage, with face/neck scope differences explicitly
retained. These findings demonstrate conditional correction capacity and
mask-dependent limitations; they do not establish learned correction accuracy
or validated skin-tone estimation. The prototype and experimental
continuous-score interface provide implementation groundwork for later
person-separated calibration and predictive evaluation.

## 1. Problem and study question

The prototype aims to predict gamma and red/blue controls from facial colour
statistics, ITA and a calibrated skin-tone estimate. Automatic mask errors can
affect both those measurements and where correction is applied. An effective
operator therefore does not by itself establish an effective automatic system.
This diagnostic study asks what the operator can recover under controlled
conditions and what limitations emerge when support is inferred from distorted
images. Original photographs are reconstruction references, not instrumental
measurements of intrinsic skin colour.

## 2. Materials and methods

### 2.1 Photographic correction diagnostics

All12previously exposed FFHQ photographic lineages were retained. Each had one
clean case, eight core cases and five composite stress-design cases, giving
168attempts. Every source used one common medium engineering severity preset;
no measured MST label or tone-stratified augmentation was assigned. All
descendants are development data; the lineages do not establish independent
person identities or an untouched evaluation cohort.

The renderer used three positive controls: direct-exponent gamma, red gain and
blue gain, blended through saved correction alpha. Fixed-support fits used the
same support for synthesis and recovery. One reference-aware local fit was
performed per nonclean case, with neutral initialization, bounds0.25–4,
maximum500evaluations and tolerances1e-10. Clean cases used exact-neutral
controls. These are per-case oracle fits, not learned model predictions.

The second diagnostic rebuilt measurement and correction support from each
actual distorted image using the frozen detector, landmarks, semantic parser,
anatomical exclusions and aligned visibility model. Explicit clear/opaque lens
choices were retained; glasses type was not automatically classified. Fits used
the declared fitting-support intersection, while final errors covered the full
original scoring support, including missed regions. One technical failure was
retained as unchanged input in the all-attempt result.

RGB8 MAE measures mean absolute channel error on a0–255scale. Relative
CIEDE2000 compares with the original photograph. Clean, core and stress results
remain separate; synthetic variants do not increase the number of people.

### 2.2 Skin-support reference diagnostics

Six selected, already exposed Stellenbosch photos from five publisher keys
were reviewed at native resolution. The release supplies224by224images and
subject-level decimal skin-tone scores. The source dataset is described by
Mbatha, Booysen and Theart(2024). This diagnostic does not reproduce that paper's
trained estimator or validate the supplied scores against physical colour.

A completed user review supplied238sparse points:129skin,101hair/beard and
eight object/other. The landmark-failure photo contained31points and remained
prediction-unavailable. Thus the paired comparison used113skin and94unwanted
points across five images. One fixed ResNet34 parser was compared with the
frozen ResNet18 baseline under unchanged downstream exclusions and saved
visibility predictions. Both have the same19-class label scheme and lack an
explicit beard class.

The reviewer also supplied36polygons across the same six photos. Their union
contained3156native pixels, with overlap counted once. Native integer polygons
were rasterized with boundary pixels included; original-pixel Lab and ITA were
measured. Actual marks included neck regions, despite the face-only instruction.
All marks were preserved, so patch overlap is not interpreted as face-only
recall. Unmarked pixels are unknown. These exposed, selected references are
neither dense ground truth nor independent evaluation.

## 3. Results

| Layer | Attempts | Input RGB8 MAE | Fixed-support oracle | Input-support oracle |
| --- | ---: | ---: | ---: | ---: |
| Clean |12|0|0|0|
| Core |96|18.665|0.135|0.591|
| Composite stress |60|53.593|11.034|13.526|

The input-support experiment had59successful stress recoveries among60attempts;
the table includes all60operational outcomes. Fixed-support synthesis clipped
53of60stress cases. Severe visual artifacts and perceptual-metric regressions
remained despite lower average RGB error. All96core inputs lost some original
correction support under the input-derived masks. Observed failures included
head-covering re-admission, collar spill and untreated boundaries; these
observations do not constitute dense object-ground-truth error rates.

| Selected-reference measure, five available images | Baseline | ResNet34 |
| --- | ---: | ---: |
| Skin points selected /113|54|77|
| Unwanted points selected /94|9|15|
| User patch pixels selected /2551|987(38.7%)|1558(61.1%)|

The larger backbone increased coverage while worsening unwanted point
inclusion. All nine prior unwanted inclusions remained, with six new ones.
The sixth photo had605manually selected patch pixels but no automatic final
prediction; it was excluded from the paired patch denominator and retained as
a failure. Original-colour statistics could be computed on all six manual
supports, which does not make them eligible calibration examples.

## 4. Prototype status and limitations

The Android prototype provides photo selection and before/trial display using
its older pipeline. The newer research masks and continuous-score candidate are
not integrated. The isolated continuous candidate replaces an integer MST
index with a predicted continuous1–10score while retaining Lab/ITA and three
correction outputs. Generated software tests establish representation and
portable-tree replay only. No real contextual MST model or photographic
correction tree was fitted in this experimental sequence.

The evidence is limited by development exposure, small selected source sets,
uncertain person relationships, low native face detail, selected-reference
scope, and remaining beard/glasses/object ambiguities. Patch pixels are not
independent samples, and neck inclusion prevents a face-only interpretation.
Reference-aware fits cannot establish automatic prediction or generalization.
No fairness, expert-rating, intrinsic-colour, clinical or final application
quality claim is made.

## 5. Discussion and next evaluation

The fixed-support results show that the three controls can closely approximate
the chosen core inverse transformations. Actual-input results show that support
variation remains consequential even with target-aware controls. The parser
comparison demonstrates why coverage alone is an insufficient model-selection
criterion: more selected skin accompanied more selected unwanted material.

A real predictive experiment requires justified measurement/reference roles,
compatible contextual calibration and person-separated evaluation. Training
rows need upstream estimates generated without their subject's calibration
labels; outer evaluation subjects must remain absent from all fitting stages.
The continuous estimate derives from the same Lab/ITA inputs, so incremental
predictive benefit remains a hypothesis. The present diagnostic evidence
supports these evaluation requirements rather than a claim that they are met.

## Reference and completion notes

Mbatha, S. K., Booysen, M. J., and Theart, R. P.(2024). Skin Tone Estimation under
Diverse Lighting Conditions. *Journal of Imaging*,10(5),109.
DOI:10.3390/jimaging10050109.

Before submission: complete focused primary-source related work and references
for FFHQ, parser and visibility model; verify novelty and venue suitability;
apply the official template and page limit; obtain author/adviser review as
appropriate. This draft contains no identifiable dataset images or per-subject
labels. Do not add private images/galleries without necessary consent. Nothing
in this draft authorizes submission, new training, source publication or contact.
