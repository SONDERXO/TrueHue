# Integrated MST pipeline stress test

28 October2026. Scripts182/183test the integrated Python pipeline with all three
saved development methods on the same fixed cases. No new models, features,
masks, source choices, thresholds or quality gates. The run plan is saved before
inference. Each source uses its prescribed ten-source held fold for every method,
not the best-looking fold or the earlier eight-source fold.

Cases: ten unchanged controls, plus the existing24counterfactualTable2inputs
(eight sources at light/medium/dark settings). Each of34inputs runs through
baseline5,chroma9andclean-leaf:102inference calls.99produce outputs. The same
75027darkinput fails face detection under all three methods, with no MST,
features, parameters or corrected output supplied. No failure is counted as
zero error or silently corrected using reference features.

Mean fixed-reference-support CIEDE2000, lower is better:

| Scope | Successful / attempted per method | No correction | Baseline5 | Chroma9 | Clean-leaf |
| --- | ---: | ---: | ---: | ---: | ---: |
| Unchanged | 10 / 10 | 0.000 | 5.489 | 3.488 | 2.767 |
| Light probe | 8 / 8 | 12.694 | 14.515 | 13.638 | 13.800 |
| Medium probe | 8 / 8 | 23.488 | 13.969 | 13.944 | 13.944 |
| Dark probe | 7 / 8 | 30.117 | 19.228 | 19.440 | 19.440 |

Within each scope all three methods have exactly the same successful-source
denominator. The dark row excludes the same one failed source from every score;
the failure remains in the attempt ledger. Do not pool scopes into one unequal
source-weighted mean: two newly accepted sources have only unchanged controls
in this stress set, while eight sources have four cases each. These are reused
development probes, not new training admissions or independent final evaluation.

The clean-leaf policy harms1/10unchanged controls versus6/10chroma9and7/10baseline5,
as previously established. It slightly worsens light recovery relative to
chroma9: four of eight light inputs remain pixel-identical, versus three for
chroma9. Four light inputs have higher error than no correction under either
chroma9orclean-leaf; baseline5harms five. Medium/dark reconstruction improves
on average, but substantial residual error remains. Counterfactual dark severity
is not dark-complexion/MST coverage. None of these results cures the failed clean
gate or overrides the nested selection procedure's rejection of every candidate.

Codex inspected75027,84364,62331and67583source boards.75027remains badly
over-lightened on clean/light inputs and unavailable on dark.62331still has
conspicuous partial corrections;67583's medium result retains patches and its
dark result has strong boundaries.84364's lighter input avoids the baseline's
strong whitening under chroma9but is left unchanged by the clean-leaf policy.
This is qualitative inspection of four sentinel boards, not a claim that every
image was newly reviewed, user acceptance or expert MOS.

## Verification and disposition

Script183independently reloads portable trees, checks every prescribed held-source
fold, all102reports,99correctedPNGs using a separate RGB formula, metrics,
matched-method denominators, known failures and original artifact/input hashes.
Software checks pass; model quality is not validated. The shared pipeline was
unchanged for this test; latest full suite remains701passed from the integration
stage, not a new full-suite run.

Retain the verified development runner and these stress results. No release
model, active asset, lookup or Android behavior changed. These findings do not
justify another rule tuned to this same cohort; light overcorrection and clean
source confusion remain central design limitations alongside approximate
recovery/clipping and weak MST. Final reference/data validation, photographer
MOS, face/neck coverage and Android correction integration remain unfinished.
Android stays paused and CPM deferred.

- [Frozen cases and method allocation](../outputs/development_mst_stress_v1/plan.json)
- [Per-call metrics and retained failures](../outputs/development_mst_stress_v1/summary.json)
- [Independent replay verification](../outputs/development_mst_stress_v1/verification.json)
- [All ten source comparison boards](../outputs/development_mst_stress_v1/review.html)
