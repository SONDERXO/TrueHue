# Thesis proposal completion tracker — 8 November 2026

The user clarified that continued development should follow the **thesis
proposal**, not merely the latest experiment plan. This tracker uses the actual
111-page `Thesis Proposal Document.pdf`, verified SHA-256
`1426f3769ba771daadf9b6e0e0b1e347729c8f04919c214e6fedc3df272e7b8a`.
Page references below are PDF pages. Existing hash-bound text extraction was read;
the PDF and thesis wording were not edited.

The goal is a local Android photographic-correction feasibility prototype using
ITA, MST and a decision tree. Original photos are synthetic-restoration targets,
not certified true skin-colour references. A colorimeter, new participants or
physical skin-reflectance recovery is not a completion prerequisite.

## Requirements and current status

| Proposal requirement | Evidence location | Current status | Remaining work |
| --- | --- | --- | --- |
| Appropriate permitted face-photo sources | 10,12–14,59 | Inventories and permitted Stellenbosch research data exist; source choice differs from the named FairFace/SCIN plan | Keep data rights and exact source roles explicit; distinguish publisher keys from verified identity |
| Automatic facial skin detection | 10,61 | Implemented, but actual-input failures and missing/contaminated skin remain | Retain failures in results; do not equate passing the pixel guard with correct skin selection |
| Lab-based ITA | 61–62 | Implemented and reproducibly measured | Report mask and lighting sensitivity; preserve matching measurement contracts |
| ITA-to-MST mapping | 10,62–63 | Experimental ITA+Lab continuous MST fits exist; not the proposed MST-E lookup | Record the change and its evidence; no rounding or incompatible lookup reuse |
| Three tone-dependent synthetic distortions per source | 11,59,62 | Several versioned experimental recipes exist, including14-condition research diagnostics | Do not call these the exact proposed three recipes; resolve the missing recipe details and retain tone-dependent versus diagnostic conditions separately |
| ITA, MST and facial colour statistics as correction inputs | 63 | Available in experiments; recent trees often do not select ITA/MST and depend strongly on brightness | Do not claim demonstrated skin-tone conditioning merely because features are available; assess actual learned behavior |
| Decision tree predicts gamma and red/blue gains | 63 | Implemented in several experimental forms; joint action tree selects a fixed control library | Distinguish direct parameter regression from finite-action image-loss learning; no candidate yet meets clean-photo protection |
| Facial correction scope | 13–14 | Experimental Python correction also includes visible neck | Neck is an implemented extension, not compliance with the proposal's explicit face-only scope; keep it documented as a method change |
| 70/15/15 MST-stratified source splits and k=5 validation | 62,65 | Current small development studies use publisher-group-held folds and a later-photo comparison | Do not describe this as the proposed final partition or five-fold validation; preserve derivative-source grouping and define a valid final design before reserving/accessing final data |
| Uncorrected baseline and reference-based CIEDE2000 improvement | 65–66 | Computed in experimental comparisons, alongside RGB MAE | Use same regions/denominators; report failures and harms as well as average improvement |
| Parameter MAE | 65–66 | Used in earlier parameter-learning work; latest image-loss studies primarily assess reconstruction | Preserve the distinction between target-control error and image error; exact target identifiability is limited by clipping and approximate inverse controls |
| Overall and per-MST-category results | 11,66–67 | Exploratory estimates and cohorts exist | Produce defensible group counts and CIEDE2000 improvements; do not infer fairness from pooled RGB error or invented group labels |
| More than10% improvement disparity as residual bias flag | 66 | No final valid pass/fail claim | Specify what the percentage denominator means before final evaluation; report undefined/near-zero cases and continuous differences, not a guessed formula |
| Photographer Mean Opinion Scores | 13,66–67 | Evaluation deferred until an initial model is ready; existing instrument exists | Conduct the actual authorised expert evaluation later; software tests and assistant visual reviews are not MOS responses |
| Local Android integration and operation | 11,13 | Older prototype works; new research models are not integrated | Promote only an accepted compatible bundle, then verify phone behavior, output parity and timing |

## Keep implemented changes visible

Learned semantic/occlusion masking, object protection, blending, neck correction,
continuous contextual MST, clean-photo constraints and expanded distortion
diagnostics are development changes. Their practical motivation does not make
them automatically approved amendments to the thesis. Preserve the appeal-letter
record; do not silently rewrite the proposal or roll back useful work to make
the status table look compliant. Transparent-glasses correction remains an
explicit-choice experimental branch, not validated automatic frame/lens parsing.

## Work order from here

1. **Close each completed experiment honestly.** The face-local candidate is
   rejected: it increases clean errors and worsens recovery despite eliminating
   outside-crop dependence. Preserve all earlier results and current app assets.
2. **Resolve the correction decision problem within the thesis scope.** The next
   substantive design must justify exposure/colour action direction and clean
   preservation using image evidence. No automatically repeated feature/crop/
   threshold sweep. It must keep ITA/MST's intended role visible and distinguish
   feature availability from demonstrated influence.
3. **Freeze the study specification before final evaluation.** Record the exact
   rendering convention and three distortion recipes (or an explicit amendment),
   source roles, reference criteria, grouping/split method, mask policy, category
   mapping, missing-case handling and disparity calculation. The proposal does
   not uniquely specify every augmentation equation; do not invent the missing
   choices and attribute them to the document.
4. **Evaluate an accepted frozen model.** Report CIEDE2000 improvement versus
   uncorrected input and per-MST evidence, control-error metrics where meaningful,
   clean-photo edits, failures and worst harms. Reused development groups are not
   an independent final test. An expert review follows model readiness.
5. **Integrate and verify Android**, then update methods/results/limitations to
   describe what was actually completed. Conference submission timing does not
   turn failed development checks into validation.

The user has authorised continued justified development without repeated routine
confirmation. This does not authorise contacts, data sharing, accepting account
terms, publication, blind sweeps or changing private-data restrictions. No new
fit, data search or annotation round is started by this tracker. No defensible
model-completion date can be promised while clean preservation remains unresolved.

## Supporting records

- [Verified proposal scope](proposal-scope-validation-2026-11-03.md)
- [Full proposal scan and unspecified recipe details](proposal-full-scan-findings.md)
- [Actual-input pipeline results](aligned-correction-pipeline-results-2026-11-07.md)
- [Four clean-error diagnosis](aligned-clean-error-trace-results-2026-11-08.md)
- [Rejected face-local comparison](face-local-action-results-2026-11-08.md)
- [Material-label limits](material-improvement-development-plan-2026-11-08.md)
