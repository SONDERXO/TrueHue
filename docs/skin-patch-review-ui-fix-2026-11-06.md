# Skin-patch review controls — 6 November 2026

User reports Save patch does nothing. The precise user-browser cause has not
been observed. Original v1 remains preserved. New
[v2 review](../outputs/stellenbosch_skin_patch_review_v2/review.html) adds default
rectangle dragging, retains click-polygon mode, brings status feedback into a
sticky visible panel and embeds its script in the HTML. A startup message now
distinguishes loaded controls from an HTML preview that does not execute scripts.
Use Edge/Chrome if an IDE preview leaves the loading message visible.

The source images, six-case manifest SHA, export schema and browser storage key
remain unchanged. Already saved v1 patches can be imported from a downloaded
draft; existing browser persistence depends on browser and file-origin policy.
Unfinished vertices from v1 were never persisted; no claim of their recovery.
Patches still require Save patch, and unavailable outcomes remain supported.

Script474passes the synthetic DOM suite, additionally exercising rectangle
drag, release and saving alongside polygon input, status protections,
persistence and export/import. JS syntax passes. No actual browser render or
reproduction of the user's particular failure is claimed. No reviewer export,
measurement, mask inference or fit is created. V1 and earlier actual point
review remain unchanged. Private dataset terms continue to apply.
