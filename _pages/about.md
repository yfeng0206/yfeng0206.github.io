---
title: "About"
permalink: /about/
---

ML Engineer at Microsoft in Seattle. Georgia Tech ECE '22, starting an M.S.E. in Robotics at Penn in 2027.

My interests are in machine learning, computer vision, and visual perception. I like building systems that can see, understand, and act on the world. At work I ship production ML services at scale. On the side I work on medical imaging, latent world models for robot manipulation, multi-object tracking, and robotics.

[View Resume](/resume/){: .btn .btn--primary}
[Download PDF](/assets/resume/gary-feng-resume.pdf){: .btn .btn--info}
[Google Scholar](https://scholar.google.com/citations?user=ofH9ujMAAAAJ&hl=en){: .btn .btn--inverse}

Seattle, WA | [garyfeng000@gmail.com](mailto:garyfeng000@gmail.com) | [GitHub](https://github.com/yfeng0206) | [LinkedIn](https://www.linkedin.com/in/garyfeng/)

## Recent

- **Published in *Science Robotics*** (Aug 2026): ["Evolution of Humanoid Locomotion Control"](https://doi.org/10.1126/scirobotics.aed3973), a survey of humanoid locomotion control from model-based foundations to learning-based approaches. Vol. 11, no. 117
- **Anatomy-shaped masking for OCT I-JEPA** reaches 0.8947 test AUC, beating random-masking I-JEPA at every probe and regime. [Writeup](/research/anatomy-guided-masking-oct/)
- **CopilotWorldLab**: V-JEPA 2-AC as a coarse manipulation controller, benchmarked over 500 fixed rollouts in MuJoCo. [Writeup](/research/reproducing-vjepa2-ac/)

## Research Interests

- **Medical AI**: Glaucoma classification on 3D OCT scans using SLIViT and I-JEPA self-supervised learning; anatomy-shaped mask targets that beat stock random masking; working toward a foundation model for ophthalmic OCT imaging. With WT Lau (PhD), Columbia
- **World Models & Robot Learning**: V-JEPA 2-AC as a coarse manipulation controller, using the model's own predictive energy as a competence gate for handoff to classical control
- **Computer Vision & Perception**: Multi-object tracking, object permanence detection with SAM2 + DINOv2, visual reasoning
- **Robotics**: Humanoid locomotion control (*Science Robotics* survey, 2026), ROS 2 control systems
- **Embedded Systems**: Self-driving cars and gesture-controlled robots with Raspberry Pi + Arduino

## What I Do at Microsoft

**ML Engineer** *(Sep 2024 - Present)*

Shipping production ML: a cross-encoder reranking service (+12% CTR, 500 RPS at 90 ms), a news-intelligence agent that clusters and dedupes daily events into ranked summaries, ScoreCard Agent for automated A/B experiment health analysis, and an LLM-based eval harness that improved offline/online alignment by 8%. Also RAG systems combining BM25 with vector search, and LLM distillation.

**Software Engineer** *(Jul 2022 - Sep 2024)*

A Kubernetes-based forecasting service (GA product) serving 15,000+ clients including Dynamics 365 CRM and Microsoft 365 Support Center, and a multi-region recommendation platform handling 20K+ daily clicks.

Full detail, plus earlier roles and every project, is on the [resume](/resume/).

## Education

M.S.E. Robotics, University of Pennsylvania *(2027 - ongoing)*

B.S. Computer Engineering, Georgia Institute of Technology (2022)

## Skills

**Languages:** C/C++, C#, Python, SQL

**ML & CV:** PyTorch, self-supervised learning (I-JEPA, V-JEPA), vision transformers, LLM distillation, RAG, LlamaIndex, agents, A/B experimentation

**Infrastructure:** Azure, Azure ML, Kubernetes, Docker, distributed training (DDP), Unix

**Robotics & Embedded:** ROS 2, MuJoCo, Raspberry Pi, Arduino, Mbed, IoT
