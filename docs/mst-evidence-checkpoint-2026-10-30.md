# MST evidence checkpoint — 30 October 2026

The existing lookup is executable and useful for disclosed development features,
but **not scientifically validated**. This audit reran no calibrator, decoded no
photographs and opened no reserved evaluation role.

## Verified existing evidence

`scripts/318_audit_mst_evidence.py` checked dependency hashes, matching current
measurement identity, the lookup's bound evaluation hash, held-subject separation,
396 saved-knot predictions and full metric accounting. Evidence is saved in
`outputs/mst_evidence_audit_20261030_v1/audit.json`.

| Evidence | Current finding |
|---|---|
| Earlier strict center/threshold recipe | Zero available held-subject predictions; retained negative result |
| Later monotone recipe | 418 attempts,396 predictions,15 measured subjects,22 processing failures |
| Equal-subject ordinal MAE | 2.306 versus3.000 median baseline |
| Exact-category accuracy | 11.11% versus14.39% baseline |
| Within-one accuracy | 33.84% versus22.22% baseline |
| Missing held-category support | 180 measured images |
| Actual packaged lookup range | Labels1–9; no emitted MST10 |
| Final independent validation | Not established |

Measured subject support by MST1–10 is2/2/2/1/1/2/1/2/1/1. Categories4,5,7,9,10
therefore lack two-subject support within this measured cohort. This is a
separation constraint, not a sample-size/power justification. The agreed limited
scope must retain explicit unsupported-category counts rather than pretend a
validated ten-category output. Do not force the endpoint to10.

The approved limited scope is recorded as **user-reported adviser confirmation**
in `adviser-mst-limited-scope-proposal.md`. Older implementation notes describing
approval as pending or zero available predictions refer to an earlier stage;
they must not be mistaken for the latest experimental monotone result.

Lookup SHA256:
`3e3f3635ed860f68ab664c86f9ac985c7c3e8e461a16475156ebcd0eafe0cd7e`.
Measurement SHA256:
`051dfb175e1356776ea59ebb5c3d63a7e1130de49d5787a7e75b7c0fa135db73`.
The audit confirms provenance/reproducibility, not scientific accuracy.

## What remains missing, without fitting again

| Requirement | Concrete next evidence needed |
|---|---|
| Independent validation | Eligible labeled subjects with provenance/exposure disclosure and a frozen subject-separated plan; historical resplitting is not untouched validation |
| Supported scope | Explicit categories and subject counts supported by the agreed data; no race-derived labels or assumed labels on new portraits |
| Acceptance criteria | Adviser-agreed scientific criteria and denominators before further calibration; MAE superiority alone does not establish adequate accuracy |
| Measurement validity | Reference-region/mask quality and stated lighting conditions for the exact measurement contract |
| Changes to masking | A separate approved method decision, then matching measurement/calibration; no reuse of the old lookup under new masks |
| Final artifact | A report that actually meets the agreed evidence requirements; a schema flag or portable-parity check is insufficient |

Retain [the existing calibration/evaluation design](mst-calibration-evaluation-design.md)
and historical exposure. MST-E stays out of correction fitting; correction
performance does not independently validate MST predictions. A color chart can
help document photographic references but does not supply an official MST label.
No new label selection, thresholds, dataset access or calibration search is
authorized by this checkpoint.
