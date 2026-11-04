# Patchy output: prediction error versus fixed-operator limits

30 October 2026. The saved reference-fitted settings do not remove the red
patches in the identified 1398 JPEG85 case. Thus this case is not fixed simply
by choosing a better tree leaf. Missing application support and unrecoverable
channel values account for much of its error under the retained operator.
Other cases still show a meaningful gap between learned and saved settings.
No smoothing, new color operator or runtime behavior is introduced.

The [protocol](patchy-correction-audit-protocol.md) reuses all 141 verified
full-path stress inputs, original reference scoring masks and actual application
masks. The learned output is compared with the original saved per-source
reference-fitted target applied through that same actual mask. These targets
are not re-fitted after JPEG compression and are not globally optimal CIEDE2000
solutions. They are diagnostic reference access, never inference inputs.

## Verified limits of gamma and red/blue gains

For every positive gamma and gain in the retained transform:

- A zero input channel stays zero, so a missing blue or green value can leave
  color patches after the nonzero channels are brightened.
- Green=255 stays 255 because green gain is fixed at one. Red/blue=255 are
  **not** fixed: their gains can reduce them.
- Pixels outside the application mask remain unchanged.

`src/evaluation/irrecoverable_rgb.py` computes the disjoint RGB-MAE contribution
of these fixed samples on the scoring region. This is a lower bound for this
operator and fixed support, **not a CIEDE2000 lower bound**, physical camera
clipping measurement or a guarantee about true skin color. It does not account
for every source of color error. It accepts reference pixels only for evaluation.

## Results on all 21 distorted cases per encoding

RGB MAE uses normalized 0–1 channel values. Lower is better.

| Encoding | Learned CIEDE2000 | Saved-target CIEDE2000 | Learned RGB MAE | Saved-target RGB MAE | Fixed-sample RGB floor |
|---|---:|---:|---:|---:|---:|
| Lossless | 11.279 | 9.017 | 0.10257 | 0.07984 | 0.06724 |
| JPEG95 | 10.889 | 9.152 | 0.09770 | 0.07953 | 0.06465 |
| JPEG85 | 11.119 | 9.402 | 0.10034 | 0.08243 | 0.06767 |

The lossless floor separates into 0.04552 from outside-support pixels and
0.02173 from invariant endpoints inside support. At JPEG85 the components are
0.05649 and 0.01118. JPEG can shift exact endpoints into neighboring values;
that does not restore the original lost information. The endpoint count itself
must not be treated as proof of a particular physical clipping event.

For these fixed supports, the lower bound is below both learned and saved-target
RGB errors in every case, as required. The gap between learned and saved-target
errors shows remaining prediction opportunity. The floor also explains why
zero reconstruction error cannot be expected merely by replacing tree settings.
Do not use it to excuse avoidable clean-photo overcorrection or poor masks.

All 26 clean cases per encoding remain in the complete saved results. The
table isolates distorted cases to avoid hiding their behavior behind clean
controls. No failed or inconvenient case was removed from the 141-run audit.

## Inspected patch case

Open [1398 JPEG85 reference/input/learned/saved-target comparison](../outputs/patchy_correction_limits_v1/patch_case_comparison.png).
Both corrected outputs visibly retain similar red patches. Their CIEDE2000
values are 17.604 learned and 17.800 saved-target; the saved RGB-fitted target
is not guaranteed to minimize CIEDE2000.

Here learned RGB MAE is 0.16097. The fixed-sample floor is 0.15260, made up
of 0.13706 from missing mask support and 0.01554 from invariant selected channel
values. There are 2,484 selected green-zero samples and 4,572 blue-zero samples;
all differ from their reference values. This local decomposition identifies
support as a dominant contribution, with endpoint loss also present. It does
not prove every visible red patch comes solely from clipping.

The preceding cleanup-order experiment recovered more forehead support but
also exposed more patchy correction. These results must be interpreted together:
better coverage alone and better parameters alone are each insufficient for
this heavily degraded example under the current three-parameter operator.

## Verification and next work

Four new tests check endpoint identities, the non-invariance of white red/blue,
disjoint support/endpoint counting, bounds across positive parameter examples,
input immutability and invalid contracts. The **full suite passes 798 tests in
10.12 seconds**, cache provider disabled.

`scripts/275_audit_patchy_correction_limits.py --verify` independently decomposes
all 141 RGB floors, reconstructs **282 learned/saved-target images and metric
sets**, checks zero/green-white invariants and outside-support preservation,
verifies frozen hashes and retains every original target/parameter. Results
are in `outputs/patchy_correction_limits_v1/`, including all oracle PNGs,
records, summary, frozen plan and verification. Zero models or targets are fitted.

This narrows the next task: improve the remaining prediction gap on recoverable
cases and report severe clipping/support-limited cases separately. A recovery
claim must remain within the paper's ITA/MST/tree/gamma-gain scope; secretly
introducing color reconstruction or smoothing is not an acceptable fix.
Existing synthetic-recipe assumptions, exposure to development sources, weak
MST calibration and the clean safety failure remain. No reserved data, new
mask approval, photographer form or demo replacement occurred.
