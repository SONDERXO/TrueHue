# New PPR10K groups: contrast improves approximation in eight further photos

2 November2026. User authorised the recommended fixed new-sample comparison.
**All eight new-photo check-block colour errors improve with four controls.**
Equal-image mean relative CIEDE2000 falls4.964 ->2.552 (48.6%). Clipping increases
in6/8; this is evidence for a promising experimental operator, not automatic
correction, an admitted training cohort or adopted fourth output.

Gallery: `outputs/ppr10k_new_group_comparison_v1/review.html`.
Scripts395(selection/acquisition),396(frozen comparison). Detailed metrics,
solver outcomes, clipping, hashes and exposure ledger are in the output folder.

## Selection and processing

Before any new pixels, ranked previously uninspected publisher-training group
IDs (<1356) by SHA256 of `TrueHue-PPR10K-newgroups-v1:` plus group ID. Took the
first8 groups, first numeric frame per group; excluded the earlier groups1398/1487.
Fixed frames:787_0,330_0,767_0,1117_0,1188_0,990_0,904_0,455_0. Editor A unchanged.
No conditioning on face attractiveness, successful processing, lighting or skin
tone. All8 retained, no failures/replacements or new user review task.

Public official archive byte-range extraction used the same source/editor-A
archive IDs and pinned documentation as the earlier inspection. Acquisition
read9,526,674 source and4,092,415 target bytes, including central-directory reads.
Each selected member's ZIP CRC checked; original16TIFF hashes recorded. Every
actual TIFF has embedded sRGB, sourceRGB16 and targetRGB8, matched pair dimensions.
Numeric fitting uses original source/65535 and target/255, not preview PNGs.
Dataset noncommercial research terms remain; local ignored files/derivatives
not uploaded. No full archives, models or new dependencies downloaded; no account,
agreement form or author message. Prior four artifact manifests remain unchanged.

Group IDs are not verified distinct people. No identity crosswalk, cross-source
duplicate resolution or tone labels are available. Visible scenes differ, but
this does not certify person independence or representative tone coverage.
All8 are now development-exposed; never treat these exact photos as unseen final
evaluation. Existing TrueHue reserved allocations remain unchanged.

## Frozen comparison

Inspected sources only, then saved `source_regions.json` before viewing fitted
outputs or expert targets. One approximate face per image: largest visible
face-outline area, ties image-left. In1188_0 this selects the man's small profile;
in904_0 the image-right man, retaining glasses/hair and difficult pose. These are
assistant polygons, not skin/anatomical truth or user approvals. They can cut
off face edges or include hair/eyes/makeup. No detector/parser/FaceOcc passes.

`fit_protocol.json` predates all fits. Both existing operators, bounds, objective,
single identity start, tolerances and8px checker fit/check split unchanged:
three-control gain*x**(1/gamma), versus fourth contrast about fixed encoded0.5
between gamma and gains. Contrast bounds[0.5,2], other controls[0.25,4]. One
squared-sRGB fit/operator/photo, maximum2000 evaluations, tolerance1e-12. No
objective/midpoint/bounds/start sweep, model selection, image replacement or
threshold tuning. All16 fits converged with no active bounds; global optimality
not proved. All16 target-aware parameter fits recorded; no MST/tree training.

## All eight outcomes

Check-block mean relative CIEDE2000, lower is closer to editor A. No perceptual
acceptability threshold declared. Errors are image-appearance differences,
not intrinsic skin colour or clinical/skin-measurement accuracy.

|Frame|Source conditions|Three|Four|Contrast|Clipped face channel samples, three -> four|
|---|---|---:|---:|---:|---:|
|787_0|Outdoor sun/hat shade, smile, fringe/lipstick|6.218|2.684|1.266|88 ->449 /15342|
|330_0|Small downward/profile face on bright boat, headpiece/net|2.708|2.154|0.966|0 ->0 /3576|
|767_0|Indoor bridal portrait, fringe/makeup, darker face|8.486|2.191|1.553|0 ->208 /17052|
|1117_0|Small spotlit face against dark studio, bright highlights/makeup|6.735|2.527|0.826|0 ->0 /3816|
|1188_0|Outdoor couple, small downward male profile/facial hair|5.978|2.443|1.304|55 ->177 /2259|
|990_0|Indoor seated portrait, hat/hair and uneven light|2.603|2.255|1.050|4 ->9 /2832|
|904_0|Outdoor family, glasses/facial hair, hard light/profile|5.576|4.871|1.226|5 ->421 /5148|
|455_0|Studio portrait, hair rollers and pronounced makeup|1.409|1.294|1.028|0 ->41 /5772|

Clipping is counted from raw out-of-range channel samples before final clip,
not merely output endpoints; denominator is all selected-face channel samples.
904_0 is particularly concerning:421/5148 (8.18%) clipped samples and relatively
high residual error despite improvement. Do not hide this behind8/8 improvement.
Some clipping may match intended dark/bright targets, but lost detail is not
therefore ruled out. Contrast can decrease (330/1117), not just increase.

Assistant visually inspected all8 source/three/four/editor crop boards. Reduced
pink/flatness is most obvious in787/767, and the strong greenish cast from the
three-control spotlit fit1117 is reduced. 1188 improves but has tiny detail;
330/990/455 gains are modest. 904 remains an imperfect, strongly shaded match
with its eyewear, profile and increased clipping. Expert colour/contrast/local
differences remain in all cases; no all-image aesthetic approval claimed.

Sharp polygon boundaries, uncorrected neck/background and forehead/face-edge
cutoffs are retained temporary diagnostic rendering limitations. Crops enlarge
original low-resolution pixels with nearest-neighbour, implying no recovered
detail. Adopted whole-face+neck continuity/blending was not tested or changed.
No warp or verified pixelwise registration: misalignment/mixed features/makeup
can contribute to residuals, which cannot all be assigned to operator capacity.

## Verification and decision

16 independent explicit-formula replays exactly match stored outputs, metrics
and raw clipping counts. Masks partition exactly; outside-region float pixels
unchanged. Sample-before-download and regions/protocol-before-fit checked;
all16 TIFF profiles/hashes and all old artifact-manifest hashes pass.
17focused tests pass/1.68s (contrast diagnostic and existing synthetic-transform
tests); no full-suite run claimed. All8 visual comparisons inspected.

This new-group check supports contrast beyond the initial wedding examples.
It does not erase the two earlier indoor regressions, establish independent
person validation, demonstrate MST coverage or solve automatic parameter
prediction. Each expert target supplied the per-photo fit; same-photo spatial
check blocks are not unseen-photo generalisation. No statistical significance
or representative-population claim follows from8selected photographs.

Bounded comparison complete. Keep fourth contrast control as a promising
experimental candidate; no adopted output-schema/runtime/thesis change. No
automatic further batch, same-photo tuning, clean-only fit, model training,
calibration or reference admission. ITA + calibrated MST + facial statistics
and decision-tree family remain retained, with reliable MST/automatic correction
unfinished. Existing Python/Android demos, submitted paper, panel approval and
immutable delivery snapshots unchanged. DAST/STW replies still pending by
user report; no inbox monitoring or external contact.
