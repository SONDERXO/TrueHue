# Regional comparison scoring is ready

1November2026. User asked to continue. No preferred-reference decision export
was found in the current review folder or Downloads, so no user judgments were
invented or bypassed. Work proceeded on the independent evaluation stage.

The comparison now has a shared scoring module for face, neck, brows, lips and
surrounding-brow skin, plus their union. Scores always use saved reference
generation masks, not a favorable subset selected by the predicted mask.
Regions must be disjoint, empty regions report unavailable rather than zero,
and omitted application pixels remain in the reconstruction-error denominator.

The module separately reports changed pixels outside application support,
correction applied outside generation support, and exact preservation of clean
identity controls. A good face score cannot conceal a bad neck/lip score or
changes outside the scoring region. Encoded-sRGB CIEDE2000/RGB errors remain
photographic-reference reconstruction metrics, not intrinsic skin color truth.

Saved no-correction baselines cover all30current version2anchor inputs. Six
unchanged control records pass the exact clean gate. These are scoring/software
checks, not model performance, training admission, new mask approval or another
scientific candidate experiment. There is no parameter optimization or model
fitting. Five meaningful tests exercise missing regions, region-specific harm,
outside-region changes, identity controls and overlap rejection.

Full Python suite: **879passed in10.10seconds**, cache disabled.

Implementation: `src/evaluation/preferred_regions.py`,
`tests/test_preferred_regions.py`, script348. Evidence:
`outputs/preferred_regional_baselines_v2/no_correction.json`,
`identity_controls.json`, `verification.json`.

The remaining user input is the exact reference review at
`outputs/preferred_reference_review_v2/review.html`. It contains ten additional
available sources plus only the newly expanded correction-mask decision for the
six anchors. Existing source/facial-mask approvals are retained; an earlier
downloaded version1export can carry matching source/facial decisions forward.
Download the decisions into the version2folder. Reference acceptance then
allows preparation of accepted new sources and identification of exact new
input-mask admission needs before the fixed comparison. No adviser-request
gate applies. No further mask tweaks are planned.
