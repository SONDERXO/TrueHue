# STW qualification: useful labels, not ready for a processing/evaluation cycle

2 November 2026. User authorised source terms, annotation-count reconciliation,
overlap checks and a bounded-evaluation decision. Script390 inspected saved
metadata only; no photos downloaded/decoded, account registration, agreement
acceptance, author contact, source relabelling or model work.

## Decision

**Keep STW as a promising label source; do not activate image processing or
calibration yet.** Its all-tone labels address a real gap, but the current release
and person grouping are not reconciled and not all underlying source access/terms
are verified. This is not a finding that STW is unusable or prohibited. No new
manual review requested. No automatic smaller clean-only fit or lookup export.

## Count reconciliation

The exact downloaded CSV has42,312 rows and42,312 unique paths. All labels are
integers1–10. There are3,587 `new_tokens` keys; each key has one label. The same
3,587 count arises from unique(dataset,tokens) pairs and from whitespace-trimmed,
case-folded provider keys. There are no duplicate paths or simple whitespace/case
aliases to remove to obtain the paper's42,313 photos/3,564 people. **Difference
unresolved**, not corrected by dropping/merging rows. Paper/version and release
reconciliation require authoritative documentation, not guesses.

FairFace accounts for1,031 rows, each with an image-based provider ID. Those keys
are not independently verified different people. Across all sources, matching
namespaces do not establish cross-source identity uniqueness. Thus3,587 is a key
count, not a verified person count; no honest whole-cohort subject-separated split
can currently be asserted. The paper's human annotation protocol does not provide
instrument-measured skin truth or automatically validate the runtime measurement.

## Exact overlap with TrueHue

STW FairFace paths preserve train/val and filename IDs despite the margin1.25
crop. Canonical source IDs were matched against the frozen600 allocations, saved
duplicate dispositions and two development-exposure records. No pixel hashes
or visual comparison of different crops was performed.

- Eight exact allocated source overlaps: seven train and one development-validation.
- Development-validation source: fairface__train/200.jpg. Its role stays locked.
- Train sources:1749,2434,2879,3454,3612,5165,5193 (all train JPG IDs).
- Nine STW FairFace sources have recorded development exposure, including two
  not in the frozen600:1506 and3183. Allocation/exposure union contains ten sources.
- No exact frozen-test source match found. This is **not** proof of no cross-source
  duplicates, same-person overlap or undiscovered exposure. The1,023 other FairFace
  paths are outside the frozen600, not automatically independent/new subjects.
- Eight overlap sources have saved duplicate dispositions. No new relations were
  inferred from pixels, and no source was reallocated or given a new local MST label.

Exact source rows, roles, existing duplicate groups and exposure flags are saved
in outputs/stw_qualification_v1/fairface_overlap.json. Crop differences cannot
make the same source new independent evidence.

## Source terms checked

This is a record of published terms/access, not blanket clearance for the merged
dataset or a legal opinion. Do not confuse unrelated CASIA-SURF/CeFA or commercial
Casia websites with these particular source datasets.

| Component | Primary documentation result | Qualification status |
|---|---|---|
| FairFace | Official README identifies CC BY4.0 | Source terms identified; STW annotation rights, source roles and people still unresolved |
| CelebA | Official agreement permits noncommercial research, limits copying to internal use at one organisation and prohibits redistribution | Source conditions identified; no photo acquisition, public reproductions or identity rights inferred |
| CASIA-Face-Africa | Author site permits research/education, restricts dissemination and directs access applications to IdealTest | Source terms identified; account/application and actual release not obtained |
| CASIA-FaceV5 | Official institute source found; page fetch failed certificate/502, IdealTest unavailable during check | Correct source known, exact current agreement not verified; no substitution of another CASIA agreement |
| FEI / Brazilian Faces | Author site permits research use but forbids distribution/reproduction | Source conditions identified; public output/reproduction permissions cannot be assumed |
| Faces94/Faces95 | Original Essex host not resolvable during check | Terms/access unresolved; no mirror licence assumed |
| LFW | Original UMass host not resolvable during check | Terms/access unresolved; no third-party licence claim accepted as primary evidence |
| STW annotations/release | Official repository says work in progress, specific licence still being derived; use each source's terms | Public CSV access does not confer universal merged-data or annotation permission |

Original primary-source HTML/README snapshots and unsuccessful-fetch records saved.
FairFace standalone LICENSE path returned404, but its official README explicitly
names the data licence. FEI direct request succeeded despite web-tool403. No
certificate validation disabled and no signed-in/account access attempted.

## What would make a bounded evaluation justified

Resolve which release/identity table and annotation permissions apply, and obtain
the required source access conditions. Then freeze actual different-person groups,
cross-source overlaps, local reserved/exposed roles and a permitted operational
scope before pixels. The all-tone CSV alone is not enough. Any later partial-
source scope must be declared before outcomes and its label coverage reported,
not selected by mapping error or used to hide difficult cases.

Matching current FaceOcc skin admission and a predeclared task-adequacy criterion
would still be needed before one subject-held ITA-to-MST evaluation. More labels
do not guarantee that ITA can recover category under uncontrolled light. Retain
ITA + calibrated MST + facial statistics -> decision-tree gamma/red/blue correction;
do not replace it with STW's classifier or fabricate MST from old estimates.
No professional-review or adviser-response prerequisite added.

The existing unsent STW inquiry already asks the material release, grouping,
label-provenance and use questions. DAST email was sent by the user; STW was not.
No duplicate DAST email or STW email sent by this audit.

## Verification and records

Script390 assertions checked row/path counts, label range, exact FairFace source
normalisation,600-role joins and unchanged metadata input hashes. Outputs:
qualification.json, fairface_overlap.json, input_sha256.json, source_access.json
and source snapshots under outputs/stw_qualification_v1/. Parsed counts sum to
their declared totals. No tests rerun for metadata-only analysis; no runtime module
changed. No actual new pixel-validity or calibrated-MST performance evidence.
Earlier ready/stop decisions remain historically scoped rather than rewritten.
No new method/dataset adoption; frozen delivery-package inputs unchanged.

Primary sources:
[STW](https://github.com/vitorpmh/STW),
[paper v2](https://arxiv.org/html/2603.02475v2),
[FairFace](https://github.com/joojs/fairface),
[CelebA](https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html),
[CASIA-Face-Africa](https://nlpr-sir.github.io/dataset/casia-face-africa/),
[CASIA-FaceV5 institute page](https://english.ia.cas.cn/db/201610/t20161026_169405.html),
[FEI](https://fei.edu.br/~cet/facedatabase.html),
[Essex](https://cswww.essex.ac.uk/mv/allfaces/),
[LFW](http://vis-www.cs.umass.edu/lfw/).
