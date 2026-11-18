# Correction training-design audit: recipe coverage and target equations

11 November2026. The user authorised auditing the training design and wants the
working correction model completed. This audit resolves the first two questions:
what the recent examples teach, and whether their target equations are correct.
It does not train a replacement or declare the model finished.

**Decision authority:** the user clarified that study decisions belong to the
researchers. Adviser consultation is not a prerequisite. The earlier adviser
brief is preserved as a historical draft, not an approval gate. No outside
permission or new data collection is required to complete this audit.

## 1. What the current examples teach

The exact44-case FFHQ dataset contains11 accepted/user-support-reviewed original
references,11underexposed,11overexposed and11red-attenuated cool derivatives.
The rejected29863 remains excluded in the48-role ledger. All examples use one
medium engineering severity. Target gamma has3values(0.7,1,1.42857143), red has
2values(1,1.04081633), blue has only1value(1). There are no warm/blue-adjustment
or combined exposure-and-colour cases, and no independent provided MST labels.

This is a bounded development diagnostic, not full coverage of the paper's
three-output task. The tree cannot demonstrate learning nonconstant blue gain
from these examples. Fixed-strength targets also do not test generalization
across correction strengths. But these omissions are not an established cause
of the existing red/identity failures: even these simpler cases should improve.

The earlier82-source/890-condition cycle already had82clean,228exposure-only,
222colour-only and358combined conditions, including warm/cool recipes. Its
failures remain closed. Therefore "add warm/combined examples" is a coverage
completion proposal, not a new demonstrated fix or authority to rerun that cycle.

## 2. Are the present target equations wrong?

No. For the current continuous transform v = u**g * [r,1,b], inverse direct
controls are [1/g,r**(-1/g),b**(-1/g)]. All44 saved targets match; float inversion
replays have maximum error below1e-12. Forward RGB8 images also match their
saved recipes exactly. Direct gamma below1 brightens, above1 darkens; no reversed
convention or red/blue channel-order bug was found in this audit.

Known controls were rendered with the actual saved masks, alpha and rounding,
and scored on every alpha-positive RGB channel, just like the saved16-input tree.

| Case | Uncorrected RGB | Known controls, blended RGB | Saved tree RGB |
| --- | ---: | ---: | ---: |
| Unchanged | 0.0000 | 0.0000 | 17.0042 |
| Underexposure | 27.5404 | 1.4715 | 20.4676 |
| Overexposure | 25.3998 | 1.5195 | 12.2891 |
| Mild cool cast | 2.1413 | 0.1032 | 17.2566 |

These are44 deterministic reference-informed diagnostic renders, not44 learned
predictions, fitted targets or unseen model results. The known controls improve
all33 distorted cases in RGB and preserve all11 identities exactly. They are
feasible correction candidates, not proved optimal controls. Their low error
shows that the rendering family can substantially restore these particular
synthetic inputs; it does not tell the tree which controls to choose at inference.

For comparison, known-control mean DeltaE is0.5608under,0.6416over,0.1235cool,
versus7.1828/4.2783/6.0623for the saved tree. The gap is large; changing the inverse
formula is not justified. Repeated mask editing likewise cannot choose controls.

## 3. Rounding and blending leave a smaller, real mismatch

Without boundary blending, nominal-inverse mean RGB residuals are0.0478under,
0.1433over and0.0132cool. With the fixed inward blend they become1.4715,1.5195,
and0.1032. Generation changed the whole cached image; correction applies only
inside the reviewed alpha and remains soft near its boundary. An exact inverse
before blending is therefore not an exact final-output inverse.

We also bounded each corrected channel by letting its preblend value vary freely
between0and255. The mean target-distance outside that reachable blended interval
is0.2422under,0.3550over and0.0026cool. This is a relaxed lower bound on any
bounded correction under the existing alpha, not the minimum attainable by the
three shared controls. The nominal-render costs above are feasible upper bounds
on the minimum RGB loss, not irreducible error floors. No optimizer was used.

This quantifies a real target/renderer difference without blaming it for the
much larger learned errors. It does not justify removing the blend, shrinking
scoring support or declaring pixel-perfect restoration necessary for the paper.

## 4. Alignment with the actual proposal

Re-read the matching cached proposal extraction, PDF38/60/62/63/65/66. The paper
specifies direct-gamma correction, gamma/red/blue outputs, synthetic exposure and
colour distortions against original references, parameter MAE and CIEDE2000.
Table2 also includes brightness, contrast and red/blue slider values with
light/medium/dark severity settings. It does not fully specify executable slider
units, operation order or exact optimisation targets. The current no-offset,
no-extra-contrast, red-attenuation recipe is a documented engineering
simplification, not a literal implementation of every Table2operation.

Full offset/contrast/clipping distortions cannot generally be inverted exactly
by gamma/red/blue alone. For example, finite positive green-channel gamma maps
zero to zero, so it cannot restore a positive green value lost to clipping.
Such pairs require explicitly approximate recovery targets and reported residuals;
do not give them nominal gamma/gain inverse labels as though those were exact.
The earlier composite-target and recipe audits already established this; this
review does not restart them. Physical skin-colour truth is not a prerequisite.

## Next concrete work

Keep the current correct inverse equations, rendering, reviews and failures.
Do not alter targets, scale weights, grow trees or add a recipe batch automatically.
The next useful deliverable is a single paper-aligned training-contract specification:
state which distortion lane is being learned, its exposure/colour/combined and
blue-control coverage, how approximate targets are constructed where required,
and how photo-held correction benefit/identity harm will be evaluated. Distinguish
coverage completion from evidence of better prediction on unseen originals.

Any proposed fit must also explain why it addresses the demonstrated wrong-control
selection beyond merely filling absent recipe names; past broader supervision
already failed. No specific new learning repair is established by this audit.
No new annotation is pending, no adviser approval is needed, and the working-model
objective remains active and unresolved. This is not a decision to narrow the
thesis to negative results or to abandon the retained tree/ITA/MST method.

## Verification and limits

Scripts818?819 check44 inverse targets, channelwise forward/inverse renders,
reachable-interval bounds, RGB/standard CIEDE2000 and4role aggregates. Independent
replay passes. These are cached256px reviewed sources and propagated same-geometry
masks, with preserved support imperfections and unvalidated MST transfer; not
independent person-level/final/fairness evidence. Blue capability remains untested.

No model/target fits, image-model calls, original-photo/holdout reads, acquisition,
contact/upload/commit/push/runtime or Android changes. Final24/older locks remain
byte-unread; all previous annotations, outputs and submitted paper are preserved.

Sources: [saved data audit](completed-ffhq-support-results-2026-11-11.md),
[baseline](reviewed-ffhq-restoration-results-2026-11-11.md),
[historical broad coverage](training-exposure-colour-audit-2026-11-09.md),
[proposal recipe audit](proposal-distortion-recipe-audit-2026-11-03.md),
[target-family checkpoint](paper-distortion-target-checkpoint.md).
