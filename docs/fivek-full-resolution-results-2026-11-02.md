# FiveK two-source full-resolution decision

2 November 2026. User explicitly authorised full-resolution inspection of the
two prominent-face sources from the fixed six. Exact IDs and rendition C were
frozen in outputs/fivek_full_resolution_v1/plan.json before downloads. Two TIFFs
only, maximum 150 MiB each, no source replacement or new editor selection.

## Result: stop before reference admission or correction training

Both acquired successfully. a4526-_DGW7879 is 2832 x 4256 RGB16 (57,253,542 bytes);
a2389-_I2E6088 is 3504 x 2336 RGB16 (44,403,572 bytes). Both embed the same 940-byte
ROMM profile, SHA-256 0a8ef7d1d958d98225b3b71d93d9e8e3cecd9c302e014973d025d2a977ecf27c.
Original files remain unchanged. No DNG, alternate edit or additional photo acquired.

| Source | Assistant full-resolution inspection | Disposition |
|---|---|---|
| a4526-_DGW7879 | Clear skin texture; prominent face; beard/moustache; unequal facial shading and nose highlight; scarf covers most neck | Potential photographic reconstruction diagnostic only, no current reference/measurement admission |
| a2389-_I2E6088 | Prominent face but pronounced grain/noise and softer detail; glasses bridge; cup/hand close to face; uneven cool/green-looking rendering | Hold as clean reference; preserve as difficult diagnostic |

These are observations, not measured colour errors or professional judgments.
Facial hair alone is not an exclusion: whether the measurement selects actual
skin is unassessed, because no mask inference was performed. Good visible detail
in the first photo does not supply a neutral-colour reference, MST label or
matching calibrated MST. A local highlight is not proof of sensor clipping.
Neither source has independent true-colour evidence established by this check.

The practical answer is that the first photograph might be useful for a narrow
photographic-reconstruction demonstration, but **this pair does not justify the
retained-method training cycle**. Do not fit on the better-looking photograph,
silently replace the other, or start another sample automatically. This does not
establish that FiveK as a whole is unsuitable. No new user annotation required.

## Colour and detail inspection

Used embedded ICC profiles, not assumed sRGB. Viewing copies quantise RGB16 with
round(value/257), then Pillow/LittleCMS converts ROMM to sRGB with relative
colorimetric intent 1. Embedded sRGB profiles are included in the PNGs. This
8-bit display path is explicitly not a colour-accurate 16-bit numeric training or
evaluation conversion; gamut mapping/quantisation can affect displayed detail.
A later numeric experiment would need its own precision-preserving conversion
contract. Original source samples were never replaced by these displays.

Inspected full-frame views and manually selected detail rectangles; coordinates
saved in technical_inspection.json. Rectangles include features/hair/background,
are display crops only, and are not skin masks or training supports. Original
uint16 exact-zero/full-scale channel fractions are recorded for the whole image
and upper endpoints for the detail rectangle. Such endpoint counts in edited
ROMM pixels cannot prove actual-skin clipping, sensor saturation or colour accuracy.
No numerical blur/skin-quality admission threshold was invented after inspection.

## Evidence and method record

outputs/fivek_full_resolution_v1/review.html includes full-frame/detail views;
plan.json, acquisition.json, technical_inspection.json, decision.json and
sha256.json bind sources and decisions. Both licence texts retained. Both images
map to the publisher Adobe/MIT list. Copyright Adobe / MIT; research use under
the saved terms. Cite MIT-Adobe FiveK, Bychkovsky et al., CVPR 2011.

Verified exact two-file membership, decoded RGB16 dimensions, original download
hashes and all artifact hashes. No inference, measurement feature computation,
calibration, distortions, correction fit, runtime change, participant recruitment
or external publication. No pytest run for source inspection; runtime unchanged.

This continues the proposed external reference investigation recorded in the
panel register, not adoption of FiveK as training data. Preserve FairFace/SCIN
roles, MST-E allocation, reserved evaluation locks and ITA + calibrated MST +
facial-statistics decision-tree gamma/red/blue method. Reliable mapping and
automatic correction remain unfinished.

Primary source: [FiveK publisher, formats and edit objective](https://data.csail.mit.edu/graphics/fivek/).
