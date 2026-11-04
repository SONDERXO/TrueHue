# TrueHue delivery checkpoint — 1 November 2026

This is the current implementation/evidence index. Earlier30October drafts and
their immutable evidence package remain historical. This checkpoint does not
declare reliable correction, thesis completion or panel acceptance.

## What can be demonstrated and what it means

| Component | Verified evidence | Important boundary |
|---|---|---|
| Whole-face/neck correction previews | Broad correction support, inward union blending and enclosed-hole repair; user accepted rendering direction | Fixed illustrative parameters, not new learned predictions; outer gaps remain |
| Separate skin measurement | Reproducible parser/anatomical/nostril exclusions | Actual skin still sometimes confused with hair/objects; no ground-truth guarantee |
| FaceOcc experimental measurement | Fixed checkpoint/MediaPipe bridge; masking diagnostics, four actual user judgments; isolated service35exact saved successes/14failure guards | Preferred experimental candidate, not active demo model or validated measurement |
| Matching-MST evidence | Previous393measurements/15subject-held folds, ordinalMAE2.124682/exact12.98%; saved refit/prediction replay | Mapping unreliable and unadopted; previous features/lookup incompatible with FaceOcc |
| Correction models | Historical reproducible decision-tree experiments and demo baseline preserved | No newly adopted reliable model; no new tree trained after recent mask changes |
| Android experimental app | Existing local pipeline;6native emulator tests/18JVM tests; fixed-example Python pixel parity; picker/save/failure/reliability flow | Older baseline5/fold1 and experimental lookup; rule-based masks; no FaceOcc/newwhole-face-neck integration or broad/phone parity claim |
| Professional review | Existing Google Form/refinement policy recorded | No invented participation, ratings or finalMOS; starts after a good initial model |

The retained scientific direction remains ITA + calibrated MST + facial statistics
→ decision-tree gamma/red/blue correction, on-device Android, one selected face.
Recent success is chiefly engineering reproducibility and improved masking on
some examples, not demonstrated true skin-colour recovery.

## Evidence to use in thesis writing

- Current masking/rendering: adopted-masking-design-2026-11-01.md,
  reference-r1-and-continuity-results-2026-11-01.md.
- FaceOcc original comparison: faceocc-comparison-evidence-2026-11-01.md.
- Broader qualitative evaluation and actual human feedback:
  faceocc-light-review-results-2026-11-01.md,
  faceocc-qualitative-conclusion-2026-11-01.md.
- Software versus scientific validity: faceocc-development-service-results-
  2026-11-01.md.35exact saved replays do not establish35approved masks.
- MST result and decision: nostril-mst-calibration-results-2026-11-01.md,
  faceocc-mst-feasibility-decision-2026-11-01.md. No newcalibration now.
- Existing Android evidence: android-integration-2026-10-31.md,
  android-emulator-check-2026-10-31.md,
  android-reliability-check-2026-10-31.md.
- Method changes for later panel letter: panel-change-register.md.

Four-case user review:2FaceOccpreferred/2similar, no reported useful-skin loss
in thosefour. Broader assistant inspection flags possible cheek-skin loss and
residual beard/glasses concerns. Keep observer attribution and exact sample
scope. Do not translate sparse marks or preferences into general accuracy.

The23-image polygon task was replaced with lower-burden qualitative review;
do not describe dense annotations or full-mask metrics as completed. All49
diagnostic attempts/35technical successes/14failures remain separate from actual
skin eligibility. Current matching FaceOcc MST subset is33attempts/23technical
measurements/four exposed subjects/categories2/4/5/9. These cannot replace the
old393measurement cohort or establish ten-category validation.

## Concrete delivery priorities

1. Use the current results addendum and claim/evidence table when incorporating
   thesis results; preserve failed experiments and original-method differences.
   Do not edit the submitted paper or claim panel approval without that scope.
2. Keep the existing experimental Android demonstration reproducible and clearly
   labelled. Physical-phone testing, broader decode/EXIF/parity, process death,
   otherAPI/ABIperformance remain the practical application-verification gaps.
   A new phone test requires an available device; no device or result is assumed.
3. Keep current Python previews and the isolated FaceOcc service distinct from
   the correction demos. No unvalidated component promotion just to match visuals.
4. Revisit a calibration study only when the documented admission/scope conditions
   change. Another metadata audit, replay or small parameter fit does not supply
   that evidence. No new annotation/recruitment burden or adviser wait imposed.

## Package and verification scope

outputs/delivery_checkpoint_20261101_v1/ contains an aggregate-only evidence
package: current summary tables, claim/status register, document snapshots,
README/index and hashes. No raw photos, individual prediction rows, APK or model
weights are embedded. Packaging is local, not a submission/publication.

Script384 verifies input/source hashes, currentAPKhash against the saved Android
reliability record, saved native-test XML counts and exact aggregate CSV/JSON
parity. That is an artifact check, not a fresh APKbuild/native test or physical
device run. Old Android startup/crash evidence remains intact.

Last broader Python test result:911passed/29.48s, excluding desktopGUIbecause
local Tcl/Tk is unavailable. Do not call that a full-suite pass. The earlier
890-test full pass remains historical. No new model inference/fitting or
reserved-image access is performed for consolidation.
