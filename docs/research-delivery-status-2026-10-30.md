# TrueHue delivery index — 30 October 2026

1November2026 update: start with [current delivery checkpoint](delivery-checkpoint-2026-11-01.md)
and [thesis addendum](thesis-results-addendum-2026-11-01.md). New aggregate-only
snapshot: outputs/delivery_checkpoint_20261101_v1/index.html and evidence.zip,
verified by script384 --verify. Android has bounded emulator evidence but still
uses the older experimental baseline; FaceOcc preferredexperimental/MSTnotready.
The30Octoberpackage and dated index below remain historical, not overwritten.

31 October follow-up: [Discussion, limitations and conclusion draft](thesis-discussion-limitations-conclusion-draft.md)
is now prepared. [Real-widget desktop flow checks](demo-flow-check-2026-10-31.md)
cover opening, processing state, display, failure export, save cancellation/error
and retry. Previous technical details now clear when a new run starts. Latest
full suite:836passed in28.36seconds; no model/measurement change. The30October
package remains an immutable earlier snapshot, not a copy of these new documents.

This index distinguishes finished evidence/software work from unfinished
scientific and application requirements. It does not start a new experiment.

## Ready for thesis writing and adviser review

| Deliverable | Where to start | What is established |
|---|---|---|
| Implemented methods/results draft | [Draft](thesis-methods-results-draft.md) | Actual method, proposal deviations, completed comparisons and limitations |
| Reproducible result tables | [Generated tables](thesis-results-tables-2026-10-30.md) | 83 saved correction aggregate rows and MST metric tables; case/source denominators retained |
| MST evidence audit | [Checkpoint](mst-evidence-checkpoint-2026-10-30.md) | Saved predictions/metrics and provenance verified without fitting; missing validation explicit |
| Adviser reference-data/scope decision | [Brief](adviser-decision-brief-2026-10-30.md) | Specific unresolved questions and completed negative results; nothing sent |
| Controlled reference-data proposal | [Protocol draft](controlled-reference-capture-proposal.md) | Proposed acquisition/data-role boundaries; no recruitment or sample-size approval assumed |
| Demo reporting | [Update](demo-reporting-update-2026-10-30.md) | Correct experimental notice, captured run provenance and saved-file checksums; older model retained |

The local package is `outputs/thesis_evidence_package_20261030_v1/`.
It contains full-precision `correction_aggregates.csv/json`, `mst_metrics.csv/json`,
`decisions.json`, selected document snapshots, a README and checksum manifest.
It contains no images, model weights, individual predictions or credentials.
It is a local review aid, not a submitted thesis or release artifact. Copied
documents retain workspace references; local galleries are not embedded.

Regenerate only into a new version if inputs change; existing snapshots must
not be overwritten. To verify this version from the project root:

```powershell
venv\Scripts\python.exe scripts/319_package_thesis_evidence.py --verify
```

The packager reads saved summaries, validates their bound hashes, exports
aggregates and checks CSV/JSON numeric parity. No inference, fitting, image
decode or reserved evaluation access occurred. No new full-suite run was needed
for packaging; latest software result remains834 passed in16.76seconds from
the demo-reporting change.

## Requirements that remain open

| Requirement | Status and next substantive dependency |
|---|---|
| Reliable automatic correction | Both planned successor comparisons failed. No candidate adoption; stop same-cohort parameter trials. Reference-data/scope decision precedes a new cycle. |
| Final calibrated MST validation | Experimental lookup only, actual labels1–9; independent subject support and agreed scientific acceptance evidence remain missing. Prior limited-scope approval remains recorded. |
| Parser and beard/moustache changes | On hold for adviser discussion. No additional-model search, account setup or parser integration resumes automatically. |
| New controlled collection | Discussion draft only; feasibility, participant access, permissions, equipment, sample-size rationale and role allocation need agreement. |
| Neck correction | Unfinished; facial results cannot establish visible neck coverage. |
| Android integration and device evaluation | User-paused; a scaffold/APK/portable tree does not establish an integrated correction app. |
| Photographer opinions | After model completion using the user's existing Google Form. No responses or scores invented. |
| Independent final correction evaluation | Reserved roles remain locked against tuning; historical duplicate-audit exposure must be disclosed. Source groups do not establish distinct people. |

The reporting changes do not require adviser approval; neither do evidence
organization or thesis writing. This does not mean the missing scientific gates
can be satisfied through more documentation alone. The package makes the
completed work reviewable and the remaining decisions concrete.
