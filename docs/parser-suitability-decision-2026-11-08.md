# Parser suitability decision — 8 November 2026

**Do not promote the existing parser alternatives or start another correction fit to compensate for missing facial support.** The current parser is not demonstrated adequate for completing automatic full-face correction. This is a development decision about available evidence, not proof that the task is impossible.

## Evidence reviewed

| Route already investigated | Finding | Decision |
| --- | --- | --- |
| Input, crop and class-order audit | No mismatch in the checked author contract or four distorted inputs | No unsupported channel/label fix |
| OpenCV versus ONNXRuntime | Identical class decisions on the four fragmented conditions, also matching cached maps | Backend switch will not fix these cases |
| Current-framing parser-only contrast | Usable measurements 3/6 → 4/6; marked coverage 653 → 843 of 3,156 pixels; unwanted point inclusions 3 → 4 | Mixed, unadopted; do not repeat a contrast sweep |
| Larger ResNet34 parser | Skin points 54 → 77 of 113, but unwanted points 9 → 15 of 94 | More coverage with worse protection; not a qualified replacement |
| Background/visibility protection | Background labels explain most missing support in the four traced conditions | Do not simply remove the veto or fill unknown regions |
| Native inward fade | Softer edges but reconstruction error worsens substantially; missing coverage remains | Blending alone is insufficient |
| Existing sparse/patch annotations | Limited references, including neck regions and three conflicting point/polygon locations | Not dense material-segmentation training truth; no automatic fine-tuning |

The comparison denominators and framing differ across experiments. These rows are not a pooled ranking or a claim of controlled equivalence. The larger-parser point trial used the earlier fixed parser appearance, while the latest contrast trial uses current geometry. Repeated conditions and exposed development examples are not independent validation.

Sources: [backend comparison](parser-backend-parity-results-2026-11-08.md), [input contract audit](fragmented-parser-contract-audit-2026-11-08.md), [current contrast results](current-parser-appearance-results-2026-11-08.md), [larger-parser results](resnet34-parser-comparison-results-2026-11-06.md), [support trace](fragmented-correction-support-results-2026-11-08.md), [fade pilot](native-inward-fade-pilot-results-2026-11-08.md), and [material development plan](material-improvement-development-plan-2026-11-08.md).

## Concrete next intervention and its prerequisite

The justified direction is **a material-aware masking candidate with explicit facial-hair/object distinctions**, followed by one fixed coverage-and-protection comparison. No complete suitable new candidate is currently verified locally. Do not present this as a selected model ready to run.

The existing [readiness record](material-candidate-readiness-2026-11-08.md) and [suitability decision](material-model-suitability-decision-2026-11-06.md) already document the access dependencies. The conversation subsequently established that the Roboflow account exposes hosted API deployment rather than the sought local-weight export. Do not send the private dataset to that API or ask for an API key as a workaround. A hosted beard detector alone is also not a skin parser or a rim/lens segmentation model.

The actionable prerequisite is an actual locally runnable checkpoint package with permitted research use, original class mapping, preprocessing/output contract and verifiable asset provenance. Acceptable access to all required components must exist before a model-specific comparison can be specified. No renewed account action, terms acceptance, author contact, dataset/model search or purchase is activated here.

If that dependency changes, first inspect and hash the supplied package without uploading images. Freeze one comparison on the already completed development references, retaining technical failures. Require additional reviewed skin coverage **and zero newly included definite unwanted points**, preserve original pixel measurements and fixed protection invariants, and report per-photo gains and losses. Existing sparse checks are necessary regressions, not complete skin accuracy or proof of safe transparent-glasses correction. Explicit clear-lens handling must still protect frames/rims; a generic glasses label does not establish this.

## Work that remains safely available now

The correction candidates and all private outputs remain available for reproducible research reporting. Keep the current demonstration marked experimental and report failure/uncertainty honestly; no demo policy change is made by this document. A decision to narrow the thesis's automatic-correction scope would need to be explicit, rather than silently calling a partial mask complete.

There is no evidence-backed next fit authorised by this review. The next substantial masking experiment depends on a qualified local candidate or an explicitly agreed alternative research scope. Further small settings trials would repeat known trade-offs without resolving the missing material evidence.

The latest correction candidate still preserves all 40 usable clean evaluation photos and improves many distorted conditions, but fails its full acceptance requirements and retains visibly incomplete support. The separate eight-group, 24-photo holdout remains byte-unread; none of these mask studies qualifies the candidate for opening it.

## Scope of this decision

Read-only synthesis of existing local reports; zero inference, fitting, new annotation, acquisition, external sharing or runtime integration. No tests were needed for this documentation-only decision. This decision supersedes an automatic suggestion to try another parser variant: future work must name the changed dependency or justified design first. Preserve all research-use and no-redistribution restrictions.
