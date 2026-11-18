# Why the expanded model lost useful corrections

8 November 2026. Saved-output diagnosis only; no new training or image-model inference.

The expanded model leaves several distorted photos unchanged because its final decision branches contain a mixture of clean and distorted training photos. In those branches, leaving everything unchanged has the lowest total training error among the existing actions. The clean-photo restriction also rules out all other actions there.

## What we found

| Existing evaluation set | Previously beneficial cases now lost | Newly beneficial cases |
| --- | ---: | ---: |
| Development core | 44 | 0 |
| Later core | 34 | 1 |
| Development stress | 5 | 0 |
| Later stress | 8 | 0 |

These are RGB reconstruction benefits in the fixed scoring regions, not judgments of visual quality. All 91 lost cases were identified from the saved outcomes, rather than selected as independent validation examples.

- All **78 lost core benefits** involve overexposure: 27 exposure-only, 26 warm-plus-overexposure and 25 cool-plus-overexposure conditions.
- The **13 lost stress benefits** involve the stress colour condition.
- All 91 cases now receive the identity action: leave unchanged.
- All reach a final branch at the existing maximum depth of three. Those branches also contain clean training photos, including newly added originals.
- The previous corrective action is still in the action list, unchanged. This is a change in decisions, not removal of the available correction.
- In every affected branch, identity is the only action allowed by the clean fitting constraints.
- Crucially, identity also has the lowest total training error **without** those constraints. The previous action has no lower aggregate cost. Simply removing the clean restriction would therefore not change the best action in these existing branches.

The later core count falls from 84 to 51 beneficial outcomes because 34 benefits were lost and one was gained; 50 were retained. Development retains 62 and loses 44. The totals reconcile with the completed comparison.

## What this means for development

The saved trees group together photos that need different treatment. Their fixed, shallow decisions favour the safe unchanged result in these mixed branches. This explains the observed action change, but does not prove that more depth, another feature or any alternative model will generalise safely. It also does not establish that masking or the action choices are adequate for every input.

The next justified step is a bounded **separability audit** of these saved mixed branches: check whether the existing features distinguish the clean fitting photos from the overexposed fitting photos, using the saved rows and costs. This can establish whether a useful clean-preserving subdivision even exists within the available features, before proposing a training change. It is not permission for a threshold, feature or capacity sweep, and must not use the closed holdout to design a fix. Any oracle subdivision result would be exploratory training evidence, not a validated model.

The expanded candidate remains frozen and unadopted. The eight-group, 24-photo holdout remains byte-unread. Mask fragmentation, visible correction boundaries, previously exposed evaluation groups and synthetic-only distortion coverage remain limitations.

## Verification and artifacts

Script 618 records all 91 losses, both decision paths, unchanged actions, leaf membership, clean blockers, feasible actions and total training costs. Script 619 independently replays the 91 candidate routes, sums all 14 action costs with scalar calculations, checks clean feasibility and verifies the bound source hashes. All checks passed; no fitting, rendering or source-image reads were needed.

Private output: `outputs/expanded_lost_benefit_diagnosis_v1`. This diagnosis adds no new accuracy result and changes neither runtime nor demo behaviour. See the [comparison results](expanded-correction-training-results-2026-11-08.md).
