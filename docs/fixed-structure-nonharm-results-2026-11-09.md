# Fixed-structure nonharm comparison — 9 November 2026

The approved comparison is complete and independently verified. It fails the
unchanged joint acceptance criteria and is **not adopted**. Freezing the old
partitions retains the six benefits lost by the global refit, but constrained
actions become much weaker for other underexposed inputs. The final eight-group,
24-photo holdout remains byte-unread.

## Recovery and provenance

Read AGENTS.md, the session handoff, fixed protocol and scripts 665–669 before
recovery. `Get-Process python*` returned no Python processes before recovery.
The 11 per-configuration partial JSON files were present; the aggregate model,
verification receipt and evaluation folder were absent.

Script 670 preserves those files. It records their SHA256 hashes, replays the
approved leaf-action reassignment in memory using the unchanged script 665 code,
and requires exact equality with each saved configuration instead of rewriting
it. It then executes the outstanding final fitting/reserved-clean constraints,
756 prediction updates and final bound-source hash checks, creating the missing
aggregate. All partial hashes remained unchanged. Recovery provenance is in
`outputs/fixed_structure_nonharm_models_v1/recovery_PRIVATE.json`.

The original session's termination cause cannot be established from its lost
process session and incomplete artifacts. Recovery found no reproducible
constraint or source-hash failure. Script 665 itself was not edited or blindly
restarted; no output directory was deleted or replaced.

## Frozen comparison

Eleven existing configurations, zero new split fits, zero MST fits and zero new
target fits. Every old pre-veto split, threshold, child link and fitting-leaf
membership is retained. Each leaf uses the minimum summed saved RGB-cost action
that gives every fitting clean row zero cost and every colour-only fitting row
cost no greater than identity; ascending action index breaks ties. Eleven
pre-veto leaf actions change across the configurations. Internal traces remain
historical. The same reserved-clean veto and frozen facial exception apply.

Rows, roles, features, calibrations, actions, costs, scoring masks, correction
support and rendering are unchanged. Evaluation is the same 756 prepared
attempts. The aligned comparator remains the acceptance comparator.

## Results

Values below are development / later. Lower mean error is better.

| Check | Aligned comparator | Previous facial exception | Global nonharm refit | Fixed structure |
| --- | ---: | ---: | ---: | ---: |
| Usable clean edits | 2/22; 2/18 | 0/22; 0/18 | 0/22; 0/18 | **0/22; 0/18** |
| Core RGB MAE | 8.0287 / 9.7567 | 9.7302 / 10.3639 | 10.1310 / 10.9828 | **12.0396 / 12.5411** |
| Core beneficial conditions | 106 / 84 | 91 / 78 | 88 / 75 | **91 / 78** |
| Core RGB and DE harms | 1 / 5 | 0 / 0 | 0 / 0 | **0 / 0** |
| Stress beneficial conditions | 45 / 43 | 40 / 35 | 40 / 35 | **40 / 36** |
| Stress RGB and DE harms | 0 / 1 | 0 / 1 | 0 / 0 | **0 / 0** |

The core scoring denominators are 176 / 144; stress denominators are 110 / 90.
Benefit counts agree for RGB and CIEDE2000 in this comparison. The 14 failed
clean measurements remain separate no-op failures, not learned preservation.

Fixed-structure core CIEDE2000 is 4.6684 / 4.9352, above aligned 3.4406 / 4.1886
(the private result contains full precision). Development stress is unchanged
from the recent candidates: RGB 38.7874, DE 15.1600. Later stress is RGB 43.5718,
DE 16.7600; its DE still exceeds aligned 16.6843. Both cohorts' core error and
benefit requirements fail; stress benefit requirements fail in both cohorts,
and later stress DE fails. No acceptance criterion was relaxed.

There are zero scored regional RGB/DE harms in all six cohort/layer combinations,
and zero whole-scene RGB harms. These are reused exposed data, not an unseen-data
safety guarantee, dense mask validation or proof of true skin colour recovery.

## Changed outputs and visual review

Thirty-seven decisions change across 16 originals versus the previous facial
exception; 34 have reference regions and three do not. Of the 34 scored changes,
one improves RGB error and 33 worsen it relative to the previous candidate.
The other 719 outputs and their candidate metric dictionaries match exactly.

All six core benefits lost by the global refit are retained: the three
underexposure conditions for each of `case_01` and `eval_16`. Retaining a benefit
does not imply retaining its previous correction strength or mean error.

The known stress case `eval_02__stress_color_none` now uses the existing action
with approximately gamma 0.999966, red gain 1.040764 and blue gain 0.999937.
Its RGB error is 5.3059 versus input 6.6667 and previous 31.5307; DE is 4.3768
versus input 4.8420 and previous 11.7017. Unlike the global candidate's identity
decision, this is a small measured benefit.

Viewed all 37 changed boards on all 10 contact sheets using view_image. Many
underexposure outputs are darker than the previous correction. Partial facial
and neck support and visible boundaries remain. The review does not establish
dense mask quality or independent naturalness. Prior review is reused only for
the 719 outputs proven identical; no fresh review of every unchanged board is
claimed. A hash-bound review receipt is saved privately.

## Verification and artifacts

- Script 666 independently checked 11 configurations, 146 split nodes, 157
  leaves, minimum feasible leaf actions, 880 repeated clean constraints, 2,383
  repeated colour constraints, 220 reserved-clean occurrences and 756 predictions.
- Script 668 independently replayed all 756 pixel outputs, 560 regional metrics,
  756 scene metrics, protected/zero-alpha pixels, summaries, transitions and
  20,143 bound source hashes. Checks passed.
- Scripts 669/671 verified unchanged-output parity and recorded exhaustive
  changed-output review, sheet/board hashes and the six recovered benefits.
- These counts include repeated fitting occurrences, not independent photos.

Private model artifacts: `outputs/fixed_structure_nonharm_models_v1`.
Private evaluation, assessment, attribution and review artifacts:
`outputs/fixed_structure_nonharm_comparison_v1`. Original partials and prior
candidates are preserved. No app integration, DINO execution, new experiment,
holdout access, contact, upload, commit or push occurred.

## Proposed next step; not executed

The evidence rules out leaf-action reassignment alone as a sufficient repair
on these frozen partitions. A possible intervention is **local constrained
partition refinement inside the conflicting leaves**, keeping clean and colour
nonharm rules and the action library fixed. Before any such fit, audit the saved
fitting vectors and costs to determine whether the colour blockers can actually
be separated from exposure rows using the existing features. Use fitting data
to assess separability, not evaluation outcomes to select thresholds. If the
features do not separate them, do not run a depth sweep or relax constraints.

This is a proposal requiring a specific protocol before new fitting; no local
split search, feasibility sweep or new experiment was executed. The present
candidate remains frozen and does not qualify for final-holdout access.
