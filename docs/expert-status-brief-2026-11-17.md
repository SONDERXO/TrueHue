# TrueHue — current research status for expert discussion

Prepared17November2026. LOCAL REVIEW DRAFT; not sent or published. This summarizes development evidence, not a finished system or expert-MOS instrument. An early methods consultation requires agreement on timing under the existing model-first review policy.

**Goal.** Predict exposure and colour-correction controls from one photograph, aiming to restore synthetically distorted images toward their original photographic references while preserving acceptable complexion. Darker-skin benefit is a research objective, not an established result; the study does not establish intrinsic skin reflectance or removal of real camera bias.

**Written design and research extensions.** The proposal uses ITA/MST and facial colour statistics with a decision tree. Development explored expanded features, a frozen ReIQAencoder, external WB-mapping coefficients as features, six controlled roles and a luminance/chroma control operator. These are disclosed amendments under investigation. Final method adoption is unresolved. Current11-source FFHQdiagnostics are repeatedly exposed, with no official MST labels or verified independent-person/tone evaluation.

**Evidence.** The WB-feature tree achieved11accepted identity cases and explicit preference for all11colour candidates in single-user development review, but the exposure batch was reported to have insufficient visible benefit. A joint-feature tree and its later prespecified fivefold-selection study improved exposure means while worsening colour. The selected study's primaryRGB/DE means were colour4.520/1.979and under6.794/2.322, versus WB-tree2.476/0.901and11.251/4.552. It failed its combined requirements and is not adopted. Numeric identity changes are not fabricated human harm judgments. No formal expert MOS or darker-skin benefit is established.

**Proposed PIQ23extension.** Access was requested; no photographs or real head training yet. A small scene-balanced exposure-quality ranking head on a frozen encoder would provide two relative score-response features for fixed brighter/darker probes. Engineering/metadata rehearsals passed, which does not establish photographic quality. Scores are scene-relative, and the public split is not certified person-disjoint. The final correction comparison remains prospective.

**Three questions for a methods consultation, if agreed:**

1. Is this proposed quality-ranking cue a coherent research extension of synthetic-to-original control prediction? Which assumptions are most concerning?
2. How should restoration benefit and preservation be evaluated so naturally darker complexion is not treated as an exposure defect?
3. What evidence and limits should be resolved before formal comparative image ratings and any claim of improvement across skin-tone groups?

This consultation would be recorded as methodological advice. It would not be reported as expert ratings of a qualified model, final validation, data-access approval or a completed bias-reduction result.
