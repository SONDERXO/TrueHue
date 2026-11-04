# From promising examples to automatic correction

2 November2026. User authorised this readiness plan and freezing the experimental
contrast-plus-smooth-boundary candidate. **Planning is complete; training is not
ready.** This document does not activate data processing, reviews, parameter fits,
MST calibration, decision-tree training or a demo change.

The practical next evidence needed is a usable, admitted source of matching MST
measurements, plus trustworthy correction-reference/support and identity grouping.
DAST/STW remain leads awaiting user-reported replies, not the only possible route.
No recruitment or adviser wait is imposed as a technical prerequisite.

## Freeze the candidate, without adopting it

Freeze these settings as the experimental reference, rather than continuing to
tune the same14exposed photos:

- Encoded-sRGB gamma then contrast about0.5 then red/blue gains; fixed green gain1.
  Raw formula `(0.5+c*(x**(1/gamma)-0.5))*[red,1,blue]`.
- Apply the fixed smooth boundary `s*log(1+exp(raw/s)) -
  s*log(1+exp((raw-1)/s))`, withs=0.02 and stable symmetric evaluation.
- Four experimental controls: gamma/red/blue/contrast, diagnostic bounds
  [0.25,4]/[0.25,4]/[0.25,4]/[0.5,2]. These are frozen experimental settings,
  not validated runtime safety bounds or a fourth-output adoption decision.
- No spatial skin smoothing, new feature/classifier or fifth learned parameter.

Machine-readable contract, readiness ledger, exposed-photo list and source
hashes: `outputs/correction_training_readiness_plan_v1/`. No photo/model files
embedded. Any change to settings or referenced implementation requires a new
contract/version and a new justified evaluation, not overwriting this freeze.

Baseline runtime remains the earlier experimental three-output model. ITA +
calibrated MST + facial statistics and the decision-tree family stay retained.
Android stays on-device with one selected face. Candidate freezing is not
pipeline adoption, schema migration, completed correction or panel approval.

## What can count as a reference

|Evidence|Possible role|What must be established before use|
|---|---|---|
|PPR10K expert edits|Photographic appearance targets|Permitted intended use; exact source/editor pairing; correct colour handling; source-selected person; trustworthy face+neck support; identity/duplicate grouping. Not intrinsic skin colour or MST labels.|
|An admitted existing photograph|Reference for synthetic restoration of that photograph|Exact source quality/support admission; distortion/target consistency and identity separation. Cannot imply that original lighting/colour is true or ideal.|
|DAST|Potential measured/controlled-capture evidence|Actual release/access terms, linkage, instrument/camera conditions and intended target relation. CST is not MST; exposure labels are not gamma targets.|
|STW|Potential MST label evidence|Annotation/source terms, label provenance, usable person grouping/overlap and actual selected-skin validity. Not a photographic correction target or instrument truth.|

No current source is newly admitted by this plan. Prior exact-image reviews and
holds retain their limited scope. PPR10K human-region masks are not skin masks;
hand-drawn diagnostic polygons are not approved measurement/correction masks.
Five earlier candidate references do not become a five-source training cohort.
The19-person MST study's11favourable/7concern/1failure is already complete, not
an unreviewed queue or permission to fit the favourable subset.

Source admission must bind image hashes, source/person/group identifiers, source
terms, quality/lighting limitations, selected face, colour metadata, versioned
measurement/correction support and exact scope of human/technical evidence.
Uncertainty/failures remain in an attempt ledger. No replacement just because
an image is difficult. Do not create another user review workload automatically.

## Keep measurement and rendering separate

Measurement uses actual facial skin, with established exclusions; the preferred
FaceOcc-assisted method is still experimental, contract
`89c7a3963dcc72bfa8c7b73433789b058093131662c88a6d30a7f25d791823fd`.
That contract must be checked against actual future artifacts, not copied as an
assertion of eligibility. Selected hair/glasses/coverings and skin validity must
be resolved on exact images; technical replay is not skin admission.

Correction uses the adopted selected whole-face+visible-neck support, explicit
protections, enclosed-hole handling and combined-boundary inward blending.
The14PPR10Kdiagnostics instead used approximate face-only hard polygons, with
two later source-only region corrections. They have not verified that full
rendering support. Before target generation, define and verify measurement,
correction alpha and scoring support independently. No transfer of historical
mask approvals or mixing incompatible parent/FaceOcc features or MST lookups.

## Define targets before generating a training table

The eventual protocol must name its scientific task: reconstruction of a supplied
photographic reference versus measured true-colour recovery. PPR10K supports
the former kind of evidence; silently claiming the latter is invalid. This
planning document does not narrow the retained thesis or adopt new dataset roles.

For a photographic source/editor pair, a future justified target-generation
protocol could fit candidate parameters using the editor target and validated
selected-person support, with the **exact** four-control smooth-boundary operator
and eventual alpha blend included. Freeze objective, weighting, bounds, solver,
failure handling and diagnostic acceptance criteria before any such run. Keep
unrepresentable targets and all regressions in reporting; no post hoc cleaner-only
cohort. Current frozen identity-start squared-sRGB diagnostic settings may be a
baseline, but are not thereby an approved label-generation recipe for full-face
plus neck. No labels are generated here.

