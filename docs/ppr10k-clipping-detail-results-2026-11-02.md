# Detail check: contrast is promising, but not ready for adoption

2 November2026. User authorised inspection of saved highlight/shadow detail,
especially the six new photographs with increased clipping. Script397 checked
all14saved comparisons, retaining the earlier indoor regressions. No fits,
new photos, model passes, mask changes, training or runtime edits.

**There is actual per-channel highlight flattening in some facial areas. Some
large clipping counts also come from background/clothing inside the approximate
regions. Do not adopt the fourth output on the current evidence.** This does
not erase the improved overall appearance or prove the operator unusable.

Gallery: `outputs/ppr10k_clipping_detail_check_v1/review.html`.
Blue marks raw shadow clipping, magenta highlights, yellow both in different
channels. A marked pixel does not imply every RGB channel is black/white.

## Fixed measurements

Used original saved floating-point sources, targets, parameters and polygons.
Verified both parent artifact manifests; explicitly reconstructed3/4control
raw transforms and matched their saved outputs and clipping totals. No operator
or threshold search. Counts distinguish raw<0 and raw>1 before clipping.

For context, report clipped channel samples whose expert target is at least
twoRGB8codes away from the endpoint. This is a descriptive count, not a success
threshold or proof of unacceptable loss. Also count horizontally/vertically
adjacent channel pairs both clipped to the same endpoint despite source or
target variation of at least oneRGB8code. Such counts overlap, do not count
independent features and depend on unverified pixelwise correspondence.

Six focus cases below; denominators remain the original approximate regions,
not certified skin or even exclusively facial pixels.

|Frame|Four-control low/high clipped channel samples|Clipped samples with target >=2codes away|Visual finding|
|---|---:|---:|---|
|787_0|299/150|409|Highlights on nose/chin/lip and dark hair/eye/face-edge areas. Red-channel highlight flattening occurs where target still varies.|
|767_0|119/89|208|Cheek/nose/chin highlights and eye shadows; visible colour improvement coexists with local channel loss.|
|1188_0|0/177|177|Bright clipping mainly follows background inside the profile polygon. Tiny face and region contamination prevent a clean facial-detail conclusion.|
|990_0|0/9|9|Small red-channel highlight spots around cheek/nose; limited extent, no broad facial-detail-preservation claim.|
|904_0|407/14|17|Large low-clipping overlay lies mainly on BLUE SHIRT included in the polygon; predominantly red-channel values near zero, often also near zero in target. Earlier8.18%region-channel clipping is not8.18%facial-detail loss.|
|455_0|41/0|26|Shadow clipping around lips/face edges in pronounced makeup, not evidence of widespread cheek texture loss.|

Important correction to prior interpretations: the approximate region for904
extends over the shirt and does not fully cover the actual face. The1188region
includes bright background along the profile. Earlier reports called these
face-region clipping counts; they are **mixed-region counts** and cannot be
interpreted as exclusively facial. Their reported colour errors are also over
those same mixed regions. Prior numerical results and original regions are
preserved rather than silently repaired/refitted. The8/8new-group improvement
is therefore improvement on the frozen approximate regions, not certified8/8
complete-face or skin improvement. Other polygons also have known edge cutoffs.

## Earlier six comparisons retained

All three wedding fits have red-channel highlight clipping on forehead/nose and,
in1398_2, cheeks. Four-control high-clipped channel totals119/100/325; most are
red (114/100/318). Corresponding source and target values vary within some
flattened endpoint patches. The loss is not just an invisible raw overflow:
clipping removes source channel distinctions and fails to reproduce some target
channel variation. Other channels can still carry luminance/texture, so this
does not mean an entire highlight becomes featureless white.

1487_0/1487_1,330_0 and1117_0 have no raw clipping in the saved regions; this
alone does not prove faithful texture or colour. 1487_2 has25low-clipped channel
samples around eyes/hair/face edge, no high clipping. The two earlier indoor
colour-error regressions are preserved regardless of clipping status.

All14boards visually inspected by the assistant. No new user judgments,
pixelwise skin truth, calibrated-display appraisal or professional opinions.
Low360pdetail limits texture judgments; nearest-neighbour enlargement adds no
detail. Makeup, hair, eyes and eyewear remain in the diagnostic regions. Hard
boundaries/uncorrected neck are temporary diagnostic rendering, not adopted
whole-face+neck continuity/blending results. No new correct-looking images were
created by this check: overlays explain existing fits only.

## Verification

28 reconstructed3/4control outputs match saved results exactly, and all28raw
clipping totals match parent counts. Parent manifests unchanged. All14region
counts, per-channel totals, low+high partition and overlay links verified.
Three hand-computed focused tests pass/0.48s: single-channel versusRGBwhite,
mask/target-endpoint handling, and collapsed adjacent variation. No full-suite
run, new inference or accuracy validation claimed. Artifact hashes and
machine-readable evidence in the output folder.

## Decision and next implication

Fourth contrast stays experimental. The better colour/tonal approximation is
real on these frozen regions, but detail preservation and region validity do
not pass a blanket acceptance claim. Before proposing adoption, address local
highlight/shadow loss and establish valid facial support for a justified future
comparison. Merely lowering contrast or selecting only good photos would not
answer both problems. No new repair, objective/bounds sweep, region redraw,
refit, batch or user-review task is activated by this diagnosis.

Original gamma/red/blue output design, ITA + calibrated MST + facial statistics
and decision-tree family remain retained. Reliable MST mapping, a justified
training cohort and automatic prediction remain unfinished. Demos/Android,
reserved roles, submitted paper and immutable delivery snapshots unchanged.
No panel approval or method adoption inferred.
