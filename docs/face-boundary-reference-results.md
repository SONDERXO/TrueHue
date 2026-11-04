# Completed facial-boundary references and saved-mask audit

26 October 2026. The reviewer confirmed that 40048 was finished and its unchecked completion box was an oversight. The exact statement and export hash are saved in [completion confirmation](../data/manifests/face_boundary_reference_v1/completion_confirmation.json). The original draft bytes, coordinates, notes and flags are archived unchanged. Completion is supported by the original two checked frames plus this later confirmation; no replacement browser export is claimed.

## Reference preparation

`scripts/90_score_face_boundary_references.py` checks the exact previously validated export hash and manifest, rechecks source/image hashes and dimensions, then rasterizes without resizing. Visual inspection of all three original/polygon overlays found broadly plausible face contours and intended eye/brow/mouth and paint exclusions, with coarse edges and blurred paint boundaries. No polygons were edited or inferred. This is a diagnostic reference set, not an accuracy-certified annotation set.

Floating polygon vertices are retained. A pixel is labeled by testing its integer center, including a center exactly on a polygon boundary. Priority is exclusion over uncertain over skin; other pixels remain unlabeled. Stored PNG values are 0 unlabeled, 1 skin, 2 uncertain, 3 excluded. A separate one-pixel interior sensitivity check erodes each scored class with a 3x3 kernel; it does not invent human uncertainty labels.

| Image | Native frame | Skin pixels | Excluded pixels | Unlabeled pixels |
| --- | --- | ---: | ---: | ---: |
| 40048 | 256x256 | 29,401 | 3,458 | 32,677 |
| 16798 | 224x224 | 25,079 | 9,190 | 15,907 |
| 60162 | 256x256 | 33,060 | 3,739 | 28,737 |

No uncertain polygons were supplied. This does not imply all edges are certain. Unmarked neck remains unlabeled and does not revoke the requested visible-neck correction requirement.

## Existing-mask findings

All 23 saved-mask comparisons were inspected in three contact sheets. Green shows selected labeled skin, blue missed labeled skin, and red selected labeled exclusions; original pixels are shown alongside. [Local review gallery](../outputs/face_boundary_reference_v1/review.html) and [full metrics/provenance](../outputs/face_boundary_reference_v1/summary.json) preserve all comparisons.

| Saved mask | Labeled-skin coverage | Selected exclusion pixels | Exclusion pixels after one-pixel interior sensitivity |
| --- | ---: | ---: | ---: |
| 40048 source generation | 97.01% | 805 | 464 |
| 40048 dark correction | 97.34% | 806 | 453 |
| 40048 unchanged correction | 97.19% | 805 | 464 |
| 40048 mild correction | 96.84% | 847 | 508 |
| 60162 source generation | 98.78% | 1,059 | 522 |
| 60162 color-shift correction | 98.75% | 1,025 | 500 |
| 16798 clean older correction policy | 91.76% | 2,152 | 1,265 |
| 16798 shifted older correction policy | 91.71% | 1,811 | 983 |

40048's previously identified cheek probe `(202, 124)` is inside labeled skin and absent from generation, all three measurement/correction masks, and all three saved padded candidates. Padded candidates have exactly the same labeled-skin coverage and exclusion overlap as their corresponding originals; added pixels outside labeled regions cannot establish recovered facial skin. The padding experiment therefore does not solve this annotated cheek loss.

The eye/eyebrow exclusion disagreements are substantial and remain after the one-pixel sensitivity check. Visual inspection shows selected eye-area regions and eyebrow margins, with some missed skin around feature exclusions. High facial-skin coverage alone does not establish usable measurement or correction quality. Source-generation contamination also matters: a correction-only change would leave the synthetic pair construction inconsistent.

60162 color-shift measurement covers 90.09% of labeled skin while its correction covers 98.75%. Measurement may use a representative subset; this difference alone is not a measurement rejection. Its exclusion overlap must still be investigated. All five saved variants are reported, including previously rejected/clipped/held cases; this audit grants no new eligibility.

16798 retains native 224 coordinates. Its two scored correction masks come from the **older pre-semantic-veto** additions-only experiment; visible red disagreement includes painted regions and eye/brow margins. These numbers cannot be attributed to the newer three-stage veto or used to claim that veto's paint safety. The prior padded experiment's unavailable paint probes remain unavailable; no replacement or fallback success is inferred.

## Decision and next experiment

Accept the three frames as completed development reference annotations, with the above limitations. Preserve all historical review decisions, technical holds, model/data policies and proposed fold status. This step creates reference rasters only; no pipeline masks, synthetic inputs, features, training tables, model or runtime rules changed.

Next, predeclare a separate anatomical-exclusion and contour experiment across generation, measurement and correction. Investigate landmark/exclusion alignment at the labeled eye/brow regions and cheek contour before widening support. Use these fixed references as development diagnostics, retain existing 32-pair and hair/paint regression checks, and obtain assessable native-frame evidence for the newer paint policy. Do not tune merely to the single cheek point or claim final accuracy from these three exposed sources. Recheck all changed stages and any regenerated inputs before considering fitting.

## Thesis distinctions and verification

Human boundary annotation is an additional development diagnostic, not a new required application-user step. Mixed 224/256 development frames are not uniform final preprocessing. Learned semantic masking and additional input features remain experimental departures from the proposed rule-based method. MST mapping, final data/split/evaluation roles, neck support, expert review and Android implementation remain unfinished; no approved proposal amendment is implied.

Every raster pixel was independently replayed using OpenCV `pointPolygonTest`, matching the vectorized even/odd implementation. Tracked source images, original export, prior point labels, reconciled user decisions, exposure ledger, saved masks and frozen model bytes were unchanged. Three new tests check fractional coordinates/boundaries, label priority and unknown-region scoring. Test-run outcome is recorded in the experiment log.
