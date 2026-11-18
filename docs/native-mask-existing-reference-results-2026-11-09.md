# Native measurement against existing human references — 9 November 2026

## Outcome

The source/support review is complete using the user's existing annotations.
**The native path is not established as a measurement improvement.** On the same
three usable reviewed photos it selects36/79skin points versus38/79before,
621/1660user-patch pixels versus653/1660, and1/55unwanted points versus3/55.
The lower unwanted total conceals **one new hair/beard inclusion** and three
removed inclusions. No new skin points are gained; two are lost.

This supplies direct reference evidence beyond visual inspection. It does not
qualify calibration or a correction-tree fit. Do not lower the protection criterion,
train on only favourable subjects, request the completed annotations again or
run another parser/crop/guard rescue. The decision tree and automatic workflow
remain binding; the final holdout remains byte-unread.

## Reusing the correct references

Scripts717–718 join all six completed point/patch reviews to the current30photos
by original full-source JPEG hashes. Reference images are small native crops,
whose PNG hashes must not be mistaken for source JPEG hashes. Each crop's pixels
exactly match the original decoded source slice at its saved bounds. Coordinates
map by the original crop offset, without resizing or warping.

All238actual points (129skin/109unwanted),36polygons and3156union patch pixels are
preserved. Original exports and saved raster masks retain their hashes. No point,
polygon, uncertain status or reviewer decision is invented. Some user patches
include neck and uncertain material boundaries, so patch coverage is not face-only
recall. Point/patch disagreements are retained explicitly; no label is removed
to improve the outcome. The new hair/beard inclusion is outside the marked patches.

The comparator is the old aligned **clean-input** path, not the earlier historical
mask import or ResNet34/SegFace candidates. The candidate is the already completed
native-readiness path. No new mask inference or source processing is required.

## Fixed paired usable comparison

| Quantity, same three usable cases | Old aligned | Native |
| --- | ---: | ---: |
| User skin points selected | 38/79 | 36/79 |
| User unwanted points selected | 3/55 | 1/55 |
| User patch pixels selected | 653/1660 | 621/1660 |
| Usable reviewed cases | 3/6 | 3/6 |

Those three cases are review02(case21),review04(case30),review05(case16).
review01(case04)has a final diagnostic mask but fails the measurement guard;
review03(case25)and review06(case29)are unavailable under the native path. Failure
is not an all-negative correct mask or learned preservation. On all six reviews,
50skin and54unwanted points lack a usable native measurement and remain in the
attempt accounting.

Diagnostic masks exist on five old photos and four native photos, including
guard failures. Diagnostic point totals are39/113skin and3/94unwanted for old,
36/96skin and1/77unwanted for native. Their denominators differ and must not be
presented as a matched precision/recall comparison. Diagnostic patch denominators
also differ (2551old,2083native). The paired usable table is the matched comparison.

## Exact transitions and cached stage trace

Independent point-key joins retain all238unique annotation keys. Among paired
usable cases: skin gains0/losses2; unwanted gains1/losses3. The new unwanted mark
is review02native-crop(33,38), original-full-image(123,134), labelled
`hair_or_beard`. Its annotation is unchanged.

At the respective normalized mask samples, both old and native parsers assign
class1(skin), and both parent masks select the location. The old final measurement
rejects it; the native final measurement retains it. The original crop bounds
change from[90,96,142,148]to[92,96,143,147], with different normalized sample cells.
This traces where the membership changes after parent selection. It does not
isolate a unique causal effect of FaceOcc, alignment, resampling or physical
material recognition, nor justify a point-specific rule or veto removal.

## Labelled coverage is a separate issue

All30photos from10publisher subjects already have preserved source MST scores.
The gap is not missing supplied score values. Actual human skin-reference reviews
cover six photos from five subjects;24photos and five subjects have no such review
in these records. Only three of the technically available photos have an existing
human reference, and no subject has three usable referenced conditions.

| Descriptive supplied-score interval | Photos with references | Technically available referenced photos |
| --- | ---: | ---: |
| [1,3) | 1 | 0 |
| [3,5) | 0 | 0 |
| [5,7) | 1 | 1 |
| [7,9) | 1 | 1 |
| [9,10] | 3 | 1 |

Every interval has six attempted photos in the30case preparation. These are
descriptive decimal-score strata, not official integer MST category counts.
Absence of a reference does not prove an image is invalid; presence of a few
points does not establish dense correctness. The deliberately selected exposed
six-case sample cannot certify all30measurements or population coverage.

## Verification and review

All six comparisons were viewed. Cropped-mask and full-frame point lookups agree;
full-frame patch placement and cropped patch overlap agree. Actual polygon unions
match the old saved rasters pixel-for-pixel. Independent point-key transitions,
source-score/reference coverage and stage samples reconcile. All bound sources,
exports, masks and metadata remain unchanged. Zero model forwards or fits.

Private evidence: `outputs/native_existing_skin_reference_audit_v1`, with original
coordinate joins, all476model/point records (238points ×2paths), paired totals,
coverage/transitions, stage trace, six boards and a hash-bound review receipt.
No photos, source identities or annotations are uploaded or published.

## Practical next boundary

The existing reference validation now confirms the measurement trade-off, rather
than merely assuming sparse masks are wrong or assuming a pixel-guard pass is
enough. A matching MST fit is not justified by changing a contract identifier or
discarding the failed cases. Credible measurement evidence remains unresolved.

The next step needs a **substantive source/support design**, with a stated new
source of information or eligible labelled evidence and prospective validation.
Do not repeat the same30photos, six reviews, source inventory or small crop/parser
variants as though they were a solution. Additional human marks alone would not
repair the masks; no repeat or new annotation task is imposed here. No source
expansion, masking intervention or next model experiment is selected by this audit.

No calibration/correction fit, admission, architecture/runtime change, acquisition,
contact, upload, commit or push. All prior artifacts remain preserved. The final
eight-group/24-photo holdout stays byte-unread.

- [Frozen reference audit](native-mask-existing-reference-protocol-2026-11-09.md)
- [Native labelled measurement preparation](native-mst-measurement-readiness-results-2026-11-09.md)
- [Original completed point review](stellenbosch-reference-point-results-2026-11-06.md)
- [Original completed patch review](skin-patch-measurement-results-2026-11-06.md)
