# CPM pattern-branch feasibility protocol

27 October 2026. Declared before checkpoint download or inspection. Continue
autonomous material-protection work, retaining all previous masks, labels,
reviews, folds, reference-quality flags and training holds.

Investigate one lead: the pattern branch of VinAIResearch/CPM, pinned source
revision `101b1ff6a4275b6da434ca5658533eb232d57fa8`. This is a feasibility
investigation, not candidate adoption or a claim of general paint recognition.
The author documents synthetic pattern masks in CPM-Synt-1; the full system
performs makeup transfer. No dataset, external portrait or example image will
be downloaded/viewed. Source documentation/code only; no source execution.

Author's checkpoint pointer:
https://drive.google.com/file/d/1ciy8INrxMQufDodT4a89KxrpZn4le4ud/view

Download only the pattern checkpoint, if accessible, with a256MiB upper bound,
to the configured models root under an experimental directory. Record actual
bytes/SHA256/final URL and retrieval status. Reject HTML/interstitial/error
responses and oversized downloads. No dependency installation or changes to
the existing Python3.14environment. No color branch or PRNet weight downloads.

Treat the published checkpoint as untrusted serialized data. Inspect ZIP
metadata and bounded `data.pkl` opcodes using `zipfile`/`pickletools` only;
never use pickle.load, torch.load, source execution or extraction. Report
serialized GLOBAL names without importing those modules. If it is not a
bounded readable ZIP/pickle stream, retain the explicit inspection limitation.
No imported serialized model, tensor inference, new mask or training follows.

Review exact label semantics, raw-portrait versus UV-texture input, scaling/
normalization, mask channel and threshold conventions, original software stack,
code versus dataset/checkpoint licensing evidence and available deployment
artifacts. Source defaults are not proof of actual checkpoint architecture or
calibration. Reconcile discrepancies before a prospective diagnostic protocol.

The desired future diagnostic would be a removal-only protected-material veto
alongside the anatomical parser, recomputed separately for each stage/input.
It is not permission to turn makeup transfer/removal into a color correction
target, use invented bare-face colors, or bypass uncertainty/reference gates.
Full native-coordinate UV mapping and independent CPU/export parity must be
specified before image inference. Actual source/reference adjudication remains
uncompleted; no current labels are promoted to expert truth.

Record a machine-readable readiness report. The current stage succeeds when
provenance/serialization/input-contract feasibility is established or precise
technical limitations are saved. Download failure is not model failure; no
unavailable result is converted into a passing protection score. Learned
material segmentation is an additional proposal departure; no Android app,
training admission, regeneration or correction-tree fitting is included.
