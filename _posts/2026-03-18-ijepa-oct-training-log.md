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

### Patch-Level Run 2: LR=0.00025 (Early Stopping Bug)

Reduced peak LR to 0.00025, shortened warmup to 5 epochs, patience=8. Training showed steady improvement but was cut short by an early stopping bug: epoch 1 (pre-warmup) recorded artificially low val_loss=0.1197 because the EMA target hadn't diverged yet, making it impossible to beat. The model improved from 0.2114 to 0.1636 (epochs 3-9) but early stopping triggered at epoch 9 since it could never beat epoch 1. Fix applied: early stopping now only counts after warmup.

### Patch-Level Run 3: LR=0.00025, Resume from Epoch 9 (Converged)

Resumed from Run 2's epoch 9 checkpoint with the early stopping fix. Training converged at epoch 11 (val_loss=0.1586) and plateaued through epoch 18 when the job crashed due to an NCCL timeout from blocking blob uploads.

| Epoch | train_loss | val_loss | cos_sim | rep_diversity | Notes |
|-------|-----------|---------|---------|---------------|-------|
| 10 | 0.1596 | 0.1586 | 0.81 | 0.80 | new best |
| 11 | 0.1574 | 0.1586 | 0.82 | 0.73 | tied best |
| 12 | 0.1589 | 0.1590 | 0.81 | 0.73 | patience 1 |
| 13 | 0.1589 | 0.1593 | 0.82 | 0.80 | patience 2 |
| 14 | 0.1595 | 0.1595 | 0.81 | 0.74 | patience 3 |
| 15 | 0.1591 | 0.1598 | 0.83 | 0.72 | patience 4 |
| 16 | 0.1595 | 0.1599 | 0.80 | 0.72 | patience 5 |
| 17 | 0.1603 | 0.1606 | 0.83 | 0.73 | patience 6 |
| 18 | 0.1618 | 0.1616 | 0.79 | 0.70 | patience 7 (crashed) |

