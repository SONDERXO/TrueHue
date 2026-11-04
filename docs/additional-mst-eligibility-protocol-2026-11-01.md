# Additional MST-E eligibility screen

1 November 2026. User authorised the next eligibility check. No calibration or
tree fitting. This is a bounded screen, not admission of all337 photographs.

Freeze all337 unique subject/image keys for subject_1/9/11/10 from official
metadata, preserving repeated-key metadata separately. Assert consistent MST and
lighting for each repeated key; preserve pose differences. Pre-pixel metadata
inspection found conflicting mask annotations: retain their sorted combined
values as a separate ambiguous stratum rather than choosing one or dropping it.
Exclude no difficult image by prior review, colour, result or visible quality.

To bound review effort, select at most two keys per subject × recorded lighting
× recorded mask-status stratum, ranked by
SHA256('additional-mst-eligibility-v1/'+image_id). Selection precedes pixel reads.
At most two attempts per occupied stratum (including ambiguous mask strata),
no replacement after failure. All other keys remain
not assessed. Recorded mask status is a stratification field, not verified
occlusion truth. Read all images of only these selected keys once using the
unchanged nostril-measurement contract1bdef31c. Save masks, maps, landmarks,
source hashes and attempts. No old-ITA fallback, retry, new thresholds or fit.

Create review boards for every successful selected attempt: original, measurement
overlay and binary mask. Programmed exclusions and replay must pass but do not
prove actual skin. Inspect each for selected hair, beard, glasses, coverings,
eyes/brows/lips and background. Record diagnostic findings separately from user
approvals. Technical failures remain failures. Ambiguity means hold, not pass.
No colour-reference or exact-MST reliability claim follows a visually clean mask.

Stop after this sample. Report attempted/success/failed/not-assessed counts by
subject and stratum, failures and visual concerns. Every unreviewed measurement
remains unadmitted. A clean sample cannot admit unsampled photos or establish
final performance. All four subjects have historical exposure; no untouched
claim. No reserved correction data or SCIN images are processed. A separate
justified protocol is required before broader processing or any fitting.
