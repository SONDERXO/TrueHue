# Current-framing contrast comparison — 8 November 2026

The fixed parser-only contrast enhancement helps some photos but does not resolve
mask reliability. It is not adopted. The correction model and app are unchanged.

Exactly five new ResNet18 parser forwards were run on the current saved clean
inputs. The existing Lab-L CLAHE transform used clip limit 2 and grid 8×8.
Landmarks, framing, class list, exclusions, minimum pixel requirement and cached
raw-input FaceOcc outputs stayed fixed. Original pixels supplied all measurements.
The sixth photo remains a landmark failure. There were no other model forwards,
fits, annotations, new datasets or parameter searches.

## Results

| Measure | Raw input | Enhanced parser copy |
| --- | ---: | ---: |
| Technically usable measurements, all six photos | 3/6 | 4/6 |
| Marked pixels in usable measurements, all 3,156 marked pixels | 653 (20.7%) | 843 (26.7%) |
| Marked pixels in diagnostic masks, including failed measurements | 687 | 848 |
| Skin points selected in diagnostic masks, same 113 points | 39 | 46 |
| Unwanted points selected in diagnostic masks, same 94 points | 3 | 4 |

The point comparison uses five photos with diagnostic masks. The sixth photo's
31 reviewed points have no predictions and are not successful exclusions.
For jointly usable measurements, the same three photos contain 79 skin points
and 55 unwanted points: selection changes 38→45 and 3→4 respectively. These
denominators differ because technical availability differs.

| Photo | Diagnostic marked pixels: raw → enhanced | Technical outcome |
| --- | ---: | --- |
| review_01 | 21 → 21 | Failed → usable |
| review_02 | 129 → 274 | Usable → usable |
| review_03 | 13 → 5 | Failed → failed |
| review_04 | 48 → 95 | Usable → usable |
| review_05 | 476 → 453 | Usable → usable |
| review_06 | unavailable | Landmark failure retained |

Review_01 passes with 1,068 normalized final-mask pixels, but its overlap with
marked patches does not increase. A new technical pass is therefore not evidence
that the annotated skin was recovered. Review_03 retains only 287 normalized
pixels after visibility filtering. Review_05 loses marked coverage. One more
reviewed unwanted point is included across both the diagnostic and paired-usable
comparisons. More coverage does not establish improved protection.

## Inspection and decision

All five fixed original/raw/enhanced/change boards were viewed. Review_02 gains
substantial central-face coverage; review_04 gains a small additional patch.
Several masks remain fragmented or forehead-dominated. Glasses, beard and fine
object boundaries remain unresolved. No complete mask accuracy is established.

The transform provides a limited improvement, with regressions and incomplete
coverage. Retain it as an experimental result; do not replace the raw pipeline,
retrain correction on it, expand its batch or tune it automatically. The four
unwanted clean-photo correction cases were not evaluated in this five-input
check, so no clean-correction safety claim follows.

The evidence now points to a limitation of recognition on these inputs rather
than a demonstrated channel/coordinate bug. Further small preprocessing trials
should not be treated as a path to completion by default. Any next intervention
should address skin recognition and unwanted-material protection together, with
its implementation and acceptance criteria agreed before another inference run.

## Limits and verification

These exposed selected patches include neck skin and are not full facial ground
truth. Sparse points cannot certify all beard, glasses or background boundaries.
Pixels and repeated conditions are not independent people. Results cover these
clean inputs only, not distorted inputs or general deployment performance.

Scripts581–582 implement and verify the comparison. Private outputs are in
`outputs/current_parser_appearance_v1`. Verification replayed all five enhanced
copies, parent masks, cached visibility services, original-pixel statistics and
native projections; independently recounted patches and source-coordinate points;
checked all 54 bound input hashes and hashed outputs. Verification adds no model
forwards. Prior artifacts, data restrictions and admission settings are preserved.
