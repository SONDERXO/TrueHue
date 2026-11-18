# Native-anchor calibration measurement readiness — 9 November 2026

## Decision

The fixed30development-photo preparation and independent verification are complete.
**Do not fit or rebind an MST calibrator from this result.** There are21technical
measurements from30attempts, versus22under the earlier pipeline; only four publisher
subjects have all three conditions available. Qualitative review still shows
substantial omissions and fragmented skin support, including tiny selected patches
among nominal passes. Calibration eligibility remains unestablished.

This answers a concrete compatibility question with real data: old measurements
are not generally identical to new native-anchor measurements. No older calibrator
is relabelled or promoted. The result does not prove that calibration or decision-
tree correction is impossible; it does not supply valid mapping accuracy either.

## Fixed sources, pipeline and data roles

Used exactly the30original `development` sources from the existing aligned plan:
10publisher subjects and3conditions each, with exact decimal scores preserved.
Source scores range2.4–9.2. No later24originals, final24photos, extra participants,
other conditions or synthetic derivatives were processed. All30inherited JPEG
hashes pass before calls; all outcomes remain. These are already exposed development
sources, not new independent test subjects or new integer MST categories.

The new contract explicitly records native YuNet anchors at .85/NMS.3/topK5000,
native1.5square context, the shared inner measurement service, unchanged1000pixel
guard, raw-appearance parser/visibility and source-JPEG assumed-sRGB limitations.
Source scores and condition names are not measurement inputs. A new contract
identifier does not itself establish skin truth or calibration validity.

Scripts713–715 prepare, batch and finalize the one declared construction. Actual
calls:60YuNet (30anchors+30parents),36landmark-helper attempts,29dense-parser and
25FaceOcc forwards. Existing margin fallbacks only; no new thresholds, alternate
crop/model, enhancement, installation or source replacement. The established CPU
batch worker is reused with only frozen package/plan path substitutions; one
forward per aligned case, no repeated inference in verification.

Five fail before FaceOcc: geometry(case02), pixel guard(case07/14/25), landmarks
(case29). Twenty-five aligned inputs yield finite logits; four more fail final
measurement(case04/05/26/28). All nine final failures remain, without substituted
masks or zero-error treatment. Zero calibration, target or correction-tree fits.

## Coverage versus the old path

| Measure | Previous stretched-anchor path | Native-anchor preparation |
| --- | ---: | ---: |
| Attempted originals | 30 | 30 |
| Available measurements | 22 | 21 |
| Available in both | 18 | 18 |
| Shared cases with exactly equal four Lab/ITA measurements | — | **2/18** |

Three technical gains:case08/12/24. Four technical losses:case02/14/26/28.
The remaining18shared cases are not18independent people. Gains are not admissions,
and a mask's passing pixel count does not certify measurement accuracy. Do not
select the gains as a favourable calibration subset.

Each following interval has two attempted publisher subjects/six photos. Intervals
are descriptive decimal-score strata, not renamed MST classes.

| Supplied-score interval | Available / attempted photos | Subjects with at least one available photo |
| --- | ---: | ---: |
| [1,3) | 3/6 | 2/2 |
| [3,5) | 5/6 | 2/2 |
| [5,7) | 5/6 | 2/2 |
| [7,9) | 6/6 | 2/2 |
| [9,10] | 2/6 | 2/2 |

Having at least one observation per subject is not full condition coverage. Four
subjects have all three measurements; their ITA ranges across conditions are
130.88°,131.91°,156.43° and154.71°. These ranges mix lighting, support and the
existing angle formula. They are not mapping errors, an invariance requirement
for correction inputs, or proof a contextual mapping cannot work. No mapped MST
prediction was produced here.

## All-photo qualitative review

Viewed all30boards on six contact sheets, source scores omitted from titles.
This is assistant inspection, not a blinded expert assessment or dense truth.
Repeatedly visible issues include sparse forehead/cheek islands, central-face
holes, unilateral lower-face selection and very small retained areas on dim
photographs. Examples include sparse available case01/08/12, forehead-dominated
case19/27/30, and large central omissions in case15/20/21/23/24. Some other cases
retain broader visible facial areas. Glasses reflections, stubble/hair boundaries
and low native detail remain uncertain. No new contamination labels are invented.

Unavailable boards retain their failure status. Some pre-FaceOcc failures have
no finalized mask and show the input as a failure display; that is not a successful
measurement overlay. All earlier human references and source decisions remain
separate exact-scope evidence.

## Independent verification

Script716 verifies all30labels/source outcomes and exact source slices where a
crop exists; replays all25cached masks and their native projections; independently
recomputes21four-value feature vectors with explicit encoded-Lab conversion and
the original rounded atan formula. It reconciles old/new availability, raw feature
deltas, descriptive-score coverage, forward counts and unchanged bound hashes.
No model forward or fit is repeated. Software verification PASS does not override
the unestablished skin-support/admission status.

Private package: `outputs/native_mst_measurement_readiness_v1` contains the frozen
source/contract plan, all30attempts,25cached logits,21available measurements,
coverage/delta verification and six viewed-sheet hashes. No labels/photos are
published or uploaded.

## Practical implication

The new native bridge cannot be made calibration-compatible by copying the old
MST coefficients or updating a hash. It has different actual measurements, and
its labelled-source support still needs validation. Nor does fitting on the21
successful rows establish that the omitted source/condition combinations work.

The remaining requirement is **credible facial-skin measurement and labelled
coverage**, rather than another correction-tree hyperparameter. A future step
needs a substantive source/support-validation design; no new calibration, parser
sweep, guard relaxation, bright-only cohort, favourable-subset fit or acquisition
is selected automatically. The decision tree, ITA/MST and automatic app workflow
remain binding. Do not portray this result as model completion.

All prior artifacts are preserved. No runtime update, external contact, upload,
commit or push occurred. The final8group/24photo holdout stays byte-unread.

- [Frozen readiness protocol](native-mst-measurement-readiness-protocol-2026-11-09.md)
- [Photographic supervision compatibility review](ppr10k-expert-control-readiness-results-2026-11-09.md)
- [Earlier support/lighting evidence](stellenbosch-support-lighting-results-2026-11-05.md)
