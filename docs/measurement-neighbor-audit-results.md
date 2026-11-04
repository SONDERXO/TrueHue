# Measurement parity and clean/distorted overlap

30 October 2026. Recomputed all 41 input feature vectors from the exact saved
images and masks. Lab statistics, ITA and experimental MST indices match the
frozen training plan exactly. This rules out a saved-feature mismatch on these
inputs; it does not validate anatomical masks or MST calibration accuracy.

Script `261_check_measurements_and_neighbors.py` reuses the frozen 26-source
held folds. For each held input it compares only fitting rows, scaling each
feature by its fitting population standard deviation. It reports the nearest
clean and distorted fitting example. Reference measurements, held statistics
and source IDs do not set scales. No model, confidence rule, skip threshold or
prediction is fitted or deployed.

| Descriptive distance | Clean inputs closer to distorted /26 | Distorted inputs closer to distorted /15 |
|---|---:|---:|
| Lab means only | 9 | 8 |
| Lab means plus ITA and MST | 7 | 8 |

No cross-source feature vectors collide exactly at float32 precision. Thus
this is neighborhood overlap, not proof of mathematically identical inputs
requiring incompatible outputs. Standardized Euclidean distance is not a
perceptual metric, uncertainty estimate or nearest-neighbor model evaluation.
ITA derives from L/b and MST from ITA, so adding them changes weighting as
well as representation. These counts do not justify dropping the required
ITA/MST inputs or establish that any particular alternative feature would help.

The result supports investigating training coverage and additional justified
facial information rather than adding source exceptions or another unvalidated
brightness cutoff. Current training has only fifteen distorted sources and
eleven additional clean-only sources; this audit adds no new approved distorted
masks. Improved dataset coverage still requires exact mask/target eligibility,
and exposed development cases cannot serve as final validation.

Verification checks frozen input hashes and the measurement contract, 41 exact
feature/lookup matches, source separation, and 82 independently recomputed
distance rankings (Lab3 and five-feature views per input). Outputs are
`outputs/measurement_neighbor_audit_v1/summary.json` and `verification.json`.
The existing diagnostic tests pass separately; the last full suite remains
786 passing tests. No library, demo, mask, calibration, training target or
reserved-data access changed.
