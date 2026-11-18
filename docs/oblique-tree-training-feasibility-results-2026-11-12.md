# Oblique-tree training-only feasibility results

12 November 2026. **One fitting-only run completed; independently verified strict fitting improvement. No held predictions or correction-quality result.**

Used exactly the frozen 40 fitting rows from ten source groups, excluding ffhq_source_16061, with the one saved ordinary axis initialization. Generated fixtures and 29863 were excluded. Existing 16 features, raw three-control targets, depth/topology and fixed solver/budgets were retained. No initialization refit, restarts or parameter changes occurred. Script 845 made one trainer call; script 846 independently replayed the saved result without optimizing.

| Raw control SSE | Saved initialization | Oblique candidate |
|---|---:|---:|
| Total | 0.08404474326173622 | 0.004164931278633912 |
| Gamma | 0.07714285714285717 | 0 |
| Red gain | 0.006901886118879054 | 0.004164931278633912 |
| Blue gain | 0 | 0 |
| Identity role | 0.008961147141072141 | 0.002082465639316956 |
| Underexposure role | 0.06642844393067518 | 0 |
| Overexposure role | 0 | 0 |
| Cool-colour role | 0.008655152189988894 | 0.002082465639316956 |

Total fitting SSE decreased about 95.04%. This is parameter-fitting loss, not image accuracy or a 95% correction benefit. All fitting gamma targets were recovered, but red-gain errors remain. Maximum identity gamma deviation became zero; maximum identity red-gain deviation decreased from 0.0291545 to 0.0204082. These are descriptive control differences, not visually unnoticeable-change judgments. Blue targets are constant, so zero blue error supplies no colour-diversity evidence.

The run completed two passes and 14 branch-solver attempts: two accepted updates and 12 rejected for no strict raw-SSE gain. It stopped with no further strict full-pass gain, without hitting a resource cap. Optimization-phase time was 0.31148 seconds on this machine; validation/conversion precedes that timer. This is neither global optimality nor phone performance. The saved tree retains 15 nodes/eight populated leaves and stores 37 nonzero branch coefficients. Greater flexibility and overfit risk remain.

Independent verification passed initial axis/oblique prediction parity on all 40 rows, scalar serialized routing and SSE replay, topology/positive-control checks, monotone recorded loss and all eight populated three-output leaf means (zero residual). All frozen source/code/contract hashes and saved run-artifact hashes remained unchanged. Run details, fitting inputs, initialization, candidate, optimizer trace and independent receipt are preserved in outputs/oblique_training_feasibility_v1. No rerun is needed.

**Next recommendation:** specify a prospective source-held correction comparison under the accepted practical numerical/visual protocol. It should reuse this exact first-fold candidate rather than refit or select another initialization, and bind the remaining fold fits, source-role roster, rendering/scoring rules and review presentation before held scoring. This report does not select or execute that comparison. All fits should precede held scoring; the final holdout remains unavailable to development. Existing exposed development cases are not fresh final validation. Lower training loss alone is insufficient: an earlier closed axis candidate achieved zero fitting loss yet failed held transfer.

The narrow cohort still lacks blue-target variation, broad severity/combined conditions and independent MST labels. Even successful development comparison cannot by itself finish the full correction task. Existing failed models remain closed and are not rescored or promoted. Keep model first/paper paused; retain one final tree, ITA/MST, traditional features, single-photo face/visible-neck support and optional manual refinement. PPR remains paused and neural correction features declined.

This stage read only fitting JSON records and saved metadata/models. Zero held-record reads, held predictions, photo/mask/NPZ reads, final24/older locked bytes, runtime/Android changes, acquisition, contact, upload or commit/push. No new user review task is created yet.
