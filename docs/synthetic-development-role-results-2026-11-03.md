# Normal examples, clipping stress tests and clean controls

3 November 2026. User authorised defining/checking this separation on generated
images. This completes that bounded development check, not photo processing,
training admission, final recipe adoption or thesis-panel approval.

## Rules fixed before the check

Script404 writes a versioned protocol before its six new target fits. Roles are
assigned from the forward operator and image/support consistency, never by
selecting cases with favourable fitted correction errors.

| Role | Rule | Intended future use, subject to admission |
|---|---|---|
| Clean control | Image exactly equals reference and forward clipping is zero | Check unnecessary changes; neutral target[1,1,1] for the three-control renderer |
| Core candidate | Nontrivial change, no reported preblend clipping, outside support unchanged | Candidate for normal development examples; not certified recoverable or admitted training data |
| Clipping stress | Forward transform exceeds[0,1] in any selected channel | Retain as stress evidence and evaluate separately; do not silently blend into normal training or discard |
| Invalid support/clean claim | Outside-support change or inconsistent clean evidence | Retain the failure; no valid pair/neutral target claim |
| Unchanged distortion | Nonclean recipe rounds to unchanged image | Retain as a no-op, not evidence of successful recovery |

Clipping requires forward-operator evidence before blending. Pixel values0/255
alone do not prove clipping. RGB8 rounding, repeated output levels, approximate
target fits and boundary blending can still lose information without preblend
clipping. Every role has training/dataset admission false. There is no new
quality threshold or automatic acceptance based on solver convergence.

## Explicit implementation change from the paper

For initial core **exposure-only** probes, use direct power x**(1/g) for under-
exposure and x**g for overexposure, with the existing three gamma magnitudes.
Remove extra offsets, contrast and additive colour from these core probes.
Retain the full directional offset/contrast/colour recipe as a separately
reported experiment; its clipped cases are stress cases.

This is a documented decomposition of Table2, not a claim that gamma alone
implements its complete distortion. Table2/full-composite cases remain saved.
The normal colour/combined recipe is NOT settled by this check. Do not describe
the whole colour-correction training distribution as complete. Proposal baseline:
PDF60/printed53,62/55,63–64/56–57; scope/source checksum is recorded in
`proposal-scope-validation-2026-11-03.md`. The original photographic-restoration
goal, ITA/calibrated MST/facial statistics and three tree outputs are retained.

## Fixed generated-data results

Evidence: `outputs/synthetic_development_roles_v1/`. Script404 reused all18
saved script403 cases without refitting and added exactly six power-only
exposure probes, one per group/direction. No replacement, strength sweep or
failure deletion. The same saved neutral ramp and alpha were used, not skin
photos or subjects with MST labels.

There are24 retained cases: **three clean controls, six core candidates and15
clipping stress cases**. These counts are diagnostic cases, not subjects,
training allocations or chosen future proportions. All15 nonclean parent cases,
including colour-only examples, clipped on this ramp; none were silently lost.

| Gamma-magnitude setting | Core under target-fit error | Core over error |
|---|---:|---:|
| Light | 0.048 | 0.056 |
| Medium | 0.133 | 0.137 |
| Dark | 0.242 | 0.206 |

Errors are average absolute RGB8 channel codes over positive-alpha pixels,
including faded boundaries. They are local target-aware fitting residuals,
not decision-tree predictions, CIEDE2000, real-photo validation or proof of exact
inversion. The dark under probe creates48 selected channel samples at an endpoint
from interior reference values through rounding despite zero preblend clipping.
That loss is reported, not renamed perfect recoverability. Stress errors remain
unchanged in CSV/JSON, including the prior30.231 combined dark-under residual.

## Evaluation and stopping rules

For a future authorised dataset cycle, generate the declared cases per admitted
source before judging model outputs. Keep every attempted case and failure;
do not reduce severity or replace sources in response to a target-fit result.
All derivatives of one source/person must stay in the same allocated split.
Reference images may supply supervision and metrics, never inference features.
Input ITA/MST/statistics still require the matching measurement contract.

Report core restoration, clean changes and stress behaviour separately, with
case counts/failures and optional clearly weighted overall summaries. Do not
report only the successful core subset as full-system performance. Target-fit
failures remain holds with no fabricated parameters, not candidates for silent
refitting. Roles alone do not establish actual-skin masks, reference quality,
person separation, MST reliability or an adequate evaluation sample.

Stop here without new photos/training or another formula search. Remaining
pretraining choices include normal colour/combined distortions, actual source
and support admission, compatible MST, justified evaluation scope/adequacy and
the final sampling distribution. No invented split counts, core/stress ratio
or error threshold is adopted.

## Verification

85 focused tests passed in2.81seconds across role rules, both exposure recipes,
existing recipes, Table2 contract, direct gamma, old/new target construction and
seamless blending. This is not a full-suite run. Six new target fits and six
independent arithmetic replays were completed;14 new saved arrays round-tripped
exactly. CSV case IDs match JSON. All18 parent cases/outputs were reused unchanged;
parent artifact/source hashes and the script399 seven sources/seven parent
manifest hashes verified unchanged. Zero photos, ML inference, tree/MST fits,
dataset admissions, runtime changes or contacts. Submitted proposal unchanged.
