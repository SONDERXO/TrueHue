# Repository maintenance — 4 November 2026

The user requested folder cleanup followed by committing and pushing the current
development work. The repository is private and the checked-out branch is
`android-ui`, tracking `origin/android-ui`. The remote was fetched and initially
had no divergence. Publication targets this branch; no force push, remote history
rewrite, merge to main or change in repository visibility is used.

## Cleanup and what is preserved

The ignore rules now exclude whole local dataset/manifests, downloaded-model,
generated-output, temporary and generated-report folders. This prevents large
model downloads and their bundled runtime libraries from entering Git and avoids
unnecessary traversal of local test directories. Previously unignored models
included a108.66MiB ONNX file. Local data/models and saved experiment artifacts
remain available on disk; ignoring them is not deletion.

Numbered scripts, tests and research documents are retained. Historical scripts
and frozen experiments depend on those paths and source versions; they cannot
be judged disposable merely because they are older. No research gallery,
dataset, model, user review, failure record or frozen snapshot was deleted.
The unchanged5.1MiB proposal PDF is retained locally. The5November continuation
excludes it and the IDE-downloaded `docs/oracleJdk-27/` runtime from the upload.

The disposable rendered preview `tmp/pdfs/adviser_brief_20261102/page-1.png`
(217,756bytes) was removed with a single explicit file deletion. Its source
document and final reports remain. Automatic safety review rejected the earlier
recursive cache-deletion command with "blocked by policy". Python cache folders
were therefore left in place and excluded from Git; no ownership/permission
changes or alternate bulk-deletion mechanism was used.

The README now explains current development status, key source folders, local
artifact boundaries and links to current working drafts/results. Direct SciPy
and requests dependencies are declared. No packages were installed or models
changed in this maintenance step. Three whitespace-only blank lines in the
tracked experiment journal were cleaned. Two historical extra-blank-line-at-EOF
warnings in a source script/demonstration guide are retained; their research
content was not rewritten for cosmetic cleanup.

## Validation

- Python:973passed in30.25seconds, using
  `python -B -m pytest tests/ --ignore=tests/test_demo_desktop.py -q -p no:cacheprovider`.
  This excludes the known Tcl/Tk-dependent desktop GUI file and is not described
  as a full-suite pass.
- Android: `scripts/130_build_android.ps1` with
  `testDebugUnitTest --rerun-tasks` completed successfully;23 tasks executed.
  The two fresh JUnit XML reports contain18tests,0failures,0errors,0skips.
  No new emulator/native instrumentation or physical-phone test was performed.
- Pre-commit review found no changed dataset/model/output/temp payloads, no
  indexed file over10MiB, and no matches for the checked credential patterns.
  The initial prepared index was about11.25MB including the reference PDF.
  This pattern scan is not a guarantee that arbitrary text cannot be sensitive.
- The Python/model research status is unchanged: no new photo processing,
  synthetic variants, MST calibration, correction-tree fit or runtime adoption.

The detailed staging review is local under
`outputs/repository_maintenance_20261104_v1/`. A new clone contains source,
tests and research documentation, but not the local proposal PDF, separately
licensed datasets, model weights, local SDK/environment or generated evidence.
Experiments requiring those artifacts need the documented local setup.

## 5 November continuation

Two normal HTTPS pushes of the initial checkpoint hit HTTP408; SSH port22 also
timed out. An API publication attempt was interrupted before a branch update;
the remote was verified still at `8f08284`. The unpublished local commit
`efb1f81ef5fc9f5adfb43767442649cdc38be29c` is preserved at the local branch
`backup/pre-push-efb1f81`. A soft reset to the unchanged remote parent preserved
all working files and staged source work for a smaller source-only checkpoint.
The local proposal and JDK stay on disk and are ignored, not deleted. The backup
branch is not part of the requested upload. Final remote/local commit equality
must be verified before reporting publication complete. No research tests were
repeated for this transport/ignore-rule continuation; the973Python/18JVM results
above remain the latest maintenance checks.

## Next development work

Resume the already identified same12-source FFHQ mask/support feasibility check
after repository maintenance. ITA-to-MST remains deferred for source work and
retained in the eventual full method. No new dataset scope, panel approval or
claim of a finished correction model follows from this repository update.
