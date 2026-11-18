# Fixed correction gate: less clean harm, many missed distortions

6November2026. The user-authorized two-stage experiment is complete. A fixed
input-only linear gate leaves18of29available clean images unchanged, but still
corrects11clean images and leaves165of368available synthetically distorted
images unchanged. Mean clean harm decreases while core/stress reconstruction
errors increase. **This gate is not adopted.**

## Frozen design and scope

Follow the [protocol](correction-gate-protocol-2026-11-06.md). Fit exactly one
logistic gate per held publisher key:10fits. Use the original five Lab/ITA/
continuous-MST features and saved depth3correction trees, not the later balanced,
chroma or unlimited-depth candidates. Gate output above the fixed zero-logit
boundary applies the saved correction; zero/negative output is an exact no-op.
No threshold/C/feature/classifier sweep or held-out outcome selection.

Logistic settings: C1,lbfgs,max_iter1000,tolerance1e-4,seed42; default L2objective.
Each fitting publisher key has equal total weight and equal clean/distorted
class weight within key. Row weights sum to fitting-row count. Fitting-only
weighted standardization uses scale1for a constant feature. All10fits converge
in13–17iterations. There are no new MST, correction-tree or target fits.

Gate training uses all397available feature rows, including40rows lacking a
usable correction target. Clean/synthetic membership is still known for these
rows, so they can supervise detection without fabricating correction targets.
The saved correction trees retain their original357trainable rows. Training
labels come from synthetic recipe membership only; no recipe, source score,
condition, reference colour or label enters the five inference features.

Every training key's MST estimate comes from a saved ridge excluding both its
own key and the outer held key. Held features use the original outer-held
predictions. This remains a development-exposed, fixed borrowed-support,
restricted measured-region study; it is not a whole-face runtime test or a
qualified calibration cohort.

## Detection results

| Held input class | Available decisions | Apply correction | Leave unchanged |
| --- | ---: | ---: | ---: |
| Clean original |29|11false positives|18true negatives|
| Synthetic distortion |368|203true positives|165false negatives|

Clean false-positive rate is37.9%; synthetic miss rate is44.8%. Of232core
distortions,118are missed; of136stress distortions with available features,
47are missed. Detecting a distortion does not establish that applying the saved
tree will improve it. These are synthetic-membership labels, not human judgments
of natural lighting, preferred appearance or whether a real photograph needs
correction.

All420attempts remain:397decisions and23unavailable decisions. Fourteen original
failures lack support; nine stress features have undefined ITA and produce
unchanged fallback outputs. Those nine are not detector true negatives or
included in the368available synthetic decisions. Their outputs are included in
scored operational image errors where support exists.

Matched trivial detection baselines are explicit: always-correct gives29clean
false positives and zero available synthetic false negatives; always-unchanged
gives zero clean false positives and368synthetic false negatives. Ordinary
accuracy alone would obscure this class imbalance.

## Operational correction errors

| Layer | Scored / attempted | Unchanged-input MAE | Ungated depth3 MAE | Gated MAE |
| --- | ---: | ---: | ---: | ---: |
| Clean |29/30|0|10.3689|3.9753|
| Core |232/240|20.7385|18.8434|19.2750|
| Stress |145/150|52.5649|34.0350|37.6530|

RGB8MAE uses the0–255channel scale. Gating reduces clean-image harm counts
29→11, core regressions98→49of232and stress regressions28→19of145versus unchanged
input. However, suppressing useful corrections raises mean distorted-case error.
Equal-key gated errors are4.2010clean,19.4446core,37.6776stress. Relative
CIEDE2000 gated means are1.3955clean,6.9491core and14.1791stress.

Per-condition clean false positives are6/10F_cool_600,1/9H_warm_600and
4/10L_warm_600; synthetic misses are53/126,77/115and35/127respectively. These are
descriptive small development counts, not causal lighting or skin-tone fairness
results. No physical or aesthetic colour truth is assumed.

## Verification and visual inspection

Script492saves the10gates, fitting memberships/weights, raw held logits,
decisions and outputs. Script493verifies3573nested training feature traces,
all10training-only weighted scaling/class masses,397independently calculated
held linear logits and all406saved renderer/metric outcomes without refitting.
Gate-off controls/output are exactly neutral/unchanged. Sources, saved upstream
models and original correction trees remain hash-identical.

Six new gate tests plus existing continuous-interface/portable-tree tests:
**50passed in4.73seconds**. Tests cover fixed zero-logit no-op semantics,
key/class masses, weighted scaling, constant features, linear export replay and
invalid class/group/input rejection. This is not a full-suite or phone check.

All29held clean original/ungated/gated boards were inspected. Eighteen images
are byte-identical no-ops; conspicuous region changes remain in some of the11
false-positive cases. No new reviewer labels, expert ratings or full420-image
visual review is claimed.

Private artifacts: `outputs/correction_gate_experiment_v1/`; verification and
boards: `outputs/correction_gate_assessment_v1/`. No runtime/Android adoption,
scientific admission, source expansion, publication, transfer or contact.
Dataset research/noncommercial, citation and no-redistribution terms remain.

## Decision

This fixed gate reduces one failure by trading away some successful corrections;
it does not solve reliable automatic correction. It is evidence about this
linear gate and these exposed features/data, not proof that every possible
input-only detector must fail. Neither gate tuning on these outcomes nor a
classifier sweep is activated. A subsequent design needs a justified new source
of inference information or an explicitly narrower operating policy and must
retain both false corrections and missed distortions. No manual app step or
final-method change follows automatically from this result.
