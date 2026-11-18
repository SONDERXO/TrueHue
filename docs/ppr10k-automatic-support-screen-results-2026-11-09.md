# Fixed eight-pair PPR10K automatic-support result — 9 November 2026

## Decision

The approved screen is complete. **Four of eight sources provide automatic
measurement and face/visible-neck support; four fail the unchanged anchor-face
detector.** All eight are retained. No source is admitted for correction training,
no four-success subset is fitted, and no detector/parser/crop rescue is started.

There is also useful positive evidence: recovering the previously missing
unchanged-input baseline shows the historical target-aware three-control fits
improve all eight pairs. This qualifies the earlier saved-readiness uncertainty
about that baseline; it does not make the fits automatic predictions.

## Exact execution and preflight

Scripts 703–704 use only the eight sources and editor-A targets frozen in the
old publisher-training sample. All sixteen TIFFs match their inherited original
hashes, dimensions, sample types and ICC hashes; their profiles identify sRGB.
Preflight completes before inference. Original files remain unchanged. RGB16
source/65535 and RGB8 target/255 remain the numeric originals; source RGB8 for
inference is round(source/257), not a new precision-preserving reference.

The existing research native-face 1.5-context bridge, threshold .85, original
appearance parser, anatomical/nostril exclusions, unchanged measurement guard,
pinned FaceOcc and protected preview are reused. No desktop correction model
or MST lookup is run. Glasses stay `uncertain`; identity parameters only. Model,
code, protocol and source bindings are saved before execution. Existing isolated
FaceOcc environment is reused without installation/download.

One preprocessing invocation per source made twelve YuNet detector forwards
(eight anchors plus four normalized-parent detections), four dense-parser
forwards, four landmark helper invocations and four FaceOcc forwards. No margin
fallback was needed on those four successful landmark calls. Landmark counts
describe helper invocations, not MediaPipe internal detector/mesh subnetworks.
Targets are never passed through automatic inference. Zero learned fits.

## All eight outcomes

Native pixel counts describe selected locations, not independent skin samples,
an accuracy score or a new minimum-size rule.

| Pair | Automatic outcome | Selected native measurement pixels | Native correction support pixels |
| --- | --- | ---: | ---: |
| 787_0 | Available | 3824 | 7282 |
| 330_0 | No anchor face detected | — | — |
| 767_0 | Available | 4426 | 7876 |
| 1117_0 | Available | 1167 | 1316 |
| 1188_0 | No anchor face detected | — | — |
| 990_0 | Available | 880 | 1266 |
| 904_0 | No anchor face detected | — | — |
| 455_0 | No anchor face detected | — | — |

All four failures have zero detected anchors, not multiple-face ambiguity or
FaceOcc failure. No manual polygons substitute for failed automatic support.
The normalized guard remains unchanged; 990_0's smaller native count is not a
contradiction because normalization and native sampling are different contracts.
This eight-photo selection is not a dataset-wide detection success estimate.

## Visual review

Viewed all eight native-size full-frame source/target/contour boards, all eight
selected-face detail boards, and all four available normalized mask boards.
The other four have retained failure reports and pair boards, not invented masks.

The four successful detected faces correspond visually to the historical selected
faces. No obvious large geometric displacement is apparent in the eight paired
views or source-contour overlays. This is qualitative correspondence screening,
not measured subpixel registration; contrast changes affect edge visibility.
No alignment/warp or image-selection rule was tuned.

- 787_0: broad lower-face measurement and face/neck correction. Fringe and upper
  forehead remain excluded; hat/hair/collar transitions are approximate.
- 767_0: broad central-face measurement, fragmented forehead between bangs;
  correction extends onto the neck. The nearby hand and neck/chest boundary need
  finer assessment; no definite dense material correctness is asserted.
- 1117_0: measurement and correction follow the small profile face, with a limited
  neck region. Normalized views enlarge small native detail; hair/edge certainty
  remains limited.
- 990_0: central-face measurement and neck correction are available but small at
  native resolution; jaw/neck transitions and hat/hair boundaries remain uncertain.

The four missed faces are visibly present in the paired images. Small/profile
faces and scene framing occur among them, but this screen does not isolate why
each detector failed; 455_0 is not declared impossible or unsuitable. No dense
skin references, expert acceptance or per-MST coverage are created by this review.

## Recovered unchanged-input baseline

Using the original hash-verified saved numeric NPZ arrays and their original
manual-polygon checker blocks, recomputed unchanged-input error with the old
metric. Selected-pixel Lab/DE calculations independently agree, and replayed
three-control output metrics match the historical values. No parameter fitting,
support change or extra correction candidate is introduced.

| Pair | Unchanged DE | Historical three-control DE |
| --- | ---: | ---: |
| 787_0 | 15.5172 | 6.2182 |
| 330_0 | 5.8500 | 2.7081 |
| 767_0 | 29.1030 | 8.4864 |
| 1117_0 | 12.1412 | 6.7349 |
| 1188_0 | 10.3736 | 5.9781 |
| 990_0 | 8.8082 | 2.6029 |
| 904_0 | 11.7592 | 5.5756 |
| 455_0 | 5.5796 | 1.4089 |
| Equal-image mean | **12.3915** | **4.9641** |

All eight improve, including the four automatic-support failures. That is possible
because the historical fits use target-aware manual diagnostic polygons. These
results show useful operator approximation on the fixed photographs, not learned
correction quality or eight training admissions. Residual mismatch, clipping,
makeup/mixed features and registration uncertainty remain. No new acceptable-error
threshold is chosen and the fourth contrast control remains unadopted.

## Verification, practical conclusion and stop

Independent checks reproduce all four measurement masks from cached artifacts,
explicit nearest-neighbour native mask projection, native alpha/protection
projection and identity rendering/protected-pixel invariants. All eight outcomes,
baseline metrics, original bindings and generated artifact hashes pass. Reusing
the existing renderer for identity is not an independent dense-mask validator.

PPR10K is a useful existing photographic-reference lead; it has not become a ready
automatic training cohort. The first concrete missing capability on these eight
is source-face availability, before beard-mask training or another correction
tree. Four successes cannot establish a reliable full workflow or adequate tone
coverage. A future acquisition/preprocessing decision would need its own bounded
design review; this failed-coverage screen does not authorise a detector-threshold,
new-crop, alternate-parser or replacement-photo sweep.

Stop the fixed screen here. Keep all existing correction gates, face/visible-neck
scope, ITA/MST requirements and final-evaluation separation. No training, automatic
model promotion, runtime update, dataset acquisition, external contact, upload,
commit or push occurred. The final eight-group/24-photo holdout remains byte-unread.

Private evidence: `outputs/ppr10k_automatic_support_v1` contains the frozen plan,
per-source processing and visual boards, original results, artifact hashes,
independent verification/baselines and a hash-bound visual-review receipt.

- [Executed protocol](ppr10k-automatic-support-screen-protocol-2026-11-09.md)
- [Prior saved readiness](ppr10k-saved-readiness-results-2026-11-09.md)
- [Historical oracle comparison](ppr10k-new-group-comparison-results-2026-11-02.md)
