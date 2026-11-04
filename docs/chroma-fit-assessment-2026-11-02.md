# CHROMA-FIT assessment: promising, with important limits

2 November 2026. User authorised examination of this dataset lead. The full
published paper was downloaded and its examples/distribution inspected, unlike
the earlier abstract-only access check. No dataset release, contact or model work.

## Published evidence

209 people; approximately 2,300 photos; forehead/forearm instrument readings.
MST assignments are derived from measured colours and aggregation, not expert
MST consensus. Figure8b (PDF page6, printed1175) shows category counts
3:1,4:14,5:151,6:14,7:23,8:6, with none at1/2/9/10; sum209 verified.
Indoor capture uses office lighting; outdoor illumination varies. Makeup/sunscreen
could affect measurements. Example eye bars were added for publication.

Source: [Pangelinan et al., WACV Workshops 2024](https://openaccess.thecvf.com/content/WACV2024W/DVPBA/papers/Pangelinan_The_CHROMA-FIT_Dataset_Characterizing_Human_Ranges_of_Melanin_for_Increased_WACVW_2024_paper.pdf),
sections3–4 and Figures7–8. These are paper descriptions, not verified release contents.

## Implication for TrueHue

Worth pursuing for comparing image-based measurements with instrument evidence.
Do not equate instrument readings with a pixelwise corrected photograph: local
skin measurements cannot prescribe a uniform RGB target for every facial pixel.
Raw measurement conditions, white point, colour conversion and anatomical site
must be understood. Forearm values should not silently become facial targets.

The published category distribution does not solve our extreme-tone coverage
problem. Mixing its measurement-derived labels with MST-E labels would need
explicit provenance and a justified compatibility analysis; it is not a new
automatic ITA-to-MST lookup. Do not adopt its swatch matching as our calibration.
Do not make a new result-dependent subset, refit or claim more people guarantee
reliable correction. Treat possible measurement evaluation and correction-target
qualification as separate questions.

## Access and next step

Rechecked [official publication page](https://research.fit.edu/idl/publications/)
and [official contact page](https://research.fit.edu/idl/contact-us/), plus public
release searches. No verified download/recipient licence identified; this does
not establish that data are unavailable. The contact page identifies Michael
King and michaelking@fit.edu. Nothing sent.

Recommend an access/clarification inquiry asking about current release, permitted
research use, raw measurements and subject links, label methodology, capture/colour
documentation, uncensored image availability and current category distribution.
Contacting anyone requires explicit user instruction. Before actual adoption,
record the proposed dataset role/method implications in the panel register.
This assessment is evidence on an existing lead, not an adopted method change.

Saved paper, rendered publication examples, extracted text, official pages,
assessment.json and checksums: outputs/chroma_fit_assessment_v1/. Local publication
inspection gallery: review.html. Initial console text extraction hit Windows
encoding; rerun explicitly in UTF-8 succeeded. No dataset-photo acquisition,
processing, fitting, runtime change or pytest run. Frozen package sources unchanged.
