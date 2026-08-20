---
title: "Reproducing V-JEPA 2-AC: What Broke, and What It Taught Us"
date: 2026-07-10
categories:
  - research
tags:
  - robotics
  - world-models
  - v-jepa
  - manipulation
  - mujoco
toc: true
toc_sticky: true
---

The plan was simple: take V-JEPA 2-AC, a frozen latent video world model, point it at a robot arm in simulation, and measure how well it plans coarse manipulation motion toward goal images. No fine-tuning, no demonstrations, just Cross-Entropy Method search over actions minimising latent distance to a goal.

The plan survived contact with reality, but almost nothing about the path to it did. This is the debugging log.

[GitHub Repo](https://github.com/yfeng0206/CopilotWorldLab){: .btn .btn--primary}

![V-JEPA 2-AC driving a Franka in MuJoCo](/assets/images/worldlab-teaser.gif)

## Both Standard Simulators Refused to Run

The obvious move is to benchmark on robosuite or ManiSkill. Neither works on a Windows box.

**robosuite 1.5.2** raises `TypeError: mj_fullM(): incompatible function arguments` on `reset()`. The cause is a binding change: robosuite calls the old two-array `mujoco.mj_fullM(model, mass_matrix, qM)`, while mujoco 3.10 requires `mj_fullM(m, d, dst)`. It is in the core dynamics path, not the OSC controller, so it fails even with the BASIC controller. robosuite 1.5.2 is the latest release and requires `mujoco>=3.3.0`, which still ships the old binding, so it only runs in a separate venv pinned to mujoco 3.3.x.

**ManiSkill 3.0.1 + SAPIEN 3.0.3** install cleanly and then fail two different ways. The `pd_ee_delta_pose` control mode raises `TypeError: 'NoneType' object is not callable` because Pinocchio, the IK backend, has no Windows wheel. Falling back to `pd_joint_delta_pos` crashes the process outright with an access violation inside the SAPIEN native sim.

So we built our own: `FrankaDroidEnv`, a Franka Panda with a Robotiq 2F-85 in MuJoCo, 7-DoF end-effector control through differential IK, real contacts, physical grasping. The embodiment choice was not arbitrary. V-JEPA 2-AC was trained on real Franka/DROID video, so matching the paper's robot is what makes a zero-shot reproduction meaningful.

Worth noting robosuite came back into the main venv afterward. Its raw-state *rendering* works fine on Windows; only closed-loop stepping is blocked.

## The 148-Second Planning Step

bf16 CEM timing was linear up to 400 samples, about 0.04 s per sample. At 800 samples the expected ~32 s became **148 s** on a 24 GB RTX 3090.

The instinct is to blame compute. A predictor-versus-pose breakdown killed that theory: the predictor was still only 31 s, the CPU pose update 1.2 s. Roughly 115 s was framework overhead, and it appeared exactly when peak memory crossed about 12 to 17 GiB.

It was allocator thrash. Once the activation working set outgrows what PyTorch's cache can serve, it falls back to synchronous `cudaMalloc`/`cudaFree` per step. Chunking the CEM sample batch through the predictor (default 200) keeps peak memory in the linear regime. Since each sample is an independent batch row, chunking is numerically identical, and we verified the planned action is unchanged. 800 samples dropped back to 32 s at 15 GiB peak.

One related trap: running the ViT-g predictor in fp32 is several times slower than bf16, because torch only dispatches fused flash and memory-efficient attention kernels for fp16/bf16. fp32 silently falls back to the slow math kernel. bf16 is the intended inference precision.

## The Camera Ablation That Found the Wrong Culprit

Grasp success was low. The natural hypotheses were that the gripper was frozen rather than planned, or that the object was too small in frame for the encoder to see.

We tested both. Enabling CEM's gripper action (`--plan-gripper`) did not help: grasp stayed around 20% either way. Moving the camera closer to roughly double the object's pixel count did not help either, with grasp stuck at 20% cup and 0% box.

The diagnostic that mattered was that the end-effector already lands about 3.4 cm in XY from the box grasp target with `held=0`. **The arm reaches correctly. The scripted close-and-lift misses.** Object salience was never the bottleneck.

Then a third camera, matching DROID's viewpoint more closely, collapsed entirely, with errors of 25 to 49 cm. That was the real finding. Changing the camera azimuth breaks the action frame, and we apply no `W*` frame correction, so the planner confidently moves the wrong way. The rule that came out of it: when changing the planning camera, keep the azimuth and elevation of the validated view and only move distance, unless you fit and apply the frame rotation. And always re-render goal images from saved `qpos_goal`, never compare a new-camera observation against an old goal PNG.

## Goal Images Are Harder Than They Look

The benchmark runs on fixed, pre-generated task bundles: a scripted expert solves each scenario once, and the saved start and goal images become the planning targets. Every ablation then runs against identical scenarios. Getting those bundles physically honest took several rounds.

**`mj_forward` does not integrate actuators.** Open-gripper and closed-gripper goal images rendered identically, because `mj_forward` computes dynamics for the current state without advancing actuators toward their targets. The 2F-85 fingers are a driven linkage; their qpos only moves when physics steps.

**Position-only moves leave the gripper tilted.** `apply_action` preserves the current end-effector orientation, so nothing ever commanded straight-down and the gripper inherited 15 to 25 degrees of drift from the random start pose. Commanding orientation explicitly at a fixed offset from the object brought tilt to about 1.3 degrees at any table position, which is the invariant that matters: the grip must be identical *relative to the object*.

**Physically releasing a one-wall rim grip is unreliable.** Opening the gripper hooks the inside finger on the cup and lifts it instead of releasing. The placed goal is now constructed directly as the intended target state, and success is scored on where the object landed plus release, not on a flaky physical release rollout.

**Two blue cubes.** A blue distractor matched the blue box manipuland. Every object now gets a distinct colour.

The meta-lesson, learned after committing 400 bundles with subtle bugs: render one bundle per task and object, inspect it in the interactive viewer, get sign-off, *then* mass-generate.

## What the Benchmark Actually Says

Five tasks x two objects x 50 fixed scenarios = 500 rollouts at paper-faithful settings.

| Task | Our success | Paper (Table 3) |
|:-----|:------------|:----------------|
| grasp | cup 38% / box 10% @6cm | 65% / 25% |
| reach_with_object | **cup 98% / box 96%** @10cm | 75% / 75% |
| grasp_and_reach | cup 18% / box 4% @10cm | custom |
| pick_place | cup 2% / box 6% @10cm | 80% / 65% |
| place_with_object | cup 80% / box 86% @10cm | custom |

`reach_with_object` beating the paper's real-robot rate is not a better controller. It is simulation: our table is a hard contact, so a light object cannot be pushed through it, and driving the gripper into the tabletop fails outright rather than tunnelling. Where the model is asked to carry something it already holds, it does very well. Where success depends on the grasp itself, everything downstream compounds, and pick-and-place falls to 1 of 50 scenarios for the cup.

## Why Any of This

The benchmark is the substrate, not the point. The thesis is that a latent world model's **own predictive energy** can serve as a competence gate: plan the variable coarse approach with the world model, and let its energy decide when to hand off to a classical, deterministic, vision-only visual servo for the precise seat.

No prior art covers that combination. V-JEPA 2-AC supplies the energy and the planner but implements no threshold or handoff. AHEAD computes predictive uncertainty and spends it truncating rollout horizon inside a frozen OpenVLA loop. VLA-JEPA uses a JEPA objective only during training, so there is no inference-time rollout at all.

The open question is whether that self-confidence signal actually predicts a failed handoff, measured as ROC AUC against a simple baseline. A negative result would be informative too, which is the main reason it is worth measuring honestly.

Full project writeup on the [project page](/portfolio/copilot-world-lab/); the complete lessons list, including the Windows and CUDA environment traps, is in [`docs/lessons_learned.md`](https://github.com/yfeng0206/CopilotWorldLab/blob/main/docs/lessons_learned.md).
