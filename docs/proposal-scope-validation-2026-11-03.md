# Verified proposal scope: photographic correction, not intrinsic colour recovery

3 November 2026. Checked the actual project-root Thesis Proposal Document.pdf,
111 PDF pages, SHA2561426f3769ba771daadf9b6e0e0b1e347729c8f04919c214e6fedc3df272e7b8a.
No proposal edits. Extracted page text and checksum saved under
outputs/proposal_scope_validation_20261103_v1/.

## Finding and correction to earlier guidance

The user is correct: true/intrinsic skin-colour recovery is NOT the required
claim in this document. Earlier assistant advice repeatedly treated measured
true-colour references as a completion prerequisite and framed photographic
restoration as a possible narrowing. That interpretation was too strong.
Photographic synthetic-restoration feasibility is already the stated scope.
This is a correction to assistant guidance, not a new thesis scope amendment.

Verified locations (PDF page / printed page):

- 10 / 3, General Objective: improve exposure and colour correction across
  diverse skin tones, using ITA and a decision tree, evaluated with MST.
- 11 / 4, Specific Objectives4–6: generate synthetic distorted pairs, use skin
  category for targeted adjustments, evaluate improvements across MST categories.
- 12–14 / 5–7, Scope and Limitations: ordinary processed source photos, exploratory
  simulated feasibility, not definitive real-world camera-bias correction.
- 14 / 7 explicitly says the study cannot prove recovery of actual skin tone;
  it evaluates improvement of synthetic distortions against an uncorrected baseline.
- 63 / 56: distorted input paired with original reference; gamma/red/blue outputs.
- 65 / 58: original unmodified dataset photo retained as target; parameter MAE
  and relative CIEDE2000 against the target.
- 66 / 59: quantitative evaluation by MST and professional appraisal.

## Consequences for development

Do not require a colorimeter, controlled participants or certified intrinsic
skin-colour targets to fulfil this photographic-restoration scope. DAST remains
potentially useful additional evidence, not a mandatory dependency. FFHQ or other
ordinary photos can in principle be source references for justified synthetic
restoration, subject to actual quality/support, rights, grouping and role checks.
High resolution alone is not admission. PPR expert edits remain a different
supervision choice from the paper's original-to-synthetic pairs, with its role
and any added contrast output explicitly recorded if adopted.

The genuine unfinished requirements remain: usable permitted sources, correct
measurement masks and matching MST evaluation, source/person separation,
distortion/parameter targets consistent with the exact rendering operator,
unchanged-photo handling, comparison against uncorrected input, subgroup evidence,
Android verification and professional review. No invented reliable MST lookup,
automatic data admission or training follows from this scope clarification.

Reference-quality checks should support the claimed photographic task rather
than silently demand physical skin-reflectance truth. Keep the all-tone evaluation
objective and disclose unsupported categories; feasibility wording is not a reason
to invent missing labels or hide failed results. Adviser input concerns actual
method/dataset/output changes and academic adequacy, not permission to revert to
the already written restoration goal.

Earlier adviser brief and source-readiness records remain dated artifacts. Read
them with this correction: missing intrinsic-colour references alone is not a
reason to require recruitment, extend the study or narrow its stated scope.
No experimental results, mask decisions, model schema, frozen snapshots or paper
text changed. Text inspection only; no new tests, inference or fits.
