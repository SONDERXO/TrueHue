# Blinded development reference-suitability review

**Not in use.** User subsequently clarified that photographer opinions are only
needed after the correction model is finished and that a Google Form already
exists. Preserve this earlier protocol as history; do not collect local-form
responses or block model work on them.

28 October2026. The current correction candidates fail quality gates. Before
another learning experiment, obtain independent photographic judgments of the
ten reference images already used. This is a **development source-suitability
review**, not final corrected-image MOS, calibrated color truth or independent
test performance. No model outputs, MST estimates, source IDs, prior acceptance
labels or quantitative outcomes are shown on the reviewer pages.

Two photographers review all ten exact saved256reference frames independently.
Use pseudonymous reviewer codesP1/P2 and a fixed separately shuffled order. Images
and order are frozen before ratings. The private case/source key remains local
with the researcher; presentation blinding cannot prevent recognition of a
previously seen face or intentional inspection of local files. The pages do not
transmit images or ratings. No dataset uploading or messages are authorized.

For each reference, record: detail(adequate/limited/cannotjudge), illumination
(usable/strongcast_or_uneven/cannotjudge), occlusion(low/substantial/cannotjudge),
and overall reconstruction-reference suitability(suitable/uncertain/unsuitable).
Provide a reason for uncertain/unsuitable decisions. These are source-screen
categories, not1–5MOS ratings; do not average them into MOS. A photographer may
flag uncertain cosmetics/lighting without claiming to know intrinsic skin color.
Judge the visible processing frame, not an inferred full-resolution original.

Reviewers self-declare photographer status. Self-declaration is not independent
credential verification. They should use a consistent display and viewing
conditions, avoid discussing judgments until both exports are saved, and note
display limitations/recognition in their session notes. No calibrated-display
claim is assumed. The blank forms contain no default decisions or fake ratings.

Keep both original JSON exports, hashes, disagreements and reasons. Do not
overwrite user mask/scene reviews, retrospectively redefine the old cohort or
refit automatically. Any future eligibility policy or disagreement adjudication
must be declared separately; agreement is not automatically ground truth.
The existing two-photographer final expertMOS requirement remains unfinished
and must later use an appropriate frozen model/evaluation design. Until actual
photographer responses arrive, this package establishes readiness only.
