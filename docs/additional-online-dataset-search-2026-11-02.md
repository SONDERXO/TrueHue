# Additional online datasets: useful new leads

2 November 2026. User requested more online dataset research. Public papers,
repositories and access documentation only; no dataset photos, training source,
code execution from repositories, contact, inference or fitting. These are leads,
not admissions or proof the retained method will succeed.

| Lead and primary source | Documented offering | Main limitation / access |
|---|---|---|
| [DAST](https://github.com/dasec/DAST-SkinTone-database) | Controlled portraits, nominal/changed exposures and instrument measurements; 80 people, 12 images each | Labels use CST, not MST. Public examples; full data by author request, actual recipient terms still needed |
| [STW](https://github.com/vitorpmh/STW) | Larger identity-labelled MST collection; paper reports 42,313 photos / 3,564 people | Repository warns release/code do not yet reflect paper; multiple source licences/access requirements |
| [PPR10K](https://github.com/csjliang/PPR10K) | 11,161 portraits, three expert edits, human-region masks | Dataset noncommercial research agreement; aesthetic targets, not measured true colour |
| [Rendered WB](https://yorkucvil.github.io/projects/public_html/sRGB_WB_correction/dataset.html) | Incorrect white-balance inputs with chart-referenced target renderings | General scenes: usable portrait coverage/terms need checking; no MST labels |

## Recommended order

**DAST first for documentation/sample-readiness assessment.** It is a stronger
match to controlled capture plus measurement needs than a general edited-photo
collection. This is a research judgment, not a verified qualified-reference claim.
Nominal exposure is not evidence of intrinsic skin colour. Do not rename CST as
MST, infer an inverse gamma from shutter settings or swap the correction method.

The downloaded [DAST paper](https://www.christoph-busch.de/files/Busch-DAST-IWBF-2026.pdf)
has a reporting inconsistency: its conclusion says ten people per CST2–9, while
TableII/current repository give CST1:2,2–8:10 each,9:8,10:0 (total80). Retain the
discrepancy. Exposure labels/aperture ordering also need clarification. Confirm
actual release metadata and conditions before relying on these as numeric targets.
Publication examples/full dataset permissions must not be inferred from code
visibility. No author inquiry or archive acquisition was performed.

**STW for MST-label/access assessment in parallel as a separate possible role.**
The [current paper](https://arxiv.org/html/2603.02475v2) describes identity-level
human annotation and broader tone coverage. Access claims in the paper are not
proof every component is freely reusable: official repository defers to each
source dataset's licence and flags work in progress. STW includes FairFace, so
TrueHue's existing reserved-source/duplicate/exposure allocations must be checked
before pixels are accessed; a new dataset name cannot make exposed identities
independent. No copying labels into existing sources or adopting SkinToneNet.

**PPR10K if the intended target is photographic restoration.** Portrait-specific
targets are more directly relevant than general FiveK person tags. Expert edits
are not instrument truth. Human masks include non-skin; groups are not assured
unique identities; full editing operations may exceed our three-parameter operator.
Distinguish the repository's code licence from dataset-specific research terms.
Do not download the large full collection just to inspect feasibility.

**Rendered WB for colour-cast correction references.** Chart-based targets supply
stronger white-balance provenance than a preferred-looking edit. They do not
guarantee true facial skin colour or qualify a portrait cohort. Check permitted use,
face availability, scene grouping and chart exclusion. Its extra FiveK rendering
set explicitly lacks targets and must not be presented as chart-calibrated data.

No single newly found source currently fulfils both reliable MST mapping and
validated true-colour correction. Separate datasets may support separate roles,
provided compatibility, licences and evaluation are justified. Keep existing
calibration/training stopped; no automatic sample, review or model adoption.
Before activating a dataset/method change, record its proposed role in the panel
register. This search adds evidence, not a changed method or panel decision.

## Saved record

outputs/online_dataset_search_v2/: DAST paper/text, repository README snapshots,
STW abstract, Rendered WB publisher page, shortlist.json and SHA-256 hashes.
DAST PDF successfully fetched directly despite web-tool timeout. Initial PPR10K
main-branch URL returned404; official master-branch README fetched successfully.
No repository setup scripts run or large datasets downloaded. No pytest run for
documentation research. Frozen delivery-package input documents remain unchanged.
