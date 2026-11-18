# Stellenbosch calibration admission decision — 5 November 2026

**Decision: do not calibrate from the current30measurements.** Access and file
integrity are resolved, but the existing skin-measurement path has not produced
a qualified cohort. This decision concerns the fixed diagnostic sample and
current measurement method, not the usability of the entire release.

The user authorised assessing the reliability and admission requirements after
the [fixed crop check](stellenbosch-face-crop-results-2026-11-05.md). Script436
uses only frozen saved evidence; no additional images, model passes or fits.

## What the evidence shows

The initial sample selected two publisher subject keys per descriptive score
interval before pixels were inspected. These intervals are sampling aids,
not MST categories or rounded source labels.

| Supplied score interval | Selected subject keys | Technical image passes / attempts | Keys with all three conditions passing |
|---|---:|---:|---:|
| [1,3) | 2 | 6/6 | 2 |
| [3,5) | 2 | 6/6 | 2 |
| [5,7) | 2 | 3/6 | 1 |
| [7,9) | 2 | 3/6 | 1 |
| [9,10] | 2 | 0/6 | 0 |

Only six of ten subject keys have technical measurements in all three lighting
conditions. Dropping the failures would remove the highest sampled interval
entirely. This is not an estimated population failure rate, but it prevents a
claim of adequate score coverage from these18passes.

For the six technically complete subjects, the saved ITA maximum-minus-minimum
across three conditions ranges100.37–149.60degrees (median108.20). This is a
descriptive feature-stability warning, not an accuracy estimate, a calibrated
error, or a new rejection threshold. Different lighting and selected skin
regions both vary; the existing atan-based ITA can also change sign sharply
when its chromatic denominator crosses zero. No causal attribution, formula
replacement or category interpretation follows from these ranges.

All30boards were inspected in the preceding crop check. Large central-face or
cheek/chin omissions persist in several passing masks. Native crops contain
only46–61pixels per side; enlarging them to256does not restore detail. Neither
the1000normalized-pixel guard nor282–725selected native locations among passes
establishes actual-skin validity or adequate colour measurement.

## Admission requirements and current disposition

| Requirement before fitting | Current disposition |
|---|---|
| Traceable permitted source, unchanged labels and source bytes | Verified locally; research/noncommercial, citation and no redistribution terms retained |
| Reliable selected facial skin with contaminant exclusions and consistent anatomical support | Unestablished; qualitative omissions remain and no dense reference validation exists |
| Native detail sufficient for the intended colour statistic | Unestablished; no validated pixel cutoff is available, so none is invented |
| Meaningful coverage across supplied score range and lighting conditions | Not demonstrated in this sample; high-score failures retained |
| Decimal-compatible target and metric | Continuous source scores preserved; retained integer-only calibrator cannot consume them unchanged |
| Subject-held evaluation with disclosed exposure and failure accounting | Design requirements below; no allocation or untouched test cohort exists yet |

An image must not be admitted merely because its measured ITA agrees with its
source score. That would select favourable answers. Likewise, no manual mask
repair, lower threshold, integer rounding, integer-only subset or alternate crop
is adopted by this decision. A justified skin-support/native-detail validation
method is required before choosing numerical acceptance limits; these30already
examined examples cannot establish an unbiased performance threshold by tuning.

## Evaluation scope to retain for any future qualified cohort

- Keep every photo of a publisher subject together. Three conditions are repeated
  observations of one subject, not three independent participants.
- Treat all30current photos as development-exposed. Do not rename them an unseen
  final test set. This diagnostic does not allocate the remaining subjects.
- Report technical and admission failures with the original denominators, by
  score interval and condition. Report conditional measurement errors separately
  from coverage, so successful-only errors cannot hide exclusions.
- Preserve decimal targets. A future mapping would need a declared continuous
  target/metric and subject-balanced fitting; any category adapter needs its own
  justification. No mapping, category boundaries or adapter is implemented here.
- Choose model settings and acceptance rules using development subjects, with
  different subjects held out for evaluation. Subject counts and final allocation
  require demonstrated eligible coverage; none is fabricated now.

These are evaluation constraints, not a claim of adequate sample size, a new
calibrator design approval or activation of training. The correction tree and
Android runtime remain unchanged; MST is not removed from the intended pipeline.

## Verification and practical outcome

Script436 checked the crop/assessment artifact manifests and bound input hashes,
all30case memberships, ten groups of three and unchanged within-subject source
scores. It independently aggregated complete-subject counts, descriptive score
coverage and saved ITA ranges. Private evidence is in
`outputs/stellenbosch_calibration_admission_v1/`; individual labels and identifiers
remain ignored, with no dataset upload or sharing. No new inference, fitting,
annotation task, recruitment or author contact occurred. Prior29focused tests
remain the software-check evidence; no new full-suite run was needed for this
saved-record aggregation.

The practical outcome is a documented hold on calibration with the present
measurement method. The next substantive work must address measurement validity
or native-detail evidence under one separately specified diagnostic, rather than
training the six successful subjects or processing the entire release. This
decision does not activate another crop sweep, batch, fit or metadata audit.
