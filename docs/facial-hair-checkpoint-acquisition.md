# Obtain the facial-hair checkpoint

30 October 2026. The next diagnostic is waiting for a model asset, not another
mask parameter change.

## Confirmed access result

The public, unauthenticated Roboflow model artifact lookup for
`facial_hair-8quxg/1` returned HTTP401: API key required. The project/version
metadata request also returned HTTP401. Evidence is saved in
`outputs/explicit_facial_hair_access_v1/access_check.json`.
These were read-only GET requests; no photograph or inference request was sent.
This confirms authentication is required for those endpoints, not that an
account will necessarily be allowed to download this particular model.

## User action needed

Open [the project](https://universe.roboflow.com/phd-witpb/facial_hair-8quxg)
in your own Roboflow account and check whether its model can be downloaded for
local inference. Prefer an ONNX instance-segmentation export for version1.
The platform's [download documentation](https://docs.roboflow.com/models/model-weights/download-roboflow-model-weights.md)
describes authenticated download options, but project-specific access may vary.

If available, place the export under
`models/explicit_facial_hair_candidate_v1/`, preserving its original filename,
along with any class-name file, preprocessing/export settings and model reuse
terms supplied with it. Expected labels include beard and mustache; their actual
numeric IDs must be read from the export, never guessed. Do not substitute the
dataset export, a beard-presence classifier or a web/API-only demonstration.

Do not paste API keys into chat or commit them. An account-authorized local
download is enough; photos can remain local. No paid access or dataset purchase
is requested. If download is unavailable, report that outcome before investing
in setup; the DINO alternative has separate access and reuse-term dependencies.

## Work after receipt

1. Hash the files and record provenance, label mapping, preprocessing, output
   tensor format and reuse terms before executing the model.
2. Declare one fixed diagnostic using the same twelve exposed training sources.
   Use only explicit beard/mustache output to remove selected preferred-mask
   pixels; keep the preferred mask and all existing outputs intact.
3. Inspect clean cheeks/chin preservation and facial-hair coverage. Record any
   failure without a threshold sweep. No dense beard ground truth is available,
   so this is a diagnostic rather than validated mask accuracy.
4. Keep the main correction demo unchanged. Even a successful mask diagnostic
   still needs broader confirmation and matching ITA/MST calibration before
   correction-pipeline adoption.

No new model inference, dependency installation, training or pytest run occurred
in this access check. The last full test result remains833 passed in11.62seconds.
