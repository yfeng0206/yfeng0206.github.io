---
title: "Publications"
permalink: /publications/
---

[Google Scholar](https://scholar.google.com/citations?user=ofH9ujMAAAAJ&hl=en){: .btn .btn--primary}

## Peer-Reviewed

**Evolution of Humanoid Locomotion Control**

Yan Gu, Guanya Shi, Fan Shi, I-Chia Chang, Yen-Jen Wang, Qilong Cheng, Zachary Olkin, Ivan Lopez-Sanchez, **Yunchu Feng**, Jian Zhang, Aaron D. Ames, Hao Su, Koushil Sreenath

*Science Robotics*, vol. 11, no. 117 (2026)

[DOI: 10.1126/scirobotics.aed3973](https://doi.org/10.1126/scirobotics.aed3973){: .btn .btn--info}

A review of humanoid locomotion control, tracing the field from model-based foundations through to learning-based control. Covers balance control, motion planning, and optimization, spanning classical algorithms (MPC, LQR, DCM) alongside the reinforcement-learning and sim-to-real approaches that now drive bipedal and humanoid locomotion.

*Work conducted under Prof. Hao Su at NYU Tandon.*

## In Progress

**I-JEPA Foundation Model for 3D OCT Medical Imaging** *(Feb 2026 – Present)*

With WT Lau (PhD), Columbia.

I-JEPA self-supervised pretraining on Harvard FairVision OCT, evaluated on binary glaucoma classification. Our anatomy-shaped masking reaches **0.8947 Test AUC**, beating random-masking I-JEPA (0.8878) at every probe and training regime (frozen +0.011, p<0.0005). The contribution is target *shape*: connected, tissue-shaped mask targets, isolated against both a matched-area random control and a MIRAGE-placed rectangle-envelope baseline. Includes a full 2x3 probe-architecture ablation with paired-bootstrap CI and an occlusion-attribution interpretability study.

*Status: Phases 1-3 and the masking study done; Phase 4 (FM baselines vs DINOv3 + OCTCube) in progress.* See the [project page](/portfolio/ijepa-3d-oct/) and the [masking writeup](/research/anatomy-guided-masking-oct/). Pretrained encoders are released on [Hugging Face](https://huggingface.co/yfeng0206/ijepa-3d-oct-checkpoints) (private repo, access on request).

**Latent World Models as Coarse Manipulation Controllers** *(Jul 2026 – Present)*

Using V-JEPA 2-AC as a frozen coarse controller for robot manipulation, with the model's own predictive energy proposed as the competence gate that hands off to a classical vision-only visual servo. Benchmarked over 500 fixed rollouts in MuJoCo with hidden-state success scoring. Target application is labware insertion for self-driving chemistry labs.

*Status: Phase 1 (fixed-bundle closed-loop benchmark).* See the [project page](/portfolio/copilot-world-lab/) and the [reproduction writeup](/research/reproducing-vjepa2-ac/).
