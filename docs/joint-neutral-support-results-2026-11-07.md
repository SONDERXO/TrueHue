# Joint control repair: clean photos protected, useful correction lost

7 November 2026. Completed the fixed [joint-control protocol](joint-neutral-support-protocol-2026-11-07.md).
No research-data trees, gates, MST models or targets were fitted. This reuses the older
clean-leaf/range-check idea on the current split-control model; it is not a new
algorithm. **The candidate is not adopted. The correction model remains unfinished.**

## What changed

The saved brightness and colour trees keep their original splits. A leaf
containing any clean fitting example now returns exactly neutral controls for
its head. If either head receives a query outside its leaf's observed fitting
ranges on any of the 12 inputs, all three controls are neutral. The existing
binary gate is unchanged. This tackles both the diagnosed exposure extrapolation
and unwanted colour shifts, without another fit or parameter search.

All metadata comes from each fold's fitting rows, excluding its held publisher
key. The full model's fitting keys exclude the later-photo keys. ITA and MST
remain in the correction inputs. Masks and rendering are unchanged.

## Main results

RGB MAE below is the mean of per-photo errors in the existing reference region;
lower is better. These regions are measurement references, not complete clean
facial ground truth. The two native mask alternatives are reported separately in
the private JSON, rather than counted as additional independent photos.

| Comparison | No correction | Retained model + gate | Joint policy + same gate |
| --- | ---: | ---: | ---: |
| Development clean, 29 scored | 0.00 | 0.06 | **0.00** |
| Development core, 232 scored | 20.73 | **13.51** | 15.05 |
| Development stress, 145 scored | 52.54 | **23.76** | 45.91 |
| Later clean, 23 scored | 0.00 | 0.03 | **0.00** |
| Later core, 184 scored, fallback masks | 21.39 | **17.43** | 19.34 |
| Later stress, 115 scored, fallback masks | 54.66 | **36.23** | 50.66 |

- Changed clean photos fall from 3 to **0 of 29** in the development folds and
  from 1 to **0 of 23** later photos. The clean screen passes for this gated policy.
- No reference-scored case becomes worse than its distorted input with the gated
  policy, across the four saved contexts. This does not establish unseen safety.
- Correction coverage falls: development core actions 73 to 47 and stress actions
  107 to 21; later fallback core actions 43 to 18 and stress actions 65 to 12.
- Of previously beneficial retained-model actions, 17/64 development core and
  85/106 development stress actions become unchanged. The later fallback counts
  are 22/40 core and 53/65 stress. Losing useful recovery is a material regression.
- Relative CIEDE2000 agrees with the main trade-off: gated core means worsen from
  5.24 to 5.73 development and 6.70 to 7.32 later fallback; stress worsens from
  9.99 to 17.58 and 14.37 to 19.47. Equal-publisher-key means also worsen.

The range check rejects 9/29 feature-available development clean inputs,
67/232 core and 99/136 stress inputs. Later fallback rejects 7/23 clean,
53/182 core and 60/86 stress inputs. Range rejection is separate from the
existing gate and clean-leaf neutralization; these counts are not correction
coverage. Missing measurements remain no-ops and remain in the attempt ledger.

## Why simply removing the gate is not a solution

The prespecified ungated diagnostic improves core MAE to **7.20** development
and **10.13** later fallback. However, it alters one later clean photo, causing
35.75 RGB MAE on that photo's 683-pixel reference region. Its gamma is about
0.6665, its gains are exactly neutral, and both heads pass all individual fitting
ranges. The gamma leaf contains no fitting clean example. The original gate
blocks this action. The same photo is repeated across the three native contexts;
this is one clean failure, not three people.

This shows that clean-leaf neutralization and individual feature ranges alone
do not reliably identify a clean photo. It also shows that the old gate suppresses
useful actions for these modified controls. Its benefit estimates were learned
for the original controls; no gate retraining is hidden in this comparison.
The ungated path is a diagnostic and fails the clean screen, not an alternative
candidate selected after looking at the results.

The ungated diagnostic also harms two later reference-scored core inputs and
two later stress inputs in each native context. Its development core/stress
harm counts are zero. Ungated stress MAE remains high (45.74 development,
51.11 later fallback), so improved core recovery does not resolve severe inputs.

The previously diagnosed darkening case is unchanged even without the gate.
The recovered warm detector-fallback case is also blocked: full-scene MAE stays
2.01958 instead of increasing to 2.05803. Its original facial reference remains
unavailable; scene error is not evidence of facial reconstruction accuracy.

## Verification and artifacts

- Nine focused tests passed in 5.24 seconds, including three new generated-array
  policy tests. The new tests do not fit models; the existing split-control tests
  perform ten small tree fits on generated fixtures, never research photos.
- All 290 fitting clean occurrences return exact neutral controls. These are
  repeated uses of the same 29 fitting originals, not 290 independent photos.
- Independent verification reconstructs leaf metadata and actions from original
  tree nodes and float32 inputs, replays RGB8 rendering with separate arithmetic,
  checks metrics and unchanged pixels outside the mask, and checks source hashes.
  All checks pass: 176 leaf metadata checks, 1,281 action checks, 2,828 RGB8
  output replays, 2,744 reference metric checks, 2,016 scene metric checks and
  3,977 bound source hashes. Details are in `verification_PRIVATE.json`.
- Scripts: `551_compare_joint_neutral_support.py` and
  `552_verify_joint_neutral_support.py`; policy:
  `src/model_training/joint_neutral_support.py`.
- Private output: `outputs/joint_neutral_support_v1`, including all 1,428 attempt
  records, both policy renders, 63 fixed review boards and a review page. There
  are 54 original photos across the two cohorts; conditions, masks and folds are
  not independent people or photos.
- Viewed all 63 fixed boards through 16 contact sheets, plus the diagnosed
  darkening case and the ungated clean brightening failure at original board
  size. The latter is a visibly brighter facial patch with hard boundaries.
  Numerical improvement does not establish a natural-looking face.

No Android/desktop integration, scientific admission, annotation, dataset search,
contact, sharing, publication, commit or push. Earlier artifacts are preserved.

## What this means for the next step

This bounded repair establishes a clean-preserving conservative comparison, but
its recovery loss is too large to replace the retained research model. Keep it
as a reference. Before specifying another fit, inspect the remaining ungated
clean exposure error alongside the useful core actions blocked by the old gate.
Any later gate fit would need benefits generated for these modified controls
and a separately frozen comparison. Do not automatically loosen ranges, remove
the gate, or start another feature, threshold, capacity or weight sweep.

All earlier limits remain: small repeatedly exposed cohorts, synthetic lighting,
uncertain/fragmented masks, acquisition cues, and photographic reconstruction
metrics that do not establish true skin colour, naturalness or fairness.
