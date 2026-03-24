---
title: "MOT17 Multi-Object Tracking"
excerpt: "YOLOv8 + ByteTrack on MOT17 pedestrian data, improving tracking accuracy by 8% over base YOLOv8."
header:
  teaser: /assets/images/mot17-teaser.jpg
sidebar:
  - title: "Tech Stack"
    text: "Python, YOLOv8, ByteTrack, Ultralytics"
  - title: "Dataset"
    text: "MOT17Det"
  - title: "Improvement"
    text: "+8% tracking accuracy"
---

Trained on MOT17 data to track pedestrians with YOLOv8 + ByteTrack, improving tracking accuracy by 8% compared to base YOLOv8.

[View on GitHub](https://github.com/yfeng0206/MOT17-Object-Detection-and-Tacking){: .btn .btn--primary}

## Overview

This project provides a sanity check and baseline evaluation pipeline for multi-object detection and tracking on the MOT17 dataset:

1. **YOLOv8 Sanity Check** — verifies inference runs end-to-end
2. **Baseline Single-Frame Eval** — evaluates one frame against ground truth with configurable IoU thresholds

## Matching Rules

Uses IoU thresholding to define hits:
- **IoU >= 0.70**: stricter, more misses for nearly-correct boxes
- **IoU >= 0.65**: more forgiving, better for visually correct detections

The pipeline prints HITS, FALSE POSITIVES, and MISSES with annotated visualizations showing GT and predicted boxes with match IDs.
