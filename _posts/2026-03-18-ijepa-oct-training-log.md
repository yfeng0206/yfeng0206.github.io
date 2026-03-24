---
title: "Training Log: I-JEPA Self-Supervised Pretraining for OCT Glaucoma"
date: 2026-03-18
categories:
  - research
tags:
  - medical-ai
  - self-supervised-learning
  - computer-vision
  - oct
  - glaucoma
toc: true
toc_sticky: true
---

Self-supervised pretraining using [I-JEPA](https://github.com/facebookresearch/ijepa) on [Harvard FairVision](https://github.com/Harvard-Ophthalmology-AI-Lab/FairVision) OCT data for binary glaucoma classification. Builds on our [SLIViT reproduction](/research/slivit-glaucoma-training-log/).

[GitHub Repo](https://github.com/yfeng0206/I-JEPTA_3D_OCT){: .btn .btn--primary}

## Motivation

Our SLIViT experiments reached 0.869 test AUC using a ConvNeXt feature extractor pretrained on Kermany OCT and a ViT integrator trained on 6K labeled volumes. Two bottlenecks limited further improvement:
1. ConvNeXt features were pretrained on a different task (not glaucoma)
2. The ViT integrator was trained from scratch on a small labeled dataset

I-JEPA addresses both by learning representations directly from unlabeled OCT data through masked prediction in representation space. No hand-crafted augmentations needed.

## Two Approaches

### Patch-Level I-JEPA (Primary)

Standard I-JEPA applied to individual 256x256 OCT slices. Each slice is patchified into a 16x16 grid of 256 patches. The encoder learns within-slice spatial features (retinal layer boundaries, RNFL thickness patterns, optic nerve structures).

**Training data:** 6,000 volumes x 100 slices = **600,000 slice images** (self-supervised, no labels).

| Component | Architecture | Params |
|-----------|-------------|--------|
| Context encoder | ViT-B/16 (12 layers, 768-d, 12 heads) | 86M |
| Target encoder | Same as context (EMA, no grad) | 86M |
| Predictor | Narrow ViT (6 layers, 384-d, 12 heads) | 11M |

### Slice-Level I-JEPA (Experimental)

Applied to sequences of slice features within each volume. A ConvNeXt encodes each of 32 slices to a 768-d vector. The encoder then learns cross-slice relationships using 1D contiguous masking.

**Spoiler: this approach collapsed.** See results below.

## Comparison with Original I-JEPA

| | Original I-JEPA | Patch-level (ours) | Slice-level (ours) |
|--|----------------|-------------------|-------------------|
| Dataset | ImageNet 1.2M | 600K OCT slices | 6K OCT volumes |
| Encoder | ViT-H/14 (630M) | ViT-B/16 (86M) | SliceViT (85M) |
| Masking | 2D block, 4 targets | 2D block, 4 targets | 1D contiguous, 4 targets |
| Hardware | 16x A100 80GB | 4x T4 16GB | 4x T4 16GB |

We use ViT-B instead of ViT-H because our dataset is 6–160x smaller than ImageNet.

## Adapting I-JEPA for 1D Slice Sequences

Three key design choices for slice-level:

1. **Joint predictor processing** - mask tokens from all 4 target blocks attend to each other, making prediction a joint reasoning task
2. **Sampled context block** - a contiguous 75–90% block (not all non-target positions) to prevent trivial interpolation
3. **Block-wise batch repetition** - maintains correct alignment across the multi-mask training loop

## Results

### Slice-Level: Representation Collapse

Collapsed within 1–2 epochs across all configurations:

| Epoch | train_loss | val_loss | cos_sim | rep_diversity |
|-------|-----------|---------|---------|---------------|
| 1 | 0.0375 | 0.0006 | 0.9998 | 0.9983 |
| 2 | 0.0006 | 0.0003 | 1.0000 | 0.9993 |
| 3 | 0.0000 | 0.0000 | 1.0000 | 0.9992 |

**Root cause:** 32 tokens is too few, and adjacent OCT slices produce highly correlated ConvNeXt features - prediction becomes trivially solvable by interpolation.

### Patch-Level Run 1: LR=0.0005 (Too High)

600K slices, ViT-B/16, effective batch=512, 15 warmup epochs. Stopped at epoch 26.

| Epoch | train_loss | val_loss | cos_sim | LR |
|-------|-----------|---------|---------|-----|
| 1 | 0.1298 | 0.2152 | 0.6971 | ~0.0001 (warmup) |
| **11** | **0.2073** | **0.2081** | **0.72** | **~0.0004** |
| 15 | 0.2153 | 0.2187 | 0.68 | 0.0005 (peak) |
| 25 | 0.3047 | 0.3059 | 0.58 | ~0.0004 |

The model learned well during warmup (epochs 1–11) but **destabilized at peak LR**. OCT images are less diverse than ImageNet, producing more correlated gradients - the effective learning rate is higher than sqrt scaling predicted.

### Patch-Level Run 2: LR=0.00025 (In Progress)

Based on Run 1 findings: halved peak LR, shortened warmup to 5 epochs, reduced patience to 8. The model learned best around LR 0.0003–0.0004 in Run 1, so a peak of 0.00025 with cosine decay should keep LR in the productive range throughout training.

**Status: training in progress.** Will update with results.

## Training Time Estimates (4x T4 GPUs)

| Phase | Dataset | Time/epoch | Epochs | Total |
|-------|---------|-----------|--------|-------|
| Patch pretraining | 600K slices | ~71 min | 50 | ~59 hrs |
| Slice pretraining | 6K volumes | ~3.5 min | 100 | ~6 hrs |
| Downstream (patch) | 6K labeled | ~2 min | 20–50 | ~1–2 hrs |

## References

- Assran et al., "Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture" ([paper](https://arxiv.org/abs/2301.08243))
- Avram et al., "SLIViT" ([paper](https://pubmed.ncbi.nlm.nih.gov/38045283/))
- Luo et al., "Harvard FairVision Dataset" ([paper](https://arxiv.org/abs/2310.02492))
