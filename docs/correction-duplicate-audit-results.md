# Correction candidate duplicate audit

The declared computational audit decoded all 600 frozen candidates and 650
historical sources successfully. It found six perceptual-hash candidate links,
including connected conflicts that quarantine three new candidates. None of
the six links is an exact decoded-pixel match; these are suspected overlaps,
not visually confirmed duplicate people or photographs.

| Frozen role | Original candidates | Screen clear, still unreviewed | Quarantined |
| --- | ---: | ---: | ---: |
| Training | 420 | 418 | 2 |
| Development-validation | 90 | 89 | 1 |
| Final test | 90 | 90 | 0 |

The original selection and seven batches are preserved. A separate verified
training queue removes quarantined IDs without replacement or reassignment.
Every retained source still needs the existing pipeline processing and human
mask/reference review before fitting. No model was fitted or activated.

All held-out images were computationally decoded for this audit. They must no
longer be described as never opened. There was no visual inspection, face or
skin processing, ITA/MST extraction, correction prediction or quality/outcome
inspection. Validation/test remain closed to model development and evaluation.
The original metadata-only ledger is historical; the separate audit access
ledger records this new access. Historical allocations and exposure metadata
hashes remain unchanged.

The protocol uses decoded shape/pixel SHA256 and a 64-bit difference hash with
the existing Hamming threshold of 4. This implementation converts to grayscale
before an INTER_AREA thumbnail resize; it does not assert fingerprint parity
with every older script. Connected groups propagate historical/cross-role
conflicts. The screen cannot establish person separation or rule out all
duplicates, and no source is automatically admitted for fitting.

Verification reconstructed every link and candidate disposition from the saved
fingerprints, checked metadata hashes and enforced training-only queue
membership. The full existing suite passed: **724 tests in 29.30 seconds**.
The next stage is training-only square256 preparation using the frozen
measurement contract and the audit dispositions, retaining all failures and
review concerns. ITA/MST and decision-tree correction remain the intended
method. Photographer evaluation waits for model completion using the existing
Google Form.

- [Predeclared audit protocol](correction-duplicate-audit-protocol.md)
- [Audit summary](../outputs/correction_duplicate_audit_v1/summary.json)
- [Candidate dispositions](../outputs/correction_duplicate_audit_v1/candidate_dispositions.json)
- [Computational access ledger](../outputs/correction_duplicate_audit_v1/access_ledger.json)
- [Training queue after quarantine](../outputs/correction_duplicate_audit_v1/verified_training_queue.json)
- [Verification and evidence hashes](../outputs/correction_duplicate_audit_v1/verification.json)
