# Five-control saved-route diagnosis: transfer failure, no qualified repair

15 November2026. Completed the user-authorized four-case diagnosis under
`five-control-saved-route-diagnosis-protocol-2026-11-15.md`. Saved metadata only;
no image/NPZ/mask reads, fits, new features, candidate predictions, renders or
ratings. The failed prediction recipe remains NOT_ADVANCED/closed/unadopted.

## Answer1: the large wrong-family errors are held-source routing failures

Across all11saved folds, none of the220fitting identity/colour occurrences
lands in a leaf containing exposure examples. In contrast, three held colour
cases and one held identity case reach exposure-only fitting leaves. Those are
exactly the four selected large failures. Their controls equal the correct
arithmetic means of the wrong family's fitting targets, with the held source
excluded. This is not a signed-offset/export/renderer arithmetic bug.

Fitting is not perfect. All110fitting identity occurrences share leaves with
colour-only rows;93/110fitting colour occurrences share leaves with identities.
This already produces nonneutral controls through target averaging. The modest
fitting control error and the much larger held error are distinct:

| Role | Fitting occurrences | Mean fitting control SSE | Held cases | Mean held control SSE |
| --- | ---: | ---: | ---: | ---: |
| Identity |110|.002236|11|.431251|
| Colour-only |110|.004678|11|.106857|

These are squared differences in the fixed five control coordinates, not image
errors or percentages of quality. Control targets can be correlated/ill-conditioned.
The110counts repeat10fitting-source appearances across11folds, not110independent
photos. No fitting images were rendered, so no fitting RGB/DE claim follows.

## Answer2: exact branches sending the selected cases into exposure subtrees

The first existing branch that excludes all fitting identity/colour rows is:

| Held case | Existing feature | Saved threshold | Held value | Chosen subtree's fitting roles |
| --- | --- | ---: | ---: | --- |
|29617colour-only|Full-crop fraction with any channel255|.06851959|.07832336|2over +2combined-over|
|48879colour-only|Facial green median|186|187|8over +8combined-over|
|49131colour-only|Joint log-colour bin u15/v15|.0000196631|.0000770939|10under +10combined-under|
|48879identity|Facial green median|186|187|8over +8combined-over|

Further existing splits narrow these to the previously recorded destination
leaves containing2,3,6and1fitting exposure examples, respectively. No leaf or
threshold was changed to rescue them.

29617's saved identity has full-crop endpoint fraction.05952454 and stays on
the other side of the same threshold, reaching an identity/colour leaf. The
colour-only edit raises this global endpoint descriptor to.07832336 without
being an exposure-only operation. That descriptor is not a unique indicator of
the required correction family. No pixel localization to skin/background was
attempted here.

48879has green median187for both identity and colour-only, consistent with the
colour operator leaving green unchanged. In its fitting fold, identity/colour
green medians range96–173, while exposure examples span13–245. Thus a valid
unchanged held appearance enters the exposure side at the root. Absolute green
brightness is not established as reliable evidence that a photograph needs
darkening. This is not a supplied complexion label or a fairness measurement.

49131's identity has0mass in u15/v15, while its colour-only version has the
small nonzero mass.0000770939. All20fitting identity/colour rows have0at that
coordinate. This existing histogram branch treats the held cast as an under-
exposure pattern. The saved clean/cast feature difference diagnoses this route;
the clean reference vector is unavailable to real single-photo inference and
must not become an input cue.

For every first-exclusion branch the held value remains inside the feature's
overall range among fitting rows reaching that node, even though it is outside
their identity/colour range. The exposure and identity/colour intervals overlap.
A simple rejection of values outside the overall single-coordinate training
range would therefore not detect these four cases at these branches. This does
not establish multivariate in-distribution status or prove no other cue can work.

## Answer3: no existing cue or new training recipe is qualified by this diagnosis

The records show why the existing thresholds fail on these sources. They do
not validate a replacement cue. The examples were selected after their failure;
moving the saturation/green/bin thresholds, adding a source exception or ranking
unused features on them would be post-hoc fitting, not reliable new evidence.
No such stump, guard, feature sweep or corrective prediction was executed.

History checked: prior gap/oblique route diagnoses already found acceptable or
colour inputs reaching pure exposure leaves; bright-scene features, normalized/
deeper objectives, split heads, image-loss action trees and relative recovery
losses have completed results with preservation/colour limits. These cannot be
renamed new repairs merely because the current operator has five outputs.
Neither control averaging nor source-transfer difficulty alone establishes
that one of those closed interventions will now work.

The explicit outcome is **no supported next training repair selected**. Preserve
the five-control operator's reference-aware capacity gains separately from this
failed prediction recipe. A future proposal must introduce justified input-
available correction-family information or a distinct transfer-learning rationale
and address clean preservation; absolute brightness alone, extra renderer
freedom or stronger synthetic errors have not supplied that evidence here.
No new feature/data/annotation queue follows automatically.

This matters for the thesis motivation: do not equate dark recorded skin with
underexposure needing brightening, or high brightness with an unwanted exposure.
The sources have no eligible supplied tone labels, so this is not a measured
darker-skin bias/harm result. It also does not license a negative-results-only
thesis fallback or abandon the user's working-model objective.

## Verification and preserved scope

`scripts/diagnose_five_control_saved_routes.py` checks all660saved fitting
routes and66saved held routes using scalar float32/<=arithmetic against their
existing native leaves/controls, and reconstructs reached fitting leaf means.
It verifies hashes of explicitly accessed JSON records only; the image/NPZ
paths named inside the prior manifest are not opened or rehashed.

Five focused helper tests passed in.19seconds. They cover first family exclusion,
mixed leaves, split ties, value-range descriptions, repeated-control-error
accounting and cycle rejection. No full-suite claim or model test was repeated.

`scripts/verify_five_control_route_diagnosis.py` independently reconstructs node
membership from saved native leaf IDs and parent ancestry, without the diagnostic
feature-route walker. It verifies32existing split records across four selected
paths and four paired context records, corresponding to six unique source-role
routes from three sources. It also checks fitting/held control-error summaries
and hashes. No new splits, threshold optimization or candidate inference.

Evidence: `outputs/five_control_saved_route_diagnosis_v1/` contains full paths,
node/leaf compositions and fitting ranges, role errors, mixed-leaf occurrences,
route/mean replay proof and independent ancestry verification. Original metadata
remains hash-identical. Human identity acceptability remains unassessed; saved
ratings are unchanged and no numeric differences are recoded as judgments.

All earlier artifacts/closures/ratings and approved59807manual/ear support
preserved.0pixel/NPZ reads,0new features/fits/predictions/renders/ratings,
0locked final24/older contents/manifests, runtime/Android or manuscript edits.
Model unfinished; paper paused; darker-skin priority and November25 retained.
