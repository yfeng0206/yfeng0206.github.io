---
title: "Gesture-Controlled Robot Car"
date: 2021-10-01
excerpt: "Oct – Dec 2021 - Hand gesture-controlled DC motor car using OpenCV, MediaPipe, Raspberry Pi 4, and Mbed over IoT."
header:
  teaser: /assets/images/gesture-car-teaser.jpg
sidebar:
  - title: "Tech Stack"
    text: "C++, Python, OpenCV, MediaPipe, Raspberry Pi 4, Mbed LPC1768, ESP8266"
  - title: "Team"
    text: "Feng Yunchu, Faiza Yousuf, Harry Nguyen, Christine Saw"
  - title: "Course"
    text: "ECE 4180 (Georgia Tech)"
---

A hand gesture-controlled car that recognizes hand commands to perform four motions: forward, reverse, right turn, and left turn.

[View on GitHub](https://github.com/yfeng0206/Gesture-Car){: .btn .btn--primary}

## How It Works

1. **Pi Camera** captures hand gestures
2. **Raspberry Pi 4** runs OpenCV + MediaPipe to detect the number of fingers held up
3. Commands are sent over WiFi to an **ESP8266** server on the **Mbed LPC1768**
4. Mbed drives the DC motors through an H-bridge

| Fingers | Action |
|---------|--------|
| 0 | Hand not detected |
| 1 | Forward |
| 2 | Reverse |
| 3 | Right turn |
| 4 | Left turn |
| 5 | Hand detected (ready) |

## Hardware

- Raspberry Pi 4 (Model B) + Pi Camera
- Mbed LPC1768 + ESP8266 WiFi module
- 2x DC motors + dual H-bridge breakout board
- 4x LED indicators
- Shadow chassis robot base

## Demo

[Summary Video](https://www.youtube.com/watch?v=mAgygFNm7wE) |
[Demo Video](https://www.youtube.com/watch?v=9tCQLGX4CgQ)
