# Material protection and reference-quality checkpoint

27 October 2026. Continue from the [broader protection test](paint-protection-validation-results.md).
Completed a [predeclared cached attribution audit](material-failure-attribution-protocol.md)
before choosing another candidate. No new model, inference, mask, parameter fit,
training-pair regeneration or source exposure. Previous decisions remain intact.

## What the cached audit establishes

[Detailed gallery](../outputs/material_failure_attribution_v1/review.html),
[region accounting CSV](../outputs/material_failure_attribution_v1/region_funnels.csv),
[verification](../outputs/material_failure_attribution_v1/verification.json).
All51 cases are retained, including three unavailable probes. There are60
region/probe rows,560 stage/region count checks and three scalar-order witnesses.
The sequential removal funnel is disjoint accounting, not causal attribution.

For16798clean, the6003pixels in the original exclusion polygons descriptively
grouped as paint are accounted for as follows:

| Accounting step | Removed pixels |
| --- | ---: |
| Dense parser does not select skin/nose | 34 |
| Coarse model does not select face-skin, after dense selection | 344 |
| Expanded anatomical exclusions, after both model selections | 1 |
| Processing bounds, after exclusions | 0 |
| Remaining in A | 5624 |

This grouping reuses earlier Codex descriptive polygon grouping; it is not an
additional user-supplied material class. F/C/C2 retain1096/1411/851pixels in those
regions. The material seed set overlaps614paint-group pixels out of21704total
seeds(clean),739/22458dark and293/19847color. These are **label-overlap counts**,
not a verified physical paint-contamination rate. The614clean pixels are2.83%
of seeds, so this does not establish that paint dominates the median or causes
the failure. We did not recompute a label-cleaned center or use annotations in
inference. Feature-group overlap is also present:178clean16798seed pixels,
172clean40048 and317clean60162.

The new provisional regions trace multiple failure paths. For example84888's
blue-eye interiors overlap54clean seeds,191A pixels and44C2pixels. Its makeup
and anatomical-feature boundaries overlap; these counts cannot distinguish
which learned/landmark component is causally responsible. 81250's three marks
overlap194clean seeds,236A pixels and112C2pixels. Lightness removal F versus
chroma-only C behaves differently on the light mark, as already visible in the
frozen experiment. No origin of the marks is inferred.

The same accounting shows labeled ordinary-skin loss before relative color:
40048clean loses271pixels at dense selection and1090at anatomical exclusions;
60162clean loses378at dense selection,27at coarse selection and913at anatomy.
No processing-bound exclusion adds further loss in either clean frame. These
are losses against supplied skin polygons, with their own boundary uncertainty;
they do not justify simply expanding exclusions to fix cosmetics.

## Important reference-quality finding

The frozen chroma scalar assigns some paint-group-labeled pixels lower distance
than some skin-labeled pixels in all three16798probes. For example clean
paint-group point(179,158) has distance0.03935, while skin-label point(222,106)
has distance6.31528. A single monotone cutoff of this particular frozen scalar
cannot reject the former while retaining the latter **under the saved labels**.

However, visual inspection of all three witness images found mixed-material
ambiguity: the clean/color skin-label witness appears in the painted cheek
edge; the dark skin-label witness is near visible nose color; the paint-group
witness is near a blended skin/paint boundary. Neither has been independently
adjudicated. These pairs **do not prove physical paint/skin inseparability**,
universal failure of color features, or that the existing labels are wrong.
The earlier working interpretation was narrowed after visual review. Saved
coordinates, label membership and counts remain unchanged, with the caveat
stored separately in `visual_qa.json`.

This makes reference quality an additional prerequisite. Do not train on these
regions, automatically flip labels to agree with a model, erase earlier scores,
or present their exact pixel overlaps as validated segmentation accuracy. The
earlier technical hold remains; its metrics now have an explicit reference
quality flag. Clear cosmetic/feature/mark overlaps and support losses still
require investigation, without extrapolating one blurred boundary to all cases.

## Requirements before another material-specific candidate

The next development artifact is an adjudicated material-reference set and a
declared experiment, with these requirements fixed before candidate results:

1. Keep immutable original user files/hashes. Any clarified polygons or labels
   become a separate version with author, date, exact frame hash/dimensions,
   rationale, changed pixels and uncertainty. Adjudication is actual reviewer
   evidence; Codex-generated polygons are not silently promoted to it.
2. Distinguish ordinary visible facial skin, visible surface paint/cosmetic or
   mark, anatomical features, other material, uncertain and unlabeled. Record
   cosmetic/feature overlap rather than assuming every eyelid error is paint.
   Ambiguous rendering/lighting stays uncertain. Label interiors and mixed
   boundaries separately; a lack of uncertainty polygons does not prove certainty.
3. Include ordinary skin near protected regions, not just distant clear cheek,
   and examples of shadows/highlights/colored lighting without known coatings.
   Include different coating colors and locations and repeated identities only
   within one source group. Do not infer tone/ethnicity or physical mark origin.
   Representative sampling/sample size must be justified; the current one broad
   paint source and four cosmetic sources are insufficient for a general claim.
4. Preserve the exposure ledger and existing source-group partitions. The17
   exposed frames remain development diagnostics. Additional development sources
   must be designated TRAIN and ledgered before viewing; final reserved sources
   remain unopened during design. Define a separate independent final evaluation
   and reviewer protocol before consuming it. No automatic reassignment of folds
   or introduction of final-evaluation labels into fitting/features.
5. A future learned material candidate must document whether its training labels
   actually represent protected materials, model/license/data provenance, input
   processing and phone feasibility. Anatomical skin classes alone are not
   evidence of material supervision. No candidate is selected or downloaded by
   this checkpoint; no unsupported promise of automatic paint recognition.
6. Freeze the next candidate and missing-output policy before execution. Compare
   all generation/measurement/correction stages, protection interiors/boundaries,
   ordinary-skin coverage, feature validity, clipping and stress consistency.
   Keep failures and qualitative cases. Preserve current protection/coverage
   holds until the adjudicated references support an explicit decision. Do not
   loosen a gate after seeing a result or treat small ROI passes as whole-mask
   validation.

These are development reference/evaluation requirements, not a new application
user annotation workflow. No claim is made that expert adjudication has already
occurred or that the dataset plan is an approved proposal amendment. A final
numerical sample-size/accuracy target requires the advisor's actual evaluation
design; none is invented here.

## Verification and thesis record

Script108reuses only cached predictions/geometry/masks and unchanged references.
Script109independently reconstructs provisional/paint-group polygons with
pixel-center point tests, checks disjoint condition accounting, distance
percentiles, seed/stage counts and witness membership/distances. All prior
recorded artifact/model/source/reference/review/ledger hashes match. Eight
three-probe contact boards and all three witness images were inspected. The
existing481Python tests pass in41.64s with a fresh writable workspace basetemp.
No production pipeline code was changed.

Relative material self-reference, learned segmentation and manual development
reference adjudication extend the proposed rule-based stage. This audit is on
known exposed224/256frames and adds no calibrated skin-color truth, independent
accuracy, physical-material impossibility result, expert MOS or phone parity.
Neck localization, operational MST, final data/splits/reference/evaluation,
expert MOS and Android remain unfinished. No candidate adoption, regeneration,
training admission, review reversal or correction-model fit follows.
