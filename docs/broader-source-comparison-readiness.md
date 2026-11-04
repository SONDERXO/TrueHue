# Broader-source comparison readiness — 30 October 2026

The completed user review has been imported into
`outputs/additional_six_source_mask_import_v2/`. The earlier partial importv1
is preserved. The exact export, decisions, notes and timestamps are retained.
There are **4 accepted /11 rejected /0 pending**. No repeat review is needed.

Accepted cases:

| Source | Exact accepted variant | Note |
|---|---|---|
| 39083 | color | No note |
| 63509 | color | No note |
| 63509 | gamma lightening | No note |
| 63509 | gamma darkening | Minor holes; exact original note retained in JSON |

The eleven rejected variants remain excluded. A rejected distorted mask does
not revoke the separately accepted original control or saved stress judgment.
These are the original rule-based masks; none uses the newer semantic parser.

## Concrete resolved comparison

The predeclared design now resolves to **121 evaluation cases /32 source
groups**:32 original controls,62 accepted primary inputs and27 stress inputs.
The source-expanded primary candidate's fitting pool is94 cases before each
held-source exclusion:32 controls +62 primary inputs. No clipped stress case
enters this candidate's primary fit.

Procedures A/B/C and all settings/gates remain those of
[the frozen protocol](broader-source-comparison-predeclaration.md).
The readiness artifact binds52 existing A/B trees and210 old predictions for
reuse. The planned execution needs34 new fits:two shared historical comparator
fits and32 source-held candidate fits. It does not require rerunning the old
26-source experiments or regenerating their saved outputs.

Only two of the six added sources contribute accepted new primary variants.
The six additional controls are useful but do not establish broad distortion,
skin-tone or identity coverage. All sources are development-exposed; reference
illumination/true skin tone and the experimental MST lookup remain limitations.

## Verification and execution boundary

`scripts/301_import_additional_six_source_masks.py` now accepts a new output
directory so a complete successor import can preserve the partial snapshot.
`scripts/314_finalize_broader_source_readiness.py` resolves exact membership and
writes `outputs/broader_source_comparison_readiness_v1/plan.json`, `summary.json`
and `verification.json`.

Checks passed for the complete exact export, original notes,242 input-image/mask
hashes,32 disjoint held-source folds,52 historical tree hashes and bound saved
predictions. All six added sources pass the frozen training-role guard.
The105 historical cases retain their verified historical development provenance;
they predate the separate600-source allocation and are not falsely relabeled as
new-allocation sources. Reserved evaluation roles remain locked.

This phase imported judgments and finalized readiness. **No trees were fitted,
no images decoded and no new correction metrics produced.** The design's
not-started execution state remains explicit. No new full-suite test result is
claimed; the last full suite remains833 passed in11.62seconds. Verification
here uses hash/provenance and membership checks appropriate to metadata work.

The next work is an executor for this one frozen comparison, followed by saved
tree/prediction verification and a decision against the existing gates. Any gate
failure means no adoption and no same-data parameter search. The current demo
stays unchanged; passing development results would still not establish thesis
completion or final MST calibration.

Parser and beard/moustache changes are **on hold while the user consults the
adviser**. Do not continue model acquisition, change masks or request account
access as part of correction-model work.
