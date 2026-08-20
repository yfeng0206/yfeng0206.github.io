---
title: "Gesture-Controlled Robot Car"
deck: "Hand gesture-controlled DC motor car using OpenCV, MediaPipe, Raspberry Pi 4, and Mbed over WiFi."
period: "Dec 2021"
order: 7
group: "Earlier work (2021-2022, undergraduate)"
teaser: /assets/images/gesture-car-teaser.jpg
redirect_from:
  - /portfolio/gesture-car/
links:
  - title: "GitHub"
    url: "https://github.com/yfeng0206/Gesture-Car"
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
