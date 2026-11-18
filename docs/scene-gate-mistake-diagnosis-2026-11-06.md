# Remaining gate mistakes: missed useful correction and avoided harmful correction

6November2026. The user explicitly selected diagnosis of the remaining mistakes.
The read-only diagnosis is complete. No models, thresholds, masks, labels or
runtime behavior were changed. The main finding is that **synthetic distortion
detection is not the same task as deciding whether this corrector helps**.

## Partition of the saved decisions

For each available held-key case, compare the saved shared corrector's RGB8
error with unchanged-input error against its photographic reference. This is
post-hoc diagnostic use of the reference, never a new inference feature or
outcome-tuned decision. Retain exact error comparisons without choosing a new
benefit margin or decision threshold.

| Scene gate decision | Core | Stress with available gate features |
| --- | ---: | ---: |
| No-op, but saved correction would reduce RGB error |101|4|
| No-op, avoiding a saved correction that would worsen RGB error |43|12|
| Apply a correction that reduces RGB error |68|106|
| Apply a correction that worsens RGB error |20|14|
| Available cases |232|136|

Thus144core detection misses include101missed useful corrections and43avoided
harmful ones. Sixteen stress misses include four missed useful corrections and
12avoided harmful ones. All six clean false corrections cause harm;23clean
no-ops avoid the original corrector's harm. This does not turn incorrect
synthetic-membership decisions into correct detection labels: the existing
confusion matrix stays unchanged. It explains operational consequences.

Denominators remain explicit:29available clean+232core+136stress=397attributed
decisions of420attempts. Fourteen original failures and nine undefined-ITA
decisions remain unavailable, not true negatives. The earlier operational
stress MAE includes145supported outputs; this diagnostic table conditions on
136available gate decisions. Do not substitute one denominator for the other.

## Where the core misses occur

| Recipe | Misses /29 available | Misses suppressing useful correction | Misses avoiding harmful correction |
| --- | ---: | ---: | ---: |
| Exposure under |25|25|0|
| Exposure over |11|10|1|
| Colour cool |19|0|19|
| Combined cool under |23|23|0|
| Combined cool over |9|9|0|
| Colour warm |22|0|22|
| Combined warm under |24|24|0|
| Combined warm over |11|10|1|

Suppression of useful exposure/combined corrections is a real gate failure.
In contrast, a more aggressive synthetic-detection gate would apply many
harmful mild-cast corrections unless the corrector changes too.

## Mild colour casts reveal a correction-model failure

All58pure colour-cast cases receive exactly the same three predicted controls
as the clean version of the same original. The tree is insensitive to these
small imposed casts at its current partitions. Every one of those58saved
ungated corrections worsens RGB error.

| Recipe | Input MAE | Ungated corrector MAE | Current scene-gated MAE |
| --- | ---: | ---: | ---: |
| Pure cool cast,29available |1.0684|13.6457|5.2887|
| Pure warm cast,29available |0.6056|14.0991|3.6163|

Their fitted target gamma ranges0.9997–1.0001, while predicted gamma spans
0.8394–1.4277. This supports the specific conclusion that exposure controls
are being applied inappropriately to these mild cast examples. The fitted
targets remain reference-aware local solutions, not runtime truth or intrinsic
skin-colour measurements. Low source-relative error does not establish natural
appearance, and the mean RGB criterion does not replace perceptual reporting.

## Six clean false corrections

All six logits replay exactly as intercept plus standardized feature
contributions. Positive logits range0.1135–1.0850; the failures are not all
floating-point boundary ties. The summed scene-feature contribution is negative
in all six cases relative to each gate's training means, but facial contributions
plus intercept outweigh it. Feature groups are correlated, so this decomposition
is not a causal ablation or proof that removing facial features fixes the gate.
No threshold adjustment was tried.

All six false-correction boards and the first sorted no-op case from each of
the eight core recipes were inspected:14focused saved-output boards. Selection
is recorded privately; it is not all144misses or another human annotation task.
Visible overcorrection remains in clean/mild cases, while several exposure
no-ops visibly retain darkening or brightening. These are assistant observations,
not newly assigned labels or expert ratings.

## Verification and decision

Script498checks all397available metric selections against their exact saved
gate action, partitions improvement/harm, decomposes six logits and verifies
bound source/artifact hashes. Script499independently checks all58matched
mild-cast-versus-clean control equalities and target/predicted gamma ranges.
Private evidence: `outputs/scene_gate_mistake_diagnosis_v1/`, with focused
selection, boards, case-level attributions and hash manifests. Case-MAE sums
are not pooled pixel errors or independent subject effects.

No production code changed or new pytest run was needed for this saved-evidence
audit. Existing tests remain historical. Zero new fits, model inference, masks,
admissions, dataset transfers, contacts, app changes or submissions. Research/
noncommercial, citation and no-redistribution terms remain.

Close this diagnosis. Another synthetic-membership gate or threshold sweep
does not address the mismatch alone. A justified next design would make the
decision objective correction benefit/harm rather than recipe membership,
while also retaining the mild-cast correction failure as a regression case.
Any benefit labels used for training must come from subject-held corrector
predictions inside each outer training partition; using these outer held
outcomes to train/tune the gate would leak evaluation information. That would
be a new nested experiment, not a relabel-and-refit shortcut using the current
held results. No such labels, fitting task or method adoption is activated here.
