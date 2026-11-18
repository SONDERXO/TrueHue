# Reviewed photographic correction comparison — 11 November 2026

**The fixed candidate fails the reference-preservation check and is not adopted.**
It improves average source RGB/DeltaE error but unnecessarily edits three of
seven held reference images. This directly tests correction quality using the
reviewed data; it does not start another calibration or source-search dependency.

Scripts787–788 execute exactly seven depth4 action-tree fits, twelve fitting
roles/six publisher groups per fold, and fourteen held-role predictions. All
sixteen attempted roles remain in the ledger, including the two unavailable904
roles. The904-only unavailable fold has no fit. Existing sixteen features,
fourteen actions, costs, mapping, masks and native renderer remain fixed. No
additional model or mapper was fitted.

## Primary results

| Source metric, equal publisher weight | Uncorrected input | Held-tree output |
|---|---:|---:|
| RGB-code MAE | 37.603367 | 32.002888 |
| CIEDE2000 | 13.241710 | 12.031091 |

RGB improves on three sources, worsens on one and is unchanged on three.
DeltaE improves on two, worsens on two and is unchanged on three. Four of seven
held identity/reference outputs are unchanged; three are edited. All protected
and zero-alpha pixels remain unchanged. Coverage and both mean-improvement checks
pass; reference-output preservation fails. Frozen checks remain unchanged.

| Source | Input → output RGB | Input → output DeltaE | Decision |
|---|---:|---:|---|
|1117|36.673 →36.673|12.459 →12.459|Identity; misses available catalogue benefit|
|1188|36.616 →36.616|12.150 →12.150|Identity; misses available catalogue benefit|
|330|17.021 →17.021|6.185 →6.185|Identity; misses available catalogue benefit|
|455|12.225 →37.783|5.659 →14.082|Wrong darkening action; substantial harm|
|767|87.002 →55.862|30.243 →17.883|Improves, substantial residual error remains|
|787|48.290 →34.183|17.131 →18.210|RGB benefit but perceptual error worsens|
|990|25.397 →5.882|8.864 →3.248|Improves both metrics|

The edited reference roles are1117,455 and787, with output RGB errors2.158,
24.103 and23.886 from zero baselines. Their DeltaE errors are2.108,8.919 and9.095.
The source455 worst harm is an increase of about25.56 RGB units and8.42 DeltaE.
Average gains must not conceal those outcomes.

## Correction behaviour and output review

All fourteen held input/output/reference panels and the blocked904 ledger panel
were viewed. The787 source is strongly brightened with a visible yellow shift;
its RGB improvement is not a perceptual success. The455 source and reference are
unnecessarily darkened.767 and990 improve measured local error; that does not
imply matching global editorial changes outside correction support. Tiny face
detail, especially1188, limits visual inspection. This is assistant diagnostic
review, not photographer MOS.

The three edited reference inputs reach source-only fitting leaves.1117's
reference reaches a leaf supported by455's source;455 and787 references reach
leaves supported by330's source. Original fitting identity constraints remain
satisfied, but do not guarantee held-reference preservation. The unchanged
1117/330 sources reach identity-supported leaves;1188 reaches a mixed leaf with
all six fitting identity roles. These recorded routes expose a correction versus
identity generalization problem, not an arithmetic failure or evidence that the
user should paint more masks.

For the two source cases whose saved catalogue minimum has gamma>1 (1117/330),
the tree predicts identity, with zero benefit. The five gamma<1 catalogue cases
average7.840672 RGB improvement and1.694866 DeltaE improvement, including the
harms shown above. These catalogue directions are descriptive and not physical
exposure labels;455's best gamma is effectively neutral. No new grouping is used
to fit or select a replacement.

Across all seven trees, splits use L*16times, b*5, ITA4, scene L*p50 four, a*once
and scene full-channel fraction once. MST remains constant and cannot split.
ITA use does not by itself prove successful tone conditioning, and no per-MST
fairness result is claimed.

## Verification and paper use

Independent replay verifies69 recorded nodes,3,536 candidate split options,
first-minimum leaf actions, fourteen held routes, fourteen native renders,
RGB/standard CIEDE2000 calculations, coverage and every frozen check. All pass;
verification performs no refits or new model calls. Exact feature/cost/mapping
bindings and cached paired-pixel hashes remain unchanged. No extra unit-test
suite was rerun; actual-run exhaustive arithmetic/render verification is recorded.

This is usable paper evidence for the photographic-supervision development
extension: small exposed publisher-held evaluation, measurable average gain,
documented preservation failure and unsupported MST-conditioning claims. It is
not the primary synthetic-original restoration benchmark, final validation,
physical-tone recovery, completed fairness evaluation or a deployable model.
Original failed comparisons and their gates remain intact.

The comparison is **complete and closed**. No repair fit, deeper tree, feature
search, veto, new calibration, dataset hunt or mask queue follows automatically.
The current result narrows the correction issue: the retained features/tree on
this small photographic supervision do not reliably distinguish identity from
the required direction/strength of correction across held groups. It does not
prove the tree family or the proposed study impossible. Any further technical
proposal must address this demonstrated correction problem and justify one
intervention before execution; no intervention is selected here.

Private evidence: `outputs/reviewed_correction_comparison_v1`. Fourteen outputs,
seven trees, all predictions/metrics, route context, boards and verification are
preserved. No original JPEG/TIFF reads or image-model calls occurred; rendering
used existing cached reviewed pixels. No runtime/Android change, acquisition,
contact, upload, commit or push. Final24 and older locked images remain byte-
unread. The user's too-bright demo is unchanged; no working-model success is
claimed. Decision tree, ITA/MST and the authorized manual option remain required.
