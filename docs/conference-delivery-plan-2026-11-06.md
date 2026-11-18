# November 14 submission: execution plan and measurement decision

Update: user chose **Yes, prepare the skin-patch review**. The
[page is ready](skin-patch-review-ready-2026-11-06.md); actual responses remain
pending. The pending-choice text below records the original decision context.

Prepared 6 November 2026 after the user reported a November14 conference paper
deadline. The venue, submission timezone, template, page limit and required
paper type have not been supplied; no venue requirements or acceptance outcome
are assumed. There are eight calendar days to the stated date. Aim to have a
submission-ready draft by November13, leaving November14 for final checks and
the user's submission. Completing a validated automatic method by then cannot
be promised from current evidence.

## Immediate measurement decision

Use the existing dataset. The received release audit already established that
all delivered images are224 by224, with no supplied skin-region annotations in
the inventoried JPEG/label release. No higher-resolution copy is established
by that archive. Do not repeat the inventory or contact the author automatically.

Automatic parent masks and larger-backbone masks show a genuine skin/material
trade-off. Another parser sweep is not the proposed solution. A practical next
diagnostic is a small human-selected facial-skin patch reference on the same
six already exposed photographs. This is a new region-measurement task, not a
repeat of completed point labels or a demand for full-face contours. The user
has been asked whether they will do this; that choice is pending. Do not
fabricate regions, assume assent, or turn the previous sparse points into
filled masks.

If selected, prepare a private offline tool with these rules:

- Show the six originals and native nearest-neighbor face crops, no prediction,
  previous points, MST score, colour enhancement or assistant-proposed outlines.
- Ask for one or more patches of clearly visible facial skin where possible.
  Exclude beard/stubble, hair, eyes/brows, lips/mouth, nostrils, frames and
  reflections; avoid uncertain boundaries. Do not require a fixed patch area,
  a whole-face outline or matching patches across photos.
- Allow no reliable patch with a reason on every image, including the detector
  failure. Do not force a successful reference for a dark or ambiguous image.
- Preserve native coordinates, source hashes, actual reviewer identity/code
  and uncertain/unavailable outcomes. Preserve all earlier point labels.
- Import only the actual export. Measure original RGB through the retained
  Lab/ITA calculation and record patch geometry, native pixel counts and
  original colour statistics. No1000normalized-pixel automatic-mask guard is
  silently applied to a different manual reference contract; no invented
  native-size adequacy threshold is substituted either.
- Compare automatic selection overlap and colour statistics on the same image.
  Differences show measurement sensitivity, not accuracy against intrinsic
  skin colour. A small selected patch need not represent the entire face;
  regional illumination and reviewer uncertainty remain limitations.

This diagnostic separates visible-skin selection from model prediction. It
does not validate an automatic mask, create a calibration cohort or support
fitting on six development images. A patch unavailable under dim light is a
retained finding, not a reason to replace the case.

If the user chooses automatic-only work, do not prepare a manual task or retry
failed auxiliary rules. Present the unresolved automatic measurement limitation
and choose the paper's defensible experimental scope with the user before any
new model test. No additional dataset is requested here.

## Schedule and explicit stop decisions

| Date | Concrete work or decision |
| --- | --- |
| Nov6–7 | Resolve the patch-review choice; if selected, prepare/verify the tool and import only actual responses. Complete the bounded comparison, retain failures, and close it. |
| Nov8 | Make one explicit paper-scope decision using the actual result. Real fitting proceeds only with substantive eligible measurement, compatible calibration and grouped evaluation evidence. Otherwise frame the paper around the supported prototype/development findings, subject to venue suitability and user agreement. No automatic six-case or favorable-subset fit. |
| Nov9–10 | Assemble methods/results tables from existing bound evidence; distinguish operator fits, automatic predictions, sparse reference findings and generated software tests. Add real predictive results only if they actually exist under an eligible frozen protocol. |
| Nov11 | Complete a coherent paper draft, limitations and citations in the actual venue template once supplied. No private dataset images or labels in a submission without the required consent; aggregate research findings are distinct from dataset redistribution. |
| Nov12 | Review claims, denominators, citations and method consistency; resolve advisor feedback if available. User approval is not assumed. |
| Nov13 | Freeze results and complete format/file checks. Preserve reproducible local evidence and prepare the final submission artifact. |
| Nov14 | User submits according to the verified venue deadline/timezone. No assistant submission is authorized. |

The dates are work targets, not scientific admission criteria. Do not lower
guards, conceal failures, invent validation or adopt a method to meet them.
If an earlier decision cannot be completed, update the schedule and claim scope
instead of silently treating unfinished research as a result.

## Evidence available today

Existing operator-fit diagnostics demonstrate conditional photographic recovery,
not learned predictive performance. Actual-input tests expose mask/support
instability. User sparse references show omissions and unwanted material;
ResNet34 improves selected skin while increasing unwanted inclusion. Continuous
MST/correction interfaces pass generated software checks, but no real contextual
MST fit or photographic correction-tree fit is admitted. Android remains on its
older pipeline. These evidence types must have separate tables and claims.

No new images, inference, fits, admissions, masks, source transfers, contacts or
paper submission occurred while preparing this plan. Private research-only,
noncommercial, citation and no-redistribution conditions remain in force.
