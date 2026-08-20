---
title: "Latent World Models as Coarse Manipulation Controllers"
deck: "A frozen V-JEPA 2-AC plans Franka arm motion to goal images in MuJoCo across a fixed 500-rollout benchmark. The open question is whether the model's own predictive energy predicts its failures."
period: "Jul 2026 - ongoing"
status: "Phase 1 of 4"
teaser: /assets/images/sel-world.gif
order: 2
featured: true
redirect_from:
  - /research/copilot-world-lab/
links:
  - title: "GitHub"
    url: "https://github.com/yfeng0206/CopilotWorldLab"
  - title: "Reproduction writeup"
    url: "/writing/reproducing-vjepa2-ac/"
facts:
  - title: "Stack"
    text: "PyTorch, V-JEPA 2-AC, MuJoCo, CEM-MPC, Franka Panda"
  - title: "Benchmark"
    text: "5 tasks x 2 objects x 50 fixed scenarios = 500 rollouts"
  - title: "Best result"
    text: "reach_with_object: cup 98% / box 96% @10cm"
---

A latent video world model ([V-JEPA 2-AC](https://arxiv.org/abs/2506.09985), Assran et al. 2025) plans coarse robot-arm motion by minimising distance to a goal image, and the model's own predictive energy is proposed as the confidence signal that hands off to a classical, vision-only precise controller. This repository is the Stage-1 simulation substrate.

[View on GitHub](https://github.com/yfeng0206/CopilotWorldLab){: .btn .btn--primary}

![V-JEPA 2-AC driving a Franka in MuJoCo](/assets/images/worldlab-teaser.gif)

## What This Is

We reproduce the planning result from V-JEPA 2 (§4) in our own MuJoCo environment, then evaluate it as a coarse controller across a fixed benchmark. The model is **frozen**; all motion comes from model-predictive control (greedy CEM) toward image goals. Gripper open/close is scripted at fixed stage boundaries, so the reported numbers isolate V-JEPA's spatial planning rather than a hand-tuned grasp policy. Success is judged from hidden simulator state, never from the latent energy.

## Benchmark

Five tasks x two objects (a rim-graspable cup and a rigid box) x 50 fixed scenarios = 500 rollouts, scored at paper-faithful settings (800 CEM samples, 10 refinement steps, horizon 1, maxnorm 0.075). Every configuration runs on the same saved bundles, so results are reproducible and directly comparable.

| Task | Object starts | V-JEPA plans | Our success | Paper (Table 3) |
|:-----|:--------------|:-------------|:------------|:----------------|
| grasp | on table | reach to grasp pose | cup 38% / box 10% @6cm | 65% / 25% |
| reach_with_object | held | carry to a goal | **cup 98% / box 96%** @10cm | 75% / 75% |
| grasp_and_reach | on table | grasp, then carry (2 goals) | cup 18% / box 4% @10cm | custom |
| pick_place | on table | grasp, vicinity, place (4/10/4) | cup 2% / box 6% @10cm | 80% / 65% |
| place_with_object | held | carry to zone, place (2 goals) | cup 80% / box 86% @10cm | custom |

`reach_with_object` exceeds the paper's real-robot rate, which is an honest artefact of simulation rather than a better controller: our table is a hard contact, so a light object cannot be pushed through it, and an arm that drives the gripper into the tabletop fails outright instead of tunnelling.

![Grasp rollout, success](/assets/images/worldlab-grasp-hit.gif)

Grasp misses are mostly a few-centimetre reach error before the object tips or slips. Pick-and-place compounds grasp, transport and release error, which is why it collapses to 1/50 scenarios for the cup and 3/50 for the box.

![Pick and place rollout, success](/assets/images/worldlab-pickplace-hit.gif)

## How Motion Is Produced

At each control step the model renders the current frame, runs CEM to find the single next end-effector action whose predicted next latent is closest to the goal image, executes it, and replans:

```
goal image  x_g ---------------------------> encode (frozen ViT-g) ---> z_g
current RGB x_k --> encode (frozen ViT-g) --> z_k                        |
end-effector state s_k (7-D) -----------------------------------------+ |
                                                                      v v
    CEM over action sequences  minimising  E = || P(a; s_k, z_k) - z_g ||_1
                                                                      |
                       execute first action only, re-plan (receding horizon)
```

The energy landscape is locally convex near the goal, so greedy descent walks the arm to the target, a learned form of visual servoing. Compositional tasks follow a fixed sub-goal schedule switched by time index (pick-and-place: 4/10/4), reproduced from the paper.

## Why a Franka, and Why Fixed Bundles

The embodiment is deliberate. V-JEPA 2-AC was trained on real Franka/DROID video, so matching the paper's embodiment is what makes a zero-shot sim reproduction meaningful. `FrankaDroidEnv` is a real 7-DoF arm with differential IK, contacts and a Robotiq 2F-85 gripper, so grasping is physical rather than a kinematic toy.

Scenarios are **not** randomised per trial. A scripted expert generates each scenario once, validates that it is solvable, and saves it. Every ablation axis (CEM population, frame calibration, fine-tuned predictor) is then scored on the identical scenarios, and every rollout records a continuous error so success at any precision threshold can be recomputed from the same run.

## The Actual Research Question

The benchmark is not the point; it is the substrate. The thesis being tested is that a latent world model's **own predictive energy** is a usable competence gate: use the world model for the variable coarse approach, and let its energy tell you when to hand off to a classical, deterministic, vision-only visual servo for the precise seat.

No prior art was found for that combination. V-JEPA 2-AC provides the energy and the CEM planner but implements no confidence threshold or handoff. AHEAD computes predictive uncertainty but spends it truncating rollout horizon inside a frozen OpenVLA loop. VLA-JEPA uses a JEPA objective only at training time. The gate is the clean novelty boundary.

The central measured question is whether that self-confidence signal reliably predicts a failed handoff, reported as ROC AUC against a simple baseline. A negative result is itself informative.

## Roadmap

| Phase | Content | State |
|:------|:--------|:------|
| 0 | Load V-JEPA 2-AC, build a paper-faithful MuJoCo env, reproduce the world model | done |
| 1 | Fixed-bundle closed-loop benchmark (5 tasks x cup/box x 50) | current |
| 2 | POV/wrist CNN coarse-to-fine handoff | planned |
| 3 | Third- + first-person cross-attention latent | planned |
| 4 | Unified cross-view latent | planned |

Downstream this feeds a self-driving-lab labware insertion application, where the simulated Franka gives way to a UR7e with a RealSense D405 wrist camera.

More on GitHub: [design and novelty claim](https://github.com/yfeng0206/CopilotWorldLab/blob/main/docs/DESIGN.md), [benchmark methodology](https://github.com/yfeng0206/CopilotWorldLab/blob/main/docs/experiments/closed_loop_benchmark.md), [experiments index](https://github.com/yfeng0206/CopilotWorldLab/tree/main/docs/experiments), [research log](https://github.com/yfeng0206/CopilotWorldLab/blob/main/docs/research_log.md).
