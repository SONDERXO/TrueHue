# Saved-tree diagnosis of severe clean-photo darkening

7 November 2026. User approves the proposed saved-trace diagnosis (“alright lets
do that”), not new training. The focal case is the persistent worst clean gamma
error in the completed MST-excluded gate comparison: development `case_28__clean`.
Its identity and outcomes are already exposed; this is retrospective diagnosis.

## Fixed scope

- Reuse the original saved split-control fold for this photo's held publisher
  group, frozen input vectors, prepared targets and images, and both retained
  and latest gate decisions. No fit, threshold/feature sweep or image-model pass.
- Replay the exact float32tree route and raw leaf mean. Count fitting recipes,
  original photos and publisher keys; compare all fitting clean vectors and
  matched clean counterparts of the distorted examples in the focal leaf.
- Check all14saved conditions from the same original and their actual saved
  routes/controls/errors. No new distortion or reference is created.
- Recompute the focal original-pixel Lab/ITA statistics and native scene features
  using their matching existing grids. Do not substitute current desktop masks.
- Render exactly four diagnostic component settings: neutral, saved gamma only,
  saved gains only and saved full controls. These are arithmetic replays, not
  new fitted targets or predictive experiments. Verify full equals saved output,
  neutral equals input, and outside-mask pixels never change.
- Test whether any gamma-only replacement could preserve the three clean photos
  changed by the retained gate while holding its saved red/blue gains fixed.
  Use analytic rounding bounds for the existing binary-mask RGB8renderer, not
  an optimizer, parameter search or an actual model intervention. An empty
  necessary interval proves impossibility only for that fixed-gain/input case,
  not for the broader correction task.

Preliminary read-only inspection already found the overexposure-only leaf and
non-neutral retained clean gains. Record those observations rather than claiming
blind or previously unobserved evidence. Keep all individual identities, masks,
vectors and bound witnesses in private ignored outputs.

## Stop and verification

Independently check route branches, member identities, raw target means,
clean-counterpart membership, component RGB changes, all14condition parity and
source hashes. Inspect focal input/mask/components and fixed-context boards.
No inference reference labels, new annotations, admissions or runtime changes.
Conclude which mechanism is supported and what a next repair would have to
address. No new training or adoption follows automatically from this diagnosis.
