# Blue-axis preparation and fitting engineering complete

13 November 2026. User authorized the generated preparation/runner stage following the [fixed coverage design](blue-axis-coverage-feasibility-protocol-2026-11-13.md). **49 generated tests passed in 17.44 seconds. No real preparation or fit executed.** Receipt: outputs/blue_axis_runner_engineering_v1/verification_PRIVATE.json; full test output and JUnit evidence are preserved alongside it.

The new preparation module preserves the existing 44 records and constructs only the 22 specified pure-blue derivatives. It recomputes all 281 features from each edited input, including Lab, ITA and the existing development MST mapping. All 11 identity vectors must exactly reproduce the saved canonical vectors before any new derivative is written. The independent verifier reconstructs the legacy 22 features exactly and checks the joint histogram with a scalar implementation at absolute/relative float32 tolerance 1e-7. This is numerical agreement, not a perceptual threshold. Forward RGB8 pixels and clipping counts must match exactly.

Tests exercise a temporary artificial workspace with 11 sources, 44 reused records and 22 derivatives, including all 66 feature records and 72 role-ledger entries. Artificial bookkeeping uses the production record schema; these temporary records are not scientific admissions. A deliberate identity-feature mismatch stops before creating derivatives. Both blue operators were checked over all 256 channel codes for rounding, clipping, unchanged red/green channels and input immutability. Blue edits demonstrably recompute the Lab/ITA/MST feature group rather than copying clean values.

The fitting join selects the exact 60 fitting case IDs before inspecting feature/target fields, rejects malformed provenance/targets/features, and excludes the held source. A generated 60-row tree is independently checked for float32 routes, export agreement and raw three-control leaf means. Deliberately corrupted trees, predictions and settings fail verification. A correctly computed constant-blue model stops the blue-learning gate. A deliberately failed fit is preserved and cannot be overwritten or retried. The scalar fitting verifier imports without NumPy or sklearn. The remaining 28 tests cover portable-tree behavior.

Code, protocol, design, dependencies and test hashes are bound to Python, NumPy, sklearn and OpenCV versions. Existing design-bound metadata/code hashes were checked before and after QA. The real preparation and first-fit output directories were confirmed absent. There were no real photo, mask or NPZ array reads, real fits, held predictions, old-model rescoring, new user reviews, raw-original or locked-holdout access, Android or manuscript edits. Existing approved manual support and frozen development artifacts remain intact.

Next execution, under the fixed design, is preparation followed by independent verification; only then the single first 60-record fit excluding 16061 and its independent verification:

```powershell
python scripts/run_blue_axis_feasibility.py --execute-preparation
python scripts/verify_blue_axis_feasibility.py --preparation
python scripts/run_blue_axis_feasibility.py --execute-first-fitting-only
python scripts/verify_blue_axis_feasibility.py --first-fit
```

These commands were not executed in this engineering stage. A preparation parity failure or blue fitting-gate failure stops the fixed route without tuning. Passing would support designing a prospective source-held comparison; it would not establish image quality, darker-skin bias reduction, final-model readiness or automatic permission for a 66-case visual task. Independent tone qualification remains unbound. The model is unfinished, paper editing remains paused, and the November 14 completion target remains at risk with exact time unspecified.
