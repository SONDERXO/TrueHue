# Demo reporting update — 30 October 2026

The main demo continues to use `baseline5`,fold1 through script180. No correction
model, operator, lookup, masks or features were replaced. Parser and beard work
remain on hold. This change improves identification and result provenance only.

The visible notice now states that the demo uses the older ten-source baseline,
that it failed quality checks and that its MST estimate is unvalidated. It does
not imply that either later rejected candidate or the retained eleven-feature
endpoint research reference has been deployed.

Technical details and exported `report.json` now share a report builder. Each
analysis records a stable run ID, analysis timestamp, captured preset, source
file hash and copied model provenance. Repeated exports of that run retain the
same analysis identity. Provenance captures existing tree, lookup, measurement
contract and experiment-summary hashes. The original stage/failure report is
preserved. Neither success nor the checksum manifest implies scientific validity.

Saving creates a new folder containing the report, available image/mask views,
and `manifest.json`. The manifest gives the save time, run ID, SHA256 and byte
count for every other exported file; it does not hash itself. Images are encoded
as before and failed runs still cannot export a partial correction. The source
path remains in the local report, so saved folders should be reviewed before
sharing identifiable photographs or personal file paths.

A regression test verifies captured provenance survives caller/global-preset
mutation, repeated saves preserve run identity and every saved file matches its
manifest. Full suite: **834 passed in16.76seconds**, cache disabled.
JUnit evidence: `outputs/demo_reporting_verification_v1/tests.xml`.

A headless smoke run on the existing demo example succeeded and verified every
manifest file and the unchanged original input. The preset remained the exact
older `baseline5`/fold1 setting; the tree SHA was
`81dcc65c9c30c61a70a8c3f123486a09575f06741ee23f98c46a1f069ed018ad`.
Evidence: `outputs/demo_reporting_verification_v1/smoke.json` and its referenced
export. No training, reserved-data access or new-photo experiment occurred.
Interactive GUI layout/click testing is not claimed.