The target is allowed to supply supervision, never inference features. Neither
the existing14per-photo oracle parameters nor old synthetic inverse parameters
are ready-made labels for the new operator. Adding contrast and smooth clipping
breaks the simple reciprocal-gamma/inverse-gain recipe, especially with blending
and quantisation. Future synthetic targets must be solved/verified against the
exact distortion/reference/correction composition; unattainable inverses must
be flagged. Do not claim exact recovery through clipped or lost input detail.

Input feature rows must come entirely from the input photograph: measured ITA,
matching calibrated mapped MST, and frozen facial statistics. Recompute or
justify any support/features on distorted inputs rather than assuming parser
selection is unchanged by colour changes. Target/reference MST must not leak
into input columns. No imputed MST, direct-classifier replacement or four-feature
fallback. Freeze the full feature list and output schema before fitting.

## Separate people and roles before variants or fitting

1. Reconcile exact/cropped/near-duplicate sources and person identities, including
   cross-dataset identity uncertainty and already exposed/reserved allocations.
2. Put all images of one person, related scene groups and synthetic descendants
   into the same partition. If different groups share a person, combine them;
   use connected components of these relations, not independent group IDs.
3. Freeze training, development and final appraisal membership and hashes before
   target generation/tuning. Existing reserved roles stay locked. Do not relabel
   exposed material as final test merely because of a new crop/dataset name.
4. Keep MST calibration/evaluation roles explicit and subject-separated; also
   document overlap with correction roles and any shared development exposure.
   A final end-to-end appraisal subject must not have contributed to learned
   calibration/correction components presented as independent of that subject.

All14PPR10Kphotos are development-exposed, listed in the package; old6include
publisher-validation groups, new8publisher-training groups. Publisher splits
do not automatically make TrueHue final appraisal valid. They remain diagnostic
only, not training admissions. PPR10K group IDs do not certify different people.
No final allocation, cohort size, split percentage or adequate ten-tone support
can honestly be fixed yet. Numeric adequacy/precision and allowed task scope must
be justified and frozen once actual identities/admissions are known, before
outcome-based splitting. Two people/category is not adequate validation by itself.

## Clean images, clipping and evaluation

Smooth boundary is **not exact identity** even at gamma=red=blue=contrast=1:
endpoint values move inward. A vector of neutral controls is not a guaranteed
unchanged-image target. A future architecture must explicitly decide between
a justified exact no-change branch and a declared alteration tolerance. Neither
branch nor tolerance is implemented/adopted here; do not hide a fifth learned
decision or tune it on final appraisal. Include unchanged-image controls and
record unwanted alteration rate before claiming an automatic model is useful.

For any future frozen automatic-prediction evaluation, compare uncorrected input,
the retained three-control comparator and the frozen smooth four-control candidate
on identical valid support. If three/four models are trained, use matching cohorts,
features and declared training procedure. Separate oracle capacity from automatic
predictions; an oracle fit with its own target is not an automatic baseline.

Report RGBMAE/relativeDeltaE, per-image/subject outcomes, regressions and tails,
RGB8 endpoint/flattened-variation evidence, unchanged-image errors, all stage
failures and technically measurable coverage. Stratify only by supported labels
and predeclared conditions; disclose missing labels/unsupported tones. Preserve
lighting, profile, makeup/covering/glasses and neck-boundary limitations. Numeric
scores do not establish true colour or dense mask accuracy. Freeze acceptance
rules and uncertainty/precision plan before final outcomes; they remain unset,
not silently passed by these demonstrations. Device parity/performance and later
professional Google Form review remain separate evidence stages.

## Readiness decision

|Requirement|Current status|
|---|---|
|Experimental operator specification/source hashes|Frozen for planning, not runtime adopted|
|Valid photographic cohort and face+neck/support admissions|Missing; fourteen exposed diagnostics only|
|Identity crosswalk and justified independent allocation|Missing; no invented subject counts/splits|
|Matching admitted skin/MST cohort and justified calibration evaluation|Missing; no reliable calibrated mapping|
|Exact smooth/blended target-generation and clean-image policy|Specified issues; implementation/admission pending|
|Complete feature/output contract and task adequacy/acceptance criteria|Must be frozen before training, not established here|
|Correction model training|Inactive; no final retained-model training authorised by this plan|

Stop before any fit while these remain unresolved. No repeated metadata audit,
same14tuning, new small review, recruitment, author message or adviser technical
gate is created. If substantive new data/access arrives, assess which requirement
it actually addresses, then propose one justified bounded next protocol. More
data is not promised to solve the retained method.

Evidence: ppr10k-smooth-boundary-results-2026-11-02.md;
ppr10k-clipping-detail-results-2026-11-02.md;
mst-subject-skin-study-results-2026-11-02.md;
stw-qualification-results-2026-11-02.md;
dast-and-stw-readiness-results-2026-11-02.md.
Earlier correction-training-admission-2026-11-02.md is historical: its pre-study
attempt counts are not the latest19-person result. This plan records current
status without erasing that evidence or modifying the thesis draft open in IDE.
