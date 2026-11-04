# Photographer reference-suitability review package ready

**Superseded by user direction,28 October2026:** do not perform the review
instructions below. Photographer opinions are deferred until the correction
model is finished, using the user's already existing Google Form. This local
package remains unused and preserved only as historical work. Responses are
not a prerequisite for continuing model development.

28 October2026. Prepared a concrete next evidence step after the failed model
gates and integrated stress checks: two independent photographer judgments of
the ten photographic references. This addresses the unresolved reference-quality
question before another learning experiment. It is **development reference
screening**, not final correction MOS or calibrated skin-color measurement.

The [protocol](photographer-reference-review-protocol.md) precedes collection.
Each page shows the same exact ten saved256reference frames, under opaque case
codes and a separate fixed shuffled order. No masks, corrected outputs, source
IDs, MST estimates or previous decisions appear in the reviewer presentation.
The researcher mapping is a separate local file. Presentation blinding cannot
prevent prior recognition or intentional examination of package internals.

## Actual next action

Arrange for two actual photographers to independently use these local pages:

- [Photographer P1](../outputs/photographer_reference_review_v1/P1.html)
- [Photographer P2](../outputs/photographer_reference_review_v1/P2.html)

Keep the package local and serve no images publicly. Reviewer pages require
their adjacent`images/`folder and`review.js`. Do not give the researcher key or
synthetic validator fixture file as review material. Have each photographer
record display/recognition limitations, judge independently, and use **Validate
and export review** to save their original JSON file. The browser may retain a
draft when local storage is available; exported originals are the evidence.
No messages or images were sent to anyone by this work.

The form asks about detail, illumination, occlusion and overall suitability as a
synthetic reconstruction reference, with reasons for uncertain/unsuitable cases.
These categorical judgments must not be averaged into MOS. An original photo
can be suitable for reconstruction yet still lack neutral exposure/color.
Photographer self-declaration does not independently verify credentials or
independence. No default judgment or response is inserted.

After actual responses are available, archive and reconcile them using:

```powershell
.\venv\Scripts\python.exe scripts/185_import_photographer_reference_reviews.py `
  --responses path/to/reference-review-P1.json path/to/reference-review-P2.json `
  --output-dir outputs/photographer_reference_responses_v1
```

Use a fresh output directory. The importer checks exact case membership,
reviewer distinction, declaration, required reasons and manifest identity,
preserves original JSON bytes/hashes and retains both decisions and disagreements.
It performs no automatic source eligibility changes, adjudication or model fit.
Existing user mask/scene acceptances and the old cohort/results remain unchanged.
If judgments motivate a revised reference cohort, declare the eligibility and
adjudication policy before fitting or selective reporting.

## Preparation verification

Script184creates the local package. Script186verifies all ten copied references
against their exact original hashes, both reviewer allocations, absence of source
IDs/externalURLs in the presentation and the matching manifest. Python importer
and JavaScript browser validator each pass14in-memory test scenarios: two complete
synthetic fixtures and12invalid variants. Synthetic fixtures are software-test
data only, not collected ratings. No real responses, MOS values or photographer
agreements are present. Browser layout/interaction was not visually tested;
validation logic was executed with Node. If the local browser blocks drafts,
the page reports this and reviewers can still export their completed responses.

[Package verification](../outputs/photographer_reference_review_v1/verification.json).
No shared algorithm module changed; latest full suite remains701passed from
pipeline integration, rather than a claimed new full-suite run. Current model
quality failures and experimental MST limitations remain. Final model-dependent
MOS must follow a suitable frozen final evaluation design; this preparatory
source review does not replace it. Android remains paused; CPM deferred.
