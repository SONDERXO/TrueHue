# FaceOcc qualitative evaluation: actual review imported

1November2026. User reported the four-case review complete. Located actual export
outputs/faceocc_four_review_v1/face.json; script379 verified schema, exact four
IDs, manifest and displayed board hashes, then preserved the original export and
judgments under outputs/faceocc_four_review_import_v1/. No notes were supplied;
none were invented. Script380 binds these judgments to the full24attempt record
and separate assistant observations in outputs/faceocc_light_conclusion_v1/.

| Fixed human-review image | Previous unwanted pixels? | With FaceOcc unwanted pixels? | Useful skin lost? | User preference |
|---|---|---|---|---|
| 39083, facial-hair challenge | No obvious problem | No obvious problem | No | Similar |
| 77101, forehead/hairline challenge | No obvious problem | No obvious problem | No | Similar |
| 29321, mouth/shadow challenge | Yes | No obvious problem | No | FaceOcc |
| 74882, glasses/object challenge | Yes | No obvious problem | No | FaceOcc |

Exact stored values for these questions are no/yes and similar/faceocc. The
review UI's no option means "No obvious problem", not proof of no non-skin pixels.
TwoFaceOccpreferences/twosimilar, no previous-method preferences. User reported
no useful-skin loss in all four. This is not a50%general improvement rate or
100%skin preservation claim. Four known exposed challenges were deliberately
fixed before predictions; this is qualitative development feedback.

## Combined conclusion

**FaceOcc is supported as a promising measurement-veto candidate on these
reviewed examples, but the cycle does not justify general reliable-skin or
runtime adoption claims.** The user judgments support the reduced mouth/shadow
and glasses/object concern in29321/74882 while showing no apparent disadvantage
in the other two reviewed examples. Do not claim all glasses or beards excluded.

The fullcycle remains24attempts/18paired outputs/six retained failures, without
new candidate technical failures. Assistant inspected all18pairs and recorded
potential cheek-skin loss in7316outside the human subset, unresolved stubble/
beard and glasses-boundary ambiguity, and some hairline/profile differences.
Those concerns are not overruled by four human judgments. Human and assistant
observations remain separately attributable, not pooled as equivalent ratings.

Earlier source rejections, contamination findings and mask approvals remain
file/scope-bound. For example, prior39083facial-hair concern and the new
"similar/no obvious problem" judgment coexist; no historical annotation or
eligibility was silently overwritten. This review never established source
lighting, true colour, correction-model quality or training admission.

No dense patch annotations are assumed completed. The earlier23-image polygon
task was abandoned as excessive manual work; its files/browser keys remain.
No full-mask precision/recall/IoU, statistically established superiority,
independent-subject validation, ten-tone coverage or Android runtime evidence.
No paired MST-category evaluation or new calibration was run. The previous
four-point diagnostic and this new qualitative cycle are distinct evidence.

## Stop and retain the evidence

This authorised qualitative cycle is complete. Retain FaceOcc checkpoint,
fixed preprocessing, outputs and evidence for a future method decision. Do not
automatically adopt it, recalibrate, fit a clean-only subset, tune thresholds,
swap models, or start another small review. Any next development transition
must explicitly state the limited intended claim and address the observed
skin-loss/occlusion risks before processing/fitting. Beard-specific model work
remains held. Current preferred measurement, correction support/rendering and
Python/Android correction demos stay unchanged.

Panel-letter evidence can state: "In a four-case qualitative challenge review,
the user preferred the FaceOcc-assisted measurement on two cases and rated two
as similar, reporting no obvious useful-skin loss in those four. A broader
assistant inspection identified remaining limitations, so the component remains
experimental rather than independently validated or adopted."

This is factual candidate-evaluation wording, not a submitted letter or approval.
The proposed change is an additional learned measurement veto plus documented
MediaPipe alignment adaptation, not a new correction model or a replacement
for ITA + calibrated MST + facial statistics → decision-tree gamma/red/blue.

Verification: exact export/manifest/board bindings passed; script380 checked
four membership and all24full-cycle dispositions and saved input hashes. No
new model inference, mask modification or fitting. No pytest rerun for actual
data import and summary; prior importer tests passed. Last broader result remains
905passed/13.40s excluding desktop GUI(Tcl/Tk unavailable), not a full-suite pass.
