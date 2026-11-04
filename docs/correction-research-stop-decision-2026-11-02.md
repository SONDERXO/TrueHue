# Existing-data decision: stop before another training run

2 November 2026. User authorised checking whether existing labelled photographs
can support the retained method. The saved evidence already answers the current
readiness question. This closes that check; another inventory, saved-mask replay
or repeated old-subject fit would not supply new measurement-validity evidence.

## Simple answer

We have photos and labels, but no admitted matching FaceOcc calibration cohort.
Do not start MST calibration or correction training now. This does not mean all
photos are bad, that the method is impossible, or that recruitment is mandatory.

## Evidence supporting the stop

- outputs/faceocc_mst_feasibility_v1/decision.json: 33 MST-E attempts, 23 technical
  measurements, ten failures, four people at categories 2/4/5/9, zero admitted.
  Each measured category has one person, so these rows do not support evaluation
  on a different person of the same category.
- outputs/faceocc_development_readiness_v1/eligibility_ledger.json: technical
  success is not evidence that selected pixels are actual skin. Four completed
  human challenge reviews were FairFace qualitative comparisons, not admission
  of the labelled MST-E cohort. Do not transfer them.
- The 393 older features use the previous measurement method and cannot fill
  gaps in FaceOcc measurements. The potential 19-person inventory is not an
  admitted/prepared cohort; categories 7/10 still have only one person each.
- Reference-source checks have not supplied verified true-colour portraits or
  matching MST. Photographic synthetic restoration can be useful without true-
  colour truth, but cannot bypass the missing retained-method MST component.

## What must change before revisiting

1. Evidence tied to exact labelled photos/current masks that the measurement
   selects usable skin, with hair, coverings, glasses and harmful skin loss
   assessed. Minimum pixel count and assistant inspection alone are insufficient
   under the existing admission policy. No approval of unsampled photographs by
   association with a reviewed person.
2. A permitted cohort with person grouping, lighting/exposure/duplicate records
   and a justified limited scope. Existing exposed people can support disclosed
   development, not invented untouched validation or ten-category support.
3. One evaluation protocol with a justified adequacy criterion before outcomes,
   subject-held evaluation, same-row baseline and preserved failures/holds. No
   automatic promotion from a better mean error or arbitrary accuracy target.

These requirements come from the already recorded bounded-development plan,
not a new adviser gate or demand for a large annotation batch. No new batch,
participant recruitment or external contact is activated. If a manageable source
of actual-skin admission evidence cannot be established, this research path
remains blocked; do not keep proposing another small dataset/fit as a solution.

## Actions now

Keep correction masks, fixed FaceOcc candidate, existing runtime models, data
roles and all prior failures unchanged. Retain ITA + calibrated MST + facial
statistics to decision-tree gamma/red/blue correction. Reliable MST mapping and
automatic correction remain unfinished. Stop further calibration/training and
repeated readiness audits until new evidence addresses the conditions above.
Do not silently divert to phone testing or packaging as correction-model progress.

This is a stop decision on existing evidence, not a new experiment, method change
or panel approval. No pixels, inference, fitting, tests or package regeneration.
Prior evidence and panel records remain unchanged. The next conversation should
explain the missing evidence plainly, rather than promise another check of the
same records. User explicitly requests simple explanations by default.
