---
title: "Anatomy-shaped Masking for OCT I-JEPA"
deck: "+0.007 AUC from changing mask shape rather than location, and the two metrics that almost hid it."
teaser: /assets/images/sel-oct.jpg
date: 2026-08-14
categories:
  - research
tags:
  - medical-ai
  - self-supervised-learning
  - computer-vision
  - oct
  - glaucoma
redirect_from:
  - /research/anatomy-guided-masking-oct/
---


I-JEPA learns by hiding parts of an image and predicting them in representation space. The masks it hides are uniformly-placed rectangles, which is a sensible default for ImageNet. On retinal OCT it is close to the worst possible choice: the retina occupies about 17.6% of the image, so most of what a random rectangle hides is vitreous and background, and most of the prediction budget is spent learning that empty space stays empty.

This post is about fixing that, and about being careful enough to know which part of the fix actually did the work.

[GitHub Repo](https://github.com/yfeng0206/I-JEPA_3D_OCT){: .btn .btn--primary}
[Checkpoints on Hugging Face](https://huggingface.co/yfeng0206/ijepa-3d-oct-checkpoints){: .btn .btn--info}

## Result

**0.8947 Test AUC** on the 3,000-volume held-out FairVision test split, from a fine-tuned MeanPool probe on an anatomy-masked encoder. The random-masking encoder reaches 0.8878.

![Best downstream Test AUC: anatomy-guided masking 0.8947 vs random-masking I-JEPA 0.8878](/assets/images/ijepa-oracle-headline.png)

The gain holds across the whole evaluation grid, not just at the best cell. Paired bootstrap, B=2000:

| Regime | Probe | Random | Anatomy-guided | Δ | p |
|:-------|:------|:------:|:--------------:|:-:|:-:|
| Frozen | MeanPool | 0.8746 | 0.8855 | +0.0109 | <0.0005 |
| Fine-tune | MeanPool | 0.8868 | **0.8947** | +0.0079 | 0.001 |
| Fine-tune | CrossAttnPool | 0.8872 | 0.8937 | +0.0065 | 0.009 |
| Fine-tune | AttentiveProbe d=1 | 0.8878 | 0.8901 | +0.0023 | 0.26 (ns) |

The gain is largest in the frozen regime and shrinks under fine-tuning, which is what you would expect: fine-tuning can partly repair a mediocre encoder, so a better encoder has less room to show its advantage.

## What Is Actually New Here

It is tempting to write this up as "we used a segmentation prior to guide masking." That claim would be too broad, and it would not be ours. Using an off-the-shelf retinal segmenter (MIRAGE) to decide *where* targets go is the obvious move and it is not the interesting part.

The contribution is narrower: **target shape**. Instead of placing rectangles on the retina, we shape connected, irregular targets to the tissue itself.

To make that distinction measurable, both arms use MIRAGE and differ only in geometry:

- `mirage_envelope` - MIRAGE places ordinary **rectangular** I-JEPA targets on the retina
- `mirage_anatomy` - MIRAGE **shapes** connected, irregular targets to the tissue

Both arms share identical weights through epoch 27 and diverge only over epochs 28-30, so nothing but the mask differs:

| Arm | Test AUC (5 probe seeds) |
|:----|:------------------------:|
| envelope ep30 | 0.8528 ± 0.0018 |
| **anatomy ep30** | **0.8582 ± 0.0003** |

Delta +0.0054. Welch t p=0.00219, Mann-Whitney p=0.0079, Cohen's d=4.20. The arms are fully separated: the worst anatomy seed (0.8578) beats the best envelope seed (0.8542). A paired bootstrap over test volumes gives +0.0044, 95% CI [+0.0010, +0.0077], p=0.012.

## Why Shape Matters: Budget Efficiency

The mechanism is not that anatomy masking hides more retina in absolute terms. Measured on 1,000 slices through the production collator:

| Arm | Total hidden | Anatomy hidden | Background hidden | On-anatomy | Dead targets |
|:----|:-----------:|:--------------:|:-----------------:|:----------:|:------------:|
| random_default | 114.1 | 24.7 | 89.4 | 21.8% | 28.68% |
| envelope_default | 117.5 | 36.2 | 81.3 | 30.7% | 3.57% |
| **anatomy** | 54.3 | 39.3 | **15.0** | **72.1%** | 2.05% |

Rectangles must spend **5.4x** more hidden budget on background to hide comparable retina (81.3 vs 15.0 cells). Anatomy masking gets a slightly *harder* task for the same tissue content: it hides 8.6% more retina and leaves 5% less retinal context, and its tissue-context per tissue-cell predicted is 0.145 versus 0.166 for the envelope. It wins anyway.

An earlier draft of this claimed a "4.3x more context per predicted token" advantage. That number counted background tokens and is retracted.

## The Control That Almost Was Not There

Comparing anatomy directly to shipped I-JEPA changes two things at once: *where* targets land and *how much* is masked (58.6 vs 116.8 cells). You cannot attribute anything to shape without holding area fixed.

So `random_matched` lowers `pred_mask_scale` to 0.055-0.075 until it matches anatomy's hidden count (57.4 vs 58.6) and context (167.8 vs 169.6) to within 2%. The only remaining variable is placement.

![Three-arm matched masking comparison](/assets/images/ijepa-masking-arms.png)

| Metric | random_default | random_matched | anatomy |
|:-------|:--------------:|:--------------:|:-------:|
| Hidden cells | 116.8 | 57.4 | 58.6 |
| Context tokens | 112.2 | 167.8 | 169.6 |
| On-region fraction | 0.349 | 0.327 | **0.983** |
| Fallback rate | 100% | 100% | 1.7% |
| rep_diversity | 0.6727 | 0.9404 | 0.9521 |
| val_loss | 0.0293 | 0.0041 | 0.0445 |

At matched budget, anatomy places **3.0x** more targets on retina (98.3% vs 32.7%) with a 1.7% fallback rate.

## Two Metrics That Lie

Building this produced two negative results that are more useful than the headline, because both are traps that would have silently corrupted the conclusion.

### Validation loss is inverted against targeting quality

| Arm | val_loss | on-region |
|:----|:--------:|:---------:|
| random_matched | **0.0041** (best) | 0.327 (worst) |
| anatomy | **0.0445** (worst) | **0.983** (best) |

A method that predicts mostly-background patches gets a trivially low loss. Retina is high-variance and genuinely hard to predict. **Validation loss cannot rank masking strategies.** Only downstream AUC can.

This generalises to checkpoint selection too. The `-lowest-pretrain-loss-*` checkpoints in our [Hugging Face release](https://huggingface.co/yfeng0206/ijepa-3d-oct-checkpoints) (private repo, access on request) are not better checkpoints; pretraining loss in I-JEPA is close to an anti-signal, and the random arm's minimum lands at epoch 1.

### Representation diversity is not a collapse metric for OCT

Retina occupies 17.6% of grid cells, so 97% of tile pairs involve at least one background tile and the all-pairs mean is dominated by background:

| Partition | Cosine similarity |
|:----------|:-----------------:|
| All pairs | 0.3297 |
| Background-background | 0.3293 |
| Retina-retina | 0.4886 |
| Retina-background | 0.3131 |

The tell: the **untrained** encoder has the largest retina/background gap (0.0851) of anything we measured, larger than any trained encoder (0.0155-0.0287), simply because raw pixel brightness already separates vitreous from tissue before any learning happens.

Read naively, anatomy (0.9521) versus baseline (0.6727) looks like anatomy causes representation collapse. The matched control overturns that: `random_matched` sits at 0.9404. The effect tracks the **masking ratio** (21% vs 46% of the image masked), not target shape. Against its proper control, anatomy adds only +0.012.

## Caveats

The three-arm comparison above is one epoch from random init on 600K slices. It demonstrates targeting mechanics and engineering correctness, not that anatomy masking produces a better encoder. The downstream evidence for that claim comes from the ep30 head-to-head and the ep100 evaluation grid, both of which warm-start from a shared random-masked checkpoint. So what is measured is what anatomy guidance adds **on top of** a random-masked foundation, not anatomy from scratch.

Mask purity also turned out not to be a validated proxy for downstream AUC. In the earlier policy sweep the MIRAGE envelope had the best target purity (0.6320 vs 0.5602 oracle, 0.4530 random), but the oracle arm produced the better downstream encoder (0.8855 vs 0.8807).

## Next

Phase 4 puts foundation-model baselines (DINOv3, OCTCube) on the same 3,000-volume test split, so the anatomy-masked encoder gets measured against models trained on far more data rather than only against its own ablations. Details and backlog live in the [research log](https://github.com/yfeng0206/I-JEPA_3D_OCT/blob/main/docs/research_log.md); the masking record is under [`docs/experiments/masking/`](https://github.com/yfeng0206/I-JEPA_3D_OCT/tree/main/docs/experiments/masking).
