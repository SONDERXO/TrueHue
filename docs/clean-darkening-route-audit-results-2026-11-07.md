# Why the brightness tree darkens a clean photo

7 November 2026. Completed the user-approved [saved-tree diagnosis](clean-darkening-route-audit-protocol-2026-11-07.md).
No predictive model or target was fitted, no image model was run, and no mask,
label or runtime was changed. Four fixed component settings were rendered only
to replay the saved controls and separate brightness from colour damage.

## Plain-language finding

The brightness tree learned to treat a particular range of **whole-scene
brightness** as evidence of added overexposure. A clean photo from the held-out
group falls into that range, so the tree chooses a darkening control learned
entirely from artificially overexposed fitting examples. The latest gate lets
that control through. The small forehead mask makes the wrong change appear
as a distinct dark patch.

The saved target for this clean input is correctly neutral: gamma/red/blue are
all1. The leaf's saved output is also the correct average of its fitting targets.
No checked target identity, feature replay, export, branch or leaf-mean mismatch
explains the error. The problem is the grouping learned by the tree and its
application outside the fitting examples, with a permissive gate.

This evidence does not prove that the background alone caused the outcome.
Whole-scene measurements include face, background and chart. Mask purity and
the contributions of acquisition conditions have not been independently isolated.

## Exact saved route

| Step | Query measurement | Saved decision |
| --- | ---: | --- |
| Whole-scene median lightness |43.92157|At most58.23529: left |
| Whole-scene median lightness |43.92157|Above43.13726: right |
| Selected facial mean lightness |17.51210|At most45.10885: left |
| Gamma leaf |6|Predict gamma1.42861255 |

The direct-exponent renderer darkens midrange pixels when gamma is above1.
Neither ITA nor estimated MST is used in these particular gamma-tree branches,
although they remain supplied features in the retained model design.

The gamma leaf contains51fitting rows:17exposure-over,17cool-plus-over and17warm-
plus-over. They are repeated variants of17original photos from7publisher groups,
not51people. **No fitting clean row reaches this leaf.** Its raw target range is
1.42745–1.42951, mean1.42861255, close to the medium overexposure inverse1/0.70.

All27fitting clean photos reach a different leaf, with predicted gamma0.99898319.
Their scene-median range is30.58824–42.35294. The query's43.92157is above that
clean range and above the43.13726split. Every one of the17matched original clean
counterparts of the focal leaf's distorted examples reaches the near-neutral leaf.

The query is also outside the observed focal-leaf member ranges:

- Scene median: query43.92157, members44.70588–53.33334.
- Facial lightness: query17.51210, members20.46370–44.21040.

It still lies inside the tree branch region. A branch assigning a value does
not mean the query resembles a fitting observation or that the regression output
is calibrated there. The neutral counterpart comparison supports a scene-level
exposure shortcut in this cohort, not final exposure detection on unseen photos.

## Damage caused by each saved control

RGB MAE is measured on the same3906selected working256pixels against the original
clean photographic reference. Those pixels are a forehead fragment, not verified
complete skin ground truth.

| Fixed diagnostic setting | Gamma | Red gain | Blue gain | RGB MAE |
| --- | ---: | ---: | ---: | ---: |
| Neutral |1|1|1|0 |
| Saved gamma only |1.42861|1|1|23.31234 |
| Saved gains only |1|1.01866|0.99637|0.30116 |
| Saved full controls |1.42861|1.01866|0.99637|23.23997 |

All pixels outside the fixed correction mask remain unchanged. Neutral equals
the original input; full equals the already-saved candidate output. These
component errors do not add linearly. The severe error is dominated by gamma;
the gain-only change is smaller but still fails exact clean preservation.

The gain predictor's corresponding leaf contains266fitting rows, including27
clean rows and several distortion types. It predicts their non-neutral average
gains1.01866/0.99637. Likewise, the near-neutral gamma leaf contains108rows:
27clean and27each of cool, warm and additive-colour stress conditions. Thus
including clean fitting targets does not itself give exact neutral controls
when the leaf also averages other targets.

## Why changing gamma alone cannot finish the retained system

We checked the3clean photos changed by the retained research gate. Their saved
red/blue gains are held fixed. For each selected pixel/channel, exact RGB8identity
requires the transformed value to lie within its rounding interval. These
requirements give necessary lower/upper bounds on gamma.

| Retained clean failure | Necessary gamma lower bound | Necessary gamma upper bound | Result |
| --- | ---: | ---: | --- |
| A |1.02195016|1.00419967|Empty interval |
| B |1.02117798|1.00182623|Empty interval |
| C |1.01003662|1.00568736|Empty interval |

Each lower bound exceeds its upper bound. Independent pixel witnesses verify
the contradiction. Consequently, **no positive gamma can make all selected
pixels unchanged in these3cases while retaining those exact gains and applying
the correction**. This is an analytic bound check, not an optimization or sweep.

The certificate applies only to these fixed gains, binary masks and RGB8renderer.
It does not prove the overall task impossible, prohibit gains/gate improvements,
establish a perceptual tolerance or say the gains are large enough to be visible
in every photo. Closed bounds deliberately relax tie-to-even endpoints; an empty
relaxed interval is sufficient for the stated infeasibility.

## What a next repair must address

1. Exposure prediction must account for this failure of absolute scene brightness
   as a proxy for added exposure; removing unrelated colour inputs does not
   change these saved branches.
2. The complete control policy must be able to output neutral gamma **and** gains
   on clean inputs, or the action policy must reliably withhold correction.
   A gamma-only intervention with the retained gains/gate cannot satisfy the
   existing zero-clean-edit screen on these cases.
3. Any repair must still be evaluated on every fixed clean/core/stress attempt,
   with unchanged-photo and individual-harm reporting. Neutral fitting behaviour
   alone is not a guarantee for unseen clean inputs.

The next useful work is to specify one joint control-policy repair against
these requirements before fitting it. This audit does not select another
threshold, feature subset, capacity setting or target adjustment automatically.
ITA/MST and the three-output scope remain. No new fit is activated here.

## Verification and visual review

Scripts549/550replayed both head routes/raw leaf means, all17matched clean
counterparts and accounted for all14conditions of the same original.13have
available feature/control replays; the remaining unavailable-feature condition
is retained and its saved unchanged output independently verified. Focal Lab/ITA statistics and
native-scene features recompute from the matching saved grids. Four component
images, changed-channel counts and RGB errors independently replay. All source
hashes match; held-group membership is excluded from fitting.

Three generated-array tests passed in0.42seconds for the analytic interval
helper: neutral feasibility, conflicting channel constraints, saturated-channel
attenuation and invalid-mask rejection. No generated or photographic fitting.

Viewed3boards: focal correction components/mask; the fitting exposure example
nearest in scene-median lightness and its clean counterpart; and five fixed
same-original conditions (clean, cool, under, over and stress-over). The training
pair is chosen by a declared feature criterion, not favourable output error.
All14saved conditions are accounted for; five are visually displayed.
Dark forehead boundaries and partial-mask recovery remain visible. No actual-skin
truth, blind appraisal or new annotation is claimed.

Private output: `outputs/clean_darkening_route_diagnosis_v1/`. It contains routes,
member identities, feature ranges, component renders, interval witnesses and
verification. Existing artifacts remain unchanged. No model adoption, Android/
desktop changes, admissions, contacts, sharing, publication, commit or push.
