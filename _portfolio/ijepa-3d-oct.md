---
title: "I-JEPA for OCT Glaucoma Classification"
date: 2026-03-18
excerpt: "Mar 2026 - Present - Self-supervised pretraining with I-JEPA on Harvard FairVision OCT data. Pretraining converged; downstream probe evaluation in progress."
header:
  teaser: /assets/images/ijepa-teaser.png
sidebar:
  - title: "Tech Stack"
    text: "Python, PyTorch, ViT-B/16, I-JEPA, DDP"
  - title: "Dataset"
    text: "600K OCT slices (self-supervised)"
  - title: "Status"
    text: "In Progress"
---

Self-supervised pretraining using [I-JEPA](https://github.com/facebookresearch/ijepa) on [Harvard FairVision](https://github.com/Harvard-Ophthalmology-AI-Lab/FairVision) OCT data for binary glaucoma classification. Builds on our [SLIViT reproduction](/portfolio/slivit-3d-oct-glaucoma/).

[View on GitHub](https://github.com/yfeng0206/I-JEPTA_3D_OCT){: .btn .btn--primary}

## Motivation

Our SLIViT experiments reached 0.869 test AUC but hit two bottlenecks: ConvNeXt features pretrained on a different task (not glaucoma), and the ViT integrator trained from scratch on only 6K labeled volumes.

I-JEPA addresses both by learning representations directly from **unlabeled** OCT data through masked prediction in representation space - no hand-crafted augmentations needed.

## Two Approaches

### Patch-Level I-JEPA (Primary)

Standard I-JEPA applied to individual 256x256 OCT slices. Each slice is patchified into a 16x16 grid of 256 patches. Training data: 6,000 volumes x 100 slices = **600,000 slice images**.

| Component | Architecture | Params |
|-----------|-------------|--------|
| Context encoder | ViT-B/16 (12 layers, 768-d, 12 heads) | 86M |
| Target encoder | Same (EMA, no grad) | 86M |
| Predictor | Narrow ViT (6 layers, 384-d, 12 heads) | 11M |

### Slice-Level I-JEPA (Experimental)

Applied to sequences of slice features within each volume. **Result: representation collapse** - adjacent OCT slices produce highly correlated features, making masked prediction trivially solvable.

## Results

### Patch-Level Pretraining

- **Run 1 (LR=0.0005):** Too aggressive for OCT. Model learned during warmup but destabilized at peak LR due to correlated gradients. Best at epoch 11.
- **Run 2 (LR=0.00025):** Steady improvement, but cut short by an early stopping bug - pre-warmup epoch recorded artificially low val_loss since EMA hadn't diverged.
- **Run 3 (LR=0.00025, resumed):** Converged at epoch 11 (val_loss=0.1586). Healthy diagnostics throughout: cos_sim ~0.80, no representation collapse.

### Downstream: Attentive Probe

Frozen ViT-B/16 encoder + attentive probe (2 transformer blocks, ~14.3M trainable params) + linear head. Features pre-computed and cached to disk for fast training (~30s/epoch).

**Results pending.**
