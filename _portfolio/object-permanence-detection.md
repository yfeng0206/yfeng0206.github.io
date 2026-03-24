---
title: "Object Permanence Detection"
date: 2026-02-25
excerpt: "Feb 2026 - Video analysis pipeline detecting physically impossible events using SAM2, RT-DETR, and DINOv2."
header:
  teaser: /assets/images/objperm-teaser.png
sidebar:
  - title: "Tech Stack"
    text: "Python, SAM2, RT-DETR, DINOv2, PyTorch"
  - title: "Tracking"
    text: "10 objects, 24 events detected"
---

A video analysis pipeline that detects **object permanence anomalies** - physically impossible events like a red ball going into a cup but a yellow ball coming out.

[View on GitHub](https://github.com/yfeng0206/object-permanence-detection){: .btn .btn--primary}

## Pipeline

The pipeline tracks objects through occlusion, containment, and disappearance using **SAM2** for mask propagation, **RT-DETR** for detection, and **DINOv2** for re-identification, then generates a narrative event log that an LLM evaluates for violations.

```
Video Frames
     │
     ▼
Phase 1: AMG Seeding (frame 0)         SAM2 automatic mask generation
Phase 2: RT-DETR Detection Sweep       Detect objects on every frame
Phase 3: Validation & Filtering         Match AMG masks ↔ RT-DETR boxes
Phase 4: Iterative SAM2 Tracking       Propagate + discover + merge
Phase 5: Frame Processing              Drift detection + event generation
Phase 6: Post-Hoc Merge                Temporal exclusivity safety net
     │
     ▼
Outputs: tracked video, event log, narrative log, per-object galleries
```

## Key Features

- **SAM2 mask tracking** - pixel-level object segmentation through every frame
- **DINOv2 re-identification** - multi-frame gallery embedding with EMA prototypes
- **Disappearance classification** - `ExitedFrame`, `ContainedLikely`, `CoveredBy`, `OccludedLikely`
- **Narrative event log** - natural language descriptions for LLM evaluation
- **Per-object descriptions** - auto-generated profiles with color, shape, size, lifecycle

## Sample Results

On a 308-frame sample video (640x480 @ 30fps):

| Metric | Value |
|--------|-------|
| Objects tracked | 10 |
| Events detected | 24 (10 born, 3 lost, 2 reappeared, 9 terminated) |
| Disappearance reasons | ExitedFrame (1), ContainedLikely (2) |

## LLM Evaluation

The narrative log is designed to be fed directly to an LLM to detect violations: identity mismatches, unexplained appearances, impossible events. The sample video passes - same ball in, same ball out.
