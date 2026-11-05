# Fixed FFHQ mask/support feasibility protocol

5 November 2026. Recorded before new inference. Source work is authorised;
ITA-to-MST remains deferred. This is a bounded development diagnostic, not
training, calibration, reference approval or runtime adoption.

Use exactly the twelve records, in order, from
`outputs/ffhq_source_preparation_v1/attempts.json`: 54632,39568,29617,29863,
16061,52445,32685,53146,48879,49131,59807,46795. Verify original hashes and
selection before running. Retain every failed stage without replacement.

Reuse the existing whole-frame 256x256 INTER_LINEAR measurement path, YuNet
confidence .85, exactly-one-face guard, existing landmark helper (including its
existing ordered margin fallbacks), pinned semantic parser, anatomical and
nostril exclusions. No new crop/threshold/model search. Save face box,
landmarks, categories, parent measurement mask, aligned FaceOcc input and matrix.

Build correction support independently from the parent facial measurement mask
using the existing full-face and associated predicted-neck implementation,
then enclosed-hole filling and inward smoothstep alpha with width
max(2,ceil(.03*parent facial-mask width)), matching script350. FaceOcc must not
shrink the correction region. Save correction/neck masks and exact floating
alpha. Show fixed .85/1.05/.95 operator settings only to inspect boundaries;
these are illustrative, never trained predictions. Verify neutral identity,
zero alpha and unchanged demonstration pixels outside support.

Run one fixed CPU FaceOcc forward per available aligned parent, using the
existing isolated environment, pinned weights, existing ImageNet normalisation
and strict logit>0 inverse-mapped validity veto. Save logits. Finalise through
the preferred experimental service using saved logits, verifying exact replay
and that no pixels were added outside the parent mask. Keep minimum1000 pixel
guard unchanged. Save the candidate mask and report, including failed masks.

Inspect all twelve boards and originals as needed. Record correction outline,
visible neck/crop, hand/object coverage, beard/glasses/hair contamination or
skin loss, pose and lighting uncertainty separately. Enclosed occluders belong
to correction by design but are unwanted in measurement. A missing neck is
unavailable support, never generated or inferred from processing success.
Assistant observations are qualitative and separate from human approval;
no annotation workload is activated. No numeric accuracy/acceptance threshold
is invented. Technical status and visual concerns are separate fields.

Hash dependencies, source images, input manifests and all pinned historical
sources/parent manifests before and after. Refuse output overwrite. Preserve
existing evidence and originals. Produce a local read-only gallery, per-case
ledger and results document. Record proposal departures in the panel register.
Stop after this diagnostic: no new photographs, variants, target fitting, MST
assignment/calibration, tree fitting, model adoption, publication or contacts.
