# One aligned input-mask and blended-correction development cycle

7 November 2026. User approves pipeline alignment before further tree changes.
Preserve all earlier data/models/reviews; no new dataset, annotation, admission,
runtime adoption or sweep. Use the existing 30 development and 24 later originals
and their fixed 14 full-scene distortion recipes, 756 attempts total.

## Preparation and geometry

First preflight the current desktop parent measurement on all 54 clean full
frames. It resizes the whole scene to256 and requires1000 skin pixels. Research
instead used face-normalized crops and CLAHE parser/visibility inputs. These
paths must not be claimed equivalent. Retain failed full-frame reports.

For the shared CANDIDATE preparation use the already established fixed1.5 native
face-square bridge, anchored by exactly one YuNet face at.85 on the ACTUAL input
scene resized256. Never borrow a clean-photo anchor or retry with detector
fallback. Then call the same nostril measurement, parser and FaceOcc service as
the current desktop on the actual crop, without research CLAHE. Keep1000pixel
minimum unchanged. Record all failures and preserve original RGB pixels for
measurement. Reuse initialized parser/model objects without changing weights,
preprocessing, dtype or inference mode. FaceOcc uses the existing isolated
CPU environment and batch runner with raw aligned RGB, no downloads or refits.

This changes framing relative to the present desktop. It defines a versioned
shared preparation CANDIDATE; the demo itself remains unchanged until adoption.
Normalization adds no native detail and does not establish measurement adequacy.

Use the exact current correction_preview composition: separate facial measurement
and face/visible-neck correction support, hole filling, object protection and
inward blending. Fixed glasses mode uncertain for unlabelled research photos:
predicted lenses remain protected; no invented clear/opaque labels or repeated
annotation request. Preserve the existing explicit clear-lens/rim branch unchanged.
Record requires_glasses_choice; no automatic glasses classifier or frame accuracy
claim. Correction beyond the fixed crop remains unavailable, not silently filled.

Project floating crop alpha to the original224 scene with INTER_LINEAR; project
protection conservatively using INTER_AREA>0 and zero alpha wherever protected.
No pixel outside projected alpha or on projected protection may change. Score
the union of available clean-reference correction support and actual-input alpha
support, and report full-scene metrics separately. Clean reference support is
evaluation supervision only, never input features or applied masks. It is an
unverified region reference, not facial ground truth. If a source has no successful
clean support, exclude it from supervised regional fitting/scoring and retain
its attempted/failure ledger and any scene-only output.

## Learning after preparation is verified

Do not reuse old MST parameters on changed measurements. Build matching
experimental ITA+Lab ridge1 calibration only from new clean measurements in the
original fitting cohort, preserving publisher-held exclusions. Cache unique
exclusion sets (full,10single,45pairs: at most56 fits if all keys usable). No
scientific calibration admission. Fitting-row MST excludes both the outer held
key and that row's key; full fitting MST excludes that row's key. Later-photo
features use the full development calibration; later labels never fit anything.
Record missing/insufficient calibration explicitly, do not invent MST values.

Retain the ORIGINAL unrestricted joint image-loss action-tree architecture,
depth3/minleaf1/tie/clean constraints and original14 per-fit action libraries.
The facial-root variant is preserved but not selected. Recalculate fitting action
costs with actual-input alpha and the broader native scoring support, on ALL
scored pixels. Same gamma/red/blue controls and RGB8 renderer. No new target
optimizer fits or action-library sweep. Fit at most11 correction trees (10old
publisher folds+full) once, with technical exclusions recorded. No automatic
replacement for a fit with insufficient data.

Evaluate on the same new mask/alpha/support every available input: identity,
saved parent joint-tree controls when available, and newly aligned controls.
Old parameters have separate old-feature provenance; do not silently pass new
measurements into old MST/tree models. Old predictions unavailable remain so.
Only compare metrics on explicitly common supports/cohorts. Report clean/core/
stress errors, harms, coverage/failures, pixel accounting and key-weighted means;
never compare old2.83/6.00 directly with new broader-region scores as if identical.

## Verification and stop

Test alpha projection, protection and blended action-cost parity on generated
arrays first. Bind pipeline/model/source hashes; verify actual-input anchoring,
features, zero protection leakage, failures, scientific flags, calibration
exclusions, fitting costs/constraints and saved outputs/metrics. Review mask/
alpha outputs as well as corrections, without requesting new annotation work.
Stop if preparation or calibration is technically insufficient; do not lower
guards, reuse incompatible lookup, or hide missing photos. No automatic follow-on
variant, fit/sweep, dataset search, sharing, contact, publication, commit or app
integration. All cohorts remain small, exposed and synthetic; results do not
establish true colour, fairness, naturalness or independent final accuracy.
