---
title: "iValet, Intelligent Parking Lot Management"
deck: "ML-powered parking system that detects vacant spots via camera and segmentation, with a React web UI and path planning. Georgia Tech senior design."
summary: "A camera watches a parking lot, works out which spaces are free, and guides a driver to the nearest one through a web page."
period: "Jan - May 2022"
order: 6
group: "Earlier work (2021-2022, undergraduate)"
collaborators: "with Kelin Yu, Faiza Yousuf, Wei Xiong Toh"
teaser: /assets/images/ivalet-teaser.png
redirect_from:
  - /portfolio/ivalet-parking/
links:
  - title: "Project page"
    url: "https://eceseniordesign2022spring.ece.gatech.edu/sd22p37/"
  - title: "GitHub"
    url: "https://github.com/Robuddies/iValetUpdate"
---

Senior capstone project at Georgia Tech, advised by Dr. Patricio Vela. Built over two semesters as part of ECE 4872.

[Project Page (Georgia Tech)](https://eceseniordesign2022spring.ece.gatech.edu/sd22p37/){: .btn .btn--primary}
[GitHub - iValetUpdate](https://github.com/Robuddies/iValetUpdate){: .btn .btn--info}

## Overview

iValet is an intelligent parking lot management system that uses computer vision to detect vacant parking spots in real time and guides drivers to open spaces through a web interface.

## How It Works

1. **Camera feed** captures the parking lot from an overhead or angled view
2. **Image segmentation** classifies each parking spot as occupied or vacant
3. Results are stored in **PostgreSQL** for state tracking
4. A **React web UI** displays real-time lot availability and provides **path planning** to guide users to the nearest open spot

## System Components

- **Computer vision backend** - Python + OpenCV for spot detection and segmentation
- **Database** - PostgreSQL for parking state persistence
- **Web frontend** - React app showing live lot status and navigation
- **Hardware** - Raspberry Pi camera module for video capture

## Team

Built by the Robuddies team: Kelin Yu, Faiza Yousuf, Wei Xiong Toh, and Yunchu Feng.
