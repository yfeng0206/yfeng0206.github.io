---
title: "Self-Driving DC Motor Car"
date: 2021-02-01
excerpt: "Feb – Jun 2021 - Autonomous DC motor car with Raspberry Pi + Arduino using OpenCV for lane detection and PID-based steering control."
header:
  teaser: /assets/images/DC_Car-teaser.png
sidebar:
  - title: "Tech Stack"
    text: "C++, Python, OpenCV4, Raspberry Pi 4, Arduino, H-bridge"
  - title: "Timeline"
    text: "Feb – Jun 2021"
---

An autonomous DC motor car that uses computer vision for real-time lane detection and PID-based motor control to follow a road.

[View on GitHub](https://github.com/yfeng0206/Self-Driving-Motor-Car-Guide){: .btn .btn--primary}

## System Architecture

- **Raspberry Pi 4** - runs the camera and OpenCV processing pipeline
- **Arduino** - handles low-level motor control via H-bridge circuitry
- **Pi Camera** - captures the road ahead in real time

## Computer Vision Pipeline

1. Capture frame from Pi Camera
2. Convert to grayscale and apply Gaussian blur
3. Canny edge detection to find lane boundaries
4. Region of interest masking to isolate the road
5. Hough line transform to extract lane lines
6. Compute steering angle from detected lane positions

## Motor Control

- Custom-soldered **H-bridge** circuit for bidirectional DC motor driving
- **PID controller** adjusts left/right motor speeds based on the steering angle error
- Supports forward, reverse, and differential turning

## Hardware

- Raspberry Pi 4 (Model B)
- Arduino Uno
- 2x DC motors + dual H-bridge
- Pi Camera module
- Shadow chassis with caster wheel
- 4xAA battery pack + USB power bank