Diagnostics remained healthy: cos_sim ~0.80 (good prediction quality), rep_diversity 0.70-0.80 (no collapse). The val_loss plateau at ~0.159 is expected for I-JEPA - loss is not strongly correlated with downstream representation quality (confirmed by community reports and [Rethinking JEPA](https://openreview.net/forum?id=2r3GUcMIFe)).

Best checkpoint: epoch 11, val_loss=0.1586, ViT-B/16 encoder.

### Key Lessons Learned

- LR=0.0005 too aggressive for OCT - 0.00025 works well
- Early stopping must ignore pre-warmup epochs (EMA target hasn't diverged)
- Blob uploads must be non-blocking to avoid DDP NCCL timeouts
- I-JEPA loss plateaus are normal; use downstream probes or RankMe to evaluate representation quality

## Downstream: Attentive Probe

Using the best pretrained encoder for downstream glaucoma classification with attentive probe + linear head.

```
OCT Volume (200 B-scans)
  -> Sample 32-100 slices (uniform)
  -> ViT-B/16 per slice -> mean-pool patches -> (B, N, 768)
  -> AttentiveProbe: [CLS] + pos embed + 2-3 transformer blocks -> (B, 768)
  -> LinearHead: LayerNorm -> Linear(768->1)
  -> BCEWithLogitsLoss -> P(glaucoma)
```

| Component | Architecture | Params | Trained? |
|-----------|-------------|--------|----------|
| Encoder | ViT-B/16 (I-JEPA target encoder) | 86M | Frozen or fine-tuned |
| Slice pooling | Mean-pool 256 patch tokens to 1 per slice | 0 | No |
| Attentive probe | 2-3 transformer blocks (768-d, 12 heads) + [CLS] + 1D pos embed | ~14.3M | Yes |
| Linear head | LayerNorm(768) to Linear(768 to 1) | 769 | Yes |

### Frozen Probe Results

Features pre-computed once and cached to disk (~3 GB), making probe training fast (~30s/epoch).

| Encoder Init | Pretrain Epochs | Probe Depth | Head | Test AUC |
|:------------|:--------------:|:-----------:|:----:|:--------:|
| ImageNet->SSL | 32 | d=3 | MLP | **0.774** |
| Random->SSL | 11 | d=3 | Linear | 0.734 |
| Random->SSL | 11 | d=2 | Linear | 0.733 |
| ImageNet->SSL | 50 | d=3 | MLP | 0.706 |
| ImageNet->SSL | 75 | d=3 | MLP | 0.695 |
| ImageNet->SSL | 99 | d=3 | MLP | 0.685 |

Key finding: **I-JEPA pretraining degrades ImageNet features over time**. Test AUC drops from 0.774 (ep32) to 0.685 (ep99). The self-supervised objective overwrites useful ImageNet features with low-level patch prediction features less relevant to glaucoma.

![ImageNet Degradation](/assets/images/ijepa-imagenet-degradation.png)

Frozen probe is capped at ~0.78 regardless of probe depth or training duration (100 epochs with WD=0 gave only +0.45% over 50 epochs).

### Unfrozen Encoder Results (Fine-tuning)

Unfreezing the encoder with differential learning rates (encoder 5e-6, probe 1e-4, head 1e-3) is the key lever. 4x T4 GPUs, batch=1/GPU with 4-step gradient accumulation, fp16 autocast.

| Encoder Init | Probe Depth | Slices | Val AUC | Test AUC |
|:------------|:-----------:|:------:|:-------:|:--------:|
| **ImageNet->SSL ep32** | **d=3** | **32** | **0.828** | **0.829** |
| ImageNet->SSL ep32 | d=2 | 64 | 0.832 | 0.829 |
| ImageNet->SSL ep32 | d=2 | 32 | 0.826 | 0.828 |
| Random->SSL ep11 | d=2 | 32 | 0.819 | -- (val only) |
| Random->SSL ep11 | d=3 | 64 | 0.815 | -- (val only) |

![Test AUC Comparison](/assets/images/ijepa-test-auc-comparison.png)

**Fine-tuning gives +8.5% AUC** over frozen probe (0.734 -> 0.819 for random-init, 0.774 -> 0.829 for ImageNet-init). All unfrozen configs with ImageNet init cluster at 0.828-0.829 -- neither deeper probe (d=3 vs d=2) nor more slices (64 vs 32) help once the encoder is unfrozen.

Best result: **0.829 test AUC**, closing the gap to SLIViT (0.869) to 4.0%.

### Key Lessons from Downstream

- Frozen probe performance is capped by encoder representation quality, not probe architecture
- 100 slices cause OOM with unfrozen encoder on T4s; 32-64 slices are the practical limit
- Deeper probes and more slices don't help once the encoder is fine-tuned -- the encoder is the ceiling
- ImageNet initialization helps both frozen (+4%) and unfrozen (+1%) but the gap narrows with fine-tuning

## ImageNet-Initialized Pretraining

Added two pretraining runs starting from ImageNet-supervised ViT-B/16 weights instead of random initialization.

### Run 4: ImageNet-Init, Gentle LR

ImageNet-pretrained encoder initially collapsed (rep_diversity 0.98) because grayscale OCT images activated similar ImageNet features. Required aggressive updates (EMA=0.996, LR=0.00025) to force encoder specialization. Best checkpoint at epoch 32.

### Run 5: ImageNet-Init, 100 Epochs

Extended training to 100 epochs. Performance degraded after epoch 32, confirming that the SSL objective progressively overwrites ImageNet features. The sweet spot for ImageNet-initialized I-JEPA on OCT is ~30-35 epochs.

## Training Time Estimates (4x T4 GPUs)

| Phase | Dataset | Time/epoch | Epochs | Total |
|-------|---------|-----------|--------|-------|
| Patch pretraining | 600K slices | ~71 min | 50 | ~59 hrs |
| Slice pretraining | 6K volumes | ~3.5 min | 100 | ~6 hrs |
| Downstream feature extraction | 10K volumes x 100 slices | N/A | 1 pass | ~50 min |
| Downstream frozen probe | cached features | ~30 sec | 50-100 | ~25-50 min |
| Downstream unfrozen | 10K volumes x 32-64 slices | ~8-15 min | 25 | ~3-6 hrs |

## References

- Assran et al., "Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture" ([paper](https://arxiv.org/abs/2301.08243))
- Avram et al., "SLIViT" ([paper](https://pubmed.ncbi.nlm.nih.gov/38045283/))
- Luo et al., "Harvard FairVision Dataset" ([paper](https://arxiv.org/abs/2310.02492))
