# Paper distortion and target checkpoint

28October2026. User requires staying with the paper. Retain the final tree's
three outputs: gamma, red gain, blue gain. Do not silently add offset/contrast
outputs or call the current gamma/gain diagnostics an implementation ofTable2.

## Mathematical mismatch

Existing transform per channel: `z = gain * x**(1/gamma)`, followed by clipping
and uint8encoding. Without clipping/encoding its inverse has
`gamma_inverse=1/gamma` and `gain_inverse=gain**(-gamma)`. These known targets
are correct only for that transform family.

Table2also specifies brightness(-20/-35/-45), contrast(+5/+8/+10) and color
slider values alongside gamma(.85/.70/.60). An additive brightness/contrast
transform cannot generally be inverted exactly by the same three outputs.
For example an additive negative offset can map a positive green intensity
to zero; any finite positive gamma maps that zero back to zero, not the original
positive intensity. More generally the green channel has no gain/offset output
and a power function cannot equal the inverse of an affine-offset power over
the whole intensity range. Clipping additionally destroys information.

Therefore taking `inverse_parameters()` of only the nominal gamma/gains after
generating fullTable2images would produce incorrect supervised targets.

## Proposed paper-preserving implementation

Keep the full synthetic distortion design and the three-output tree. Fit best
approximate gamma/red/blue recovery parameters against each clean reference
using only the fitting pair's designated scoring/support region. These become
optimization-derived training targets, explicitly distinguished from exact
inverse targets. Report residual target-fit error, clipping and failure rates.
Never use the reference image in inference or to choose held-source predictions.
This target construction is an additional implementation choice requiring
documentation, not a claim that the paper specifies the optimization details.

The alternative is narrowing the synthetic operators to gamma/gains only,
which is a visible departure fromTable2. The user was asked which path to take;
no composite training data were generated while that question is pending.

Before either path, define operator order, brightness units, contrast pivot/
formula and cyan-red/yellow-blue slider-to-RGB conversion. Table2values are
not themselves executable definitions; do not invent an image-editor formula
and describe it as dictated by the proposal. Existing grouping convention is
lightMST1–3, medium4–7, dark8–10in training_manifest.py; preserve its documented
implementation provenance, not a new unstated boundary. Actual lookup estimates
remain experimental and missingMST10output is disclosed.

## Implemented training-row contract

`src/data_preparation/mst_training_contract.py` now checks explicit eligible
TRAIN pair IDs, FairFace/SCINonly, successful unclipped rows, square256mask and
measurement contract, lookup hash, consistent source groups and all five
input-derived features. Official/referenceMSTcannot be substituted for mapped
distorted-inputMST. Exact targets reject offset/contrast/composite transforms.
No existing candidate is admitted by this validator and no runtime changed.

Seventeen tests check admission, dataset/data-role, dimension/hash mismatches,
MST feature leakage, clipping/failure, invalid label/numerics and invalid inverse
targets. A future composite target method must have its own versioned contract
and tests; it will not be accepted by the exact-inverse path accidentally.

Expanded32pairs retain their original holds and different processing policies.
No final training dataset, correction fit or improved performance claim here.
Android stays paused; CPM remains deferred.
