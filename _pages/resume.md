---
title: "Resume"
permalink: /resume/
toc: true
toc_sticky: true
---

[Download PDF](/assets/resume/gary-feng-resume.pdf){: .btn .btn--primary}
[Google Scholar](https://scholar.google.com/citations?user=ofH9ujMAAAAJ&hl=en){: .btn .btn--info}

Machine Learning Engineer. Computer vision, self-supervised learning, robotics.
Seattle, WA. [garyfeng000@gmail.com](mailto:garyfeng000@gmail.com) | [GitHub](https://github.com/yfeng0206) | [LinkedIn](https://www.linkedin.com/in/garyfeng/)

## Education

**Georgia Institute of Technology** *(May 2022)*
B.S. Computer Engineering, Atlanta, GA

## Experience

### Machine Learning Engineer, Microsoft
*Sep 2024 - Present*

- Shipped a cross-encoder reranking service delivering **+12% CTR** in A/B test, serving 500 RPS at 90 ms p50
- Launched a news-intelligence agent that ingests daily sources, clusters and dedupes events, and generates ranked summaries
- Built ScoreCard Agent, an automated A/B experiment health analyzer running 25+ statistical checks (SRM, guardrails, Simpson's paradox, novelty effects) that produces SHIP/NO-SHIP verdicts with full audit trails
- Deployed a personality-based evaluation harness using Prometheus-2 (7B LLM) to score Copilot suggestion pills at scale, improving offline/online alignment by 8%
- Developed retrieval-augmented generation systems integrating BM25 keyword search with vector search via LlamaIndex
- Distilled large language models, optimizing Phi-2 into a BERT-based model for accelerated inference and domain specialization
- Designed data pipelines in Azure ML for scalable, secure model training and deployment

### Software Engineer, Microsoft
*Jul 2022 - Sep 2024*

- Designed and maintained a Kubernetes-based forecasting service (GA product) serving **15,000+ clients**, including Dynamics 365 CRM and Microsoft 365 Support Center
- Built a multi-region recommendation platform on Azure and Docker handling **20,000+ daily active users**
- Led a cross-functional team with data scientists and a partner dev team to refine model outputs using A/B insights
- Provided on-call support, diagnosing and resolving production incidents to maintain uninterrupted service

### Software Engineer, Skeena Bioenergy Ltd.
*May 2020 - Aug 2020, Vancouver, BC*

- Developed a computer vision application for automated PDF-to-SQL data migration, streamlining internal data processing
- Created interactive Power BI dashboards from operational production data and built Python automation scripts for the internal toolset

## Publications

**Evolution of Humanoid Locomotion Control**
Y. Gu, G. Shi, F. Shi, I-C. Chang, Y-J. Wang, Q. Cheng, Z. Olkin, I. Lopez-Sanchez, **Y. Feng**, J. Zhang, A. D. Ames, H. Su, K. Sreenath.
*Science Robotics* 11(117), 2026. [doi:10.1126/scirobotics.aed3973](https://doi.org/10.1126/scirobotics.aed3973)

## Research Projects

### Anatomy-shaped Masking for OCT I-JEPA
*Mar 2026 - Present* | [Project page](/portfolio/ijepa-3d-oct/)

- Self-supervised I-JEPA pretraining of ViT-B/16 on 600K retinal OCT slices for glaucoma classification on Harvard FairVision
- Proposed anatomy-shaped connected mask targets reaching **0.8947 test AUC**, beating random-masking I-JEPA (0.8878) at every probe and training regime (frozen +0.011, p<0.0005)
- Isolated target shape from target area with a matched-budget random control and a MIRAGE-placed rectangle-envelope baseline; ran a 2x3 probe-architecture ablation with paired-bootstrap confidence intervals
- Released pretrained encoders on Hugging Face; documented two metric traps where validation loss and representation diversity both rank masking strategies incorrectly

### CopilotWorldLab, Latent World Models for Manipulation
*Jul 2026 - Present* | [Project page](/portfolio/copilot-world-lab/)

- Reproduced V-JEPA 2-AC as a frozen coarse manipulation controller planning to goal images via CEM model-predictive control in MuJoCo
- Built a reproducible 500-rollout benchmark (5 tasks x 2 objects x 50 fixed scenarios) scored from hidden simulator state, after robosuite and ManiSkill both proved unrunnable on the target platform
- Diagnosed a CUDA allocator cliff causing a 4.6x planning slowdown at high CEM sample counts; fixed by batch chunking with numerically identical output
- Investigating the model's own predictive energy as a competence gate for handoff to a classical visual servo

### SLIViT for 3D OCT Glaucoma Classification
*Mar - Apr 2026* | [Project page](/portfolio/slivit-3d-oct-glaucoma/)

- Reproduced the SLIViT ConvNeXt + ViT architecture for binary glaucoma classification on 10K OCT volumes, reaching 0.869 test AUC
- Trained with 4-GPU DDP and fp16; showed 32 slices per volume matches 64 at a fraction of the cost

### Object Permanence Detection
*Feb 2026* | [Project page](/portfolio/object-permanence-detection/)

- Built a video pipeline detecting physically impossible events using SAM2 mask propagation, RT-DETR detection, and DINOv2 re-identification
- Generated narrative event logs consumable by an LLM for violation detection across occlusion, containment, and disappearance

### MOT17 Multi-Object Tracking
*Jan 2026* | [Project page](/portfolio/mot17-object-tracking/)

- Trained YOLOv8 with ByteTrack on MOT17 pedestrian data, improving tracking accuracy 8% over base YOLOv8

## Earlier Engineering Projects

- **[iValet, Intelligent Parking Management](/portfolio/ivalet-parking/)** (Georgia Tech ECE 4872 senior design, 2022) - camera-based vacancy detection with image segmentation, PostgreSQL state tracking, and a React UI with path planning. Advised by Dr. Patricio Vela
- **[Gesture-Controlled Robot Car](/portfolio/gesture-car/)** (ECE 4180, 2021) - OpenCV and MediaPipe finger detection on Raspberry Pi 4, commands sent over WiFi to an Mbed LPC1768 driving DC motors through an H-bridge
- **[Self-Driving DC Motor Car](/portfolio/self-driving-car/)** (2021) - OpenCV lane detection with Canny edges and Hough transform, PID steering control across a Raspberry Pi 4 and Arduino with a custom-soldered H-bridge

## Skills

**Languages:** Python, C/C++, C#, SQL

**ML & CV:** PyTorch, self-supervised learning (I-JEPA, V-JEPA), vision transformers, LLM distillation, RAG, LlamaIndex, A/B experimentation

**Infrastructure:** Azure, Azure ML, Kubernetes, Docker, distributed training (DDP), Unix

**Robotics & Embedded:** ROS 2, MuJoCo, Raspberry Pi, Arduino, Mbed, IoT
