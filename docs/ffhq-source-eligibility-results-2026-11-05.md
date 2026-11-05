# FFHQ eligibility: references usable, full-pipeline admission still separate

5November2026. The authorised review is complete. The assistant inspected all
twelve original1024px images under the
[pre-recorded protocol](ffhq-source-eligibility-protocol-2026-11-05.md), adding
full-resolution reference observations to the existing mask/variant evidence.
**All12 have judgeable visible-face pixels usable as photographic-restoration
references within their recorded limitations.** This passes the reference screen;
it does not certify ideal light, intrinsic colour, exact masks or training readiness.

[Open the per-source decisions](../outputs/ffhq_source_eligibility_v1/review.html).
Machine-readable [source ledger](../outputs/ffhq_source_eligibility_v1/eligibility.json),
[12-row CSV](../outputs/ffhq_source_eligibility_v1/sources.csv) and
[168-descendant CSV](../outputs/ffhq_source_eligibility_v1/descendants.csv) are saved.

## Separate decisions, rather than blanket approval/rejection

| Gate | Decision |
|---|---|
| Visible-face photographic reference | All12 usable with individual limits; assistant full-resolution screen |
| Exact correction support for training | Not automatically admitted; existing object/neck/boundary concerns retained |
| Actual facial-skin measurement | Not admitted; beard/hair concerns and unverified fine boundaries remain |
| Photo lineage | 12 exact source lineages;14derived cases bound to each |
| Independent people / final allocation | Unknown; no train/dev/test split or independent-person claim |
| Matching MST/full correction tree | Unavailable; no new calibration or tree fit |

Reference suitability was judged from the original photographs, not favourable
target-fit error. Ordinary photographed light/colour can be the target of
synthetic restoration. Directional light, beard or an occluder does not by itself
make the remaining visible original pixels unusable. Occluded anatomy, however,
is not supplied as an unobstructed reference by assumption. A usable reference
does not mean every derived mask/target is acceptable.

| Source | Main full-resolution limitation retained |
|---|---|
| 54632 | Visible facial/beard detail; softer eye detail, covering and obscured/cropped neck; beard remains a measurement hold |
| 39568 | Judgeable face with directional shadow, forehead highlights and hair strand; partial cropped neck |
| 29617 | Judgeable visible nose/cheek/mouth/chin; sunglasses and hand conceal other regions; limited neck |
| 29863 | Judgeable texture despite dim/uneven appearance; beard and white covering; severe-distortion covering spill retained |
| 16061 | Facial detail visible, but strong clear-lens reflections obscure eye detail; fringe/stubble/collar boundaries unverified |
| 52445 | Visible face usable; clothing/foreground immediately below chin and no clearly exposed neck |
| 32685 | Visible face usable with downward pose/fringe and softer bright appearance; neck largely hidden, collar spill concern |
| 53146 | Facial texture visible under hard sunlight/shadow and squint; cap and limited cropped neck |
| 48879 | Visible oblique face usable, with soft fine detail and blond hair across temple/cheek; hair measurement concern retained |
| 49131 | Broad face/neck visible; stubble/softness and actual-input jaw/neck transition remain |
| 59807 | Facial texture visible; clear glasses/reflections, fringe, microphone/hand, necklace and partial neck |
| 46795 | Visible face usable despite hard light/shadow and softness; high collar hides almost all neck |

No missing neck was manufactured. In52445, no clearly exposed neck is not a
reason to reject the visible face as a photographic reference. Where a mask
selects clothing or misses visible neck, that remains a support issue. This
does not silently change the intended face-plus-visible-neck correction design.

Known measurement holds remain explicit for54632/29863(beard) and48879(possible
hair). Other images are unverified, not declared objectively clean. This screen
does not override actual-skin admission rules, the completed human reviews,
or the actual-input diagnostic's failures. No arbitrary error/IoU threshold or
favourable-only training subset was introduced. Full-pipeline admissions remain0.

## Lineage and grouping decision

The saved publisher metadata and integrity records bind12different original
photo URLs and12different original pixel hashes. Each source's14derived cases
now share one `ffhq_photo_ID` lineage. All168 are development-exposed and stay
in one conservative **unsplit development holding block** while person/scene/
cross-source relationships are unresolved. No recognition, author-name identity
inference or visual person matching was used.

The block does not assert that all photos show one person, or that they show12
independent people. It prevents an accidental source/descendant or unresolved-
relationship split. It is not a final allocation or unseen test cohort. It also
does not require identifying people by name: a future justified common development
role can retain the block instead of claiming independence between its members.

Original author/photo/licence links are retained per row. This records the
existing local-research provenance; it is not a new terms review, legal clearance
or permission to publish the photographs/models. No external contact or download.

## Matching MST: concrete next constraint

This FFHQ screen does not create labelled MST calibration data. FFHQ must not
receive MST labels from appearance, filename, the common engineering severity
preset, an old incompatible lookup or a reference feature substituted for a
measured distorted-input feature. A compatible mapping from a separately
qualified labelled cohort is needed for the retained model.

The latest [completed nineteen-subject study](mst-subject-skin-study-results-2026-11-02.md)
already contains actual human answers:11structured favourable,7concern/uncertain,
1parent failure. Those are not calibration admissions. Subject4's lighting note
and assistant hair/chin concerns remain. Categories1/4/5 have two structured-
favourable people each before other concerns; this is not an adequate ten-category
calibration or a precision justification. Do not repeat that review or fit just
the favourable subset. The older393measurements use an incompatible mask method.

The next calibration task requires new substantive evidence resolving:

1. An exact labelled-image/current-mask eligibility set, with actual-skin concerns
   accounted for rather than promoted from technical success.
2. A justified supported person/category scope and adequacy before fitting.
3. One subject-held protocol using the retained mapping recipe, same-row baseline
   and full failure/hold denominators.

The [previous feasibility decision](faceocc-mst-feasibility-decision-2026-11-01.md)
remains in force. No ready calibration cohort was established by this FFHQ
reference screen, so no MST fit was run. This is not a demand for intrinsic
colour truth, mandatory new recruitment, a DAST purchase or waiting for an adviser.
Do not start another FFHQ formula/mask inventory as a substitute for that evidence.

## Verification and scope

Script427 creates a new package and refuses overwrite. All12source hashes,
12source rows,168descendant memberships,14descendants per source, single unsplit
holding block and CSV/JSON membership parity were checked. Parent packages,
original images and historical pinned sources/manifests are unchanged; artifact
SHA256 records are saved. This is an evidence/eligibility export, so no new
pytest run was needed. The prior26focused tests remain the last relevant code
check; they do not validate the scientific decisions here.

Zero new segmentation/FaceOcc inference, synthetic variants, target/MST/tree fits,
human annotation tasks, contacts, publication or runtime changes. All failures
and old approvals/concerns remain preserved. The submitted proposal and working
thesis drafts are unchanged. The panel register records these separate gate and
grouping decisions without claiming panel approval.
