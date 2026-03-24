---
title: "Self-Driving DC Motor Car"
excerpt: "Autonomous DC motor car with Raspberry Pi + Arduino, using OpenCV for roadside detection."
header:
  teaser: /assets/images/selfdriving-teaser.jpg
sidebar:
  - title: "Tech Stack"
    text: "C++, OpenCV4, Raspberry Pi, Arduino, H-bridge"
  - title: "Timeline"
    text: "Feb – Jun 2021"
---

An autonomous DC motor car built with Raspberry Pi and Arduino that uses OpenCV4 (C++) for real-time roadside detection and H-bridge motor control circuitry.

[View on GitHub](https://github.com/yfeng0206/Self-Driving-Motor-Car-Guide){: .btn .btn--primary}

## Overview

This embedded systems project combines:

- **Raspberry Pi** for camera input and computer vision processing
- **Arduino** for motor control
- **OpenCV4 (C++)** for real-time roadside/lane detection
- **Soldered H-bridge** motor control circuitry for DC motor driving

The car autonomously follows road boundaries detected through the camera feed, adjusting motor speeds and direction in real time.
