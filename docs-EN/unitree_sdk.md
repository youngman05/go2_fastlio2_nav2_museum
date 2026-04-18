# Unitree SDK Integration

The current Go2 control bridge is built around the official Python SDK:

- Repo: `https://github.com/unitreerobotics/unitree_sdk2_python`
- Python package: `unitree_sdk2py`

## Current Integration Model

When `dry_run: false`, `go2_cmd_bridge` will attempt to:

1. call `ChannelFactoryInitialize(0, <network_interface>)`
2. create `SportClient`
3. call `SportClient.Init()`
4. convert ROS2 `/cmd_vel` into `SportClient.Move(vx, vy, wz)`
5. call `StopMove()` on watchdog timeout

## Install

Recommended on the Jetson target:

```bash
cd ~/go2_fastlio2_nav2_museum
make setup
make setup-unitree-sdk
```

The script will:

- fetch `third_party/unitree_sdk2_python`
- install `cyclonedds` prerequisites when needed
- install `unitree_sdk2py`

## Parameters

In `src/bringup/config/master_params.yaml`:

- `dry_run`: keep `true` on development machines
- `network_interface`: NIC connected to Go2, for example `eth0`
- `startup_mode`: start with `none`

Supported startup modes:

- `none`
- `stand_up`
- `free_walk`
- `recovery_stand`
- `recovery_and_free_walk`

## Safety Notes

- Do not enable aggressive startup motion for first hardware tests.
- Validate Nav2 and `/cmd_vel` in `dry_run` before enabling real motion.
- Keep the area around the robot clear before startup.
