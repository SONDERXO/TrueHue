# TrueHue: thesis-writing entry point

**Evidence checkpoint: 18 November 2026. Research and qualification remain incomplete.**

The user now authorizes starting thesis editing and preparing this repository for ChatGPT web. Older statements that manuscript work is paused are superseded for evidence-based drafting. This does not adopt a correction model, authorize invented results or make the thesis submission-ready. The editable manuscript has not been edited by this repository update; provide the current manuscript to the writing session.

Repository: `SONDERXO/TrueHue`. Current research branch: **`ffhq-correction-development-20261105`**. Do not assume `main` contains this checkpoint. Read this file and the linked current evidence before historical drafts or long session logs.

## Read in this order

1. This status and claim guide.
2. [ChatGPT writing prompt](docs/thesis/chatgpt-writing-prompt.md).
3. [Proposal versus actual implementation](docs/paper-alignment-reaudit-2026-11-15.md).
4. [WB314 numerical correction results](docs/wb-feature-direct-results-2026-11-15.md).
5. [Latest eight-case exposure rereview](docs/wb-feature-exposure-rereview-results-2026-11-18.md) and [completed pure-underexposure review](docs/wb-remaining-underexposure-review-results-2026-11-18.md).
6. [Implementation and experiment map](docs/thesis/research-map.md), [complete document index](docs/thesis/document-index.md), and [current session handoff](docs/session-handoff-2026-11-17.md).

## What the thesis proposes

The written study is post-capture, single-photo, on-device Android correction. It uses facial skin measurement, CIELAB-based ITA, an MST mapping, facial statistics and a decision tree predicting gamma and red/blue correction gains. Synthetically distorted processed photographs are paired with their original dataset photographs. The reference is a photographic target, not calibrated intrinsic skin colour.

The proposal names FairFace/SCIN for training and MST-E for evaluation, a 70/15/15 stratified partition, five-fold validation, parameter MAE, CIEDE2000 improvement versus the uncorrected image, tone-group reporting and genuine expert MOS. The exact augmentation equations, mapper roles and some disparity-denominator details need accurate operational wording; see the proposal re-audit rather than inventing missing specifications. The PDF itself stays local and is not included in Git.

## Actual development and scope changes

Implemented research includes learned face/occlusion parsing, separate measurement and application support, blending, object/eye protection, visible-neck/brow/lip support, optional manual refinement and specifically approved ear support. These are changes from the original rule-based, face-only design. Measurement and correction support must not be conflated; a good mask does not establish a valid MST mapping or correction decision.

Correction research spans ordinary trees, finite-action image-loss trees, controlled source expansion, alternative traditional features, oblique and linear-leaf investigations, frozen neural features, task-specific WB coefficients, PIQ quality supervision and complete PPR mapping. They are separate experiments with different contracts. Investigated extensions are not automatically the adopted final method or literal proposal compliance. Most are failed/closed; preserve their outcomes.

## Most informative current candidate: WB314

WB314 uses 281 traditional/input-derived measurements plus 33 coefficients from a frozen external white-balance method. The final learner is an ordinary depth-four, seed-42 regression tree. The camera-inspired task contains **11 exposed photographic sources and 66 cases**, six conditions per source. It uses linear-light half-stop exposure and fixed red/blue perturbations with a five-field luminance/chroma renderer. These feature, data, operator and validation choices are explicit research amendments, not the original three-output experiment unchanged.

The comparison used 11 source-held folds per arm (22 real trees across the matched281 and314 arms), fitting-only constants and sealed predictions before reference scoring. Independent implementation verification passed. Numerical means below are **primary-support RGB image MAE / CIEDE2000**, each over11sources. RGB image MAE is not parameter MAE.

| Condition | Uncorrected input | WB314 |
| --- | --- | --- |
| Original/identity | 0 / 0 | 3.726 / 1.471 |
| Colour only | 6.564 / 4.885 | 2.476 / 0.901 |
| Underexposure | 20.410 / 6.835 | 11.251 / 4.552 |
| Overexposure | 23.046 / 7.268 | 1.597 / 0.811 |
| Combined underexposure | 21.497 / 9.300 | 7.570 / 3.743 |
| Combined overexposure | 21.953 / 7.601 | 1.249 / 0.535 |

The candidate passed its frozen numerical gate. It improves all five distorted-condition means versus input and the fitting-only constant. Pure underexposure is worse than the matched281 baseline; that regression remains. Means do not imply every photo improved. One colour case is numerically worse than input. Nine original outputs are unchanged; two changed original appearances were accepted in the user's preservation review.

### Latest user judgments: do not use stale summaries

