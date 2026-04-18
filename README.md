# Go2 FAST-LIO2 Nav2 Museum Guide

ROS 2 Humble monorepo scaffold for a Unitree Go2 indoor guidance project based on:

- Livox MID360 + IMU
- FAST-LIO2 for LiDAR-inertial odometry
- Nav2 for indoor navigation and obstacle avoidance
- A ROS 2 command bridge for Unitree Go2
- A waypoint-based museum guide manager

## Goal

Build a Go2 museum guide robot that can:

- localize indoors with LiDAR + IMU only
- navigate from one exhibit point to another
- avoid obstacles with Nav2
- execute guide routes with a simple waypoint mission manager

## Repository Layout

```text
src/
|- bringup/                    Launch files, shared config, RViz assets
|- control/
|  \- go2_cmd_bridge/          ROS 2 /cmd_vel bridge for Unitree Go2
|- navigation/
|  \- museum_guide_manager/    Waypoint mission manager for museum tours
|- perception/                 Notes and integration placeholder for FAST-LIO2
\- sensor_drivers/             Notes and integration placeholder for Livox + IMU

third_party/                   Non-ROS external dependencies
docs-CN/                       Chinese project docs
docs-EN/                       English project docs
scripts/                       Runtime helpers
runtime-data/                  Logs, maps, bags, generated runtime artifacts
```

## Planned Stack

### Phase 1

- `livox_ros_driver2`
- IMU driver
- `fastlio2`
- `pointcloud_to_laserscan`
- `slam_toolbox` localization or mapping mode
- `navigation2`
- `go2_cmd_bridge`
- `museum_guide_manager`

### Phase 2

- stronger relocalization
- better obstacle filtering for legged motion
- audio guide interaction
- multi-floor mission logic

## Quick Start

```bash
cd ~/go2_fastlio2_nav2_museum
make setup
make setup-unitree-sdk
make build
source install/setup.bash
bash scripts/init_runtime_data.sh
```

## Unitree SDK2 Python Integration

This repository now expects the official Unitree Python SDK for real Go2 motion control:

- Repo: `unitreerobotics/unitree_sdk2_python`
- Python package: `unitree_sdk2py`
- Core Go2 high-level interface used by this project:
  - `ChannelFactoryInitialize(...)`
  - `SportClient.Init()`
  - `SportClient.Move(vx, vy, wz)`
  - `SportClient.StopMove()`
  - optional `SportClient.RecoveryStand()` / `SportClient.FreeWalk()`

For a first hardware bringup:

```bash
cd ~/go2_fastlio2_nav2_museum
make setup
make setup-unitree-sdk
```

Then set `dry_run: false` in `src/bringup/config/master_params.yaml` only on the Jetson connected to the robot.

## Launch Targets

```bash
make launch-slam
make launch-nav
make launch-guide
```

## Current State

This repository is a framework scaffold. It already includes:

- ROS 2 workspace structure
- base documentation
- dependency manifest
- a Go2 command bridge skeleton
- a museum guide manager skeleton
- shared launch and parameter files

The hardware-specific Unitree SDK binding and FAST-LIO2/Nav2 runtime tuning still need to be completed on the Jetson target.
