# PPR10K bounded access recheck

11 November2026. The user authorised checking availability and retrieving the
already frozen16pairs only if bounded access works. Existing-datasets-only,
no-local-copy and no-capture decisions remain unchanged.

A small check received206responses for suffix and22-byte metadata ranges on
both existing publisher source and target-A archives. Only4,917access-page bytes
were consumed; archive response bodies were closed. Its recorded status
bounded_access_available describes those probe headers only. It did not prove
that directory/member-range retrieval would work or that the16pairs were local.

One new retrieval attempt was therefore made in an isolated v4folder, retaining
all old attempts. It kept the SAME16groups/32files,32,022,050-byte cumulative cap,
4MBper-read cap, CRC/size checks and rejection of whole-archive200responses.
The public confirmation and initial ZIP metadata access succeeded, but the
central-directory read did not return the exact required partial response.
The reader rejected it before consuming that response body and stopped. No
selected TIFF/photo member was acquired. No automatic retry, expanded cap,
full archive, mirror or changed roster followed.

**Current outcome: selected-batch access remains unavailable.** The earlier
publisher quota is preserved as an earlier diagnosis; this attempt records an
exact-range failure and does not independently identify the latest response as
quota HTML. Small successful probes cannot be described as successful file access.

Files: outputs/ppr_bounded_availability_check_v1/result_PRIVATE.json and
outputs/existing_ppr_additional_evidence_v4/acquisition_PRIVATE.json. The v4
attempt is incomplete/preserved, not a ready data package. No previews, source
quality, registration, supports, targets or training eligibility are inferred.

The planned next inspection is conditional on actual selected files becoming
available through bounded publisher access or an existing local copy. The user
already confirmed no local copy; do not ask again or request a full archive.
A later availability change must be checked and recorded separately. No retry
schedule/background job is selected by this report.

No new photos, masks, annotations, image-model calls, target/MST/tree fits,
contact/upload/commit/push, runtime or Android changes. Existing experiments
remain closed. Final24 and older locked image allocations remain byte-unread;
all previous outputs and decisions preserved. Correction quality remains unfinished.
