---
title: "I-JEPA for OCT Glaucoma Classification"
date: 2026-04-08
excerpt: "Mar 2026 - Present - Self-supervised pretraining with I-JEPA on Harvard FairVision OCT data. Best downstream result: 0.829 test AUC (unfrozen encoder with ImageNet init)."
header:
  teaser: /assets/images/ijepa-teaser.png
sidebar:
  - title: "Tech Stack"
    text: "Python, PyTorch, ViT-B/16, I-JEPA, DDP"
  - title: "Dataset"
    text: "600K OCT slices (self-supervised)"
  - title: "Best Result"
    text: "0.829 Test AUC (unfrozen)"
  - title: "Status"
    text: "In Progress"
---

Self-supervised pretraining using [I-JEPA](https://github.com/facebookresearch/ijepa) on [Harvard FairVision](https://github.com/Harvard-Ophthalmology-AI-Lab/FairVision) OCT data for binary glaucoma classification. Builds on our [SLIViT reproduction](/portfolio/slivit-3d-oct-glaucoma/).

[View on GitHub](https://github.com/yfeng0206/I-JEPTA_3D_OCT){: .btn .btn--primary}

## Results Summary

| Method | Encoder Init | Encoder | Slices | Test AUC |
|:-------|:-----------|:--------|:------:|:--------:|
| **SLIViT baseline** | Kermany OCT | ConvNeXt+ViT | 32 | **0.869** |
| **I-JEPA unfrozen d=3** | **ImageNet->SSL ep32** | **ViT-B/16 fine-tune** | **32** | **0.829** |
| I-JEPA unfrozen d=2 | ImageNet->SSL ep32 | ViT-B/16 fine-tune | 64 | 0.829 |
| I-JEPA unfrozen d=2 | ImageNet->SSL ep32 | ViT-B/16 fine-tune | 32 | 0.828 |
| I-JEPA frozen d=3 | ImageNet->SSL ep32 | ViT-B/16 frozen | 100 | 0.774 |
| I-JEPA frozen d=3 | Random->SSL ep11 | ViT-B/16 frozen | 100 | 0.734 |

![Test AUC Comparison](/assets/images/ijepa-test-auc-comparison.png)

## Key Findings

1. **Fine-tuning is the key lever**: Unfreezing the encoder gives +8.5% AUC (0.734 -> 0.819 for random-init, 0.774 -> 0.829 for ImageNet-init). Task-specific adaptation matters more than better pretraining.
2. **ImageNet init helps frozen probe** (+4%): 0.774 vs 0.734, but only at early pretraining epochs.
3. **I-JEPA pretraining degrades ImageNet features over time**: Test AUC drops 0.774 -> 0.685 from ep32 to ep99. The SSL objective overwrites useful ImageNet features with low-level patch prediction features.
4. **Probe depth and slice count don't matter once encoder is unfrozen**: d=2/32s (0.828), d=2/64s (0.829), d=3/32s (0.829) are all within noise.

![ImageNet Degradation](/assets/images/ijepa-imagenet-degradation.png)

## Motivation

Our SLIViT experiments reached 0.869 test AUC but hit two bottlenecks: ConvNeXt features pretrained on a different task (not glaucoma), and the ViT integrator trained from scratch on only 6K labeled volumes.

I-JEPA addresses both by learning representations directly from **unlabeled** OCT data through masked prediction in representation space - no hand-crafted augmentations needed.

## Architecture

### Patch-Level I-JEPA (Primary)

Standard I-JEPA applied to individual 256x256 OCT slices. Each slice is patchified into a 16x16 grid of 256 patches. Training data: 6,000 volumes x 100 slices = **600,000 slice images**.

| Component | Architecture | Params |
|-----------|-------------|--------|
| Context encoder | ViT-B/16 (12 layers, 768-d, 12 heads) | 86M |
| Target encoder | Same (EMA, no grad) | 86M |
| Predictor | Narrow ViT (6 layers, 384-d, 12 heads) | 11M |

### Slice-Level I-JEPA (Failed)

Applied to sequences of slice features within each volume. Collapsed within 1-2 epochs - adjacent OCT slices produce nearly identical features, making masked prediction trivially solvable.

## Pretraining

- **Run 1 (LR=0.0005):** Too aggressive for OCT. Destabilized at peak LR.
- **Run 2-3 (LR=0.00025):** Converged at epoch 11 (val_loss=0.1586). Healthy diagnostics: cos_sim ~0.80, no collapse.
- **Runs 4-5 (ImageNet init):** ImageNet-initialized encoder with gentle LR. Best checkpoint at epoch 32.

## Downstream Evaluation

Frozen ViT-B/16 encoder + attentive probe (2-3 transformer blocks) + classification head.

**Frozen probe** is capped at ~0.78 AUC regardless of probe depth or training duration. The frozen encoder's representation capacity is the bottleneck.

**Unfrozen encoder** (differential LR: encoder 5e-6, probe 1e-4, head 1e-3) reaches **0.829 test AUC** - closing the gap to SLIViT (0.869) to 4.0%. All 3 completed unfrozen configs cluster at 0.828-0.829.

See the full [experiment logs](https://github.com/yfeng0206/I-JEPTA_3D_OCT/tree/docs/experiment-tracking/docs/experiments), [pretraining details](https://github.com/yfeng0206/I-JEPTA_3D_OCT/tree/docs/experiment-tracking/docs/experiments/pretraining), and [lessons learned](https://github.com/yfeng0206/I-JEPTA_3D_OCT/blob/docs/experiment-tracking/docs/lessons_learned.md) on GitHub.
