# FFHQ correction development source checkpoint

5November2026. User requests committing and pushing accumulated work. The work
is packaged on `ffhq-correction-development-20261105` from the published main
checkpoint917f89eb3659c80e940faab6c8a500cc5e1aa88c. This preserves the project's
work-branch rule; no main merge, force push or remote history rewrite is requested.

This source checkpoint includes scripts414–428, the object/clear-lens/reusable
preview modules and launcher, photographic target/support-shift diagnostic
modules and tests, protocols/results/eligibility/correspondence records, the
current guide and panel register. Development remains unfinished. No learned
correction model or reliable MST mapping is adopted. The user reports sending
the Stellenbosch inquiry; archived unsent draft/evidence bytes stay preserved.

Publication scope is code and documentation only. Local original photos, models,
environments, SDKs, generated galleries/results and frozen evidence stay on disk
and ignored. The submitted proposal and working thesis drafts are unchanged.
Source-only collaborators require the documented optional assets for research
execution; local gallery links are not evidence that generated images were pushed.

## Verification

The fresh broader Python run passed1002tests in18.64seconds, excluding
`tests/test_demo_desktop.py` for the known Tcl/Tk environment issue. This is not
an unqualified full-suite pass, a fresh dependency installation, new Android
validation or scientific model validation. Command:

```powershell
venv\Scripts\python.exe -B -m pytest tests/ --ignore=tests/test_demo_desktop.py -q -p no:cacheprovider --basetemp=tmp/commit_validation_20261105_v1 --tb=short
```

The initial sandboxed attempt had881passes and121temporary-fixture permission
errors. Rerunning with the fresh workspace temp path and permitted execution
resolved those errors without source changes. No tests were dropped beyond the
already documented desktop GUI file. No recursive cache cleanup was performed.

Before staging, all4192frozen-input hashes from the latest source investigation
were verified. The initial47changed source/doc files totalled327,124bytes; none
exceeded1MiB and no known private-key/GitHub/AWS/OpenAI credential patterns were
found. Root README/checkpoint notes are added after this initial inventory.
Staged content and blob sizes are checked separately before commit.

The staged whitespace check identifies one trailing space on line56 of the
already frozen `scripts/421_verify_reusable_correction_preview.py`. Its exact
bytes are retained rather than invalidating saved experiment source hashes for
a cosmetic edit. No source logic or global/repository whitespace setting is
changed; the single known exception is checked separately from other errors.

The sandbox initially blocked GitHub networking and Git ref writes. Approved
execution verified remote main still matched917f89e and created the work branch.
Final commit and remote branch SHA verification are recorded locally under
`outputs/source_checkpoint_20261105_v1/publication.json` after successful push.
This document alone does not claim that publication succeeded.
