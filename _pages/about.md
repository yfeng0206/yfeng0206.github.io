---
title: "About"
permalink: /about/
---

ML Engineer at Microsoft in Seattle. Georgia Tech ECE '22.

My interests are in machine learning, computer vision, and visual perception. I like building systems that can see, understand, and act on the world. At work I ship production ML services at scale. On the side I work on medical imaging, multi-object tracking, and robotics.

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

- **Medical AI**: Glaucoma classification on 3D OCT scans using SLIViT and I-JEPA self-supervised learning; working toward a foundation model for ophthalmic OCT imaging
- **Computer Vision & Perception**: Multi-object tracking, object permanence detection with SAM2 + DINOv2, visual reasoning
- **Robotics**: Humanoid locomotion control (co-authoring a Science Robotics review), ROS 2 control systems
- **Embedded Systems**: Self-driving cars and gesture-controlled robots with Raspberry Pi + Arduino

## Earlier Work at Georgia Tech

A lot of what I do now traces back to projects I built in school. Two that shaped how I think about perception and control:

**iValet** was my senior capstone, an intelligent parking lot system that used a camera feed and image segmentation to detect which spots were open, stored the state in PostgreSQL, and served it through a React web app with path planning. It was my first time building an end-to-end CV pipeline that had to work reliably in real conditions, not just on a benchmark. Dealing with lighting changes, occlusion from other cars, and camera angles that didn't match the training data taught me more about deployment than any class did. That experience directly informed how I think about production ML systems today.

**Gesture-Controlled Robot Car** was a group project for ECE 4180 where we built a robot that responded to hand gestures captured by a Pi Camera. We used OpenCV and MediaPipe on a Raspberry Pi 4 to count fingers in real time, sent commands over WiFi to an Mbed microcontroller, and drove DC motors through an H-bridge. It was a small system, but it connected computer vision to physical actuation in a tight loop. That feedback loop between perception and action is something I keep coming back to, whether it's in robotics or in building agents that observe, decide, and act.

## Education

B.S. Computer Engineering, Georgia Institute of Technology (2022)

## Skills

C/C++, C#, Python, Azure, Kubernetes, Docker, LlamaIndex, Unix, SQL, ROS 2, IoT, PyTorch, Azure ML
