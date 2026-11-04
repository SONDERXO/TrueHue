# Preserved application masks on the current Table 2 inputs

28 October 2026. Compared the earlier broader correction support with the current
application mask on identical saved inputs. This is an exposed-development
diagnostic, with no fitting, measurement-policy change or runtime adoption.

The earlier method was not deleted. Script 59 used material-checked, hair-vetoed
HSV/YCrCb and YCrCb-only supports, joined through an additions-only lower-face
boundary. Script 85 later intersected that correction support with the semantic
body/face-skin categories. The latter experiment also changed generation and
measurement policies; **only its correction branch** is reproduced here. Its
old measurements are not substituted into the current MST feature path.

Compared three policies without tuning:

- `current`: saved HSV AND YCrCb measurement mask, used for application in the
  latest Table 2 evaluation.
- `legacy_broad`: earlier material/hair checks and additions-only boundary.
- `legacy_non_skin`: the same broader support with the later non-skin veto.

All methods use the same actual input, frozen input-derived Lab/ITA/MST features,
held-source prediction and saved photographic reference/scoring support. No
reference statistics enter support construction or prediction. The measurement
contract remains `051dfb175e1356776ea59ebb5c3d63a7e1130de49d5787a7e75b7c0fa135db73`.

All 24 input masks reproduce exactly. All broader candidates are available;
geometry failure or insufficient YCrCb pixels would be reported without fallback.
Sixteen inputs from the eight previously accepted sources receive their existing
predictions. Eight inputs from rejected 51739/40048/42532/63870 are mask-only
diagnostics: no predictions, metrics, fitting or reinstatement. Their rejection
reasons and earlier reviews remain intact. Changed masks have no new user approval.

Mean CIEDE2000, lower is better:

| Inputs | No correction | Current | Earlier broad | Earlier broad + non-skin veto |
| --- | ---: | ---: | ---: | ---: |
| All 16 | 10.244 | 10.729 | 10.368 | 10.352 |
| Eight distorted | 20.488 | 14.935 | 14.247 | 14.254 |
| Eight unchanged | 0.000 | 6.524 | 6.490 | 6.449 |

Broader application improves distorted-input reconstruction modestly but does
not pass either original adoption gate. Overall error remains worse than no
correction, and the same four unchanged controls are harmed: 22211, 62331, 75027
and 84364. These are diagnostic results, not newly selected models or final
generalization evidence. References are photographs, not calibrated skin truth.

On the eight distorted inputs, mean retained reference-mask support rises from
73.65% to 80.52% with the broad method and 80.08% with the non-skin veto. Mean
selected pixels outside that support are 684.4, 891.9 and 583.1 respectively.
Neither measure is annotated skin accuracy: outside-reference skin may be valid,
and the reference mask itself can contain unwanted regions. The semantic veto
also removes some potential skin. No neck-performance claim follows.

Codex inspected all 12 source boards, covering all 24 mask comparisons and all
16 corrected-output comparisons. More continuous support is visible on distorted
62331/84364; 62331 still has conspicuous color patches, and 75027 still has large
uncorrected lower-face regions. 67583 remains visibly undercorrected. The light
inputs 22454/6236 still receive identity parameters and cannot improve through
support changes. Clean 62331/75027 remain visibly over-lightened. The earlier
hair checks remove some selected hair, but the rejected scenes remain rejected;
preview inspection is neither new annotation nor photographer MOS.

The evidence supports the user's recollection of broader earlier facial coverage,
but does not establish a perfect earlier mask. Severe distortion, irrecoverable
clipping, binary boundaries and wrong parameters remain separate problems.
Do not widen masks or refit serially to conceal the failed correction gates.

[Review all comparisons](../outputs/table2_application_mask_comparison_v1/review.html) |
[Full records](../outputs/table2_application_mask_comparison_v1/summary.json) |
[Independent verification](../outputs/table2_application_mask_comparison_v1/verification.json).

Scripts 161/162 prepare and verify the diagnostic. Independent verification
checks 72 masks, 48 corrected PNGs using a separately written RGB formula, all
16 frozen portable predictions, unchanged original corrected-output hashes,
metrics, excluded-source separation and tracked input/model/review hashes.
The full suite passes **692 tests in 13.93 seconds**, with one existing pytest
cache warning. The initial sandbox run produced 95 temporary-directory setup
errors (597 passed); the approved unrestricted rerun resolved those setup errors.

Next user verification is the concrete review page: confirm whether these
preserved broader policies match the earlier method being recalled and assess
their coverage/material boundaries. This review cannot approve the failed model.
No active model, Android asset, dataset allocation or measurement lookup changed.
Android remains paused; CPM remains deferred.
