# Workspace cleanup

28 October2026. User authorized cleaning the full directory before further
model development. Removed22,952generated files across1,087targets, totaling
406,793,245bytes (387.95MiB logical file size).

| Removed category | MiB |
| --- | ---: |
| Python bytecode caches | 166.00 |
| Verified SDK installer ZIP | 136.41 |
| Android intermediates | 72.31 |
| Old pytest workspaces | 12.43 |
| Nested pytest workspaces | 0.38 |
| One-off Gradle thread dump | 0.37 |
| Pytest discovery/history cache | 0.05 |

Installed Python packages, SDK/Gradle dependencies, the APK and Android test/lint
reports remain available. Source code, numbered experiment scripts, thesis
documents, raw datasets, model artifacts, masks, manifests, original reviews,
holds and historical results were retained. Those records are still needed
for source dependencies, thesis evidence and reproducibility; age alone is not
a reason to delete them. Unique helper scripts under `tmp/` were retained.

All1,087targets were validated as recognized generated paths inside the
resolved workspace before recursive deletion. No tracked file was selected,
no linked target/descendant was allowed, and there were0deletion failures.
After deletion,13,672protected files match their recorded SHA256hashes.
All selected paths are absent. Python OpenCV/NumPy imports and the frozen-tree
prediction pass; APK checksum and installed SDK are intact. The full Python
suite was not rerun because source behavior was unchanged and that would
recreate the disposable test workspaces. No model fitting or method change.

[Audit/deletion verification](../outputs/workspace_cleanup_20261028_v1/verification.json) ·
[Exact deletion results](../outputs/workspace_cleanup_20261028_v1/deletion_results.json) ·
[Development workspace map](workspace-guide.md).

Scripts132/133 retain the audit and constrained deletion procedure. Cleanup
reports are a new record; existing thesis/review files were not edited by this
cleanup. Model development remains the priority; Android stays on hold.
