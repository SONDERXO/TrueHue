# Reviewed cheek regions: measurement decision

28October2026. User accepted frame7's revised squares ("Better/ Continue
what's next."). Recorded that confirmation separately against the exactV2
coordinate hash. Earlier user acceptance covers the other11frames. Original
V1coordinates, scores and uncertainty flags remain preserved. This is approval
of visible patch placement, not mask accuracy, neutral lighting or model quality.

Recomputed all12frames using the frozenV2points. Both revised frame7patches
are fully selected by the existing mask. Total selected pixels remain204/216:
the missed patch in frame0and partial patch in frame11remain. No production
pixel-count threshold was relaxed;18-pixel summaries are sparse QA only.

## Same person under different photographed conditions

Four same-subject pairs occur naturally in this fixed12set. No pair was selected
or discarded according to results.

| Subject / official MST | Recorded lighting pair | Absolute ITA difference, reviewed patches | Existing full mask |
| --- | --- | ---: | ---: |
| subject16 / MST1 | well / poorly lit | 120.146 | 73.167 |
| subject6 / MST5 | poorly / poorly lit | 2.887 | 4.576 |
| subject4 / MST9 | poorly / well lit | 37.891 | 32.623 |
| subject3 / MST6 | poorly / well lit | 84.868 | 73.853 |

The three differently labeled lighting pairs all have larger patch differences
than full-mask differences. These are sparse exposed development observations,
not a controlled lighting experiment or proof about all cheek estimators.
Nonetheless, they do not support adopting these patches as a stable replacement.
Coordinates need not correspond to identical physical skin across poses;
highlights, spatial illumination, native detail and small patch size also matter.
User-confirmed visible skin is not illumination-normalized skin color.

## What this rules out as the immediate fix

Moving squares away from glasses improves the reference placement. It does not
by itself validate an automatic cheek locator, improve MST estimation or add
independent subjects. No new estimator, mask or lookup was adopted.

A metadata-only count of existing successful **well-lit** measurements gives:

| MST | Images | Subjects |
| --- | ---: | ---: |
| 1 | 49 | 2 |
| 2 | 16 | 1 |
| 3 | 18 | 2 |
| 4 | 22 | 1 |
| 5 | 33 | 1 |
| 6 | 21 | 1 |
| 7 | 29 | 1 |
| 8 | 28 | 2 |
| 9 | 15 | 1 |
| 10 | 9 | 1 |

Thus filtering to well-lit photos would leave seven singleton categories. It
would also restrict capture conditions relative to the intended app. No such
filter or mapping fit was applied. A well-lit-only calibration could be a
separately declared limited development experiment, not automatic fulfillment
of the proposed all-condition ten-category validation.

## Next decision required for a defensible final method

The paper's retained MST stage needs a documented calibration/evaluation data
role and a validation design feasible with its limited subjects, together with
an explicit statement of photographed-condition limitations. The current strict
ten-category midpoint recipe cannot satisfy that. Do not convert its blocked
folds into fabricated thresholds or accuracy. Independent labeled support or
an actually agreed limited evaluation design is needed before calling it final.

Retain the paper's MST step while resolving those constraints; do not silently
return to the directLabbaseline. Further diagnostic artifacts cannot replace
this method/data decision. No new review request or source admission is implied.

[Reviewed replay](../outputs/mst_region_quality_v2/summary.json) ·
[User confirmation](../outputs/mst_region_quality_v2/completion_confirmation.json) ·
[Independent patch accounting and pair contrasts](../outputs/mst_region_quality_v2/reviewed_verification.json).

Script143independently recomputes patchLab/ITA and mask overlap on all24patches,
checks source/mask/reference hashes, and derives all4same-subject pairs from
official metadata. No fitting, label change, threshold search or runtime edit.
Latest full suite remains607passed; no new runtime behavior changed. Android
paused; CPM deferred. Glasses clearance remains a placement review rule, not an
implemented automatic glasses detector or application-user annotation workflow.
