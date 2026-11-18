# Broader source preparation: first stage — 8 November 2026

Prepared a bounded route toward more independent development examples instead
of fitting another variation on the same22clean originals. **No new correction
model was fitted.** The initial measurement screen provides83parent-stage passes
from96new development photos; final masking and skin validity remain unresolved.

## Why this is the next development route

The current aligned full model uses227conditions but only22clean-reference
photos from10publisher groups. Derivative conditions do not provide227independent
examples. Recent feature, gate and calibration changes repeatedly preserve
fitting cleans but harm unseen cleans. Greater source diversity is worth testing;
this does not prove the small cohort is the only cause or that expansion will fix
it. Earlier unsuccessful source expansions remain recorded evidence.

This is not a new dataset search. It uses the already received, permitted
Stellenbosch release. The thesis goal remains synthetic photographic restoration,
not recovery of physical skin reflectance. No new participants, annotations or
neutral-colour reference collection is made mandatory.

## Metadata and separation

Existing release metadata lists285publisher groups.28appear in the three known
image-selection plans/latest exclusions;257do not. A broader check found no
direct matching candidate source records in85canonical existing metadata files.
The120candidate source hashes have no exact cross-publisher duplicates in the
release inventory. These checks are not universal exposure, perceptual-duplicate
or verified-identity certificates.

Froze40candidate groups before opening their photos:10per descriptive source-score
interval[1,3),[3,5),[5,7),[7,9), using deterministic SHA256 selection. Eight per
interval are development candidates; two per interval form a closed candidate
holdout. Three fixed front-facing conditions per group give96development and
24holdout photos. This40group budget is an engineering preparation choice, not
a statistical power calculation or the proposal's final70/15/15partition.

All four groups in[9,10]were previously used, leaving no fresh group in that
highest interval. Do not claim fresh all-tone evaluation. The intervals are
descriptive continuous-score bands, not rounded integer MST categories.

## Development-only screen

Opened only the96development photos. The24holdout photos remain byte-unread.
Used the unchanged aligned parent pipeline: actual-input YuNet.85single anchor,
native1.5crop, raw parser, landmarks/anatomical exclusions, nostril guard and
1000processing-pixel minimum. No CLAHE, detector fallback or threshold change.

| Descriptive interval | Parent passes | Attempts |
| --- | ---: | ---: |
| [1,3) | 22 | 24 |
| [3,5) | 23 | 24 |
| [5,7) | 19 | 24 |
| [7,9) | 19 | 24 |
| Total | 83 | 96 |

Twenty-one of32groups have all three conditions pass the parent stage. The
13failures are retained:7insufficient-skin-pixel failures,4no-overlapping-skin
failures,1degenerate-geometry failure and1initial face-count failure. There were
95parser forwards and no FaceOcc forwards. The screen did not replace failed
sources or change their roles.

Parent passes represent46–1020selected native grid locations despite passing the
1000pixel check in an enlarged processing frame. They are not83scientifically
qualified photos, final masking passes or correct-skin annotations. Visual
inspection of32fixed first-condition cases confirms broad masks in some photos
and fragmented or forehead-only support in others, plus uncertain beard/glasses
boundaries. The sample is fixed by condition, not selected for successful outcomes;
the remaining64photos were numerically verified, not all visually inspected.

## Verification and artifacts

- Scripts597–599 inventory, freeze and verify metadata/roles/hash duplicates.
- Script600 prepares only development parent measurements; script601 verifies
  cached evidence without another model call.
- Verified95native crops/256resizes and90saved parent masks, statistics and native
  projections; all96attempt/role records and139bound source hashes checked.
- Viewed all32fixed boards in8contact sheets. No manual annotations were created.
- The focused sampling/crop/semantic/nostril suite passed23tests in2.87seconds;
  these are software checks, not mask accuracy or correction-model validation.
- Private outputs: `training_diversity_metadata_audit_v1`,
  `group_diversity_candidates_v1`, `group_diversity_parent_screen_v1` under outputs.

The proposal, appeal letter, previous experiments, current correction model and
apps remain unchanged. Source permissions and admission flags are unchanged.
No cloud inference, contacts, uploads, publication, commit or push.

## Next step and success conditions

Complete the unchanged cached-alignment/raw-FaceOcc stage for the83parent passes,
retaining the other13as unavailable, and assess final masks/native support before
generating distortions or fitting. This is the next bounded preparation step,
not permission to declare all technical successes clean skin.

Only after that evidence supports a useful development cohort should a matching
training protocol be frozen. It must keep every source's derivatives together,
retain prior failure cases, preserve the closed holdout, and test zero unwanted
clean edits together with distortion recovery. Do not open the holdout for model
repair or generate a large synthetic batch by default. More groups alone do not
guarantee the correction decision problem is solved. No completion date is yet
substantiated.
