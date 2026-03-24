---
title: "SLIViT for Glaucoma Classification on 3D OCT"
date: 2026-03-12
excerpt: "Mar 2026 - Reproducing SLIViT for binary glaucoma classification on Harvard FairVision OCT data. Achieved 0.869 test AUC."
header:
  teaser: /assets/images/slivit-teaser.png
sidebar:
  - title: "Tech Stack"
    text: "Python, PyTorch, ConvNeXt, ViT, DDP, fp16"
  - title: "Dataset"
    text: "Harvard FairVision - 10K OCT volumes"
  - title: "Best Result"
    text: "0.869 Test AUC"
---

Reproducing the [SLIViT](https://github.com/cozygene/SLIViT) architecture for binary glaucoma classification on [Harvard FairVision](https://github.com/Harvard-Ophthalmology-AI-Lab/FairVision) OCT data.

[View on GitHub](https://github.com/yfeng0206/SliViT_3D_OCT_Glaucoma){: .btn .btn--primary}

## How SLIViT Works

SLIViT classifies 3D medical volumes without a full 3D CNN by slicing the volume into 2D images and processing them in stages:

1. **ConvNeXt-Tiny (feature extractor)** - processes each OCT slice independently. Pretrained on ImageNet, then on the Kermany OCT dataset (84K retinal OCT images).
2. **ViT (integrator)** - takes per-slice features and learns cross-slice relationships.
3. **Classification head** - `LayerNorm + Linear(256, 1)`, outputs a single logit.

## Architecture

```
OCT Volume (200x200x200)
  -> Sample N slices uniformly
  -> Resize each to 256x256, convert grayscale to 3-channel
  -> Tile vertically into one tall image
  -> ConvNeXt-Tiny (ImageNet -> Kermany OCT pretrained)
  -> N feature maps of 768x64 each
  -> Linear projection: 49152-d -> 256-d per token
  -> ViT encoder (5 layers, 20 heads)
  -> CLS token -> LayerNorm -> Linear(256, 1) -> logit
```

Total: 77.8M params (27.8M ConvNeXt, 50M ViT + projections + head).

## Results

### Phase 1: Frozen Feature Extractor

| Slices | Val AUC | Best Epoch |
|--------|---------|------------|
| 32     | 0.831   | 6          |
| 32     | 0.832   | 6          |

### Phase 2: Full Fine-Tuning

| Slices | LR (fe / vit / head) | Test AUC | Best Epoch |
|--------|----------------------|----------|------------|
| 32     | 5e-6 / 1e-5 / 5e-5  | **0.869** | 4         |
| 64     | 1e-6 / 5e-6 / 5e-5  | 0.868    | 6          |
| 64     | 1e-6 / 5e-6 / 5e-5  | 0.866    | 9          |
| 32     | 1e-6 / 5e-6 / 5e-5  | 0.864    | 7          |

**32 slices is enough** - running controlled experiments with gradient accumulation showed negligible difference between 32 and 64 slices (0.866 vs 0.864).

## Training Setup

- **Hardware:** 4x NVIDIA T4 (16GB each)
- **Timing:** 32 slices ~5 min/epoch; 64 slices ~24 min/epoch
- **Stack:** PyTorch 1.13.1, CUDA 11.7, 4-GPU DDP with fp16

## What's Next

- 16 attention heads (eliminate projection layers, drop 50M → ~15M trainable params)
- Data augmentation (random flips, intensity jitter)
- Label smoothing
- Fairness analysis using demographic metadata
