# Portrait calibration source strategy — 11 November 2026

Two sources merit targeted documentation/access checks: **STW for direct
photographic MST references**, and **CHROMA-FIT for independently measured facial
colour**. Neither is acquisition-ready or admitted. Do not run another fit from
the exhausted local batches, reopen the failed experiments or request more masks.

## Ranked leads

**1. Skin Tone in the Wild (STW): first metadata/readiness priority.** The
[October2026 paper](https://arxiv.org/html/2603.02475v2) reports 42,313 portraits
from 3,564 identities with identity-level MST labels. A primary annotator labels
the full set; two others assess a subset. FairFace and CelebA are among its
constituents, so source overlap matters. This is estimated appearance annotation,
not physical colorimetry. The
[author repository](https://github.com/vitorpmh/STW) links image/split files but
warns that its current release differs from the paper. It requires following
constituent dataset licences; an aggregate licence is unfinished. The Drive
landing page opened, but item-level release membership was not established.

Our next step should establish actual released annotation/split schemas, source
identity mapping and permitted training use before any image acquisition. Compare
source IDs against existing train/development/locked metadata without opening
locked images. No annotator label or image has been imported. Do not install or
adopt SkinToneNet: the final correction model remains a decision tree.

**2. CHROMA-FIT: strongest physical-reference lead, access unresolved.** The
[author publication](https://openaccess.thecvf.com/content/WACV2024W/DVPBA/html/Pangelinan_The_CHROMA-FIT_Dataset_Characterizing_Human_Ranges_of_Melanin_for_Increased_WACVW_2024_paper.html)
describes approximately2,300 portrait images of209 participants indoors/outdoors,
with corresponding measured skin-tone references. The
[Florida Tech lab publication list](https://research.fit.edu/idl/publications/)
confirms the work. A usable file release, training terms and an MST reference
field were not verified. The publisher's full paper fetch returned403; its indexed
abstract and lab listing were accessible. Do not infer a training licence from
the paper or invent an MST conversion from colorimeter values. No contact or
access request was sent.

## Sources that do not resolve this task

- [MSKCC Skin Tone Labeling](https://api.isic-archive.com/collections/413/)
  supplies colorimeter/MST-related metadata but its4,879 images are dermoscopic,
  not portrait inputs. Physical-reference quality alone does not fix modality.
- [TrueSkin](https://arxiv.org/abs/2509.10980) uses six classes, not the retained
  ten-tone MST label space. Do not fabricate a six-to-ten mapping.
- [FACET](https://ai.meta.com/datasets/facet/) describes evaluation-only rights;
  it is not a new calibration-training source.
- The [MST-E paper's use statement](https://openreview.net/pdf?id=L9I9FhHfS3)
  prohibits training models on its images. Existing protected allocations and
  stopped local screens must not become a fitting cohort.
- DAST remains user-dropped. Its reappearance in search is not authorization to
  contact, reacquire or reconsider that decision. Existing PPR10K targets remain
  correction evidence, not intrinsic MST labels; the local SCIN nine-case screen
  remains closed with zero facial measurements.

## What would make the first lead actionable

For STW, verify a named release and annotation provenance; actual available
source-image keys and identity groups; training permissions per constituent;
cross-source/locked allocation conflicts; and label disagreement/missingness.
Only then design a bounded image-slot portrait/support/brightness screen with
all failures retained and no outcome-based subset. More samples do not guarantee
the required lighting stability or preservation gates.

For CHROMA-FIT, first establish the access route, recipient terms, reference
measurement site/illuminant/geometry, identity records and whether actual MST
annotations exist. Colorimeter Lab, CST and MST must remain distinct. Any use as
physical-colour validation instead of direct MST calibration needs an explicit
role design; do not silently change the user's retained ITA/MST requirement.

This review selects **metadata-level readiness work on STW first**, with
CHROMA-FIT a documented alternative. It does not select acquisition, a model
checkpoint, training, a new calibration formula or architectural change. No
camera/participant request is repeated. No email, form submission or external
message occurred. Public documentation and source papers were browsed only; no
dataset/checkpoint assets, repositories or packages were downloaded.

All local sources, annotations and negative results remain preserved. Zero local
photo reads, image-model calls, fits or predictions occurred. Final24 and older
locked images remain byte-unread. Decision tree, ITA/MST and single-photo inference
remain required. No runtime/Android change, upload, commit or push. The working
model remains incomplete; neither source is promised to solve it.