- **Identity:** all11acceptable.
- **Colour:** the original raw file recorded4candidate/7input selections, but the user explicitly corrected the interpretation to **all11candidate preferred**, with all11appearance acceptable. Preserve the raw file and separate correction; do not write seven effective input preferences.
- **Eight exposure/combined cases, repeated at the user's request:**3candidate preferred,2input preferred,3no useful difference; all8appearance acceptable. The old batch-level "looks like input" feedback remains historical and is not eight fabricated individual ratings or proof the user made a mistake.
- **Nine additional, previously unreviewed pure-underexposure cases:** all9candidate preferred and appearance acceptable.
- **Complete pure-underexposure role:** **9/11candidate preferred,2/11no useful difference,11/11appearance acceptable**. The two no-useful-difference cases are genuine neutral predictions. Current evidence therefore DOES demonstrate useful underexposure correction in nine specific outputs; blanket "no exposure usefulness demonstrated" wording is obsolete.
- Source29617also has a note that the correction stands out against its gray/low-exposure background. Keep that concern alongside its candidate/acceptable selections. Do not invent an unwanted-change rating or silently boost exposure.

There are17unique exposure/combined cases reviewed and27not reviewed. The complete eleven-case underexposure result overlaps the first eight-case screen; do not add11and8as independent observations. These are the user's development judgments, not expert MOS, independent participants or population-level evidence.

## Later candidates and negative evidence

| Study | Result and disposition |
| --- | --- |
| Joint4410 and nested fivefold selection | Better underexposure means but colour failures; closed. A separate231-fit selection study did not repair colour. |
| Synthetic exposure ranking / probe316 | Held ranking29/44was a narrow positive with severe overconfidence. Downstream correction failed colour; closed. |
| PPR319 coefficient features | Numerical gate passed but a newly brightened original raised the user's brightness concern; closed. |
| Frozen FIQA underexposure pilot | Some directional ordering, failed fixed false-positive/detection requirements; closed. |
| Actual PIQ23 head | One head trained on3630Train images/35scenes;1486Test images/15scenes. Equal-scene ranking85.51%, all15scenes above chance, but held loss1.45248worse than tied0.69315; fixed quality screen failed. |
| Direct actual-PIQ316 correction follow-on | Separately approved despite historical head loss failure. Numerical gate passed, but no tree split used either PIQ cue; repeated the exact previously concerning brightened original. Closed without adoption. |
| Complete frozen PPR RGB mapping | Native/scalar mechanics passed. All five numerical correction-role gates failed; all11originals changed. Closed. Positive improvement in three earlier misses does not rescue the overall failure. |

See the research map for exact protocols/results and earlier studies. Never turn engineering success, a positive subset or later permission into a retrospective pass of a failed scientific gate.

## What remains unestablished

- A finally selected, frozen and qualified combined correction model. WB314 is retained for further qualification; the above user review is not automatic final adoption or an all-data final fit.
- Reliable, compatible ITA-to-MST mapping across intended lighting/domain conditions. Experimental calibration results exist, including failures. Do not equate software availability with a validated mapping.
- Supported independent darker-skin/tone-group benefits. The11FFHQ sources have no independently qualified MST labels in this study. Do not infer tone groups from visible darkness, race, predicted appearance or PIQ scene labels.
- The proposal's complete final partition/validation and disparity analysis. Derivatives must stay grouped with their photographic source; unresolved person/pretraining overlap must be disclosed.
- Actual professional appraisal/refinement/final MOS and current-model Android parity/performance. Earlier Android or GUI checks refer to earlier experimental bundles unless explicitly stated otherwise.

## Drafting rules and source hierarchy

Use the latest dated result/explicit user clarification, then the fixed protocol and recorded execution, then historical drafts. The current manuscript supplied by the user controls structure; it is not proof that an unfinished result happened. Older documents contain historical "next" steps, paused statuses and superseded recommendations. Report what was actually executed, not every proposed plan as an experiment.

Each numerical claim should cite its exact repository result file and identify condition, cohort, region, comparator and whether it is development, generated QA or independent evaluation. Do not pool incompatible cohorts or report synthetic variants as independent people. Use pending language for unavailable results. Mark evidence gaps explicitly. The adviser assists with paper format/conferences only.

Raw datasets, model weights, galleries, individual private evidence and locked holdout contents/manifests remain local. `outputs/...` references in documents are provenance pointers, not files available in the GitHub checkout. Selected scalar summaries are mirrored in [the evidence snapshot](docs/thesis/evidence-snapshot.json); they do not substitute for unavailable raw evidence or constitute a new experiment. Never fabricate access to local artifacts, citations, expert responses or final model performance.

## ChatGPT web access

Connect GitHub and authorize `SONDERXO/TrueHue` in a supported ChatGPT experience. Explicitly provide this development branch and this file's path. Ask it to confirm what it actually retrieved before drafting. GitHub access is on-demand and varies by plan/surface; a repository link alone is not proof the whole project was read. See [OpenAI's GitHub guide](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt).

The repository update also prepares local text/ZIP handoff files under `output/thesis-web-handoff-2026-11-18/` for upload when branch access is unavailable. Those are local delivery artifacts, not publicly committed research data. Upload the current thesis manuscript separately so the writing assistant can preserve its structure, formatting instructions and bibliography.
