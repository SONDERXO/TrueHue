# Table2 composite and approximate recovery targets

28October2026. User explicitly chose fullTable2distortions with approximate
gamma/red/blue recovery targets. Implemented the fixed
[operator/optimizer protocol](table2-target-fit-protocol.md), without modifying
the existing exact gamma/gain transform or active correction model.

The composite operator preserves the Table2numeric settings, while explicitly
defining their previously unspecified execution: encodedRGBpower, contrast
about0.5, brightness in8bit units, additive red/blue shifts, one finalclip and
uint8rounding. This is an implementation interpretation, not a claimed match
to an unspecified editor. It must be described in the actual thesis method.

Recovery targets are bounded three-parameter RGB least-squares fits from a
fixed identity start, not exact inverse parameters. The existing three-output
tree architecture is retained. Input/reference images and explicit fitting
and scoring masks are needed for target construction only; they do not enter
inference. Parameters, bounds, convergence, rank and residuals are recorded.
Failed/degenerate fits stay unavailable. No global optimum is claimed.

## Synthetic-only verification

Script150uses a fixed32×32syntheticRGBfixture, not skin photos or study sources:

| Setting | Identity RGB RMSE | Fitted RGB RMSE | Pixels clipped by distortion /1024 |
| --- | ---: | ---: | ---: |
| Light | .135065 | .028952 | 21 |
| Medium | .251746 | .108942 | 486 |
| Dark | .324007 | .174240 | 741 |

These are normalized encodedRGBcapacity diagnostics, not CIEDE2000, skin-tone
accuracy or learned model quality. All three fits converge with rank3and no
active parameter bounds, but retain substantial irrecoverable/approximation
residuals. No clipping severity was tuned away. Study-pair eligibility still
excludes clipped training inputs under the existing contract; stress/oracle
diagnostics are kept separate. Passing target-fit checks never overrides it.

[Exact synthetic transform/fit records](../outputs/table2_target_verification_v1/summary.json).

The MST training-row validator now distinguishes exact gamma/gain targets from
composite approximate targets. Composite rows require a converged rank3report,
matching target parameters, adequate explicit support, finite residuals and
report provenance. The caller must verify report hashes against actual files;
the row validator checks their declared format, not external file contents.
No existing held source/pair is promoted by this code.

**671tests pass in12.08s**, including12newtarget/operator tests and7additional
composite-contract tests. Known in-family recovery, identity, residual reporting,
clipping, invalid/flat/small inputs and exclusion of outside-support reference
pixels are covered. SciPy's bounded local optimizer is used as documented in
the [official least_squares reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html).

## Next stage

Freeze a bounded feasibility check on already exposed FairFace development
sources, using the exact256measurement/experimentalMSTcontract. Measure source
and distorted-input availability, clipping and target-fit residuals before
forming a training cohort. Retain all failures and existing holds; any new masks
or source processing require their own quality record. Do not merge native224
rows or the different256veto/ten-feature candidates into this five-feature path.
No study-image generation, tree training, final cohort admission or runtime
replacement happened in this synthetic checkpoint. Android paused, CPM deferred.
