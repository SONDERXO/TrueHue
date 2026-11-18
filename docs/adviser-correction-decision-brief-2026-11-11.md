# TrueHue: correction-model decision brief

11 November 2026 | Draft for adviser discussion; not sent

**Decision requested:** agree the next bounded research direction before another
training or annotation campaign. Retain the decision tree, ITA/MST and the
paper's photographic-restoration question. No reliable replacement model is ready.

**Study scope and current progress**

The proposal tests decision-tree restoration of synthetically distorted photos
toward their originals, not intrinsic skin-colour recovery. Outputs remain gamma
and red/blue gains from one photo. Face/visible-neck support and optional manual
refinement are user-requested extensions to document explicitly.

All 11 latest FFHQ measurement/correction reviews are verified; none needs
repeating. The twelfth original was rejected as underexposed. Reviewed masks
remain imperfect. The demo retains historical controls; mask editing alone does
not recompute them. No failed candidate has replaced the demo model.

**Latest correction evidence**

Each comparison uses 11 photo-held folds: 40 fitting/4 held cases per fold,
44 predictions from 11 originals. These are exposed development cases, not
44 people or a final test. The second tree adds two bright-weighted scene-colour
inputs to the 16-input baseline; the saved baseline was not refitted.

Mean CIEDE2000 below; lower is better. Each input type has 11 cases.

| Test input | No correction | 16-input tree | 18-input tree |
| --- | ---: | ---: | ---: |
| Unchanged originals | 0.000 | 5.856 | 6.699 |
| Underexposed | 9.575 | 7.183 | 7.183 |
| Overexposed | 8.705 | 4.278 | 4.983 |
| Mild colour cast | 2.269 | 6.062 | 6.538 |

Both trees improve the exposure averages, with individual failures. Both worsen
the mild-colour average and alter all 11 unchanged originals. The extra inputs
leave 40 outputs byte-identical; one changed case improves and three worsen.
Independent numerical verification passes, but correction-quality checks fail.
Neither candidate was adopted; earlier failures remain recorded and closed.

**What remains unresolved**

Normal and colour-shifted photos reach exposure-correction leaves. The learning
problem remains; this does not establish one sole cause or prove all trees fail.
Current MST transfer is unvalidated, tone-group benefit is not demonstrated,
and this fixed recipe set cannot test learned blue-gain recovery because its
blue targets are constant. The full proposed distortion/evaluation programme,
photographer assessment and Android validation remain incomplete.

Zero identity edits is an engineering check, not a verbatim proposal requirement.
Colour regression independently fails the restoration-benefit question. Do not
relax failed checks after results or claim final accuracy/fairness.

**Discussion and recommendation**

1. Which substantive change to training evidence or input information is worth
   one bounded study within the retained tree/ITA/MST method? Name what new
   evidence it adds, feasible resources and the comparison before collection,
   annotation or fitting. No specific successful repair is currently established.
2. If no justified redesign is feasible within the project, is a clearly scoped
   feasibility/limitations evaluation an acceptable thesis direction, and which
   remaining evaluations would it require? This would need an explicit decision;
   it would not mean the requested working model has been completed.

Resolve that choice before more small trials or mask reviews. No chart, physical
colour truth, perfectly invariant MST, acquisition or family change is required
by this brief. Earlier user-reported limited-MST approval is not reopened.

**Supporting records**

- [Paper/model scope](correction-model-and-paper-realignment-2026-11-11.md)
- [Verified support reviews](completed-ffhq-support-results-2026-11-11.md)
- [16-input baseline](reviewed-ffhq-restoration-results-2026-11-11.md)
- [Learning diagnosis](ffhq-correction-learning-review-2026-11-11.md)
- [18-input comparison](bright-scene-cue-comparison-results-2026-11-11.md)

The final holdout and older locked allocations remain byte-unread. All prior
artifacts are preserved. This draft records no adviser approval, authorizes no
new experiment or acquisition, and has not been sent to anyone.
