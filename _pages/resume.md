---
title: "Resume"
permalink: /resume/
toc: true
toc_sticky: true
---

[Download PDF](/assets/resume/gary-feng-resume.pdf){: .btn .btn--primary}
[Google Scholar](https://scholar.google.com/citations?user=ofH9ujMAAAAJ&hl=en){: .btn .btn--info}

Seattle, WA. [garyfeng000@gmail.com](mailto:garyfeng000@gmail.com) | [GitHub](https://github.com/yfeng0206) | [LinkedIn](https://www.linkedin.com/in/garyfeng/)

## Education

**University of Pennsylvania** - M.S.E. Artificial Intelligence *(ongoing, part-time)*

**Georgia Institute of Technology** - B.S. Computer Engineering *(May 2022)*

## Experience

### Machine Learning Engineer, Microsoft
*Sep 2024 - Present, Seattle, WA*

- Shipped cross-encoder reranking service; **+12% CTR** via A/B test, serving 500 RPS at 90 ms
- Launched news-intelligence agent ingesting daily sources; clustered and deduped events; generated ranked summaries and prompts
- Deployed a personality-based eval harness using Prometheus-2 (7B LLM) to score Copilot suggestion-pill at scale, improving offline/online alignment by 8% using Azure ML
- Developed advanced RAG systems integrating BM25 and vector search with LlamaIndex, improving retrieval accuracy using GPT-4.5-distilled evaluation metrics
- Designed and managed robust data pipelines in Azure ML, ensuring scalability, security, and performance for model training and deployment

### Software Engineer, Microsoft
*Jul 2022 - Sep 2024, Seattle, WA*

- Designed and maintained a Kubernetes-based forecasting service (GA product) serving **15,000+ clients**, including Dynamics 365 CRM and Microsoft 365 Support Center
- Built multi-region recommendation platform (Azure, Docker) accommodating 20k+ daily clicks
- Led a cross-functional team to refine model outputs using A/B insights; aligned delivery with business goals
- Provided critical on-call support, diagnosing issues and deploying solutions to maintain service

### Software Engineer, Skeena Bioenergy Ltd.
*May 2020 - Aug 2020, Vancouver, BC, Canada*

- Developed a computer vision app for automated PDF-to-SQL migration, streamlining internal data processing
- Created interactive and insightful dashboards in Power BI using operational production data

## Publications

**Evolution of Humanoid Locomotion Control**
*Science Robotics* 11(117), Aug 2026 | with Prof. Hao Su, New York University | May 2025 - Oct 2025

Y. Gu, G. Shi, F. Shi, I-C. Chang, Y-J. Wang, Q. Cheng, Z. Olkin, I. Lopez-Sanchez, **Y. Feng**, J. Zhang, A. D. Ames, H. Su, K. Sreenath. [doi:10.1126/scirobotics.aed3973](https://doi.org/10.1126/scirobotics.aed3973)

- Co-authored a survey on humanoid locomotion control systems, synthesizing recent research in balance control, motion planning, and optimization across classical algorithms (MPC) and learning-based approaches

## Research

### I-JEPA for 3D OCT, Computer Vision
*Feb 2026 - Ongoing* | with Wai Tak Lau (PhD), Columbia University | [Project page](/portfolio/ijepa-3d-oct/)

- Self-supervised pretrained ViT-B/16 via I-JEPA on 600K OCT B-scans for glaucoma classification
- Proposed anatomy-shaped connected mask targets reaching **0.8947 test AUC**, beating random-masking I-JEPA (0.8878) at every probe and training regime (frozen +0.011, p<0.0005)
- Ablated 3 probe heads (Attentive, CrossAttn, Mean) with paired-bootstrap confidence intervals; validated interpretability via occlusion attribution
- Released pretrained encoders on Hugging Face

## Projects

### CopilotWorldLab, Latent World Models for Manipulation
*Jul 2026 - Ongoing* | [Project page](/portfolio/copilot-world-lab/)

- Reproduced V-JEPA 2-AC as a frozen coarse manipulation controller planning to goal images via CEM model-predictive control in MuJoCo
- Built a reproducible 500-rollout benchmark (5 tasks x 2 objects x 50 fixed scenarios) scored from hidden simulator state

### MOT17 Multi-Object Tracking, CV Project
*Jan 2026 - Feb 2026* | [Project page](/portfolio/mot17-object-tracking/)

- Trained on MOT17 data to track with YOLOv8 + ByteTrack, improving tracking accuracy by 8% compared to base YOLOv8

### ROS 2 Robot, Odometry & Control
*Feb 2025 - May 2025*

- Prototyped diff-drive stack in ROS 2 Jazzy: URDF, C++/Python nodes; simulated in Gazebo with RViz2
- Applied localization: wheel odometry, TF2, IMU sim, EKF fusion; verified via launch and parameter configs

### iValet Parking System, Senior CV Project
*Jan 2022 - May 2022* | with Kelin Yu, Faiza Yousuf, Wei Xiong Toh | [Project page](/portfolio/ivalet-parking/)

- Built an ML-powered parking system that detects vacant spots via camera and segmentation, stores results in PostgreSQL, and guides users to spots through a web UI with path planning

### Self-Driving DC Car, Embedded Project
*Feb 2021 - Jun 2021* | [Project page](/portfolio/self-driving-car/)

- Engineered an autonomous DC motor car with Raspberry Pi + Arduino; implemented roadside detection using OpenCV4 (C++) and soldered H-bridge motor control circuitry

## Skills

C/C++, C#, Python, PyTorch, SQL, Azure ML, Kubernetes, Docker, RAG, CV/ML, Agents, Claude Code
