# Recovery-oriented exposure controls: declared supplemental recipe

30 October 2026. The user authorized primary training-data preparation. The
unchanged three-variant recipe on 26 approved references produces eleven
unclipped screen-passing candidates: ten color and one exposure. To avoid
training a nominal exposure model on almost no usable exposure examples,
prepare two explicitly supplemental gamma-only controls per existing source.
This is data preparation, not a feature/model search or automatic admission.

Let g be the source's already recorded Table 2 gamma (currently light/medium
groups). Keep these magnitudes; no strength sweep or pixel threshold search.
On the exact approved reference support, generate:

- `gamma_lighten`: y = x**g.
- `gamma_darken`: y = x**(1/g).

Green and red/blue gains stay one, with no contrast, brightness or channel
offsets. In float arithmetic these positive powers map [0,1] to [0,1] without
range clipping. Their direct-exponent inverse targets are respectively 1/g
and g, with both gain targets one. Encode once by round-to-nearest uint8.
Before encoding the inverse is algebraic; after quantization recovery is not
exact. Report newly zeroed/nonzero channel samples and target reconstruction
residuals instead of claiming quantization is harmless.

This **is not the complete Table 2 augmentation** and not a formula claimed
verbatim from the proposal. It is a versioned supplemental training control
that exercises the same gamma/red/blue correction family. The original Table 2
values, composite recipes, three-variant set and authorized clipped stress
training are preserved; none are silently weakened or deleted. Future thesis
method/results must describe the supplemental data separately.

Use exactly the same 26 approved originals, original square256 rule mask and
matching experimental MST, source groups, notes and locked evaluation roles.
Input measurement uses generated pixels only. Retain original controls and
generate 52 supplemental inputs. Compute input features and masks anew; no
reference-based mask fallback. Retain the fixed existing support screen and
1000-pixel measurement minimum; no new mask threshold.

Every new distorted mask remains pending explicit review, irrespective of
reference approval or an algebraic target. No correction-tree fitting or
new final-evaluation claims. Freeze gamma controls, color candidates and
identity roles before the single planned training comparison. Verify all
52 power curves, quantization, targets, measurement masks and feature vectors,
role counts and unchanged source/reference evidence.
