---
title: "iValet - Intelligent Parking Lot Management System"
date: 2022-01-01
excerpt: "Jan – May 2022 - ML-powered parking system that detects vacant spots via camera + segmentation, with a React web UI and path planning."
header:
  teaser: /assets/images/ivalet-teaser.png
sidebar:
  - title: "Tech Stack"
    text: "Python, OpenCV, React, PostgreSQL, Raspberry Pi"
  - title: "Team"
    text: "Kelin Yu, Faiza Yousuf, Wei Xiong Toh, Yunchu Feng"
  - title: "Advisor"
    text: "Dr. Patricio Vela"
  - title: "Course"
    text: "ECE 4872 Senior Design (Georgia Tech, Spring 2022)"
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
