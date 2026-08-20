---
title: "About"
permalink: /about/
---

ML Engineer at Microsoft in Seattle. Georgia Tech ECE '22.

My interests are in machine learning, computer vision, and visual perception. I like building systems that can see, understand, and act on the world. At work I ship production ML services at scale. On the side I work on medical imaging, latent world models for robot manipulation, multi-object tracking, and robotics.

[Resume (PDF)](/assets/resume/gary-feng-resume.pdf){: .btn .btn--primary}
[Google Scholar](https://scholar.google.com/citations?user=ofH9ujMAAAAJ&hl=en){: .btn .btn--info}

## Recent

- **Published in *Science Robotics*** (Aug 2026): ["Evolution of Humanoid Locomotion Control"](https://doi.org/10.1126/scirobotics.aed3973), a review of humanoid locomotion control from model-based foundations to learning-based approaches. Vol. 11, no. 117
- **Anatomy-shaped masking for OCT I-JEPA** reaches 0.8947 test AUC, beating random-masking I-JEPA at every probe and regime. [Writeup](/research/anatomy-guided-masking-oct/)
- **CopilotWorldLab**: V-JEPA 2-AC as a coarse manipulation controller, benchmarked over 500 fixed rollouts in MuJoCo. [Writeup](/research/reproducing-vjepa2-ac/)

## What I Do at Microsoft

**ML Engineer (Sep 2024 – Present)**
- Shipped a cross-encoder reranking service: +12% CTR via A/B test, serving 500 RPS at 90ms
- Launched a news-intelligence agent that ingests daily sources, clusters/dedupes events, and generates ranked summaries
- Built ScoreCard Agent, an automated A/B experiment health analyzer with 25+ statistical checks (SRM, guardrails, Simpson's paradox, novelty effects), produces SHIP/NO-SHIP verdicts with full audit trails
- Deployed a personality-based eval harness using Prometheus-2 (7B LLM) to score Copilot suggestion-pill at scale, improving offline/online alignment by 8%
- Developed advanced RAG systems integrating BM25 and vector search with LlamaIndex
- Distilled large language models, optimizing Phi-2 into a BERT-based model for faster inference

**Software Engineer (Jul 2022 – Sep 2024)**
- Designed and maintained a Kubernetes-based forecasting service (GA Product) serving 15,000+ clients, including Dynamics 365 CRM and Microsoft 365 Support Center
- Built a multi-region recommendation platform accommodating 20K+ daily clicks
- Led a cross-functional team to refine model outputs using A/B insights

## Research Interests

- **Medical AI**: Glaucoma classification on 3D OCT scans using SLIViT and I-JEPA self-supervised learning; anatomy-shaped mask targets that beat stock random masking; working toward a foundation model for ophthalmic OCT imaging. With WT Lau (PhD), Columbia
- **World Models & Robot Learning**: V-JEPA 2-AC as a coarse manipulation controller, using the model's own predictive energy as a competence gate for handoff to classical control
- **Computer Vision & Perception**: Multi-object tracking, object permanence detection with SAM2 + DINOv2, visual reasoning
- **Robotics**: Humanoid locomotion control (*Science Robotics* review, 2026), ROS 2 control systems
- **Embedded Systems**: Self-driving cars and gesture-controlled robots with Raspberry Pi + Arduino

## Education

M.S.E. Artificial Intelligence, University of Pennsylvania *(ongoing, part-time)*

B.S. Computer Engineering, Georgia Institute of Technology (2022)

## Skills

C/C++, C#, Python, Azure, Kubernetes, Docker, LlamaIndex, Unix, SQL, ROS 2, MuJoCo, IoT, PyTorch, Azure ML
