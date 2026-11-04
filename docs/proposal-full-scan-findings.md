# Full proposal scan: augmentation details

29 October 2026. Scanned the searchable text of all111 PDF pages, indexed
augmentation/software/equation terms, inspected relevant method and definition
passages, checked references and both appendices, and rendered the algorithm
figures, representative examples and appendix overview pages. The original PDF
is unchanged. There are no embedded file attachments.

## What the paper actually specifies

| Requirement | Location | Finding |
| --- | --- | --- |
| Gamma convention | PDF38 / printed31, definition of Gamma Correction | Gamma below1 brightens; above1 darkens. Pixel intensity is described as raised to the gamma power. |
| Synthetic count | PDF59 / printed52 | Three distorted versions per selected source. The identities/recipes of those three versions are not specified. |
| Tone-dependent settings | PDF62 / printed55, Table2 | Light/medium/dark gamma, brightness, contrast and channel-shift values are listed. |
| Correction model | PDF63 / printed56 | ITA, mapped MST and facial color statistics; decision-tree gamma and red/blue multipliers. |
| Detailed mask | PDF61 / printed54 and activity flow PDF71–72 | Face-local YCrCb, largest component, exclude below1000 selected pixels. |
| Evaluation timing | PDF60 / printed53 | Expert evaluation after system construction/testing. |

The gamma definition says: “Values of gamma less than 1 brighten darker regions,
while values greater than 1 darken them.” The current reciprocal exponent
`x ** (1 / gamma)` has the opposite behavior **for the same numeric gamma**.
The direct-power convention `x ** gamma` matches that definition on normalized
intensities. These are different parameterizations of the same family of power
curves; conversion requires reciprocating gamma. It is unsafe to flip the
operator underneath existing targets, learned trees and Android parity vectors.

This corrects the previous audit: the method pages alone did not define the
full recipe, but the definition section **does constrain gamma semantics**.
Keep that correction visible rather than silently discarding the prior audit.

## What remains unspecified or inconsistent

No complete augmentation equation, source-code listing, generating script name,
editor preset, operation order, brightness/contrast transfer functions and units,
channel-shift formula or intermediate clipping policy was found. Appendices
contain app screens and the expert questionnaire, not augmentation source code.
Generic mentions of Python, OpenCV, scikit-image or GitHub do not identify the
script that created the representative images.

There is a wording tension: the gamma definition says below1 brightens, while
Table2 lists below1 values under “Gamma/Midtone” and the simulated-environment
description says progressive midtone darkening (PDF65 / printed58). An editor's
midtone parameter could differ from the defined correction gamma; the paper
does not explain that distinction. Do not claim the full synthetic algorithm
is resolved merely by changing an exponent. The previous sensitivity test also
shows that swapping the exponent alone does not reproduce Table3 exactly.

Likewise, the paper's three-distorted-version requirement is not satisfied by
calling an unchanged identity control one of the three distortions. The recent
new cohort has one assigned Table2 composite plus an identity control. That is
a development subset, not the complete three-version training specification.
Do not invent the missing two recipes or describe the current subset as fully
paper-compliant.

## Implementation consequence

The next justified work is a versioned augmentation/correction specification:
explicitly name the gamma convention, preserve legacy parameter meanings,
document any choices the paper leaves open, and validate fixed examples before
regenerating reviewed training pairs. Retain Table2 values, ITA/MST and the
decision-tree architecture; distinguish literature requirements from engineering
choices. Reassess clipping and input-mask behavior on matched sources afterwards.
No new formula, target conversion, dataset regeneration or active model change
was made during this scan.

Evidence includes an all-page search index, method excerpts, visual overview
sheets and the full-resolution gamma-definition page. Personal CV/contact
details were not copied into the method-evidence excerpts. PDF hash and all
audit artifacts verify. This is a source audit, not a new model validation.

- [Gamma definition, rendered PDF38](../outputs/proposal_full_scan_v1/gamma_definition_page38.png)
- [Whole-document findings](../outputs/proposal_full_scan_v1/summary.json)
- [111-page text search index](../outputs/proposal_full_scan_v1/all_page_search_index.json)
- [Relevant method/definition excerpts](../outputs/proposal_full_scan_v1/method_evidence.json)
- [Verification](../outputs/proposal_full_scan_v1/verification.json)
