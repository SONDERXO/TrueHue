# Frozen gray-pixel selector: generated-only engineering protocol

12 November 2026, Asia/Manila. Authorized next step is complete lightweight selector specification and generated tests only. No development/original/final photos, correction fits or neural extractor.

## Paper facts visually checked

Yang et al.2015 PDFpage4 equations6-8 and page6 section3.1 were rendered and viewed. Use GP(std):3x3log-channel standard deviations s_c; m=mean_c(s_c); P=sqrt(mean_c((s_c-m)**2)/m); GI=7x7boxmean(P/L), L=mean RGB. Rank GI ascending, pool original input RGB of lowest0.01percent, as used in the published single-illuminant experiments. The mean log-contrast denominator is INSIDE the square root; this is not std(s)/mean(s). No gradient/2019/nighttime/cluster variant. Source: published article captured in outputs/gray_pixel_selector_engineering_v1/source_paper.pdf; source receipt binds its SHA.

## Declared engineering conventions, not author-code parity

Input actual RGB8 HxWx3, at least16x16. Convert to float64 code/255; natural log without added epsilon. Reflect101 neighborhood boundaries. Compute3x3populationstd by centered differences (two passes), not unstable subtraction of large moments. An initial center is valid only when every component of its3x3window is strictly positive and m>0; truly constant patches have zero centered differences and are unavailable. No darkness cutoff: positive dark pixels retained, with published inverse-L weighting.255values retained and counted, not hidden or corrected. Code-zero handling is numeric-domain handling, not app confidence gating.

Final center requires all49initialcenters in its7x7window valid; this conservative full-support convention avoids padding unavailable scores with artificial zeros or inventing partial-support means. Thus zeros/flat neighborhoods can yield unavailability, even when paper code might choose a different undefined-value convention. No support dilation, fallback or compensating new window. No selected neutral-ground-truth claim.

Let N=H*W. K=max(1,ceil(N*0.0001)), using full-frame denominator, capped at number of finite valid scores. PrimarysortkeyGI, tiekeyrow-major index. Record ties at the cutoff, count valid/selected pixels, zeros/saturated pixels and selected coordinates. Do not break ties by redness, brightness, labels or target look. A zero-score tie can select coloured surfaces; stable ties are deterministic, not colour-neutral. If no candidates exist, return explicit unavailable and no feature vector; no identity fallback/admission inferred.

Pool arithmetic means e_R/e_G/e_B over selected original input pixels and output log(e_R/e_G),log(e_B/e_G), no plusone. Selected pixels arepositive so denominatorspositive. These are contextual descriptors, NOT correction gains, an estimated physical illuminant, MST labels or a trusted neutral mask. Existing16features/tree/MST/support/runtime remain untouched. No standalone white-balance operation, correction gate or new mask is connected.

## Generated fixtures and checks frozen before implementation

Use deterministic64x64neutral, uniformlycoloured and mixedcolour/neutral textured frames; fixed identity,gamma1/.7,gamma.7,red245/255 recipes from existing diagnostic. No new scientific cases/recipes. Use RGB8rint and record both quantized response and candidate regions. Mixed fixture has a generated known-neutralhalf solely to measure false selection; no such material labels would be available for real input.

Tests independently replay the complete scalar3x3/7x7/rank/mean pipeline, verify equation6 denominator, ties/counts, invariance of grayscale under channel permutations, finite outputs, zeros/flat/saturated/invalid inputs and determinism/nonmutation. Include quantized colour falsecandidates and fullyunavailable cases. No accuracy thresholds, sigma/percentile/channelsweep, real-case masks or new learned model. Report every fixture outcome, including whether cast-free gamma inputs produce nonneutral descriptors and whether quantization changes selected locations.

## Decision rule and scope

EngineeringPASS means formulas/handling work as specified, not successful neutral identification or correction. Review selection provenance, falsecandidates and quantization ambiguity before any cached extraction. If generated results undermine the proposed cast-versus-exposure interpretation, do not automatically advance to44photo preparation or model training; explain what is still unsupported. No minimumneutralfraction or response-size gate will be invented after results. This does not prove every GPfamily useless or impose physical-colour truth on our photographic-restoration study.

Runtime/resource measurements are desktop-only, no phone claim. Implementation independently follows published equations; GPLauthorZIP is not downloaded/copied/executed. SourcePDF rendered with isolated pypdfium2 tool under this output directory because no local renderer was initially installed; project/runtime dependencies unchanged. Generatedarrays stay outside data/annotations and no acquisition/contact/upload/commit/push/runtime/Android or holdout access occurs. All earlier failures remain closed; ReIQA declined; PPRpaused.
