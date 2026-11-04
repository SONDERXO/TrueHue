# Pinned FFHQ support metadata

`ffhq-repository-4826aa6.json` is the existing saved official GitHub repository-
tree response for `NVlabs/ffhq-dataset`, revision
`4826aa6ea77aa7f1a7802b938ed7c40afb985cda`. It records published paths and Git
blob hashes; it contains no photos, MST labels, credentials or trained models.
It is copied byte-for-byte from the existing TrueHue acquisition evidence so
the original downloader can verify its pinned upstream script in a fresh clone.

FFHQ is by NVIDIA, associated with Karras, Laine and Aila,
*A Style-Based Generator Architecture for Generative Adversarial Networks*.
Official source: https://github.com/NVlabs/ffhq-dataset/tree/4826aa6ea77aa7f1a7802b938ed7c40afb985cda

FFHQ's metadata/documentation licence is CC BY-NC-SA4.0; its original licence
notice is retained in `ffhq-LICENSE.txt`. The JSON support record is unchanged
upstream metadata, and is identified as such rather than claimed as original
TrueHue implementation. Individual photograph licences remain separate and
are recorded by the photographic acquisition scripts. See the official README
and the source-preparation report for attribution/use limitations.

`scripts/413_restore_ffhq_support_metadata.py` copies this public support record
to the legacy local path required by script408. It never fabricates the rest
of that historical assessment or overwrites a differing existing record.
