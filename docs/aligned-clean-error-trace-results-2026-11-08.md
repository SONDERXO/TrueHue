# Why four clean photos are changed — 8 November 2026

The saved model routes clean inputs into leaves learned only from distorted
inputs. Three errors come from a colour-cast branch and one from an exposure
branch. This diagnosis runs no fitting or model inference and changes no policy.

| Clean case | Chosen action | Fitting examples in that leaf | Decision inputs | Regional RGB MAE introduced |
| --- | --- | --- | --- | ---: |
| case_02 | Red gain 1.167, blue gain 0.783; gamma 0.996 | 6 additive colour-cast conditions, no clean | Scene median lightness and zero-channel fraction | 10.77 |
| case_28 | Gamma 1.428, red gain 1.059, blue gain 0.999 | 5 combined cool/overexposure conditions, no clean | Scene median lightness only | 24.19 |
| eval_13 | Red gain 1.159, blue gain 0.791; gamma 0.996 | 7 additive colour-cast conditions, no clean | Scene median lightness and zero-channel fraction | 7.98 |
| eval_15 | Same action as eval_13 | Same 7 fitting conditions | Same branch as eval_13 | 6.50 |

The recipe identifier `stress_color_none` means an additive colour-cast stress
condition with no exposure direction. It is **not** an unchanged image.
Counts in this table are fitting conditions, not independent people.

## What the successful cases show

The same colour branch improves the distorted `case_02__stress_color_none` by
2.17 RGB MAE while damaging that source's clean photo. In the later full model,
the branch improves `eval_17__stress_color_none` by 4.14 and
`eval_11__stress_color_none` by 3.49, but damages the two later clean photos.
These are explicitly outcome-selected same-leaf comparators, not independent
validation. The two later comparators are shown for both clean queries and must
not be counted twice as additional photos.

For case_28, no successful evaluation input reaches the same leaf in its held
publisher-group fold. Its five fitting conditions do show a summed action cost
28.61 versus 134.37 for identity. This is training evidence only, not evidence
that its correction generalizes.

Across the four clean query routes, no skin Lab, ITA, MST or scene-chroma feature
is consulted. Those inputs are available to the models but are not selected on
these paths. The two scene-brightness branches and clipping statistic do not
reliably identify a colour cast or overexposure in these unseen clean photos.
This is a route description, not a controlled demonstration that background
changes cause the errors.

## Why simple guards are insufficient

All four chosen leaves have zero clean fitting examples. The hard fitting-clean
constraint therefore permits the action, which has lower summed error on the
leaf's distorted fitting members. This is consistent with the verified fitting
constraints; it does not indicate a tree export or runtime action mismatch.

Case_02 is outside seven leaf feature ranges, case_28 outside nine, and eval_15
outside three. **Eval_13 is inside every recorded range**, despite being harmed.
A rule rejecting out-of-range inputs cannot catch all four. Rejecting every leaf
without clean examples would also reject the useful comparator corrections.
Earlier neutral/range experiments already lost substantial recovery, so this
audit does not authorise another range or threshold trial.

The masks are imperfect, but there are no manual patch annotations on these four
photos. This trace cannot establish mask contamination as their cause or promise
that repairing masking will fix their action decisions.

## Development implication

The next learning design needs evidence that a correction is needed, rather than
letting scene brightness or clipping alone stand in for that evidence. It must
distinguish colour-cast decisions from exposure decisions and preserve recovery
on the same useful distorted cases. Repeating a generic capacity, threshold or
feature-removal sweep is not justified by this trace. No next fit is selected or
authorised here; the current model remains experimental and unadopted.

Roboflow's user-visible deployment option only established cloud API use. The
user found no local-export option. Close that access route unless a local model
asset/access change is provided; no SDK installation or private-photo upload.
Its absence does not block this saved correction-model diagnosis.

## Verification and artifacts

Scripts584–585 produce private `outputs/aligned_clean_error_trace_v1`.
The independent verifier checked four exported-tree routes, leaf memberships,
clean exclusions, action costs, float32 range checks and 38 available sibling/
comparator routes. All source hashes were preserved. Four focal and five
outcome-selected comparator boards (three distinct comparator conditions) were
viewed using saved reference/input/output images. No correction was rerendered.

RGB reconstruction error on these existing regions is not perceived naturalness
or true skin-colour accuracy. All sources are already exposed development
evidence; publisher grouping is not verified identity. No new annotations,
datasets, fits, forwards, admission flags or app changes occurred.
