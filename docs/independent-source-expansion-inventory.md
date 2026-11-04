# Additional training-source inventory — 30 October 2026

The existing allocation contains **407 duplicate-screen-clear FairFace sources
outside the current 26-source cohort**. This is a concrete expansion pool, not
407 approved references or verified independent people. All have already been
processed in training development. No new images were opened for this inventory.

The completed primary comparison remains stopped. ITA, calibrated MST and facial
statistics remain required inputs to the decision tree. The endpoint research
candidate and the separate demo preset remain unchanged.

## Reconciled allocation

| Frozen training allocation | Sources |
| --- | ---: |
| Total | 420 |
| Duplicate quarantine, retained without replacement | 2 |
| Screen clear | 418 |
| Already in the current 26-source cohort | 11 |
| Additional screen-clear source groups | 407 |

The other 15 current-cohort sources come from earlier work; they do not expand
this allocation. The 90 development-validation and 90 final-test allocations
remain locked. Their previous computational duplicate-audit exposure remains
disclosed; this inventory does not access their pixels or outcomes.

The additional pool has 250 saved target candidates pending review, 62 distorted
processing failures, 80 reference failures and 15 unavailable targets. These are
technical statuses from the original preparation, not updated human judgments.
Among the 407, 69 have collected scoped review evidence and 338 have none in
the checked imports. Exact annotations, notes, scopes and evidence paths are
preserved in the inventory. An acceptance for another mask or variant is not
transferred. Absence from these records does not prove a photo was never seen.

Exposure reconciliation includes the historical additions ledger, the 418-source
preparation ledger and available later output access ledgers. No historical
ledger or allocation was rewritten. The original duplicate screen does not
prove person independence or detect every repeated photograph.

## A bounded planning list

Saved 24 planning candidates from 269 additional sources with successful saved
reference measurements and no collected scoped review annotation. Selection
uses a declared deterministic image-ID hash, one duplicate group per source.
It does not rank by clipping, skin tone or correction outcome. The list is an
inventory aid, not an adopted cohort or a request to review these photographs.

IDs: 50457, 16951, 61590, 2434, 76204, 10567, 9572, 76067, 25517, 72939,
86255, 47439, 71785, 46277, 65420, 19067, 72367, 68317, 2025, 65641,
75119, 58767, 11900 and 39083.

Nineteen have saved target candidates; five have distorted-processing failures.
Those five remain explicitly held for distorted use. A successful reference
measurement alone does not approve an unchanged training control.

Before selecting a fitting cohort, the minimum missing judgments are source
reference suitability (including color filters, lighting, detail and foreign
material), the exact original-rule facial mask, and each exact distorted mask
that would be used. Existing scoped reviews must be reused where applicable.
Reference suitability must distinguish a useful reconstruction reference from
independently measured true skin color. No additional review is requested now.

## Coverage and reference limitations

The additional pool has experimental reference-derived severity counts of 59
light, 266 medium, two dark and 80 unavailable. The planning list has four light
and 20 medium, with no dark case. These are historical lookup estimates, not
validated MST labels. This list cannot establish ten-tone or dark-tone coverage.
It is not an MST-stratified cohort. Zero clipping would neither establish
reference quality nor remove the need for exact mask judgments; filtering on
it could bias the source distribution.

ITA and mapped MST use the same facial color measurements. More source groups
may help, but this inventory does not show that they can independently separate
illumination from intrinsic skin tone or guarantee reliable correction.

## SCIN remains a separate readiness issue

The existing metadata audit lists 368 head/neck, at-distance image candidates.
Fourteen cases match the historical training-candidate selection; 354 have no
training allocation established by these records. The nine previously recorded
local images all belong to the historical training-candidate cases. Availability
was not rechecked and no images were downloaded or opened.

These cases lack the FairFace allocation's verified duplicate dispositions.
Body-part tags do not establish a usable face, a neutral-color reference or
person independence. Retain both India/US annotations and their gradability:
151 cases agree, 216 disagree and one has neither usable annotation. The
agreement cases have no MST9/10 support. Neither choosing a favorable annotator
nor accepting only agreement cases establishes balanced coverage. SCIN needs
explicit role, duplicate and reference-quality decisions before fitting; none
of these 368 is automatically admitted by this inventory.

## Separate MST requirement and next decision

Keep the development lookup experimental. Before a final calibration, declare
MST-E calibration/validation subject roles, reconcile historical exposure and
duplicate relationships, and freeze the validation procedure. Use the same
hashed square256 facial measurement contract; a changed mask contract requires
matching calibration evidence. Report per-tone support, uncertainty and
held-subject mapping results rather than inventing thresholds or passing
criteria after seeing outcomes. No correction-tree training uses MST-E.

The next substantive decision is a bounded source/reference-quality and coverage
plan using this inventory, including how missing dark-tone support and SCIN
readiness will be handled. It is not another same-cohort parameter trial. If
independent lighting/reference information becomes necessary, prepare an
adviser-facing method decision before implementation. No adviser message is sent.

## Evidence and verification

Reproduce with `venv\Scripts\python.exe scripts/285_inventory_additional_training_sources.py`
from the project root, using a new output location if retaining this run.
The script refuses to overwrite an existing inventory. It checks training-role
access, exact 418-source queue/attempt parity, 24 distinct planning groups,
zero current-cohort overlap and unchanged metadata input hashes. It opens no
image files, fits no model and approves no masks. Full pytest was not rerun for
this metadata-only inventory; the handoff's 798-test result remains historical.

- [Summary](../outputs/independent_source_inventory_v1/summary.json)
- [All 420 training dispositions and scoped annotations](../outputs/independent_source_inventory_v1/fairface_inventory.json)
- [Bounded planning list](../outputs/independent_source_inventory_v1/planning24.json)
- [SCIN metadata inventory](../outputs/independent_source_inventory_v1/scin_inventory.json)
- [Evidence hashes and checks](../outputs/independent_source_inventory_v1/verification.json)
