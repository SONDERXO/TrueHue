# Candidate: reference-conditioned chromaticity residual context

13November2026. User requested the next step after the source-shape rationale check. Assess a concrete learned reference-colour prior before adding another feature. **Candidate for a generated feasibility design only; no real prior or correction tree fitted, no actual roster selected.**

## Primary basis and limits

Ayan Chakrabarti2015, Color Constancy by Learning to Predict Chromaticity from Luminance, sections2–3, learns pixel-colour statistics conditioned on brightness and pools evidence for illuminant estimates. Its empirical-histogram baseline is non-neural; its later discriminative variant is a separate learned formulation. Primary paper: https://proceedings.neurips.cc/paper_files/paper/2015/file/9778d5d219c5080b9a6a17bef029331c-Paper.pdf .

The published experiments use linear RAW-derived camera images, chart-derived illumination labels and hundreds of training photos. That evidence does not validate a prior trained on our few processed portraits. Our gamma/red/blue edit operators and photographic restoration target differ from illumination recovery. No chart, RAW capture or physical-ground-truth prerequisite is imposed on TrueHue, and the proposed adaptation is explicitly our own, not author-method reproduction.

## Own adaptation: learn acceptable colour, not a neutral colour

Build a small empirical reference table from permitted FITTING photographic references only: expected log(R/G) and log(B/G) conditional on the reference green-channel level. Green is the conditioning variable in this proposed adaptation, rather than the paper's luminance. Pure red/blue edits leave green unchanged, so a red or blue gain shifts its corresponding log-ratio while the conditioning variable is stable, before quantization/clipping. This gives a specific reason to investigate the cue for correction-axis separation; it is not brightness-conditioned neutralization.

For a distorted input, compare its positive-RGB pixel log-ratios to those expected at the observed green values, then aggregate signed residuals separately for red and blue. The reference table can represent nonzero, brightness-dependent acceptable chromaticity; there is no rule setting scene or skin colour to gray. The correction tree would receive these evidence features alongside the retained traditional inputs and ITA/MST. References do NOT enter inference, and no reference/source/edit label selects a control directly.

Conceptually, if input u=mu(G)+edit_R and v=nu(G)+edit_B, these residuals can remove the modeled material/brightness trend while retaining edit direction. If the source has an additional unmodeled chromatic offset, it remains in the residual and can still be mistaken for an edit. This is a statistical prior with explicit failure cases, not recovered per-photo ground truth.

The green-only condition is stable only for pure red/blue edits. Gamma changes green, channel clipping/quantization alters log relationships, and backgrounds need not resemble the reference corpus. Availability/counts and unsupported green ranges must be explicit; no missing bin can be silently replaced by a neutral expectation. No real bin count, smoother, interpolation rule, pseudocount, leaf-feature replacement, classifier, penalty or training roster is chosen in this candidate review.

## Architectural and paper scope

Retain ONE gamma/red/blue correction tree, single-photo inference, ITA/MST and existing face/visible-neck/manual support. The table is an additional LEARNED preprocessing component; do not advertise this as the identical original one-stage model merely because final correction uses one tree. It requires a method extension and a new training/inference contract. It is distinct from appending an invariant summary or merely changing a ridge penalty.

This proposal does not revive the failed two-coordinate linear-leaf recipe. Whether residual context is useful must be established before selecting how a final tree consumes it. No choice between constant/linear leaves, combined models or additional fits is made now. It also cannot fix the earlier human preferences simply by recovering mathematically nominal controls more accurately.

## Source weighting, darker-skin priority and leakage

An eventual table must weight each fitting source equally, rather than letting images with many eligible pixels dominate. Every source's variants, reference and any prior-learning records stay entirely inside its source-held fitting fold. The held photographic reference cannot enter the table even though it is already exposed development data. Prior construction must be repeated within each permitted fitting fold; a table learned once from all11reference photos would leak held targets.

Equal source weighting is not equal tone coverage. The current11-source cohort lacks independent tone labels and is not a credible basis for claiming a broad, unbiased colour prior. A learned table can favor the common complexion/background distribution and correct away naturally darker skin. No appearance-derived labels, bright-pixel restriction, assumed white skin/background or pooled fairness claim is allowed. The source balance and later independently qualified tone evidence remain necessary, and processed references can contain their own biases.

## History check and bounded next step

Scoped report search found no completed TrueHue experiment learning this green-conditioned acceptable-reference chromaticity table. Earlier eye/highlight cues sought particular neutral patches; joint histograms describe the input distribution; target-normalized/deeper/split predictors change fitting objectives or architecture; the source-shape check removes absolute shifts. None establishes this conditional reference prior. This is a local workflow distinction, not research novelty or proof of additional information independent of all prior inputs.

Next IF pursued: freeze ONE generated-only table/aggregation specification before implementation. Tests must include a non-neutral brightness-dependent reference trend with pure red and blue edits; unseen source compositions with the same conditional trend; unmodeled source-colour offsets that violate it; equal-source versus unequal-pixel contributions; excluded-source/held-reference leakage traps; missing bins/zero channels; gamma, quantization and clipping stress. Separate any ideal mechanism gain from bias/availability failures. No settings grid, extra tree fit, real-photo extraction or user review follows automatically.

A generated pass could establish engineering and conditional mechanism only. A photographic trial would still need an exact eligible source roster, held-prior exclusion, prospective numeric/visual evaluation and honest limits on tone coverage. Current small exposed portraits and primary-paper results do not supply that qualification automatically. There is no ready real training recipe in this review.

All earlier closed trials, ratings, generated artifacts, preserved baseline and approved59807manual/ears remain unchanged. No dataset arrays/model fit/new prediction/raworiginal/lockedholdout/runtimeAndroid/manuscript change. Modelunfinished/paperpaused/darker-skinpriority/November14complete-deliverytargetatrisk/exacttimeunspecified/no guarantee.
