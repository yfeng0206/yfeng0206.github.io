---
title: "I-JEPA for OCT Glaucoma Classification"
date: 2026-05-04
excerpt: "Mar 2026 - Present - I-JEPA self-supervised pretraining on Harvard FairVision OCT. 0.8878 test AUC fine-tuned, with a probe-architecture ablation and an occlusion-attribution interpretability study."
header:
  teaser: /assets/images/ijepa-teaser.png
sidebar:
  - title: "Tech Stack"
    text: "Python, PyTorch, ViT-B/16, I-JEPA, DDP"
  - title: "Dataset"
    text: "Harvard FairVision - 600K OCT slices (SSL), 10K volumes (eval)"
  - title: "Best Result"
    text: "0.8878 Test AUC (fine-tune, LLRD γ=0.5)"
  - title: "Status"
    text: "Phase 4 in progress (FM baselines)"
---

Self-supervised pretraining with [I-JEPA](https://github.com/facebookresearch/ijepa) (Assran et al., CVPR 2023) on [Harvard FairVision](https://github.com/Harvard-Ophthalmology-AI-Lab/FairVision) OCT data, evaluated via frozen probe + fine-tune on binary glaucoma classification. Builds on our [SLIViT reproduction](/portfolio/slivit-3d-oct-glaucoma/).

[View on GitHub](https://github.com/yfeng0206/I-JEPTA_3D_OCT){: .btn .btn--primary}

## Top-line Result

Random-init ViT-B/16, 100 epochs SSL on 600K OCT slices. Held-out test split (3,000 volumes).

| Method | Probe | **Test AUC** |
|:-------|:------|:------------:|
| **Fine-tune + LLRD γ=0.5** | AttentiveProbe d=1 | **0.8878** |
| Frozen probe | CrossAttnPool (277K params) | 0.8791 |

**Headline finding:** under fine-tuning, probe architecture is irrelevant. AttentiveProbe (7.17M), CrossAttnPool (277K), and MeanPool (zero probe params, just a 2.3K linear head) all land within 0.001 Test AUC of each other (p > 0.6 pairwise, paired bootstrap B=2000). In the frozen regime CrossAttnPool is Pareto-optimal; under fine-tune, MeanPool is. Full 2x3 probe x train-regime matrix with confidence intervals in the [ablation analysis](https://github.com/yfeng0206/I-JEPTA_3D_OCT/blob/main/docs/experiments/frozen/ablation_analysis.md).

![Probe-architecture ranking on ep100](/assets/images/ijepa-probe-ranking.png)

## Method

I-JEPA on 256x256 OCT slices, ViT-B/16, peak LR 0.00025, EMA 0.996 → 1.0, effective batch 512, 100 epochs on 4x T4. Downstream: frozen ViT encodes each slice (patches mean-pooled within slice → per-slice 768-dim token), 100 slices per volume, slice-aggregation probe + linear head. Fine-tune uses MAE-style LLRD γ=0.5 with base LR 2e-4.

Architecture-agnostic occlusion attribution confirms the three fine-tune probes converge on the same slice-level structure (MeanPool vs CrossAttnPool curves correlate at r = 0.94), and the apparent "bimodal disc-rim" pattern is an OD/OS axial-storage artefact rather than bilateral anatomy. [Interpretability writeup](https://github.com/yfeng0206/I-JEPTA_3D_OCT/blob/main/docs/experiments/interpretability.md).

## Roadmap

- Phase 1 (done): Random-init I-JEPA SSL → frozen probe + fine-tune evaluation
- Phase 2 (done): Probe-architecture ablations (2x3 matrix with bootstrap CI)
- Phase 3 (done): Interpretability (occlusion attribution, OD/OS mirror test, fp16 precision fix)
- Phase 4 (in progress): Foundation-model baselines on the same Test split (DINOv3, OCTCube)
- Phase 5 (planned): 3D-aware SSL extension (multi-view / axial)

More on GitHub: [architecture spec](https://github.com/yfeng0206/I-JEPTA_3D_OCT/blob/main/docs/architecture.md), [experiments index](https://github.com/yfeng0206/I-JEPTA_3D_OCT/tree/main/docs/experiments), [research log](https://github.com/yfeng0206/I-JEPTA_3D_OCT/blob/main/docs/research_log.md).
