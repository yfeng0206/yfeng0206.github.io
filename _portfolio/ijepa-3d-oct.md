---
title: "I-JEPA for OCT Glaucoma Classification"
date: 2026-08-14
excerpt: "Mar 2026 - Present - I-JEPA self-supervised pretraining on Harvard FairVision OCT. Anatomy-shaped masking reaches 0.8947 test AUC, beating random-masking I-JEPA at every probe and regime."
header:
  teaser: /assets/images/ijepa-teaser.png
sidebar:
  - title: "Tech Stack"
    text: "Python, PyTorch, ViT-B/16, I-JEPA, MIRAGE, DDP"
  - title: "Dataset"
    text: "Harvard FairVision - 600K OCT slices (SSL), 10K volumes (eval)"
  - title: "Best Result"
    text: "0.8947 Test AUC (anatomy-shaped masking, fine-tune)"
  - title: "Contribution"
    text: "Anatomy-shaped connected mask targets"
  - title: "Collaboration"
    text: "with Wai Tak Lau (PhD), Columbia University"
  - title: "Status"
    text: "Phase 4 in progress (FM baselines)"
---

Self-supervised pretraining with [I-JEPA](https://github.com/facebookresearch/ijepa) (Assran et al., CVPR 2023) on [Harvard FairVision](https://github.com/Harvard-Ophthalmology-AI-Lab/FairVision) OCT data, evaluated via frozen probe + fine-tune on binary glaucoma classification. Builds on our [SLIViT reproduction](/portfolio/slivit-3d-oct-glaucoma/).

[View on GitHub](https://github.com/yfeng0206/I-JEPA_3D_OCT){: .btn .btn--primary}
[Checkpoints on Hugging Face](https://huggingface.co/yfeng0206/ijepa-3d-oct-checkpoints){: .btn .btn--info}

## Top-line Result

Best downstream glaucoma classifier: **0.8947 Test AUC** on the 3,000-volume held-out FairVision test split, from a fine-tuned MeanPool probe on an encoder pretrained with **anatomy-guided masking**, which biases I-JEPA's prediction targets onto the retinal band instead of scattering them uniformly.

![Best downstream Test AUC: anatomy-guided masking 0.8947 vs random-masking I-JEPA 0.8878](/assets/images/ijepa-oracle-headline.png)

Paired bootstrap, B=2000, on the Test split:

| Regime | Probe | Random | Anatomy-guided | Δ | p |
|:-------|:------|:------:|:--------------:|:-:|:-:|
| Frozen | MeanPool | 0.8746 | 0.8855 | +0.0109 | <0.0005 |
| Fine-tune | MeanPool | 0.8868 | **0.8947** | +0.0079 | 0.001 |
| Fine-tune | CrossAttnPool | 0.8872 | 0.8937 | +0.0065 | 0.009 |
| Fine-tune | AttentiveProbe d=1 | 0.8878 | 0.8901 | +0.0023 | 0.26 (ns) |

## The Contribution: Target Shape, Not Target Location

The novelty is **anatomy-shaped connected targets**, not the use of a segmentation prior in general. To make that precise we run two MIRAGE-guided arms that both put targets on the retina and differ only in target geometry:

- `mirage_envelope` - MIRAGE places ordinary **rectangular** I-JEPA targets on the retina
- `mirage_anatomy` - MIRAGE **shapes** connected, irregular targets to the tissue itself

Both arms share identical weights through epoch 27 and diverge only over epochs 28-30:

| Arm | Test AUC (5 probe seeds) |
|:----|:------------------------:|
| envelope ep30 | 0.8528 ± 0.0018 |
| **anatomy ep30** | **0.8582 ± 0.0003** |

Delta +0.0054, Welch p=0.00219, Cohen's d=4.20. The arms fully separate: the worst anatomy seed (0.8578) still beats the best envelope seed (0.8542).

The mechanism is **budget efficiency**. Rectangles must spend 5.4x more hidden budget on background to hide comparable retina (81.3 vs 15.0 background cells). Anatomy masking puts 72.1% of masked cells on tissue versus 30.7% for the rectangle envelope, at a comparable retinal budget.

![Three-arm matched masking comparison](/assets/images/ijepa-masking-arms.png)

A matched-area control (`random_matched`) isolates shape from area: at matched hidden count and context, anatomy places **3.0x** more targets on retina (98.3% vs 32.7%) with a 1.7% fallback rate.

## Two Negative Results Worth Reporting

**Validation loss cannot rank masking strategies.** It is inverted against targeting quality: `random_matched` gets the best val loss (0.0041) with the worst on-region fraction (0.327), while anatomy gets the worst val loss (0.0445) with the best targeting (0.983). Predicting mostly-background patches is trivially easy. Only downstream AUC ranks these methods.

**Representation diversity is not a collapse metric for OCT.** Retina occupies only 17.6% of grid cells, so 97% of tile pairs involve background and the all-pairs mean is dominated by it. The apparent collapse signal tracks masking ratio, not target shape; against its proper matched control, anatomy adds only +0.012.

## Probe-architecture Ablation (random-init baseline)

Random-init ViT-B/16, 100 epochs SSL on 600K OCT slices, full 2x3 matrix on the Test split.

| Method | Probe | Params (trainable) | **Test AUC** |
|:-------|:------|:------------------:|:------------:|
| Fine-tune + LLRD γ=0.5 | AttentiveProbe d=1 | 7.17M + 86M encoder | **0.8878** |
| Fine-tune + LLRD γ=0.5 | CrossAttnPool | 277K + 86M encoder | 0.8872 |
| Fine-tune + LLRD γ=0.5 | MeanPool | 2.3K + 86M encoder | 0.8868 |
| Frozen probe | CrossAttnPool | 277K | 0.8791 |
| Frozen probe | MeanPool | 2.3K | 0.8746 |
| Frozen probe | AttentiveProbe d=1 | 7.17M | 0.8706 |

**Finding:** under fine-tuning, probe architecture is irrelevant. AttentiveProbe (7.17M), CrossAttnPool (277K), and MeanPool (zero probe params, just a 2.3K linear head) all land within 0.001 Test AUC of each other (p > 0.6 pairwise, paired bootstrap B=2000). In the frozen regime CrossAttnPool is Pareto-optimal; under fine-tune, MeanPool is. Full matrix with confidence intervals in the [ablation analysis](https://github.com/yfeng0206/I-JEPA_3D_OCT/blob/main/docs/experiments/frozen/ablation_analysis.md).

![Probe-architecture ranking on ep100](/assets/images/ijepa-probe-ranking.png)

## Method

I-JEPA on 256x256 OCT slices, ViT-B/16, peak LR 0.00025, EMA 0.996 → 1.0, effective batch 512, 100 epochs on 4x T4. Downstream: frozen ViT encodes each slice (patches mean-pooled within slice → per-slice 768-dim token), 100 slices per volume, slice-aggregation probe + linear head. Fine-tune uses MAE-style LLRD γ=0.5 with base LR 2e-4.

Architecture-agnostic occlusion attribution confirms the three fine-tune probes converge on the same slice-level structure (MeanPool vs CrossAttnPool curves correlate at r = 0.94), and the apparent "bimodal disc-rim" pattern is an OD/OS axial-storage artefact rather than bilateral anatomy. [Interpretability writeup](https://github.com/yfeng0206/I-JEPA_3D_OCT/blob/main/docs/experiments/interpretability.md).

## Checkpoints

Both pretraining arms are published on [Hugging Face](https://huggingface.co/yfeng0206/ijepa-3d-oct-checkpoints) (private repo, access on request): `random-posfix-100ep/` (stock uniform-random block placement, ep025-ep100) and `oracle-anatomical-100ep/` (anatomy-guided target placement, forked from random ep025). Each file is a full training state; use `target_encoder`, the EMA teacher, for feature extraction.

One trap worth flagging: the `-lowest-pretrain-loss-*` checkpoints are **not** better. Pretraining loss in I-JEPA is close to an anti-signal, and the random arm's minimum lands at epoch 1. Use `ep100`.

## Roadmap

- Phase 1 (done): Random-init I-JEPA SSL → frozen probe + fine-tune evaluation
- Phase 2 (done): Probe-architecture ablations (2x3 matrix with bootstrap CI)
- Phase 3 (done): Interpretability (occlusion attribution, OD/OS mirror test, fp16 precision fix)
- Masking strategy (done): anatomy-guided masking beats random, frozen +0.011 (p<0.0005) and fine-tune +0.008 (p=0.001); matched-budget and rectangle-envelope controls isolate target shape
- Phase 4 (in progress): Foundation-model baselines on the same Test split (DINOv3, OCTCube)
- Phase 5 (planned): 3D-aware SSL extension (multi-view / axial)

More on GitHub: [architecture spec](https://github.com/yfeng0206/I-JEPA_3D_OCT/tree/main/docs/architecture), [masking experiments](https://github.com/yfeng0206/I-JEPA_3D_OCT/tree/main/docs/experiments/masking), [experiments index](https://github.com/yfeng0206/I-JEPA_3D_OCT/tree/main/docs/experiments), [research log](https://github.com/yfeng0206/I-JEPA_3D_OCT/blob/main/docs/research_log.md).
