# Development workspace map

28 October2026. Current priority is the Python correction model. Android work
is on hold at the user's request; retain its SDK and dependencies for resumption.

| Location | Role | Cleanup policy |
| --- | --- | --- |
| `src/` | Python pipeline and experimental implementations | Retain; historical tests/scripts still import experimental modules |
| `tests/` | Python verification | Retain source; generated test fixtures/caches are disposable |
| `scripts/` | Numbered reproducible development stages and current runners | Retain; older stages are referenced by provenance and later scripts |
| `docs/` | Thesis method, decisions, protocols and results | Retain historical findings and limitations |
| `data/raw/` | Original datasets | Retain; not disposable build output |
| `data/manifests/` | Partitions, reviews, annotations, exclusions and exposure records | Retain unchanged |
| `models/` | Local pipeline assets and fitted/deferred models | Retain; current and historical hashes depend on these artifacts |
| `outputs/` | Experiment evidence, masks, reports and development artifacts | Retain evidence; remove pytest workspaces/bytecode caches |
| `outputs/android_toolchain/` | Installed SDK and Gradle dependencies | Retain installed tools/caches; verified downloaded installer ZIP is disposable |
| `android-app/` | Paused application scaffold and tree component | Retain source, APK and reports; intermediates are rebuildable |
| `venv/` | Working Python environment | Retain packages; bytecode caches regenerate automatically |
| `tmp/` | Unique historical report-generation helpers | Retain unique source files; the directory name alone does not make them disposable |

## Start here for model development

- [Implementation scope](implementation-plan.md) and [method alignment](thesis-method-alignment.md).
- [Current core pipeline results](core-pipeline-check-results.md).
- [Control-recipe comparison](core-control-comparison-results.md) and [failure diagnostic](core-feature-conflict-results.md).
- [Existing source readiness](core-source-readiness-results.md): no new cohort admission established.
- `scripts/116_run_core_pipeline.py`: current input-only Python development runner.
- [Offline checkpoint instructions](thesis-demo-guide.md).

The portable tree is a software baseline, not an accepted final correction
model. Operational MST and correction quality remain unresolved. CPM stays
deferred; paint/makeup handling remains a limitation. Preserve previous reviews,
holds and source groups when preparing the next model stage.

## Cleanup record

`outputs/workspace_cleanup_20261028_v1/` records selected disposable paths,
file/byte totals, protected-file hashes, deletion outcomes and verification.
Scripts132/133 separate auditing from deletion and constrain deletion to
recognized generated paths under the resolved workspace root. This cleanup
does not move old evidence or break its saved paths to make the tree look shorter.
