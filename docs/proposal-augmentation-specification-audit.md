# Proposal augmentation specification audit

Correction after the requested full111-page scan: PDF38/printed31 explicitly
states gamma below1 brightens and above1 darkens. The earlier method-page-only
audit missed this definition. The full composite still lacks uniquely specified
units/order, and “Gamma/Midtone” versus progressive-darkening wording needs
distinguishing from correction gamma. PDF59 also requires three distorted
versions per source, without defining all three recipes.
[Full scan and implementation implications](proposal-full-scan-findings.md).

29 October 2026. Re-read the original proposal's treatment-of-data pages and
visually rendered Table 3 (PDF page 64 / printed page 57). The current Table 2
composite was an explicit development interpretation, not a formula recovered
from the paper. Its fidelity now needs resolving before further mask tuning
or a new correction-tree fit on regenerated inputs.

The method pages supply Table 2 gamma, brightness, contrast and channel-shift
values but do not specify enough operations to reproduce them uniquely:
gamma exponent/convention, operation order, adjustment transfer functions and
units, intermediate clipping and full-frame versus facial compositing remain
underspecified. The paper also calls the Table 3 images representative examples,
not a formal numerical conformance set.

## Embedded example comparison

Extracted all six distinct Table 3 assets without editing the PDF. Content-stream
placement verifies each row's reference/bias pairing and confirms the target
reuses the reference image. Visually inspecting the rendered page confirms
column and group placement. Applied the unchanged current composite to each
embedded native224 reference, across the full image solely to inspect the
pointwise formula, and compared it with the embedded simulated input.

| Paper row | Current formula versus embedded bias: RGB MAE, 0–255 | Zero-valued channels in embedded bias | Zero-valued channels under current formula |
| --- | ---: | ---: | ---: |
| Light | 13.89 | 0.074% | 24.48% |
| Medium | 62.81 | 0.002% | 16.78% |
| Dark | 72.23 | 0.002% | 74.54% |

The current formula produces substantially darker outputs and far more zero
channels than the illustrated biases. This supports a material reproduction
mismatch; it is not proof that a particular alternative formula is correct.
An exponent-direction sensitivity check changes the discrepancies but also
fails to reproduce the examples. Do not adopt it merely because it is closer.
JPEG reference decoding, illustration provenance and possible editor operations
also prevent deriving a canonical equation from three images alone.

These figures are native-image formula reproduction errors, **not correction
model scores, skin-region ground truth, MST validation or a reproduction of
the full masked-square256 training pipeline**. The experiment does not establish
how much of each earlier mask failure is caused by this mismatch. It shows why
the existing numerical implementation should not be called uniquely specified
by Table 2 or used to justify endless mask changes without checking provenance.

## Concrete next requirement

Obtain the script or editor preset that generated the proposal's simulated
inputs, or establish an explicit documented augmentation convention where the
paper leaves equations open. A question about the generating tool/location
has been sent to the user. No source implementation was identified by the
repository search in this step. Do not fabricate a replacement or calibrate
one retrospectively to make a model result pass.

Once that convention is established, implement it as a new version, freeze
units/order/clipping and reference-image fixtures, then regenerate only the
reviewed training pairs for a matched comparison. Preserve the current recipe
and all negative results. Keep ITA/calibrated MST/facial statistics and the
gamma/red/blue decision-tree architecture. Never reuse mask-dependent MST
thresholds if the measurement pixels change.

Read-only PDF verification, image ordering, current formula reproduction and
artifact hashes pass. The original PDF, masks, datasets, correction trees and
measurement contract remain unchanged. Dependencies for PDF inspection were
installed into an ignored output directory, not the project environment.
No reserved training-check, validation or final-test image was accessed and
no new source was admitted or model fitted. The last full algorithm suite
remains 742 passing tests; this source audit adds no model-quality claim.

- [Paper-versus-current comparison boards](../outputs/proposal_augmentation_audit_v1/review.html)
- [Rendered Table 3](../outputs/proposal_augmentation_audit_v1/table3_page64.png)
- [Full findings](../outputs/proposal_augmentation_audit_v1/summary.json)
- [Verification](../outputs/proposal_augmentation_audit_v1/verification.json)
